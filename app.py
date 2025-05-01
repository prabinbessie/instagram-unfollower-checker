import os
import json
import time
from io import BytesIO
from flask import Flask, request, send_file, jsonify
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from flask import Flask, request, send_file, jsonify, render_template 

app = Flask(__name__)
app.config.update(
    MAX_CONTENT_LENGTH=2 * 1024 * 1024,  # 2MB limit
    SECRET_KEY=os.environ.get('SECRET_KEY', os.urandom(24).hex()),
    JSON_AS_ASCII=False
)

class InstagramAnalyzer:
    @staticmethod
    def validate_files(files):
        if 'following' not in files or 'followers' not in files:
            raise ValueError("Both files are required")
            
        following = files['following']
        followers = files['followers']
        
        if not (following and followers):
            raise ValueError("Empty file upload detected")
            
        if not (following.filename.endswith('.json') and 
                followers.filename.endswith('.json')):
            raise ValueError("Only JSON files are allowed")

    @staticmethod
    def process_file(file):
        try:
            data = json.load(file)
            return data
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format in uploaded file")
        except Exception as e:
            raise ValueError(f"File processing error: {str(e)}")

    @staticmethod
    def extract_users(data, key):
        users = []
        for item in data.get(key, []):
            try:
                if isinstance(item, dict) and item.get('string_list_data'):
                    users.append(item['string_list_data'][0]['value'])
            except (KeyError, IndexError, TypeError):
                continue
        return sorted(list(set(users)))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        # Validate request
        analyzer = InstagramAnalyzer()
        analyzer.validate_files(request.files)
        
        # Process files
        following_data = analyzer.process_file(request.files['following'])
        followers_data = analyzer.process_file(request.files['followers'])
        
        # Extract users
        following = analyzer.extract_users(following_data, "relationships_following")
        followers = analyzer.extract_users(followers_data, "relationships_followers")
        
        # Compare lists
        non_followers = list(set(following) - set(followers))
        
        # Generate PDF
        pdf_buffer = BytesIO()
        pdf = canvas.Canvas(pdf_buffer, pagesize=letter)
        
        # PDF Content
        pdf.setTitle("Instagram Unfollower Report")
        pdf.setFont("Helvetica-Bold", 18)
        pdf.drawString(72, 750, "Instagram Unfollower Report")
        
        # Create table
        data = [[i+1, user] for i, user in enumerate(non_followers)]
        table = Table(data, colWidths=[50, 450])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F8F9FA")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor("#E1306C")),
            ('GRID', (0,0), (-1,-1), 1, colors.lightgrey),
        ]))
        table.wrapOn(pdf, 0, 0)
        table.drawOn(pdf, 72, 700)
        
        pdf.save()
        pdf_buffer.seek(0)
        
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=f"unfollowers_report_{int(time.time())}.pdf",
            mimetype='application/pdf'
        )

    except Exception as e:
        app.logger.error(f"Error: {str(e)}")
        return jsonify(error=str(e)), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))