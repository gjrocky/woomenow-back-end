import re

from django.core.exceptions import ValidationError


class CustomPasswordValidator:
    def validate(self, password, user=None):
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long.")
        if len(password) > 20:
            raise ValidationError("Password must not exceed 20 characters.")
        if not re.search(r'[A-Z]', password):
            raise ValidationError("Password must contain at least one uppercase letter.")
        if not re.search(r'[a-z]', password):
            raise ValidationError("Password must contain at least one lowercase letter.")
        if not re.search(r'\d', password):
            raise ValidationError("Password must contain at least one digit.")
        if not re.search(r'[_!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError("Password must contain at least one special character (!@#$%^&*()).")

    def get_help_text(self):
        return "Your password must be between 8-20 characters, contain uppercase & lowercase letters, at least one number, and one special character (!@#$%^&*())."
