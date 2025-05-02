import pytest
import json
from io import BytesIO
from werkzeug.datastructures import FileStorage
from app import app, InstagramAnalyzer, ERROR_MESSAGES

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

class TestInstagramAnalyzer:
    def test_validate_files_valid(self):
        files = {
            'following': FileStorage(
                stream=BytesIO(b'{}'),
                filename='following.json',
                content_type='application/json'
            ),
            'followers': FileStorage(
                stream=BytesIO(b'{}'),
                filename='followers.json',
                content_type='application/json'
            )
        }
        InstagramAnalyzer.validate_files(files)

    def test_validate_files_missing(self):
        files = {'following': FileStorage(
            stream=BytesIO(b'{}'),
            filename='following.json'
        )}
        with pytest.raises(ValueError) as e:
            InstagramAnalyzer.validate_files(files)
        assert ERROR_MESSAGES['missing_files'] in str(e.value)

    def test_process_file_valid_json(self):
        file = FileStorage(
            stream=BytesIO(json.dumps({'test': 'data'}).encode()),
            filename='test.json'
        )
        result = InstagramAnalyzer.process_file(file)
        assert result == {'test': 'data'}

    def test_process_file_invalid_json(self):
        file = FileStorage(
            stream=BytesIO(b'invalid'),
            filename='test.json'
        )
        with pytest.raises(ValueError) as e:
            InstagramAnalyzer.process_file(file)
        assert ERROR_MESSAGES['invalid_json'] in str(e.value)

class TestEndpoints:
    def test_home_page(self, client):
        response = client.get('/')
        assert response.status_code == 200
        assert b"Instagram Unfollower Analyzer" in response.data

    def test_analyze_json_success(self, client):
        data = {
            'following': (BytesIO(b'{"relationships_following": []}'), 'following.json'),
            'followers': (BytesIO(b'{"relationships_followers": []}'), 'followers.json')
        }
        response = client.post('/analyze/json', data=data)
        assert response.status_code == 200
        assert 'non_followers' in response.json

    def test_analyze_pdf_success(self, client):
        data = {
            'following': (BytesIO(b'{"relationships_following": []}'), 'following.json'),
            'followers': (BytesIO(b'{"relationships_followers": []}'), 'followers.json')
        }
        response = client.post('/analyze/pdf', data=data)
        assert response.status_code == 200
        assert response.mimetype == 'application/pdf'

    def test_file_size_limit(self, client):
        # Test with valid JSON structure that exceeds size limit
        large_content = json.dumps({"data": "a" * (2 * 1024 * 1024)})
        data = {
            'following': (BytesIO(large_content.encode()), 'large.json'),
            'followers': (BytesIO(large_content.encode()), 'large.json')
        }
        response = client.post('/analyze/json', data=data)
        assert response.status_code == 413