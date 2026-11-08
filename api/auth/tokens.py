"""Short-lived tokens that authorize a password change.

The reset flow is: request a code, verify the code, set a new password.
Verifying the OTP consumes it, so the final step has no evidence the code was
ever checked unless it carries something back. This token is that evidence.
"""

from django.core import signing

SALT = 'woomenow.password-reset'
MAX_AGE_SECONDS = 15 * 60

# Enough of the hash to detect a change without storing the whole thing.
_HASH_FINGERPRINT_LENGTH = 22


def _fingerprint(user) -> str:
    return (user.password or '')[-_HASH_FINGERPRINT_LENGTH:]


def issue_password_reset_token(user) -> str:
    return signing.dumps(
        {'uid': user.pk, 'pw': _fingerprint(user)},
        salt=SALT,
    )


def password_reset_token_is_valid(token, user) -> bool:
    if not token or not isinstance(token, str):
        return False
    try:
        # SignatureExpired subclasses BadSignature, so this covers both the
        # tampered and the stale case.
        data = signing.loads(token, salt=SALT, max_age=MAX_AGE_SECONDS)
    except signing.BadSignature:
        return False
    if not isinstance(data, dict):
        return False
    # Binding the password hash makes the token single-use: once the password
    # changes the fingerprint no longer matches, so a replay is rejected.
    return data.get('uid') == user.pk and data.get('pw') == _fingerprint(user)
