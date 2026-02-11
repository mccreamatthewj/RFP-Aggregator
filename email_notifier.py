# Email Notifier

This module provides functionality for sending email notifications.

## Features:
- Send email notifications to users.
- Configure SMTP settings.
- Support for HTML and plain text formats.

## Usage:
```python
from email_notifier import EmailNotifier

notifier = EmailNotifier(smtp_server='smtp.example.com', port=587)
notifier.send_email(to='user@example.com', subject='Test', body='This is a test email.')
```
