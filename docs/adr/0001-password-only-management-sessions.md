---
status: accepted
---

# Use password-only persistent Management sessions

For hackathon ease of use, every deployment uses password-only access to the Management workspace: MFA and action-specific re-authentication are removed permanently, including enrolled TOTP secrets. Management sessions use a rolling 400-day persistent lifetime, shared with Django admin, and have no inactivity timeout; explicit logout is the normal termination path, while password changes, account disablement, cookie loss, and platform-level invalidation may still end access.

## Consequences

This deliberately reduces protection against stolen passwords and unattended browsers. Password and registration throttling remain, historical security audit records remain immutable, and billing retains its unrelated QR-code dependency.
