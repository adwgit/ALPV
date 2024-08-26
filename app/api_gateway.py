# app/api_gateway.py
from flask import Flask, request, jsonify
from flask_httpauth import HTTPBasicAuth
from list_management_service import ListManagementService

app = Flask(__name__)
auth = HTTPBasicAuth()
list_service = ListManagementService()

users = {
    "admin": "admin_password"
}

@auth.verify_password
def verify_password(username, password):
    user = list_service.db.get_user(username)
    if user and user[2] == password:
        return username

@app.route('/token', methods=['POST'])
@auth.login_required
def get_auth_token():
    token = list_service.generate_token(auth.current_user())
    return jsonify({'token': token})

@app.route('/check', methods=['POST'])
def check_value():
    token = request.headers.get('Authorization').split()[1]
    username = list_service.verify_token(token)
    if username is None:
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.json
    result = list_service.check_value(data['list_id'], data['value'])
    return jsonify(result)

@app.route('/add', methods=['POST'])
def add_value():
    token = request.headers.get('Authorization').split()[1]
    username = list_service.verify_token(token)
    if username is None:
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.json
    result = list_service.add_value(data['list_id'], data['value'], data['comment'], username)
    return jsonify(result)

@app.route('/edit', methods=['PUT'])
def edit_value():
    token = request.headers.get('Authorization').split()[1]
    username = list_service.verify_token(token)
    if username is None:
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.json
    result = list_service.edit_value(data['list_id'], data['old_value'], data['new_value'], data['comment'], username)
    return jsonify(result)

@app.route('/delete', methods=['DELETE'])
def delete_value():
    token = request.headers.get('Authorization').split()[1]
    username = list_service.verify_token(token)
    if username is None:
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.json
    result = list_service.delete_value(data['list_id'], data['value'])
    return jsonify(result)

@app.route('/change_type', methods=['PUT'])
def change_list_type():
    token = request.headers.get('Authorization').split()[1]
    username = list_service.verify_token(token)
    if username is None:
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.json
    result = list_service.change_list_type(data['list_id'], data['new_type'])
    return jsonify(result)

@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    token = request.headers.get('Authorization').split()[1]
    username = list_service.verify_token(token)
    if username is None:
        return jsonify({'error': 'Unauthorized'}), 401
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})
    if file and file.filename.endswith('.csv'):
        list_id = request.form.get('list_id')
        result = list_service.process_csv(file, list_id, username)
        return jsonify(result)
    return jsonify({'error': 'Invalid file type'})

@app.route('/search', methods=['GET'])
def search_values():
    token = request.headers.get('Authorization').split()[1]
    username = list_service.verify_token(token)
    if username is None:
        return jsonify({'error': 'Unauthorized'}), 401
    list_id = request.args.get('list_id')
    search_term = request.args.get('search_term')
    filter_by = request.args.get('filter_by')
    result = list_service.search_values(list_id, search_term, filter_by)
    return jsonify(result)

@app.route('/report/actions', methods=['GET'])
def get_action_report():
    token = request.headers.get('Authorization').split()[1]
    username = list_service.verify_token(token)
    if username is None:
        return jsonify({'error': 'Unauthorized'}), 401
    result = list_service.get_action_report(username)
    return jsonify(result)

@app.route('/report/actions/<target_username>', methods=['GET'])
def get_user_action_report(target_username):
    token = request.headers.get('Authorization').split()[1]
    username = list_service.verify_token(token)
    if username is None:
        return jsonify({'error': 'Unauthorized'}), 401
    result = list_service.get_user_action_report(username, target_username)
    return jsonify(result)

@app.route('/add_notification', methods=['POST'])
def add_notification():
    token = request.headers.get('Authorization').split()[1]
    username = list_service.verify_token(token)
    if username is None:
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.json
    result = list_service.add_notification(data['list_id'], data['threshold'], username)
    return jsonify(result)

@app.route('/check_notifications', methods=['POST'])
def check_notifications():
    token = request.headers.get('Authorization').split()[1]
    username = list_service.verify_token(token)
    if username is None:
        return jsonify({'error': 'Unauthorized'}), 401
    result = list_service.check_notifications()
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
