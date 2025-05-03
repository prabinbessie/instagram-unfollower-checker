import pytest
import json
import sys
from io import BytesIO
from werkzeug.datastructures import FileStorage
from app import app, InstagramAnalyzer, ERROR_MESSAGES, __version__

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def create_test_file(content, filename):
    return FileStorage(
        stream=BytesIO(content.encode()),
        filename=filename,
        content_type='application/json'
    )

# Test data
VALID_FOLLOWING = '''
[
  {
    "relationships_following": [
      {"string_list_data": [{"value": "user1"}]},
      {"string_list_data": [{"value": "user2"}]}
    ]
  }
]'''

VALID_FOLLOWERS = '''
[
  {
    "relationships_followers": [
      {"string_list_data": [{"value": "user1"}]}
    ]
  }
]'''

def test_json_endpoint_success(client):
    data = {
        'following': create_test_file(VALID_FOLLOWING, 'following.json'),
        'followers': create_test_file(VALID_FOLLOWERS, 'followers.json')
    }
    response = client.post('/analyze/json', data=data)
    assert response.status_code == 200
    assert len(response.json['non_followers']) == 1
    assert response.json['non_followers'][0]['username'] == 'user2'

def test_pdf_endpoint_success(client):
    data = {
        'following': create_test_file(VALID_FOLLOWING, 'following.json'),
        'followers': create_test_file(VALID_FOLLOWERS, 'followers.json')
    }
    response = client.post('/analyze/pdf', data=data)
    assert response.status_code == 200
    assert response.mimetype == 'application/pdf'

def test_missing_files(client):
    response = client.post('/analyze/json', data={})
    assert response.status_code == 400
    assert ERROR_MESSAGES['missing_files'] in response.json['error']

def test_invalid_file_extensions(client):
    data = {
        'following': create_test_file('{}', 'following.txt'),
        'followers': create_test_file('{}', 'followers.csv')
    }
    response = client.post('/analyze/json', data=data)
    assert response.status_code == 400
    assert ERROR_MESSAGES['invalid_extension'] in response.json['error']

def test_malformed_json(client):
    data = {
        'following': create_test_file('{invalid', 'following.json'),
        'followers': create_test_file(VALID_FOLLOWERS, 'followers.json')
    }
    response = client.post('/analyze/json', data=data)
    assert response.status_code == 400
    assert ERROR_MESSAGES['invalid_json'] in response.json['error']

def test_different_data_formats():
    analyzer = InstagramAnalyzer()
    
    # Test old format (direct dict)
    old_format = {"relationships_following": [{"string_list_data": [{"value": "user_old"}]}]}
    # Test new format (list of containers)
    new_format = [{"relationships_following": [{"string_list_data": [{"value": "user_new"}]}]}]
    
    assert analyzer.extract_users(old_format, 'relationships_following') == ['user_old']
    assert analyzer.extract_users(new_format, 'relationships_following') == ['user_new']

def test_missing_data_fields():
    analyzer = InstagramAnalyzer()
    invalid_data = '''
    [{"relationships_following": [
        {"invalid": "data"},
        {"string_list_data": []}
    ]}]'''
    file = create_test_file(invalid_data, 'test.json')
    data = analyzer.process_file(file)
    users = analyzer.extract_users(data, 'relationships_following')
    assert len(users) == 0

def test_file_size_limit(client):
    # Generate valid JSON over 2MB limit
    large_data = {'relationships_following': []}
    large_content = json.dumps([large_data]*150000)
    data = {
        'following': create_test_file(large_content, 'following.json'),
        'followers': create_test_file(VALID_FOLLOWERS, 'followers.json')
    }
    response = client.post('/analyze/json', data=data)
    assert response.status_code == 413

# def test_version_command(capsys):
#     sys.argv = ['app.py', '--version']
#     with pytest.raises(SystemExit):
#         app.run()
#     captured = capsys.readouterr()
#     assert __version__ in captured.out

def test_empty_result_handling(client):
    following_data = '''
    [{"relationships_following": [
        {"string_list_data": [{"value": "user1"}]}
    ]}]'''
    
    followers_data = '''
    [{"relationships_followers": [
        {"string_list_data": [{"value": "user1"}]}
    ]}]'''
    
    data = {
        'following': create_test_file(following_data, 'following.json'),
        'followers': create_test_file(followers_data, 'followers.json')
    }
    response = client.post('/analyze/json', data=data)
    assert len(response.json['non_followers']) == 0