# tests/test_api.py
import pytest
from app.api_gateway import app
from io import StringIO

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_get_auth_token(client):
    response = client.post('/token', auth=('admin', 'admin_password'))
    assert response.status_code == 200
    assert 'token' in response.json

def test_check_value_unauthorized(client):
    response = client.post('/check', json={'list_id': 1, 'value': 'test_value'})
    assert response.status_code == 401

def test_check_value(client):
    token_response = client.post('/token', auth=('admin', 'admin_password'))
    token = token_response.json['token']
    response = client.post('/check', headers={'Authorization': f'Bearer {token}'}, json={'list_id': 1, 'value': 'test_value'})
    assert response.status_code == 200
    assert 'exists' in response.json

def test_add_value(client):
    token_response = client.post('/token', auth=('admin', 'admin_password'))
    token = token_response.json['token']
    response = client.post('/add', headers={'Authorization': f'Bearer {token}'}, json={
        'list_id': 1,
        'value': 'test_value',
        'comment': 'test comment',
        'author': 'admin'
    })
    assert response.status_code == 200
    assert 'success' in response.json

def test_edit_value(client):
    token_response = client.post('/token', auth=('admin', 'admin_password'))
    token = token_response.json['token']
    response = client.put('/edit', headers={'Authorization': f'Bearer {token}'}, json={
        'list_id': 1,
        'old_value': 'test_value',
        'new_value': 'new_test_value',
        'comment': 'updated comment',
        'author': 'admin'
    })
    assert response.status_code == 200
    assert 'success' in response.json

def test_delete_value(client):
    token_response = client.post('/token', auth=('admin', 'admin_password'))
    token = token_response.json['token']
    response = client.delete('/delete', headers={'Authorization': f'Bearer {token}'}, json={
        'list_id': 1,
        'value': 'new_test_value'
    })
    assert response.status_code == 200
    assert 'success' in response.json

def test_upload_csv(client):
    token_response = client.post('/token', auth=('admin', 'admin_password'))
    token = token_response.json['token']
    data = {
        'list_id': 1,
        'author': 'admin'
    }
    response = client.post('/upload_csv', headers={'Authorization': f'Bearer {token}'}, data=data, content_type='multipart/form-data', data={
        'file': (StringIO("value,comment\ntest_csv_value,test_comment"), 'test.csv')
    })
    assert response.status_code == 200
    assert 'results' in response.json

def test_search_values(client):
    token_response = client.post('/token', auth=('admin', 'admin_password'))
    token = token_response.json['token']
    response = client.get('/search', headers={'Authorization': f'Bearer {token}'}, query_string={
        'list_id': 1,
        'search_term': 'test',
        'filter_by': 'value'
    })
    assert response.status_code == 200
    assert 'results' in response.json

def test_get_action_report(client):
    token_response = client.post('/token', auth=('admin', 'admin_password'))
    token = token_response.json['token']
    response = client.get('/report/actions', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    assert 'results' in response.json

def test_get_user_action_report(client):
    token_response = client.post('/token', auth=('admin', 'admin_password'))
    token = token_response.json['token']
    response = client.get('/report/actions/admin', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    assert 'results' in response.json

def test_add_notification(client):
    token_response = client.post('/token', auth=('admin', 'admin_password'))
    token = token_response.json['token']
    response = client.post('/add_notification', headers={'Authorization': f'Bearer {token}'}, json={
        'list_id': 1,
        'threshold': 10
    })
    assert response.status_code == 200
    assert 'success' in response.json

def test_check_notifications(client):
    token_response = client.post('/token', auth=('admin', 'admin_password'))
    token = token_response.json['token']
    response = client.post('/check_notifications', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    assert 'success' in response.json
