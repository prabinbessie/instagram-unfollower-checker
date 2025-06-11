"""
Instagram Unfollower Analyzer v4
"""
import os
import json
import sys
import time
import logging
import csv
from collections import Counter
from datetime import datetime
from io import BytesIO
from flask import Flask, request, jsonify, send_file, render_template
from bs4 import BeautifulSoup
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from version import __version__


app = Flask(__name__, template_folder='templates')
app.config.update(
    MAX_CONTENT_LENGTH=5 * 1024 * 1024,  # 5MB limit
    SECRET_KEY=os.environ.get('SECRET_KEY', os.urandom(24).hex()),
    JSON_AS_ASCII=False
)

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
app.logger = logging.getLogger('InstagramUnfollowerChecker')

ERROR_MESSAGES = {
    'missing_files':    "Please upload both following and followers files",
    'invalid_file':     "Invalid file format. We support JSON and HTML files from Instagram",
    'empty_file':       "Uploaded file appears to be empty",
    'size_limit':       "File size exceeds 5MB limit",
    'same_files':       "You uploaded the same file for both following and followers"
}

@app.context_processor
def inject_version():
    return dict(version=__version__)

class InstagramAnalyzer:
    @staticmethod
    def validate_files(files):
        """Enhanced file validation"""
        required = {'following', 'followers'}
        if not required.issubset(files):
            raise ValueError(ERROR_MESSAGES['missing_files'])
        f1, f2 = files['following'], files['followers']
        if f1.filename == f2.filename:
            raise ValueError(ERROR_MESSAGES['same_files'])
        for f in (f1, f2):
            if not f or not f.filename:
                raise ValueError(ERROR_MESSAGES['empty_file'])
            
            ext = f.filename.rsplit('.', 1)[-1].lower()
            if ext not in ('json', 'html'):
                raise ValueError(ERROR_MESSAGES['invalid_file'])
            f.stream.seek(0, os.SEEK_END)
            if f.stream.tell() > 5 * 1024 * 1024:
                raise ValueError(ERROR_MESSAGES['size_limit'])
            f.stream.seek(0)

    @staticmethod
    def detect_file_type(name):
        return name.rsplit('.', 1)[-1].lower()

    @classmethod
    def _auto_detect_files(cls, f1, f2):
        n1, n2 = f1.filename.lower(), f2.filename.lower()
        if n2.count('following') > n2.count('followers'):
            return f2, f1
        # peek JSON
        try:
            data = json.load(f1.stream)
            f1.stream.seek(0)
            if isinstance(data, dict) and 'relationships_followers' in data:
                return f2, f1
        except Exception:
            f1.stream.seek(0)
        return f1, f2

    @classmethod
    def parse_html(cls, stream):
        soup = BeautifulSoup(stream.read(), 'html.parser')
        users = {
            a['href'].rstrip('/').split('/')[-1]
            for a in soup.select(
                'div.pam._3-95._2ph-._a6-g.uiBoxWhite.noborder a[href*="instagram.com"]'
            )
        }
        return sorted(users)

    @classmethod
    def parse_json(cls, stream):
        data = json.load(stream)
        stream.seek(0)
        if isinstance(data, dict):
            entries = data.get('relationships_following') or data.get('relationships_followers') or []
        elif isinstance(data, list):
            entries = data
        else:
            entries = []
        return sorted({
            itm['string_list_data'][0]['value']
            for itm in entries if itm.get('string_list_data')
        })

    @classmethod
    def process_file(cls, f):
        f.stream.seek(0)
        if cls.detect_file_type(f.filename) == 'html':
            return cls.parse_html(f.stream)
        return cls.parse_json(f.stream)

    @classmethod
    def get_non_followers(cls, f1, f2):
        # auto-swap if needed
        fol, folr = cls._auto_detect_files(f1, f2)
        following = cls.process_file(fol)
        followers = cls.process_file(folr)
        diff = sorted(set(following) - set(followers))
        return [
            {'id': i+1, 'username': u, 'profile_url': f"https://www.instagram.com/{u}"}
            for i, u in enumerate(diff)
        ]
    @classmethod
    def get_detailed_analysis(cls, f1, f2):
        """Enhanced analysis with detailed statistics"""
        fol, folr = cls._auto_detect_files(f1, f2)
        following = cls.process_file(fol)
        followers = cls.process_file(folr)

        following_set = set(following)
        followers_set = set(followers)

        non_followers = sorted(following_set - followers_set)
        not_following_back = sorted(followers_set - following_set)
        mutual_followers = sorted(following_set & followers_set)

        # Calculate ratios
        total_following = len(following)
        total_followers = len(followers)
        mutual_count = len(mutual_followers)

        follow_back_ratio = (mutual_count / total_following * 100) if total_following > 0 else 0
        follower_ratio = (total_followers / total_following) if total_following > 0 else 0

        return {
            'summary': {
                'total_following': total_following,
                'total_followers': total_followers,
                'mutual_followers': mutual_count,
                'non_followers': len(non_followers),
                'not_following_back': len(not_following_back),
                'follow_back_ratio': round(follow_back_ratio, 2),
                'follower_ratio': round(follower_ratio, 2)
            },
            'lists': {
                'non_followers': [
                    {'id': i+1, 'username': u, 'profile_url': f"https://www.instagram.com/{u}"}
                    for i, u in enumerate(non_followers)
                ],
                'not_following_back': [
                    {'id': i+1, 'username': u, 'profile_url': f"https://www.instagram.com/{u}"}
                    for i, u in enumerate(not_following_back)
                ],
                'mutual_followers': [
                    {'id': i+1, 'username': u, 'profile_url': f"https://www.instagram.com/{u}"}
                    for i, u in enumerate(mutual_followers[:100])  # Limit for performance
                ]
            },
            'charts': {
                'relationship_breakdown': {
                    'mutual': mutual_count,
                    'non_followers': len(non_followers),
                    'not_following_back': len(not_following_back)
                },
                'follow_ratios': {
                    'following': total_following,
                    'followers': total_followers,
                    'mutual': mutual_count
                }
            }
        }

    @staticmethod
    def export_to_csv(data_list, filename_prefix):
        """Export user list to CSV format"""
        output = BytesIO()

        # Convert BytesIO to text mode for CSV writer
        text_stream = io.TextIOWrapper(output, encoding='utf-8', newline='')

        writer = csv.writer(text_stream)
        writer.writerow(['ID', 'Username', 'Profile URL'])

        for user in data_list:
            writer.writerow([user['id'], user['username'], user['profile_url']])

        text_stream.flush()
        output.seek(0)

        return output



@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze/json', methods=['POST'])
def analyze_json():
    try:
        InstagramAnalyzer.validate_files(request.files)
        nf = InstagramAnalyzer.get_non_followers(
            request.files['following'], request.files['followers']
        )
        return jsonify({'count': len(nf), 'results': nf})
    except Exception as e:
        app.logger.error(f"Analysis error: {e}")
        return jsonify(error=str(e)), 400

@app.route('/analyze/pdf', methods=['POST'])
def analyze_pdf():
    try:
        InstagramAnalyzer.validate_files(request.files)
        nf = InstagramAnalyzer.get_non_followers(
            request.files['following'], request.files['followers']
        )
        if not nf:
            return jsonify(error="No non-followers to generate PDF"), 400

        buf = BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=letter)
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(
            name='ProfileLink',
            textColor=colors.HexColor('#E1306C'),
            fontSize=10,
            leading=14
        ))
        elems = [Paragraph("Instagram Non-Followers Report", styles['Title']), Spacer(1, 24)]

        table_data = [["#", "Username", "Profile Link"]] + [
            [str(u['id']), u['username'],
             Paragraph(f"<a href='{u['profile_url']}'>{u['profile_url']}</a>", styles['ProfileLink'])]
            for u in nf
        ]
        tbl = Table(table_data, colWidths=[40, 120, 340])
        tbl.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F8F9FA")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor("#E1306C")),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('GRID', (0,0), (-1,-1), 1, colors.lightgrey),
        ]))
        elems.append(tbl)
        doc.build(elems)
        buf.seek(0)

        return send_file(buf, as_attachment=True,
                         download_name=f"instagram_non_followers_{int(time.time())}.pdf",
                         mimetype='application/pdf')
    except Exception as e:
        app.logger.error(f"PDF error: {e}")
        return jsonify(error=str(e)), 400
@app.route('/analyze/detailed', methods=['POST'])
def analyze_detailed():
    """Enhanced analysis endpoint with detailed statistics"""
    try:
        InstagramAnalyzer.validate_files(request.files)
        
        analysis = InstagramAnalyzer.get_detailed_analysis(
            request.files['following'], 
            request.files['followers']
        )
        
        return jsonify({
            'success': True,
            'analysis': analysis,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        app.logger.error(f"Detailed analysis error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/analyze/csv', methods=['POST'])
def analyze_csv():
    """CSV export endpoint"""
    try:
        export_type = request.form.get('export_type', 'non_followers')
        
        InstagramAnalyzer.validate_files(request.files)
        
        analysis = InstagramAnalyzer.get_detailed_analysis(
            request.files['following'], 
            request.files['followers']
        )
        
        # Get the requested data list
        data_lists = {
            'non_followers': analysis['lists']['non_followers'],
            'not_following_back': analysis['lists']['not_following_back'],
            'mutual_followers': analysis['lists']['mutual_followers'],
            'all_following': analysis['lists']['non_followers'] + analysis['lists']['mutual_followers']
        }
        
        if export_type not in data_lists:
            return jsonify({'error': 'Invalid export type'}), 400
            
        data_list = data_lists[export_type]
        
        if not data_list:
            return jsonify({'error': f'No data available for {export_type}'}), 400
        
        # Create CSV
        csv_buffer = InstagramAnalyzer.export_to_csv(data_list, export_type)
        
        filename = f"instagram_{export_type}_{int(time.time())}.csv"
        
        return send_file(
            csv_buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='text/csv'
        )
        
    except Exception as e:
        app.logger.error(f"CSV export error: {e}")
        return jsonify({'error': str(e)}), 400

@app.after_request
def add_security_headers(resp):
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["X-Frame-Options"] = "DENY"
    return resp

@app.errorhandler(413)
def handle_too_large(e):
    return jsonify(error=ERROR_MESSAGES['size_limit']), 413

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))