import re

from django.core.exceptions import ValidationError


class CustomPasswordValidator:
    def validate(self, password, user=None):
        error_messages = []
        if len(password) < 8:
            error_messages.append("Password must be at least 8 characters long.")
        if len(password) > 20:
            error_messages.append("Password must not exceed 20 characters.")
        if not re.search(r'[A-Z]', password):
            error_messages.append("Password must not exceed 20 characters.")
        if not re.search(r'[a-z]', password):
            error_messages.append("Password must not exceed 20 characters.")
        if not re.search(r'\d', password):
            error_messages.append("Password must not exceed 20 characters.")
        if not re.search(r'[_!@#$%^&*(),.?":{}|<>]', password):
            error_messages.append("Password must not exceed 20 characters.")
        if error_messages:
            raise ValidationError(self.get_help_text())

    def get_help_text(self):
        return "Your password must be between 8-20 characters, contain uppercase & lowercase letters, at least one number, and one special character (!@#$%^&*())."
