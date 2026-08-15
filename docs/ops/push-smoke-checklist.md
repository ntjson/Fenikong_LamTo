# Real-device push smoke checklist

Manual verification of FCM registration and deep-link routing on a physical
device (or a fully configured emulator with Firebase platform config installed
**out of band** — never commit `google-services.json` /
`GoogleService-Info.plist`).

**Preconditions**

- [ ] Non-production backend with pilot seed (`PILOT_ALLOW_FIXTURES=1 … seed_pilot --fixture`)
- [ ] Resident app build that includes Firebase platform config for this install
- [ ] Backend has `PUSH_ENABLED=1` and a valid `FIREBASE_CREDENTIALS` path
- [ ] Login as seeded resident (`pilot-resident@pilot.lamto.test` or equivalent)

Record device model, OS version, app build id, and date at the top of each run.

---

## 1. Permission request (spec §7.5 / A4)

| Step | Action | Expected | Pass |
|------|--------|----------|------|
| 1.1 | Fresh install (or clear app data). Sign in. Do **not** expect a permission prompt at launch. | No OS notification dialog on cold start / login | ☐ |
| 1.2 | Open **Phản ánh**, submit a report (text + location; photo optional). | After successful submit, OS notification permission dialog appears **once** | ☐ |
| 1.3 | Grant permission. | Dialog dismisses; no second prompt on later submits | ☐ |
| 1.4 | (Optional) Deny path: reinstall, submit again, deny. Later submits must **not** re-prompt. Enabling notifications in system settings should allow a subsequent successful register without re-prompt. | Once-per-install flag holds | ☐ |

---

## 2. Device registration (spec §7.2)

| Step | Action | Expected | Pass |
|------|--------|----------|------|
| 2.1 | After granting permission in §1, inspect server `Device` rows (admin/shell) for this user. | One active device with stable `install_id`, current FCM token, platform, app version | ☐ |
| 2.2 | Force-kill and relaunch; submit another report (or wait for any post-auth register path). | Upsert by `install_id` — **no** duplicate active rows for the same install | ☐ |

---

## 3. Token refresh re-registration

| Step | Action | Expected | Pass |
|------|--------|----------|------|
| 3.1 | Simulate FCM token rotation (Firebase debug / clear app data of Google Play services token if available, or use a debug hook that emits `onTokenRefresh`). | Client calls `POST /api/v1/devices` again with the **same** `install_id` and **new** token | ☐ |
| 3.2 | Confirm server row. | Token updated; still a single active install for that id | ☐ |

---

## 4. Background / terminated notification-tap routing (spec §7.4)

Send a data/notification payload (via Firebase console or server push) with
allowlisted deep-link fields only — **no** amounts, names, or report text in the
payload:

| Case | Payload (data) | App state | Expected | Pass |
|------|----------------|-----------|----------|------|
| 4.1 Report | `type=report`, `id=<known report id>` | App in **background** | Tap opens issue detail for that id (API re-fetch; 404/403 → safe fallback) | ☐ |
| 4.2 Ledger | `type=ledger`, `id=<known ledger id>` | App in **background** | Tap opens ledger detail | ☐ |
| 4.3 Feed | `type=notifications` (or feed key per client map) | App in **background** | Tap opens notifications feed | ☐ |
| 4.4 Terminated report | same as 4.1 | App **force-stopped / killed** | Cold start from tap lands on issue detail | ☐ |
| 4.5 Unknown type | `type=not_a_real_route`, `id=1` | Any | Ignored — no crash; stay on / open shell safely | ☐ |

Also confirm the in-app **Thông báo** feed remains authoritative if a push is
dropped.

---

## 5. Logout deregistration (spec §7.2 / A5)

| Step | Action | Expected | Pass |
|------|--------|----------|------|
| 5.1 | From **Tài khoản**, sign out (this device). | Client deactivates device for current `install_id` before clearing the session | ☐ |
| 5.2 | Inspect server device row. | Device inactive / gone for that install; no further pushes to that token for this user session | ☐ |
| 5.3 | Sign in again on the same install; complete §1–§2 again. | New active registration for (possibly same) install id after consent path | ☐ |
| 5.4 | (Optional) Airplane-mode logout: sign out offline. | Local session clears; pending deregister is retried on next successful authenticated session | ☐ |
| 5.5 | **Đăng xuất mọi thiết bị** (if exercised). | Server logout-all + this install deactivated; user ends on login | ☐ |

---

## Sign-off

| Role | Name | Date | Result |
|------|------|------|--------|
| Mobile | | | ☐ pass / ☐ fail |
| Backend / ops | | | ☐ pass / ☐ fail |

**Notes / defects:**

-
