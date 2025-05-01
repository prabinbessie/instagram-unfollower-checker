import os
import json
import time
from io import BytesIO
from flask import Flask, render_template, request, send_file, flash
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.platypus import Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER

app = Flask(__name__)
app.secret_key = os.urandom(24).hex()  # For flash messages

def extract_usernames(json_data, key):
    """Extract usernames from Instagram JSON structure"""
    return [item['string_list_data'][0]['value'] 
            for item in json_data.get(key, [])
            if item.get('string_list_data')]

@app.route('/', methods=['GET'])
def home():
    """Render main page"""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        # Validate files
        if 'following' not in request.files or 'followers' not in request.files:
            flash('Please upload both files')
            return render_template('index.html'), 400
            
        following_file = request.files['following']
        followers_file = request.files['followers']
        
        # Process JSON data
        following_data = json.load(following_file)
        followers_data = json.load(followers_file)
        
        # Extract usernames
        following = extract_usernames(following_data, "relationships_following")
        followers = extract_usernames(followers_data, "relationships_followers")
        
        # Find non-followers
        non_followers = sorted([user for user in following if user not in followers])
        
        # Generate PDF
        buffer = generate_pdf_report(non_followers)
        
        # Return PDF
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f"unfollowers_report_{int(time.time())}.pdf",
            mimetype="application/pdf"
        )
        
    except json.JSONDecodeError:
        flash('Invalid JSON files - please upload original Instagram data')
        return render_template('index.html'), 400
    except KeyError as e:
        flash(f'Invalid file structure: {str(e)}')
        return render_template('index.html'), 400
    except Exception as e:
        app.logger.error(f'Error processing request: {str(e)}')
        flash('An unexpected error occurred. Please try again.')
        return render_template('index.html'), 500

def generate_pdf_report(users):
    """Generate professional PDF report"""
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    styles = getSampleStyleSheet()
    
    # Custom Styles
    styles.add(ParagraphStyle(
        name='Header',
        fontSize=24,
        leading=30,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#E1306C')
    ))
    
    # Header Section
    pdf.setAuthor("Instagram Unfollower Checker")
    header = Paragraph("Instagram Unfollower Report", styles['Header'])
    header.wrapOn(pdf, width-100, height)
    header.drawOn(pdf, 50, height-100)
    
    # Metadata
    pdf.setFont("Helvetica", 10)
    pdf.drawString(50, height-140, f"Report generated: {time.strftime('%d %b %Y %H:%M')}")
    pdf.drawString(50, height-160, f"Total unfollowers found: {len(users)}")
    
    # Content
    y_position = height-200
    for idx, user in enumerate(users, 1):
        text = f"{idx}. {user}"
        pdf.setFont("Helvetica", 12)
        pdf.drawString(72, y_position, text)
        y_position -= 20
        
        if y_position < 100:
            pdf.showPage()
            y_position = height-100
            
    pdf.save()
    buffer.seek(0)
    return buffer

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
