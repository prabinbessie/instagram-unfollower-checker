"""
Instagram Unfollower Analyzer v5.0
"""
import os
import json
import sys
import time
import logging
import csv
import zipfile
from datetime import datetime
from io import BytesIO, StringIO
from flask import Flask, request, jsonify, send_file, render_template
from bs4 import BeautifulSoup
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from version import __version__


app = Flask(__name__, template_folder='templates')
app.config.update(
    MAX_CONTENT_LENGTH=16 * 1024 * 1024,
    SECRET_KEY=os.environ.get('SECRET_KEY', os.urandom(24).hex()),
    JSON_AS_ASCII=False
)

logging.basicConfig(
    stream=sys.stdout, 
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
app.logger = logging.getLogger('InstagramUnfollowerChecker')

ERROR_MESSAGES = {
    'missing_files': "Please upload both following and followers files or a ZIP archive",
    'invalid_file': "Invalid file format. We support JSON, HTML files, or ZIP archives from Instagram",
    'empty_file': "Uploaded file appears to be empty",
    'size_limit': "File size exceeds 16MB limit",
    'same_files': "You uploaded the same file for both following and followers",
    'zip_structure': "ZIP file must contain Instagram data in connections/followers_and_following/ folder"
}

@app.context_processor
def inject_version():
    return dict(version=__version__)


class SimpleUpload:
    def __init__(self, filename: str, data: bytes):
        self.filename = filename
        self.stream = BytesIO(data)


class InstagramAnalyzer:
    
    @staticmethod
    def validate_files(files):
        if not files:
            raise ValueError(ERROR_MESSAGES['missing_files'])
        
        if 'following' in files and files['following'] and files['following'].filename.lower().endswith('.zip'):
            app.logger.info(f"ZIP file detected: {files['following'].filename}")
            return
        if 'followers' in files and files['followers'] and files['followers'].filename.lower().endswith('.zip'):
            app.logger.info(f"ZIP file detected: {files['followers'].filename}")
            return
        
        required = {'following', 'followers'}
        if not required.issubset(files):
            raise ValueError(ERROR_MESSAGES['missing_files'])
        
        f1, f2 = files['following'], files['followers']
        
        if not f1 or not f1.filename:
            raise ValueError(ERROR_MESSAGES['empty_file'])
        if not f2 or not f2.filename:
            raise ValueError(ERROR_MESSAGES['empty_file'])
        
        if f1.filename == f2.filename:
            raise ValueError(ERROR_MESSAGES['same_files'])
        
        for f in (f1, f2):
            ext = f.filename.rsplit('.', 1)[-1].lower() if '.' in f.filename else ''
            if ext not in ('json', 'html'):
                raise ValueError(ERROR_MESSAGES['invalid_file'])
            
            f.stream.seek(0, os.SEEK_END)
            size = f.stream.tell()
            if size > 16 * 1024 * 1024:
                raise ValueError(ERROR_MESSAGES['size_limit'])
            if size == 0:
                raise ValueError(ERROR_MESSAGES['empty_file'])
            f.stream.seek(0)

    @staticmethod
    def detect_file_type(name):
        return name.rsplit('.', 1)[-1].lower() if '.' in name else ''

    @classmethod
    def _auto_detect_files(cls, f1, f2):
        n1, n2 = f1.filename.lower(), f2.filename.lower()
        
        if 'followers' in n1 and 'following' not in n1:
            return f2, f1
        if 'followers' in n2 and 'following' not in n2:
            return f1, f2
        
        try:
            f1.stream.seek(0)
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
            for a in soup.select('a[href*="instagram.com"]')
            if a.get('href')
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
        
        users = set()
        for itm in entries:
            if isinstance(itm, dict) and itm.get('string_list_data'):
                for item in itm['string_list_data']:
                    if item.get('value'):
                        users.add(item['value'])
        
        return sorted(users)

    @classmethod
    def process_file(cls, f):
        f.stream.seek(0)
        file_type = cls.detect_file_type(f.filename)
        
        if file_type == 'html':
            return cls.parse_html(f.stream)
        return cls.parse_json(f.stream)

    @classmethod
    def get_analysis(cls, f1, f2):
        fol, folr = cls._auto_detect_files(f1, f2)
        following = cls.process_file(fol)
        followers = cls.process_file(folr)

        following_set = set(following)
        followers_set = set(followers)

        unfollowers = sorted(following_set - followers_set)

        total_following = len(following)
        total_followers = len(followers)
        unfollowers_count = len(unfollowers)

        return {
            'summary': {
                'total_following': total_following,
                'total_followers': total_followers,
                'unfollowers': unfollowers_count
            },
            'lists': {
                'following': [
                    {'id': i+1, 'username': u, 'profile_url': f"https://www.instagram.com/{u}"}
                    for i, u in enumerate(following)
                ],
                'unfollowers': [
                    {'id': i+1, 'username': u, 'profile_url': f"https://www.instagram.com/{u}"}
                    for i, u in enumerate(unfollowers)
                ]
            }
        }

    @staticmethod
    def export_to_csv(data_list, filename_prefix):
        text_buf = StringIO()
        writer = csv.writer(text_buf)
        writer.writerow(['ID', 'Username', 'Profile URL'])

        for user in data_list:
            writer.writerow([user['id'], user['username'], user['profile_url']])
        
        csv_bytes = text_buf.getvalue().encode('utf-8-sig')
        return BytesIO(csv_bytes)

    @staticmethod
    def _extract_instagram_zip(file_storage):
        try:
            app.logger.info(f"Extracting ZIP: {file_storage.filename}")
            
            with zipfile.ZipFile(file_storage.stream) as zf:
                names = zf.namelist()
                app.logger.info(f"ZIP contains {len(names)} files")
                
                following_file = None
                followers_file = None
                
                for name in names:
                    # Skip directories, hidden files, and __MACOSX
                    if name.endswith('/') or '/__MACOSX/' in name or name.startswith('__MACOSX/'):
                        continue
                    
                    lower = name.lower()
                    
                    # Check if in followers_and_following folder
                    if 'followers_and_following' in lower:
                        ext = name.rsplit('.', 1)[-1].lower() if '.' in name else ''
                        if ext not in ('json', 'html'):
                            continue
                        
                        basename = os.path.basename(name).lower()
                        if 'following' in basename and 'followers' not in basename:
                            following_file = name
                            app.logger.info(f"Found following file: {name}")
                        elif 'followers' in basename:
                            followers_file = name
                            app.logger.info(f"Found followers file: {name}")

                if not following_file or not followers_file:
                    app.logger.error(f"Missing files. Following: {following_file}, Followers: {followers_file}")
                    raise ValueError(ERROR_MESSAGES['zip_structure'])

                following_data = zf.read(following_file)
                followers_data = zf.read(followers_file)

                return (
                    SimpleUpload(os.path.basename(following_file), following_data),
                    SimpleUpload(os.path.basename(followers_file), followers_data),
                )
        except zipfile.BadZipFile as e:
            app.logger.error(f"Invalid ZIP: {e}")
            raise ValueError("Invalid ZIP file")
        except Exception as e:
            app.logger.error(f"ZIP extraction error: {e}", exc_info=True)
            raise

    @classmethod
    def resolve_inputs(cls, files):
        if 'following' in files and files['following'] and files['following'].filename.lower().endswith('.zip'):
            return cls._extract_instagram_zip(files['following'])
        if 'followers' in files and files['followers'] and files['followers'].filename.lower().endswith('.zip'):
            return cls._extract_instagram_zip(files['followers'])

        cls.validate_files(files)
        return files['following'], files['followers']


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/analyze/json', methods=['POST'])
def analyze_json():
    try:
        app.logger.info("Starting analysis")
        InstagramAnalyzer.validate_files(request.files)
        f_following, f_followers = InstagramAnalyzer.resolve_inputs(request.files)
        analysis = InstagramAnalyzer.get_analysis(f_following, f_followers)
        app.logger.info(f"Analysis complete. Found {analysis['summary']['unfollowers']} unfollowers")
        return jsonify({'success': True, 'analysis': analysis})
    except Exception as e:
        app.logger.error(f"Analysis error: {e}", exc_info=True)
        return jsonify(error=str(e)), 400

@app.route('/analyze/pdf', methods=['POST'])
def analyze_pdf():
    try:
        app.logger.info("Starting PDF generation")
        InstagramAnalyzer.validate_files(request.files)
        f_following, f_followers = InstagramAnalyzer.resolve_inputs(request.files)
        analysis = InstagramAnalyzer.get_analysis(f_following, f_followers)
        
        unfollowers = analysis['lists']['unfollowers']
        
        if not unfollowers:
            app.logger.info("No unfollowers found")
            return jsonify({'message': 'Great! Everyone you follow is following you back!'}), 200

        buf = BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=letter)
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(
            name='ProfileLink',
            textColor=colors.HexColor('#E1306C'),
            fontSize=10,
            leading=14
        ))
        
        elems = [
            Paragraph("Instagram Unfollowers Report", styles['Title']),
            Spacer(1, 24),
            Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']),
            Spacer(1, 12),
            Paragraph(f"By Prabin Bhandari", styles['Normal']),
            Spacer(1, 18)
        ]

        table_data = [["#", "Username", "Profile Link"]] + [
            [
                str(u['id']),
                u['username'],
                Paragraph(f"<a href='{u['profile_url']}'>{u['profile_url']}</a>", styles['ProfileLink'])
            ]
            for u in unfollowers
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

        app.logger.info("PDF generated")
        return send_file(
            buf,
            as_attachment=True,
            download_name=f"instagram_unfollowers_{int(time.time())}.pdf",
            mimetype='application/pdf'
        )
    except Exception as e:
        app.logger.error(f"PDF error: {e}", exc_info=True)
        return jsonify(error=str(e)), 400


@app.route('/analyze/csv', methods=['POST'])
def analyze_csv():
    try:
        export_type = request.form.get('export_type', 'unfollowers')
        app.logger.info(f"CSV export: {export_type}")
        
        InstagramAnalyzer.validate_files(request.files)
        f_following, f_followers = InstagramAnalyzer.resolve_inputs(request.files)
        
        analysis = InstagramAnalyzer.get_analysis(f_following, f_followers)
        
        data_lists = {
            'unfollowers': analysis['lists']['unfollowers'],
            'following': analysis['lists']['following']
        }
        
        if export_type not in data_lists:
            return jsonify({'error': 'Invalid export type'}), 400
            
        data_list = data_lists[export_type]
        
        if not data_list:
            return jsonify({'error': f'No data for {export_type}'}), 400
        
        csv_buffer = InstagramAnalyzer.export_to_csv(data_list, export_type)
        filename = f"instagram_{export_type}_{int(time.time())}.csv"
        
        app.logger.info(f"CSV complete: {filename}")
        return send_file(
            csv_buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='text/csv'
        )
        
    except Exception as e:
        app.logger.error(f"CSV error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 400

@app.after_request
def add_security_headers(resp):
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["X-Frame-Options"] = "DENY"
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    return resp

@app.errorhandler(413)
def handle_too_large(e):
    return jsonify(error=ERROR_MESSAGES['size_limit']), 413

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5001)))