# Deployment checklist (security, backup, network)

Use this list before promoting a pilot environment. Every item is required unless marked optional.

- [ ] `buffalo_l` (~326MB) is baked under `INSIGHTFACE_HOME`; never download it on first request.
- [ ] Changing the face model triggers resident re-enrolment and threshold recalibration.

## Transport and edge

- [ ] HTTPS terminated at the reverse proxy with a valid certificate
- [ ] HSTS enabled at the reverse proxy (`Strict-Transport-Security`)
- [ ] Django `SECURE_PROXY_SSL_HEADER` set when behind TLS-terminating proxy
- [ ] Session and CSRF cookies: `Secure`, `HttpOnly` (session), `SameSite=Lax` (or stricter)
- [ ] CSRF protection enabled on all state-changing views

## Data at rest and in transit

- [ ] TLS to managed PostgreSQL
- [ ] TLS to object storage (S3-compatible endpoint)
- [ ] Encrypted database volumes
- [ ] Encrypted WAL-G backups (`WALG_LIBSODIUM_KEY`)
- [ ] Private, versioned object buckets with server-side encryption
- [ ] No public ACLs / no public bucket policies on document or ops buckets

## Secrets

- [ ] Secret-manager injection for `SECRET_KEY`, DB password, storage keys
- [ ] Secret-manager injection for `PLATFORM_SIGNER_PRIVATE_KEY`
- [ ] Secret-manager injection for blockchain relayer private key
- [ ] Secret-manager injection for contract-owner private key
- [ ] No secrets in git, images, or CI logs
- [ ] Log redaction for Authorization headers, cookies, OTP codes, passwords

## Blockchain / RPC

- [ ] Blockchain RPC reachable only on localhost or a private network
- [ ] Platform signer, relayer, and owner keys never exposed to browsers or stakeholders
- [ ] Run `uv run python manage.py authorize_platform_signer` with the contract owner key before starting workers

## Identity and privileged access

- [ ] Argon2 password hasher preferred
- [ ] Staff MFA (TOTP) enrolled before staff workspace access
- [ ] Recent re-authentication (password + OTP, ≤300s) for signed financial actions
- [ ] Auth throttle: 5 failures / 15 minutes across workers
- [ ] Session rotation on login/MFA; full revocation on logout
- [ ] Every staff user has an active building-scoped Management membership
- [ ] Cross-building object access returns 404; inactive or missing Management access returns 403

## Exports and health

- [ ] Audit CSV export restricted to authenticated Management users in the active building
- [ ] Formula neutralization on CSV text cells
- [ ] Exports never include raw file bytes, wallet private data, or bank account numbers
- [ ] Ops health + pilot metrics restricted to authenticated Management users in the active building
- [ ] Health/metrics never display stakeholder signatures/private keys or document content

## Backup and recovery

- [ ] Daily WAL-G base/WAL backup scheduled (`ops/backup/backup.sh`)
- [ ] Object version backup + signed marker after each successful DB backup
- [ ] Restore-drill cadence documented and executed (`ops/backup/restore-drill.sh`)
- [ ] Drill report retained; isolated DB/prefix destroyed after report export
- [ ] Documented key and session revocation runbook (staff password reset, TOTP revoke, wallet revoke)

## Application config reminders

- [ ] `DEBUG=0` in production
- [ ] `ALLOWED_HOSTS` locked down
- [ ] ClamAV and AI triage endpoints reachable only from app network
- [ ] Worker process supervised (`run_worker`) with connection recycling
