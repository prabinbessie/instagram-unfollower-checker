"""
Instagram Unfollower Analyzer v3.1.2
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
    'size_limit': "File size exceeds 5MB limit",
    'same_files': "You uploaded the same file for both following and followers"
}

class InstagramAnalyzer:
    """
    Core analyzer class with HTML/JSON support
    """
    
    @staticmethod
    def validate_files(files):
        """Enhanced file validation"""
        required = {'following', 'followers'}
        if not required.issubset(files):
            raise ValueError(ERROR_MESSAGES['missing_files'])
        if files['following'].filename == files['followers'].filename:
            raise ValueError(ERROR_MESSAGES['same_files'])
            
        for f in files.values():
            if not f or f.filename == '':
                raise ValueError(ERROR_MESSAGES['empty_file'])
            
            ext = f.filename.rsplit('.', 1)[-1].lower()
            if ext not in ('json', 'html'):
                raise ValueError(ERROR_MESSAGES['invalid_file'])
            f.stream.seek(0, os.SEEK_END)
            size = f.stream.tell()
            f.stream.seek(0)
            if size > 5 * 1024 * 1024:  # 5MB
                raise ValueError(ERROR_MESSAGES['size_limit'])

    @classmethod
    def detect_file_type(cls, filename):
        """Determine file type from extension"""
        return filename.rsplit('.', 1)[-1].lower()

    @classmethod
    def _auto_detect_files(cls, following_file, followers_file):
        """Enhanced file detection with multiple strategies"""
        names = {
            'following': following_file.filename.lower(),
            'followers': followers_file.filename.lower()
        }
        scores = {
            'following': names['following'].count('following') * 2,
            'followers': names['followers'].count('followers') * 2
        }

        try:
            def peek_file(f):
                pos = f.stream.tell()
                data = json.load(f.stream)
                f.stream.seek(pos)
                return data
                
            if cls.detect_file_type(following_file.filename) == 'json':
                following_data = peek_file(following_file)
                if 'relationships_followers' in following_data:
                    return (followers_file, following_file)
        except:
            pass

        if scores['followers'] > scores['following']:
            return (followers_file, following_file)
        return (following_file, followers_file)

    @classmethod
    def parse_html(cls, file_stream):
        """Parse Instagram HTML files"""
        try:
            soup = BeautifulSoup(file_stream.read(), 'html.parser')
            users = []
            for div in soup.select('div.pam._3-95._2ph-._a6-g.uiBoxWhite.noborder'):
                link = div.find('a', href=lambda x: x and 'instagram.com' in x)
                if link:
                    username = link['href'].rstrip('/').split('/')[-1]
                    users.append(username)
            return sorted(set(users))
        except Exception as e:
            raise ValueError(f"HTML parsing error: {e}")

    @classmethod
    def parse_json(cls, file_stream):
        """Improved JSON parsing with structure detection"""
        try:
            data = json.load(file_stream)
            users = []
            
            if isinstance(data, list):
                entries = data  
            elif 'relationships_following' in data:
                entries = data['relationships_following']  # following.json
            elif 'relationships_followers' in data:
                entries = data['relationships_followers']  # followers.json
            else:
                raise ValueError("Unsupported JSON structure")
            
            for item in entries:
                if 'string_list_data' in item:
                    users.append(item['string_list_data'][0]['value'])
            return sorted(set(users))
        except Exception as e:
            raise ValueError(f"JSON parsing error: {e}")

    @classmethod
    def process_file(cls, file_storage):
        """Process either HTML or JSON file with stream reset"""
        file_type = cls.detect_file_type(file_storage.filename)
        try:
            file_storage.stream.seek(0)
            if file_type == 'html':
                return cls.parse_html(file_storage.stream)
            elif file_type == 'json':
                return cls.parse_json(file_storage.stream)
            else:
                raise ValueError(ERROR_MESSAGES['invalid_file'])
        except Exception as e:
            raise ValueError(f"File processing error: {e}")
        finally:
            file_storage.stream.seek(0)

    @classmethod
    def get_non_followers(cls, following_file, followers_file):
        """Smart file handling with fallback"""
        try:
            orig_following = cls.process_file(following_file)
            orig_followers = cls.process_file(followers_file)
            
            processed_following, processed_followers = cls._auto_detect_files(following_file, followers_file)
            auto_following = cls.process_file(processed_following)
            auto_followers = cls.process_file(processed_followers)
            
            if len(auto_following) > len(auto_followers):
                final_following = auto_following
                final_followers = auto_followers
            else:
                final_following = orig_following
                final_followers = orig_followers

            non_followers = set(final_following) - set(final_followers)
        except Exception as e:
            app.logger.error(f"Comparison error: {e}")
            non_followers = set(orig_following) - set(orig_followers)

        return [
            {
                'id': i + 1,
                'username': user,
                'profile_url': f"https://www.instagram.com/{user}/"
            }
            for i, user in enumerate(sorted(non_followers))
        ]


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
        app.logger.error(f"Analysis error: {e}")
        return jsonify(error=str(e)), 400


@app.route('/analyze/pdf', methods=['POST'])
def analyze_pdf():
    try:
        InstagramAnalyzer.validate_files(request.files)
        non_followers = InstagramAnalyzer.get_non_followers(
            request.files['following'],
            request.files['followers']
        )

        if not non_followers:
            return jsonify(error="No non-followers to generate PDF"), 400

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()

        elements = create_pdf_elements(non_followers, styles)
        doc.build(elements)

        buffer.seek(0)
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f"instagram_non_followers_{int(time.time())}.pdf",
            mimetype='application/pdf'
        )
    except Exception as e:
        app.logger.error(f"PDF error: {e}")
        return jsonify(error=str(e)), 400


def create_pdf_elements(non_followers, styles):
    """Modular PDF creation with error handling"""
    elements = []
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
    data = [["#", "Username", "Profile Link"]]
    for user in non_followers:
        data.append([
            str(user['id']),
            user['username'],
            Paragraph(
                f"<a href='{user['profile_url']}'>{user['profile_url']}</a>", 
                styles['ProfileLink']
            )
        ])
    
    # Table styling
    table = Table(data, colWidths=[40, 120, 340])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#F8F9FA")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#E1306C")),
        ('ALIGN',    (0, 0), (-1, -1), 'LEFT'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID',     (0, 0), (-1, -1), 1, colors.lightgrey),
    ]))
    elements.append(table)

    return elements  


@app.after_request
def add_security_headers(response):
    headers = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "Access-Control-Expose-Headers": "Content-Disposition",
        "Content-Security-Policy": "default-src 'self'",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains"
    }
    response.headers.update(headers)
    return response


@app.errorhandler(413)
def handle_file_too_large(error):
    return jsonify(error=ERROR_MESSAGES['size_limit']), 413


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
