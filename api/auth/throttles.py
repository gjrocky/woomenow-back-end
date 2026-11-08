"""Rate limits for the OTP endpoints.

Verifying an OTP is the last barrier before a password reset, and requesting
one sends mail to an arbitrary address. Both need limits.

The per-email classes are the ones that matter. An attacker can rotate source
IPs cheaply, but not the address of the account they are trying to reach, so
keying on the target is what actually bounds an attack. The per-IP classes
exist to stop one host from hammering many accounts.
"""

import hashlib

from rest_framework.throttling import SimpleRateThrottle


class _EmailScopedThrottle(SimpleRateThrottle):
    """Keyed on the email in the request body rather than the caller."""

    def get_cache_key(self, request, view):
        try:
            email = str(request.data.get('email') or '').strip().lower()
        except Exception:
            # Unparseable body. The IP-scoped throttle still applies, and the
            # view will reject the request on its own.
            return None
        if not email:
            return None
        # Hashed so the cache doesn't hold a list of addresses.
        ident = hashlib.sha256(email.encode()).hexdigest()
        return self.cache_format % {'scope': self.scope, 'ident': ident}


class _IPScopedThrottle(SimpleRateThrottle):
    def get_cache_key(self, request, view):
        return self.cache_format % {
            'scope': self.scope,
            'ident': self.get_ident(request),
        }


class OTPVerifyEmailThrottle(_EmailScopedThrottle):
    scope = 'otp_verify_email'


class OTPVerifyIPThrottle(_IPScopedThrottle):
    scope = 'otp_verify_ip'


class OTPIssueEmailThrottle(_EmailScopedThrottle):
    scope = 'otp_issue_email'


class OTPIssueIPThrottle(_IPScopedThrottle):
    scope = 'otp_issue_ip'
