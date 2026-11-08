"""Generation of the one-time codes used for signup and password reset."""

import secrets

OTP_DIGITS = 6
_LOWER = 10 ** (OTP_DIGITS - 1)
_RANGE = (10 ** OTP_DIGITS) - _LOWER


def generate_otp() -> str:
    """A 6-digit code from the CSPRNG.

    `random` is seeded predictably and shared process-wide, so codes drawn
    from it can be reconstructed by anyone who observes a few of them.
    """
    return str(_LOWER + secrets.randbelow(_RANGE))
