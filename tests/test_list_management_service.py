# tests/test_list_management_service.py
import pytest
from app.list_management_service import ListManagementService
from unittest.mock import MagicMock


@pytest.fixture
def service():
    service = ListManagementService()
    service.db = MagicMock()
    service.notification_service = MagicMock()
    return service

def test_check_value(service):
    service.db.retrieve_list.return_value = {'test_value': {'value': 'test_value'}}
    result = service.check_value(1, 'test_value')
    assert result['exists'] is True

    result = service.check_value(1, 'nonexistent_value')
    assert result['exists'] is False

def test_add_value(service):
    service.db.retrieve_list.return_value = {}
    service.validate_value = MagicMock(return_value=True)
    result = service.add_value(1, 'test_value', 'test comment', 'admin')
    assert result['success'] == 'Value added'

    service.db.retrieve_list.return_value = {'test_value': {'value': 'test_value'}}
    result = service.add_value(1, 'test_value', 'test comment', 'admin')
    assert result['error'] == 'Value already exists'

    service.validate_value = MagicMock(return_value=False)
    result = service.add_value(1, 'invalid_value', 'test comment', 'admin')
    assert result['error'] == 'Invalid value'

def test_edit_value(service):
    service.db.retrieve_list.return_value = {'test_value': {'value': 'test_value'}}
    service.validate_value = MagicMock(return_value=True)
    result = service.edit_value(1, 'test_value', 'new_test_value', 'updated comment', 'admin')
    assert result['success'] == 'Value edited'

    service.db.retrieve_list.return_value = {}
    result = service.edit_value(1, 'nonexistent_value', 'new_test_value', 'updated comment', 'admin')
    assert result['error'] == 'Value not found'

    service.validate_value = MagicMock(return_value=False)
    result = service.edit_value(1, 'test_value', 'invalid_value', 'updated comment', 'admin')
    assert result['error'] == 'Invalid value'

def test_delete_value(service):
    service.db.retrieve_list.return_value = {'test_value': {'value': 'test_value'}}
    result = service.delete_value(1, 'test_value')
    assert result['success'] == 'Value deleted'

    service.db.retrieve_list.return_value = {}
    result = service.delete_value(1, 'nonexistent_value')
    assert result['error'] == 'Value not found'

def test_change_list_type(service):
    result = service.change_list_type(1, 'grey')
    assert result['success'] == 'List type changed'

def test_process_csv(service):
    csv_content = "value,comment\ntest_value,test_comment\ninvalid_value,test_comment"
    file = MagicMock()
    file.stream.read.return_value.decode.return_value = csv_content
    service.validate_value = MagicMock(side_effect=[True, False])
    service.db.retrieve_list.return_value = {}
    result = service.process_csv(file, 1, 'admin')
    assert result['results'][0]['status'] == 'Added'
    assert result['results'][1]['status'] == 'Invalid value'

def test_add_notification(service):
    result = service.add_notification(1, 10)
    assert result['success'] == 'Notification added'

def test_check_notifications(service):
    service.db.get_notifications.return_value = [(1, 1, 10, False)]
    service.db.get_list_count.return_value = 11
    result = service.check_notifications()
    assert result['success'] == 'Notifications checked'
    service.notification_service.send_slack_notification.assert_called_once()

def test_send_notification(service):
    service.send_notification(1, 11, 10)
    service.notification_service.send_slack_notification.assert_called_once_with(
        'Notification: List 1 has 11 items, exceeding threshold 10'
    )
