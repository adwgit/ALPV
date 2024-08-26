# tests/test_notification_service.py
import pytest
from app.notification_service import NotificationService
from unittest.mock import patch

def test_send_slack_notification():
    service = NotificationService("https://hooks.slack.com/services/test/webhook")

    with patch('requests.post') as mock_post:
        mock_post.return_value.status_code = 200
        service.send_slack_notification("Test message")
        mock_post.assert_called_once()

    with patch('requests.post') as mock_post:
        mock_post.return_value.status_code = 400
        with pytest.raises(ValueError):
            service.send_slack_notification("Test message")
