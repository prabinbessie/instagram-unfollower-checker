import io
import os
import sys
import json
import zipfile

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app, InstagramAnalyzer


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def json_file(usernames, name='following.json'):
    """Build an Instagram-style JSON upload (top-level list of entries)."""
    payload = [{"string_list_data": [{"value": u}]} for u in usernames]
    return io.BytesIO(json.dumps(payload).encode('utf-8')), name


def html_file(usernames, name='following.html'):
    links = ''.join(f'<a href="https://www.instagram.com/{u}/">{u}</a>' for u in usernames)
    return io.BytesIO(f'<div>{links}</div>'.encode('utf-8')), name


def zip_file(following_users, followers_users):
    buf = io.BytesIO()
    base = 'connections/followers_and_following/'
    with zipfile.ZipFile(buf, 'w') as zf:
        zf.writestr(base + 'following.json', json_file(following_users)[0].getvalue())
        zf.writestr(base + 'followers_1.json', json_file(followers_users)[0].getvalue())
    buf.seek(0)
    return buf, 'instagram_data.zip'


def post(client, following, followers, route='/analyze/json'):
    data = {'following': following, 'followers': followers}
    return client.post(route, data=data, content_type='multipart/form-data')


def test_homepage(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Instagram Unfollower Checker' in response.data


def test_json_analysis(client):
    response = post(client,
                    json_file(['user1', 'user2', 'user3'], 'following.json'),
                    json_file(['user2'], 'followers_1.json'))
    assert response.status_code == 200
    analysis = response.get_json()['analysis']
    assert analysis['summary'] == {
        'total_following': 3, 'total_followers': 1, 'mutual': 1, 'unfollowers': 2,
    }
    unfollowers = [u['username'] for u in analysis['lists']['unfollowers']]
    assert unfollowers == ['user1', 'user3']


def test_classification(client):
    # user2 follows back (mutual); user1 and user3 do not (unfollowers).
    response = post(client,
                    json_file(['user1', 'user2', 'user3'], 'following.json'),
                    json_file(['user2'], 'followers_1.json'))
    analysis = response.get_json()['analysis']

    assert [u['username'] for u in analysis['lists']['mutual']] == ['user2']
    assert [u['username'] for u in analysis['lists']['unfollowers']] == ['user1', 'user3']

    by_name = {u['username']: u['follows_back'] for u in analysis['lists']['following']}
    assert by_name == {'user1': False, 'user2': True, 'user3': False}
    assert all(u['follows_back'] is False for u in analysis['lists']['unfollowers'])


def test_html_analysis(client):
    response = post(client,
                    html_file(['user1', 'user2'], 'following.html'),
                    html_file(['user2'], 'followers.html'))
    assert response.status_code == 200
    analysis = response.get_json()['analysis']
    assert analysis['summary']['unfollowers'] == 1
    assert analysis['lists']['unfollowers'][0]['username'] == 'user1'


def test_swapped_uploads_are_auto_corrected(client):
    # Followers file dropped into the "following" field and vice versa.
    response = post(client,
                    json_file(['user2'], 'followers_1.json'),
                    json_file(['user1', 'user2', 'user3'], 'following.json'))
    assert response.status_code == 200
    assert response.get_json()['analysis']['summary']['unfollowers'] == 2


def test_zip_upload(client):
    data = {'following': zip_file(['user1', 'user2', 'user3'], ['user2'])}
    response = client.post('/analyze/json', data=data, content_type='multipart/form-data')
    assert response.status_code == 200
    assert response.get_json()['analysis']['summary']['unfollowers'] == 2


def test_pdf_generation(client):
    response = post(client,
                    json_file(['user1', 'user2'], 'following.json'),
                    json_file(['user2'], 'followers_1.json'),
                    route='/analyze/pdf')
    assert response.status_code == 200
    assert response.mimetype == 'application/pdf'


def test_csv_export(client):
    response = post(client,
                    json_file(['user1', 'user2'], 'following.json'),
                    json_file(['user2'], 'followers_1.json'),
                    route='/analyze/csv')
    assert response.status_code == 200
    assert response.mimetype == 'text/csv'
    assert b'user1' in response.data


def test_missing_files(client):
    response = client.post('/analyze/json', data={}, content_type='multipart/form-data')
    assert response.status_code == 400
    assert b'upload both' in response.data.lower()


def test_invalid_format(client):
    response = post(client,
                    (io.BytesIO(b'nope'), 'a.txt'),
                    (io.BytesIO(b'nope'), 'b.txt'))
    assert response.status_code == 400
    assert b'invalid file format' in response.data.lower()


def test_same_file(client):
    response = post(client,
                    json_file(['user1'], 'data.json'),
                    json_file(['user1'], 'data.json'))
    assert response.status_code == 400
    assert b'same file' in response.data.lower()


def test_empty_file(client):
    response = post(client,
                    (io.BytesIO(b''), 'empty.json'),
                    (io.BytesIO(b''), 'empty2.json'))
    assert response.status_code == 400
    assert b'empty' in response.data.lower()
