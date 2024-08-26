# app/list_management_service.py
from app.database import Database
import re
import jwt
from datetime import datetime, timedelta
from io import StringIO
import csv
from app.notification_service import NotificationService
import os

SECRET_KEY = 'your_secret_key'
SLACK_WEBHOOK_URL = 'your_slack_webhook_url'

class ListManagementService:
    def __init__(self):
        self.db = Database()
        self.notification_service = NotificationService(SLACK_WEBHOOK_URL)

    def check_value(self, list_id, value):
        list_items = self.db.retrieve_list(list_id)
        exists = value in list_items
        return {'exists': exists}

    def add_value(self, list_id, value, comment, author):
        if not self.validate_value(value):
            return {'error': 'Invalid value'}
        list_items = self.db.retrieve_list(list_id)
        if value in list_items:
            return {'error': 'Value already exists'}
        self.db.store_list(list_id, value, comment, author)
        return {'success': 'Value added'}

    def edit_value(self, list_id, old_value, new_value, comment, author):
        if not self.validate_value(new_value):
            return {'error': 'Invalid value'}
        list_items = self.db.retrieve_list(list_id)
        if old_value not in list_items:
            return {'error': 'Value not found'}
        self.db.update_list(list_id, old_value, new_value, comment, author)
        return {'success': 'Value edited'}

    def delete_value(self, list_id, value):
        list_items = self.db.retrieve_list(list_id)
        if value not in list_items:
            return {'error': 'Value not found'}
        self.db.delete_value(list_id, value)
        return {'success': 'Value deleted'}

    def change_list_type(self, list_id, new_type):
        self.db.change_list_type(list_id, new_type)
        return {'success': 'List type changed'}

    def validate_value(self, value):
        if len(value) > 255:
            return False
        if not re.match(r'^[a-zA-Z0-9_\-]+$', value):
            return False
        return True

    def process_csv(self, file, list_id, author):
        csv_file = StringIO(file.stream.read().decode('utf-8'))
        csv_reader = csv.reader(csv_file, delimiter=',')
        results = []
        for row in csv_reader:
            if len(row) < 1:
                continue
            value = row[0]
            comment = row[1] if len(row) > 1 else ''
            if not self.validate_value(value):
                results.append({'value': value, 'status': 'Invalid value'})
                continue
            list_items = self.db.retrieve_list(list_id)
            if value in list_items:
                results.append({'value': value, 'status': 'Already exists'})
                continue
            self.db.store_list(list_id, value, comment, author)
            results.append({'value': value, 'status': 'Added'})
        return {'results': results}

    def create_user(self, username, password, role):
        if self.db.get_user(username):
            return {'error': 'User already exists'}
        self.db.create_user(username, password, role)
        return {'success': 'User created'}

    def generate_token(self, username):
        token = jwt.encode({
            'username': username,
            'exp': datetime.utcnow() + timedelta(hours=1)
        }, SECRET_KEY, algorithm='HS256')
        return token

    def verify_token(self, token):
        try:
            decoded_token = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            return decoded_token['username']
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def search_values(self, list_id, search_term, filter_by):
        if not search_term:
            return {'error': 'No search term provided'}
        list_items = self.db.retrieve_list(list_id)
        filtered_items = []
        for value, details in list_items.items():
            if filter_by == 'value' and search_term in value:
                filtered_items.append(details)
            elif filter_by == 'comment' and search_term in details['comment']:
                filtered_items.append(details)
        return {'results': filtered_items}

    def add_notification(self, list_id, threshold):
        self.db.add_notification(list_id, threshold)
        return {'success': 'Notification added'}

    def check_notifications(self):
        notifications = self.db.get_notifications()
        for notification in notifications:
            list_id, threshold, notified = notification[1], notification[2], notification[3]
            count = self.db.get_list_count(list_id)
            if count > threshold:
                self.send_notification(list_id, count, threshold)
                self.db.mark_notification_as_sent(notification[0])
        return {'success': 'Notifications checked'}

    def send_notification(self, list_id, count, threshold):
        message = f'Notification: List {list_id} has {count} items, exceeding threshold {threshold}'
        self.notification_service.send_slack_notification(message)
