"""
Instagram Unfollower Analyzer v3
"""
import os
import json
import sys
import time
import logging
from io import BytesIO
from flask import Flask, request, send_file, jsonify, render_template
from bs4 import BeautifulSoup
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

app = Flask(__name__)
app.config.update(
    MAX_CONTENT_LENGTH=5 * 1024 * 1024,  # 5MB limit
    SECRET_KEY=os.environ.get('SECRET_KEY', os.urandom(24).hex()),
    JSON_AS_ASCII=False
)

# Configure logging
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
app.logger = logging.getLogger('InstagramUnfollowerChecker')

ERROR_MESSAGES = {
    'missing_files': "Please upload both following and followers files",
    'invalid_file': "Invalid file format. We support JSON and HTML files from Instagram",
    'empty_file': "Uploaded file appears to be empty",
    'processing_error': "Error processing your request",
    'size_limit': "File size exceeds 5MB limit"
}

class InstagramAnalyzer:
    """
    Core analyzer class with HTML/JSON support
    """
    
    @staticmethod
    def validate_files(files):
        """Validate uploaded files meet requirements"""
        required = {'following', 'followers'}
        if not required.issubset(files):
            raise ValueError(ERROR_MESSAGES['missing_files'])
            
        for f in files.values():
            if not f or f.filename == '':
                raise ValueError(ERROR_MESSAGES['empty_file'])
            
            ext = f.filename.split('.')[-1].lower()
            if ext not in ('json', 'html'):
                raise ValueError(ERROR_MESSAGES['invalid_file'])

    @classmethod
    def detect_file_type(cls, filename):
        """Determine file type from extension"""
        return filename.split('.')[-1].lower()

    @classmethod
    def parse_html(cls, file_stream):
        """Parse Instagram HTML files"""
        try:
            soup = BeautifulSoup(file_stream.read(), 'html.parser')
            users = []
            for div in soup.select('div.pam._3-95._2ph-._a6-g.uiBoxWhite.noborder'):
                link = div.find('a', href=lambda x: x and 'instagram.com' in x)
                if link:
                    username = link['href'].split('/')[-1]
                    users.append(username)
            return sorted(set(users))
        except Exception as e:
            raise ValueError(f"HTML parsing error: {str(e)}")

    @classmethod
    def parse_json(cls, file_stream):
        """Parse Instagram JSON files"""
        try:
            data = json.load(file_stream)
            users = []
            
            # Handle different JSON structures
            if isinstance(data, list):
                entries = data
            elif 'relationships_following' in data:
                entries = data['relationships_following']
            elif 'relationships_followers' in data:
                entries = data['relationships_followers']
            else:
                entries = []
            
            for item in entries:
                if 'string_list_data' in item:
                    users.append(item['string_list_data'][0]['value'])
            return sorted(set(users))
        except Exception as e:
            raise ValueError(f"JSON parsing error: {str(e)}")

    @classmethod
    def process_file(cls, file_storage):
        """Process either HTML or JSON file"""
        file_type = cls.detect_file_type(file_storage.filename)
        file_stream = file_storage.stream
        
        if file_type == 'html':
            return cls.parse_html(file_stream)
        elif file_type == 'json':
            return cls.parse_json(file_stream)
        else:
            raise ValueError(ERROR_MESSAGES['invalid_file'])

    @classmethod
    def get_non_followers(cls, following_file, followers_file):
        """Main analysis method"""
        following = cls.process_file(following_file)
        followers = cls.process_file(followers_file)
        return [{
            'id': i+1,
            'username': user,
            'profile_url': f"https://www.instagram.com/{user}"
        } for i, user in enumerate(set(following) - set(followers))]

    @staticmethod
    def print_version():
        print(f"instagram-unfollow-checker v{__version__}")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze/json', methods=['POST'])
def analyze_json():
    try:
        InstagramAnalyzer.validate_files(request.files)
        non_followers = InstagramAnalyzer.get_non_followers(
            request.files['following'],
            request.files['followers']
        )
        return jsonify({
            'count': len(non_followers),
            'results': non_followers
        })
    except Exception as e:
        app.logger.error(f"Analysis error: {str(e)}")
        return jsonify(error=str(e)), 400

@app.route('/analyze/pdf', methods=['POST'])
def analyze_pdf():
    try:
        InstagramAnalyzer.validate_files(request.files)
        non_followers = InstagramAnalyzer.get_non_followers(
            request.files['following'],
            request.files['followers']
        )

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []

        # Custom styles
        styles.add(ParagraphStyle(
            name='ProfileLink',
            textColor=colors.HexColor('#E1306C'),
            fontSize=10,
            leading=14
        ))

        # Header
        elements.append(Paragraph("Instagram Non-Followers Report", styles['Title']))
        elements.append(Spacer(1, 24))

        # Table data
        if non_followers:
            data = [["#", "Username", "Profile Link"]]
            for user in non_followers:
                data.append([
                    str(user['id']),
                    user['username'],
                    Paragraph(f"<a href='{user['profile_url']}'>{user['profile_url']}</a>", 
                            styles['ProfileLink'])
                ])
            col_widths = [40, 120, 340]
        else:
            data = [["All your follows are mutual! 🎉"]]
            col_widths = [500]

        # Table styling
        table = Table(data, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F8F9FA")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor("#E1306C")),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTSIZE', (0,0), (-1,0), 12),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('GRID', (0,0), (-1,-1), 1, colors.lightgrey),
        ]))
        elements.append(table)

        doc.build(elements)
        buffer.seek(0)
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f"instagram_non_followers_{int(time.time())}.pdf",
            mimetype='application/pdf'
        )
    except Exception as e:
        app.logger.error(f"PDF error: {str(e)}")
        return jsonify(error=str(e)), 400

@app.after_request
def add_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    return response

@app.errorhandler(413)
def handle_file_too_large(error):
    return jsonify(error=ERROR_MESSAGES['size_limit']), 413

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))