# BUGZERO AI

Python-powered AI coding assistant built on your supplied BugZero landing page.

## Features
- Existing BugZero landing page retained at `/`.
- Workspace at `/app`.
- Flask JSON APIs for code review, debugging, security analysis, code fixing, test generation, code generation and chat.
- BugZero Intelligence: a four-stage AI workflow (Detect → Explain → Fix → Verify) that returns corrected code and a second static AI review. It does not execute submitted code.
- SQLite history for authenticated users.
- Registration/login with hashed passwords.
- Basic local security pattern checks.
- Optional GitHub repository listing through a server-side personal access token.

## Run locally
Requires Python 3.10+.

```bash
# Windows PowerShell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Edit `.env`, set a strong `SECRET_KEY`, and add `OPENAI_API_KEY`. To enable GitHub repository listing, set a GitHub token with minimum required repository read permissions in `GITHUB_TOKEN`.

```bash
python -m backend.app
```

Open:
- Landing page: http://127.0.0.1:5000/
- Workspace: http://127.0.0.1:5000/app
- Health: http://127.0.0.1:5000/health

## API
- `POST /api/review` `{ "code": "...", "language": "Python" }`
- `POST /api/debug` same payload
- `POST /api/security` same payload
- `POST /api/fix` same payload
- `POST /api/smartfix` same payload; returns diagnosis, beginner-friendly explanation, proposed corrected code, and a second AI review.
- `POST /api/tests/generate` same payload
- `POST /api/generate` `{ "prompt": "...", "language": "Python" }`
- `POST /api/chat` `{ "message": "...", "code": "...", "language": "Python" }`
- `POST /api/auth/register` `{ "username": "...", "email": "...", "password": "..." }`
- `POST /api/auth/login` `{ "email": "...", "password": "..." }`
- `POST /api/auth/logout`
- `GET /api/history` (login required)
- `GET /api/github/repositories` (requires server-side `GITHUB_TOKEN`)

## Important security notes
- AI features require a valid API key and may incur provider charges.
- Never commit `.env` or expose API keys in browser code.
- User code is sent to the configured AI provider when AI endpoints are called. Do not submit secrets or confidential source unless you have approval.
- Submitted code is never executed by this application. BugZero's Verify stage is a static AI review, not a real test run.
- The GitHub integration in this starter uses a server-side token. For a public multi-user product, implement GitHub OAuth per user, encrypted token storage, webhook signature validation and scoped permissions before launch.
- Before production, configure HTTPS, secure cookie settings, CSRF protection, rate limiting, robust logging, backups, and a production database.
- The supplied landing page's original waitlist handler depends on a host-specific `window.claude` object; that handler is not a Flask integration and needs a dedicated waitlist endpoint before using the waitlist in production.
