# Demo Setup and Professor Q&A Guide

This project is a student demonstration of a secure library system, not a production SaaS deployment. Present it as a working cybersecurity-focused prototype with clear security controls, tests, and known deployment limits.

## What Is Ready

- Object-oriented backend with services, repositories, models, routers, and encrypted file storage.
- Text-file database in the project `data/` directory: `users.dat`, `books.dat`, `borrows.dat`, `audit.dat`.
- Passwords are hashed with bcrypt and are never stored as plaintext.
- Personal user data is only returned from `/api/users/me`; Administrator and Advanced user list views expose only user ID and role.
- Role-based access:
  - `Administrator`: create/delete users, manage books, view limited user info, run reminders, verify/replay/restore audit data.
  - `Advanced user`: view limited user info and overdue borrows, send SMS/email reminder runs.
  - `User`: register, borrow books, see full own profile, see own borrows, return books, delete own account under GDPR.
- Encrypted audit log with HMAC integrity checks and replay/recovery support.
- Frontend demo for registration, login, catalog filtering, borrowing, profile/GDPR flow, admin actions, staff reminder actions.
- Unit tests cover the main security and business rules.

## What Not To Claim

- Do not call it production-ready.
- Do not claim `.env` secrets are safe if committed. They must stay local or in hosting provider secret storage.
- Do not claim the frontend alone enforces security. The backend is the security boundary; frontend checks are only UX.
- Do not claim real SMS/email is guaranteed unless Twilio/SMTP credentials are configured and tested.

## Local Demo Setup

From the repository root:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Generate secret values and put them into `.env`:

```powershell
python scripts\generate_keys.py
```

Required secret settings for a credible demo:

```text
SECRET_KEY=...
FERNET_KEY=...
AUDIT_HMAC_KEY=...
```

Seed demo data:

```powershell
python scripts\seed_books.py
python scripts\seed_admin.py
```

`seed_books.py` currently contains 22 sample books across the required genres: fantasy, criminal, and drama. It is safe to run more than once because existing sample books are skipped.

Start the backend:

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Start the frontend from a second terminal:

```powershell
cd frontend
python -m http.server 8080
```

Open:

- Frontend: `http://localhost:8080`
- API docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

Do not open `frontend/index.html` directly from disk for the main demo. Serve it over `localhost:8080` so browser origin and API calls behave consistently.

## Test Command

```powershell
pytest -q
```

Before presentation, run tests from a clean terminal after installing dependencies. If a professor asks why tests matter, answer: they prove role restrictions, validation, password hashing, borrow rules, notification behavior, GDPR deletion, audit integrity, and recovery behavior at the code level.

## Demo Script

1. Show `data/` before/after actions and explain the files are custom text records encrypted at rest.
2. Register a normal user and borrow a book for a selected number of days.
3. Show that the user can see full own personal data and own borrow list.
4. Delete that account and explain GDPR deletion removes the user and related borrow records.
5. Login as Administrator, open the Admin panel, create an Advanced user, add/delete a book, and show that user list contains only ID and role.
6. Login as Advanced user, open Staff panel, show limited user/overdue views, and run SMS or email reminder action.
7. Open `/docs` and show protected endpoints return 401/403 without the correct token/role.
8. Run audit verify/recover-preview endpoints or scripts to explain database recovery from logs.

## Hosting Recommendation

For the safest live demonstration, use local hosting on the presenter laptop. It avoids free-tier sleep, blocked SMTP/Twilio egress, file persistence surprises, and public exposure of a student demo.

If remote hosting is required:

- Host backend on Render, Railway, Fly.io, or a small VPS.
- Configure `SECRET_KEY`, `FERNET_KEY`, and `AUDIT_HMAC_KEY` as provider secrets.
- Use a persistent disk/volume for `DATA_DIR`; otherwise the text-file database can disappear on redeploy.
- Run one backend worker for the file-based repository. Multiple workers can race on the same text files.
- Host frontend as static files only after setting it to call the deployed backend API URL.
- Use HTTPS and restrict CORS to the real frontend origin.

## Likely Professor Questions

**Why text files instead of SQL?**  
The assignment asks for text files in a custom format. The repository layer hides the file format, and the plaintext custom records are encrypted before being written to disk.

**Where are passwords stored?**  
Only bcrypt hashes are stored. Login verifies a password against the hash; the original password cannot be recovered.

**Who can see personal data?**  
Only the authenticated owner through `/api/users/me`. Administrator and Advanced user endpoints return `UserPublic`, which contains only `id` and `role`.

**How can the database be restored after data loss?**  
Every important operation writes a signed audit event. Recovery replays the audit log and rebuilds `users.dat`, `books.dat`, and `borrows.dat`.

**How is tampering detected?**  
Audit entries are protected with HMAC signatures. Verification detects entries whose content no longer matches the signature.

**What protects the database and logs?**  
The proposed protection is Fernet encryption for data files and audit logs, plus HMAC signatures for audit integrity. Keys live outside Git in `.env` or hosting secrets.

**Is frontend role checking enough?**  
No. Frontend role checks only hide buttons. Backend dependencies enforce role access and return 403 for forbidden requests.

**What are the remaining production gaps?**  
Use a managed database, rotate keys, add rate limiting, add CSRF strategy if cookie auth is introduced, add centralized secret management, add HTTPS-only deployment, add structured monitoring, and replace local file locking assumptions with transactional storage.
