
"""
Instagram Unfollower Analyzer
-----------------------------
A Flask application to identify users who don't follow you back on Instagram.
"""

from version import __version__
import os
import json
import sys
import time
import logging
from io import BytesIO
from flask import Flask, request, send_file, jsonify, render_template
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

app = Flask(__name__)
app.config.update(
    MAX_CONTENT_LENGTH=2 * 1024 * 1024,  # 2MB limit
    SECRET_KEY=os.environ.get('SECRET_KEY', os.urandom(24).hex()),
    JSON_AS_ASCII=False
)

# Configure logging
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.DEBUG)

ERROR_MESSAGES = {
    'missing_files': "Please upload both following.json and followers.json files",
    'invalid_json': "The file contains invalid JSON formatting",
    'empty_file': "Uploaded file appears to be empty",
    'invalid_extension': "Only JSON files are allowed",
    'processing_error': "Error processing your request"
}

class InstagramAnalyzer:
    """
    Core analyzer class for processing Instagram follower data
    """
    
    @staticmethod
    def validate_files(files):
        """Validate uploaded files meet requirements"""
        if 'following' not in files or 'followers' not in files:
            raise ValueError(ERROR_MESSAGES['missing_files'])
            
        f = files['following']
        u = files['followers']
        
        if not (f and u):
            raise ValueError(ERROR_MESSAGES['empty_file'])
            
        if not (f.filename.lower().endswith('.json') and 
                u.filename.lower().endswith('.json')):
            raise ValueError(ERROR_MESSAGES['invalid_extension'])

    @staticmethod
    def process_file(file_storage):
        """Load and validate JSON data from file"""
        try:
            return json.load(file_storage)
        except json.JSONDecodeError:
            raise ValueError(ERROR_MESSAGES['invalid_json'])

    @staticmethod
    def extract_users(data, key):
        """Extract usernames from Instagram data structure"""
        users = []
        if isinstance(data, list):
            for container in data:
                if key in container:
                    entries = container.get(key, [])
                else:
                    entries = [container] if 'string_list_data' in container else []
                
                for item in entries:
                    try:
                        users.append(item['string_list_data'][0]['value'])
                    except (KeyError, IndexError, TypeError):
                        continue
        elif isinstance(data, dict):
            entries = data.get(key, [])
            for item in entries:
                try:
                    users.append(item['string_list_data'][0]['value'])
                except (KeyError, IndexError, TypeError):
                    continue
                
        return sorted(set(users))

    @classmethod
    def get_non_followers(cls, following_file, followers_file):
        """Calculate list of users who don't follow back"""
        following_data = cls.process_file(following_file)
        followers_data = cls.process_file(followers_file)
        
        following = cls.extract_users(following_data, 'relationships_following')
        followers = cls.extract_users(followers_data, 'relationships_followers')
        
        return list(set(following) - set(followers))

    @staticmethod
    def print_version():
        """Print the version of the application."""
        print(f"instagram-unfollow-checker-py v{__version__}")

if "--version" in sys.argv:
    InstagramAnalyzer.print_version()
    sys.exit(0)

@app.route('/')
def home():
    """Render main interface"""
    return render_template('index.html')

@app.route('/analyze/json', methods=['POST'])
def analyze_json():
    """JSON API endpoint for non-follower analysis"""
    try:
        InstagramAnalyzer.validate_files(request.files)
        non_followers = InstagramAnalyzer.get_non_followers(
            request.files['following'],
            request.files['followers']
        )
        result = [{'id': i+1, 'username': user} 
                 for i, user in enumerate(non_followers)]
        return jsonify(non_followers=result)
        
    except Exception as e:
        app.logger.error(f"Error processing request: {str(e)}")
        return jsonify(error=str(e)), 400

@app.route('/analyze/pdf', methods=['POST'])
def analyze_pdf():
    """Generate PDF report of non-followers"""
    try:
        InstagramAnalyzer.validate_files(request.files)
        non_followers = InstagramAnalyzer.get_non_followers(
            request.files['following'],
            request.files['followers']
        )

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()

        # Build report title
        elements.append(Paragraph("Instagram Unfollower Report", styles['Title']))
        elements.append(Spacer(1, 20))

        # Prepare table data
        if non_followers:
            data = [["#", "Username"]] + [
                [str(i+1), user] for i, user in enumerate(non_followers)
            ]
            col_widths = [50, 450]
        else:
            data = [["No non-followers found"]]
            col_widths = [500]

        # Configure table styling
        table = Table(data, colWidths=col_widths)
        table_style = TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F8F9FA")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor("#E1306C")),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTSIZE', (0,0), (-1,0), 12),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('GRID', (0,0), (-1,-1), 1, colors.lightgrey),
        ])
        
        if not non_followers:
            table_style.add('SPAN', (0,0), (-1,0))
            
        table.setStyle(table_style)
        elements.append(table)

        doc.build(elements)
        buffer.seek(0)

        return send_file(
            buffer,
            as_attachment=True,
            download_name=f"unfollowers_report_{int(time.time())}.pdf",
            mimetype='application/pdf'
        )
        
    except Exception as e:
        app.logger.error(f"PDF generation error: {str(e)}")
        return jsonify(error=str(e)), 400

@app.after_request
def add_security_headers(response):
    """Add security headers to all responses"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response

@app.errorhandler(413)
def handle_file_too_large(error):
    """Handle file size limit errors"""
    return jsonify(error=ERROR_MESSAGES['processing_error']), 413

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))