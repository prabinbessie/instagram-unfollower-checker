import sys
import os
import io
import json
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app, InstagramAnalyzer

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024 
    with app.test_client() as client:
        yield client

def generate_json_file(usernames, key='relationships_following'):
    return io.BytesIO(json.dumps([
        {
            "string_list_data": [{"value": username}]
        } for username in usernames
    ]).encode('utf-8')), f"{key}.json"

def generate_html_file(usernames, label="following"):
    html_content = '<div class="pam _3-95 _2ph- _a6-g uiBoxWhite noborder">'
    for u in usernames:
        html_content += f'<a href="https://www.instagram.com/{u}/">{u}</a>'
    html_content += '</div>'
    return io.BytesIO(html_content.encode('utf-8')), f"{label}.html"

def test_homepage(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Instagram Unfollower Checker' in response.data

def test_json_analysis_with_valid_files(client):
    following_file, following_name = generate_json_file(['user1', 'user2', 'user3'], 'relationships_following')
    followers_file, followers_name = generate_json_file(['user2'], 'relationships_followers')

    data = {
        'following': (following_file, following_name),
        'followers': (followers_file, followers_name)
    }
    response = client.post('/analyze/json', data=data, content_type='multipart/form-data')
    assert response.status_code == 200
    result = response.get_json()
    assert result['count'] == 2
    usernames = [u['username'] for u in result['results']]
    assert 'user1' in usernames and 'user3' in usernames

def test_html_analysis(client):
    following_file, following_name = generate_html_file(['user1', 'user2'], 'following')
    followers_file, followers_name = generate_html_file(['user2'], 'followers')

    data = {
        'following': (following_file, following_name),
        'followers': (followers_file, followers_name)
    }
    response = client.post('/analyze/json', data=data, content_type='multipart/form-data')
    assert response.status_code == 200
    result = response.get_json()
    assert result['count'] == 1
    assert result['results'][0]['username'] == 'user1'

def test_pdf_generation(client):
    following_file, following_name = generate_json_file(['user1', 'user2'], 'relationships_following')
    followers_file, followers_name = generate_json_file(['user2'], 'relationships_followers')

    data = {
        'following': (following_file, following_name),
        'followers': (followers_file, followers_name)
    }
    response = client.post('/analyze/pdf', data=data, content_type='multipart/form-data')
    assert response.status_code == 200
    assert response.mimetype == 'application/pdf'

def test_missing_files(client):
    response = client.post('/analyze/json', data={}, content_type='multipart/form-data')
    assert response.status_code == 400
    assert b'please upload both following and followers files' in response.data.lower()

def test_invalid_format_file(client):
    bad_file = io.BytesIO(b'invalid content')
    bad_file_2 = io.BytesIO(b'invalid content 2')
    data = {
        'following': (bad_file, 'invalid.txt'),
        'followers': (bad_file_2, 'invalid2.txt')
    }
    response = client.post('/analyze/json', data=data, content_type='multipart/form-data')
    assert response.status_code == 400
    assert b'invalid file format' in response.data.lower()

def test_same_file_uploaded(client):
    file1, name = generate_json_file(['user1'])
    file2, _ = generate_json_file(['user1'])  # Generate a second file with same content
    data = {
        'following': (file1, 'same.json'),
        'followers': (file2, 'same.json')
    }
    response = client.post('/analyze/json', data=data, content_type='multipart/form-data')
    assert response.status_code == 400
    assert b'same file' in response.data.lower()

def test_empty_file(client):
    empty_file1 = io.BytesIO(b'')
    empty_file2 = io.BytesIO(b'')
    data = {
        'following': (empty_file1, 'empty.json'),
        'followers': (empty_file2, 'empty2.json')
    }
    response = client.post('/analyze/json', data=data, content_type='multipart/form-data')
    assert response.status_code == 400
    assert b'expecting value' in response.data.lower()

def test_large_file(client):
    large_data1 = io.BytesIO(b'0' * (5 * 1024 * 1024 + 1))  # Just over 5MB
    large_data2 = io.BytesIO(b'0' * (5 * 1024 * 1024 + 1))
    data = {
        'following': (large_data1, 'large.json'),
        'followers': (large_data2, 'large2.json')
    }
    response = client.post('/analyze/json', data=data, content_type='multipart/form-data')
    assert response.status_code in [400, 413]  # Accept both 400 and 413
    assert b'5mb' in response.data.lower() or b'request entity too large' in response.data.lower()
