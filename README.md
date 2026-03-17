# ProgectLibrary - Library Management System

A modern, OOP-based library management system built with FastAPI. Features user authentication, book catalog management, borrowing system with availability tracking, overdue notifications, audit logging, and GDPR compliance.

##  Table of Contents

- [Features](#features)
- [System Requirements](#system-requirements)
- [Installation Guide](#installation-guide)
  - [Step 1: Clone the Repository](#step-1-clone-the-repository)
  - [Step 2: Set Up Python Virtual Environment](#step-2-set-up-python-virtual-environment)
  - [Step 3: Install Dependencies](#step-3-install-dependencies)
  - [Step 4: Configure Environment Variables](#step-4-configure-environment-variables)
  - [Step 5: Verify Installation](#step-5-verify-installation)
- [Running the Application](#running-the-application)
- [Running Tests](#running-tests)
- [How the Project Works](#how-the-project-works)
- [Where Your Code Goes](#where-your-code-goes)
- [For Frontend Developers](#for-frontend-developers)
- [API Documentation](#api-documentation)
- [Troubleshooting](#troubleshooting)

---

## Features

✅ **User Management**
- User registration and authentication
- Role-based access control (Admin, Advanced User, Regular User)
- GDPR-compliant user deletion

✅ **Book Catalog**
- Add/update/delete books
- Track total and available quantities
- Book categorization (Fantasy, Criminal, Drama)

✅ **Borrowing System**
- Borrow books with configurable periods (1-365 days)
- Track availability in real-time
- Return management with automatic quantity restoration
- Overdue detection and notifications

✅ **Security & Audit**
- JWT-based authentication (access + refresh tokens)
- Password hashing with bcrypt
- Fernet encryption for data files at rest
- HMAC-signed audit logs for tampering detection
- Comprehensive audit trail with replay capability

✅ **Notifications**
- SMS notifications via Twilio (configurable)
- Email notifications via SMTP (Gmail, custom servers)
- Automatic overdue reminders (daily at 9 AM)

✅ **Data Persistence**
- File-based encrypted storage (no database required)
- Atomic operations with threading locks to prevent race conditions

---

## System Requirements

### Windows & Mac
- **Python**: 3.11 or higher
- **Git**: For cloning the repository
- **Disk Space**: ~1 GB (including virtual environment)
- **RAM**: 512 MB minimum

### Check Your Python Version

**Windows (PowerShell):**
```powershell
python --version
```

**Mac (Terminal):**
```bash
python3 --version
```

---

## Installation Guide

### Step 1: Clone the Repository

**All OS (Windows PowerShell, Mac Terminal):**
```bash
git clone https://github.com/your-username/ProgectLibrary.git
cd ProgectLibrary
```

---

### Step 2: Set Up Python Virtual Environment

A virtual environment isolates this project's dependencies from your system Python.

#### **Windows (PowerShell):**

```powershell
# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\Activate.ps1

# If you get an execution policy error, run this first:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**✅ Success**: Your prompt will show `(venv)` at the beginning, like:
```
(venv) PS C:\Users\YourName\ProgectLibrary>
```

#### **Mac (Terminal):**

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate
```

**✅ Success**: Your prompt will show `(venv)` at the beginning, like:
```
(venv) your-machine:ProgectLibrary yourname$
```

---

### Step 3: Install Dependencies

With the virtual environment activated, install all required packages:

**Windows & Mac (same command):**
```bash
pip install -r requirements.txt
```

⏳ This takes 2-3 minutes. You'll see `Successfully installed` message at the end with 30+ packages.

---

### Step 4: Configure Environment Variables

Create a `.env` file in the project root with required configuration.

#### **Windows (PowerShell):**

```powershell
# Create the .env file
New-Item -Path .env -ItemType File

# Edit it (opens in Notepad)
notepad .env
```

#### **Mac (Terminal):**

```bash
# Create and edit the .env file
nano .env
```
Press `Ctrl+O`, then `Enter` to save, then `Ctrl+X` to exit nano.

#### **Contents of `.env` file:**

Copy and paste the following, then follow the key generation steps below:

```ini
# ════════════════════════════════════════════════════════════════
# CRITICAL: Must be configured before first run
# ════════════════════════════════════════════════════════════════

# JWT Secret for access/refresh tokens
SECRET_KEY=your-super-secret-key-min-32-chars-long-please

# Generate these using the script below
FERNET_KEY=
AUDIT_HMAC_KEY=

# Application Environment
APP_ENV=development
LOG_LEVEL=INFO

# ════════════════════════════════════════════════════════════════
# OPTIONAL: Notifications (leave blank for development)
# ════════════════════════════════════════════════════════════════

# SMS via Twilio (intentionally left for production setup)
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_FROM_NUMBER=

# Email via SMTP (Gmail shown as example)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=

# ════════════════════════════════════════════════════════════════
# OPTIONAL: Storage (default should work fine)
# ════════════════════════════════════════════════════════════════

DATA_DIR=./data
```

#### **Generate Encryption Keys**

You need to generate `FERNET_KEY` and `AUDIT_HMAC_KEY`. Run the key generation script:

**Windows & Mac:**
```bash
python scripts/generate_keys.py
```

This outputs two keys. Copy them into your `.env` file:
```
FERNET_KEY=gAAAAABlFxxx...xxxx
AUDIT_HMAC_KEY=gAAAAABlFyyy...yyyy
```

#### **Set a Strong SECRET_KEY**

The `SECRET_KEY` is used for JWT signing. Create a strong string:

**Option 1 - Using Python (all OS):**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the output into `SECRET_KEY=` in `.env`.

**Option 2 - Manual (any OS):**
Use any string with 32+ random characters:
```
SECRET_KEY=MyL0ng_RandomK3y_At_L3ast_32_Chars_0912837465
```

---

### Step 5: Verify Installation

Test that everything works:

**Windows & Mac (same command, venv still active):**
```bash
python -c "from app.main import app; print('✅ Application imports successfully')"
```

Expected output:
```
✅ Application imports successfully
```

---

## Running the Application

Once installation is complete, start the development server:

**Windows & Mac:**
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Expected output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

### Access the API

- **Interactive Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Alternative Docs**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

### Stop the Server

Press `Ctrl+C` in the terminal.

---

## Running Tests

The project includes comprehensive tests using pytest.

**Windows & Mac (venv active):**
```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=app --cov-report=html --cov-report=term

# Run specific test file
pytest tests/test_auth_router.py -v

# Run tests matching a pattern
pytest -k "book" -v
```

Test results are displayed in terminal. Coverage report generates HTML in `htmlcov/` directory.

---

## How the Project Works

### The Basic Idea

This is a **backend API** (a service that handles data). Think of it like a restaurant:

- **Frontend** = Customer interface (what users see and click on)
- **API** = The kitchen (processes requests, returns data)
- **Database** = The storage (where ingredients/data live)

Your frontend sends **requests** to the backend (like "give me all books"). The backend processes the request, reads/writes data, and sends back a **response** (like "here are the books").

### How Code Moves Through the System

```
Frontend (HTML/JavaScript)
    ↓ asks for data (HTTP request)
    ↓
Routers (app/routers/*.py) 
    "Which endpoint was called? /api/books?"
    ↓
Services (app/services/*.py)
    "What should I do? Find books and return them"
    ↓
Repositories (app/repositories/*.py)
    "Go read the data from storage"
    ↓
Models (app/models/*.py)
    "Shape the data into the right format"
    ↓
API Response (back to frontend)
    ← returns JSON data (like: [{"id": "123", "title": "Harry Potter"}])
```

### Real Example: Borrowing a Book

1. **Frontend** - User clicks "Borrow Book" button  
   → Sends request: `POST /api/borrows {"book_id": "123", "days": 14}`

2. **Router** (`app/routers/borrows.py`) - Receives the request  
   → Calls the BorrowService to handle the logic

3. **Service** (`app/services/borrow_service.py`) - Decides what to do  
   → "Is the book available? If yes, reduce the count and save the borrow"  
   → Calls repositories to read/write data

4. **Repositories** (`app/repositories/`) - Get/save actual data  
   → `BookRepository.find_by_id()` - Find the book  
   → `BorrowRepository.save()` - Save the borrow record

5. **Response** - Sent back to frontend  
   → `{"id": "borrow-456", "book_id": "123", "date_taken": "2026-03-17", "days": 14}`

The frontend then shows "Book borrowed successfully!" to the user.

---

## Where Your Code Goes

As a **backend developer**, you'll mostly work in these folders:

### 🔴 **If adding a NEW FEATURE** (e.g., "Add book reviews")

| What | Where | Example |
|------|-------|---------|
| **Data structure** (what fields?) | `app/models/` | Create `app/models/review.py` with ReviewCreate, ReviewInDB |
| **Business logic** (what happens?) | `app/services/` | Create `app/services/review_service.py` with add/delete review |
| **Storage** (how to save?) | `app/repositories/` | Create `app/repositories/review_repo.py` |
| **API endpoints** (what URLs?) | `app/routers/` | Create `app/routers/reviews.py` with POST, GET, DELETE |
| **Security** (who can do it?) | `app/dependencies.py` | Add role checks if needed |
| **Tests** (does it work?) | `tests/` | Create `tests/test_review_service.py` |

**Do NOT modify:**
- `app/main.py` (unless adding new routers)
- `app/core/` (unless fixing bugs)
- `requirements.txt` (unless adding dependencies)

### 🟡 **If modifying EXISTING code**

Just edit the relevant `app/services/` or `app/repositories/` file. The routers will automatically use the updated code.

**Example:** To make book borrowing stricter:
1. Edit `app/services/borrow_service.py` - Change the validation logic
2. That's it! No other changes needed.

---

## For Frontend Developers

### What You Need to Know

**The backend is already built.** Your job is to create a nice interface (HTML/CSS/JavaScript) that uses it.

### How Frontend Connects to Backend

Your HTML form sends **HTTP requests** to the backend API. The backend responds with **JSON data**.

#### Example: Login Form (HTML)

```html
<form id="loginForm">
  <input type="email" id="email" placeholder="Email">
  <input type="password" id="password" placeholder="Password">
  <button type="submit">Login</button>
</form>

<script>
  document.getElementById("loginForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    
    // Send request to backend
    const response = await fetch("http://localhost:8000/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({
        username: email,  // "username" field expected by backend
        password: password
      })
    });
    
    const data = await response.json();
    // data contains: {access_token: "...", refresh_token: "...", token_type: "bearer"}
    
    // Save token for future requests
    localStorage.setItem("access_token", data.access_token);
    
    console.log("Login successful!");
  });
</script>
```

### Swagger UI - What It Is

When the backend runs, it automatically generates **interactive API documentation** at **[http://localhost:8000/docs](http://localhost:8000/docs)**.

**Swagger UI shows:**
- All available endpoints (URLs)
- What data each endpoint needs
- What data it returns
- A "Try It Out" button to test endpoints

**You don't need to use it for your frontend**, but it's useful to understand what data the backend expects.

### How to Test Your Frontend

**Backend running:**
```bash
uvicorn app.main:app --reload
```

**Frontend running:**
```bash
# Simple approach: open your HTML file in browser
# Open frontend/index.html directly in your browser
# (or use a simple Python server)
```

**Testing in browser console:**
```javascript
// Test if backend is running
fetch("http://localhost:8000/health")
  .then(r => r.json())
  .then(data => console.log("Backend status:", data))
  .catch(e => console.log("Backend not running:", e));
```

### Where to Put Your Frontend Code

Edit the files in `frontend/`:
- `frontend/index.html` - Your main page layout
- `frontend/style.css` - Your styles (create if needed)
- `frontend/script.js` - Your JavaScript (create if needed)

Replace the placeholder HTML with your own code.

### Common Endpoints (For Frontend)

| What | Method | URL | Notes |
|------|--------|-----|-------|
| **Register** | POST | `/api/auth/register` | Send: full_name, email, phone, date_of_birth, address, password |
| **Login** | POST | `/api/auth/login` | Send: username (email), password. Get: access_token |
| **Get books** | GET | `/api/books` | Requires: access_token header, returns list of books |
| **Borrow book** | POST | `/api/borrows` | Send: book_id, days, quantity. Returns: borrow record |
| **Return book** | POST | `/api/borrows/{borrow_id}/return` | Returns: updated borrow record |
| **Get my borrows** | GET | `/api/borrows/me` | Returns: list of your borrows |

### Example: Get All Books (HTML)

```html
<button id="refreshBooks">Load Books</button>
<ul id="bookList"></ul>

<script>
  async function loadBooks() {
    const token = localStorage.getItem("access_token");
    
    const response = await fetch("http://localhost:8000/api/books", {
      headers: { "Authorization": `Bearer ${token}` }
    });
    
    const books = await response.json();
    
    const list = document.getElementById("bookList");
    list.innerHTML = books.map(book => 
      `<li>${book.title} by ${book.author}`
    ).join("");
  }
  
  document.getElementById("refreshBooks").addEventListener("click", loadBooks);
</script>
```

### CORS (Cross-Origin) - Already Set Up

The backend is configured to accept requests from your frontend. Don't worry about CORS errors—they're already handled.

---

## Project Files - Quick Reference

| File/Folder | What It Does | Who Uses It |
|-------------|------------|-----------|
| `app/main.py` | Starts the backend, combines all parts | Backend devs (read only) |
| `app/models/` | Defines data shapes (like database schemas) | Backend devs (edit to add features) |
| `app/services/` | Business logic ("if available < quantity, reject") | Backend devs (edit for logic changes) |
| `app/repositories/` | Read/write from storage files | Backend devs (usually don't edit) |
| `app/routers/` | API endpoints (URLs users call) | Backend devs (edit to add endpoints) |
| `app/core/` | Security, encryption, logging | Backend devs (don't touch unless bug fix) |
| `tests/` | Automated tests (make sure code works) | Backend devs |
| `frontend/` | HTML, CSS, JavaScript | Frontend devs |
| `requirements.txt` | List of libraries needed | Everyone (used by pip install) |
| `.env` | Secret keys and settings | Created locally (don't commit) |
| `scripts/` | One-time setup scripts | Run once by everyone |
| `data/` | Where encrypted data is stored | Auto-created (don't edit manually) |

---

## Swagger UI & API Docs

### What is Swagger?

Swagger (now called "OpenAPI") is **auto-generated documentation** for your backend API.

When you run the backend, FastAPI automatically creates:
- **Swagger UI** at [http://localhost:8000/docs](http://localhost:8000/docs) (interactive, prettier)
- **ReDoc** at [http://localhost:8000/redoc](http://localhost:8000/redoc) (alternative documentation)

### Why It's Useful

**For testing endpoints:**
1. Go to [http://localhost:8000/docs](http://localhost:8000/docs)
2. Click on an endpoint (e.g., `POST /api/books`)
3. Click "Try It Out"
4. Enter data
5. Click "Execute"
6. See the response

**For understanding the API:**
- See what each endpoint needs as input
- See what it returns
- See error codes

**Note:** Your frontend doesn't use Swagger—it uses `fetch()` to call the API. Swagger is just for humans to understand/test.

---

## Troubleshooting

###  "python/python3" command not found

**Windows:**
- Python not installed? Download from [python.org](https://www.python.org) (check "Add Python to PATH")
- Restart PowerShell after install

**Mac:**
- Install Homebrew: `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`
- Then: `brew install python3`

### ❌ "(venv) not showing in terminal"

Virtual environment not activated.

**Windows PowerShell:**
```powershell
.\venv\Scripts\Activate.ps1
```

**Mac Terminal:**
```bash
source venv/bin/activate
```

### ❌ "Module not found" error (e.g., "No module named 'fastapi'")

Virtual environment not active. Run activation command from Step 2 again.

### ❌ "FERNET_KEY is not set in environment"

Missing encryption key in `.env`. Run:
```bash
python scripts/generate_keys.py
```

Copy output to `.env` file.

### ❌ Port 8000 already in use

Another app is using port 8000. Either:

**Option 1:** Stop the other app

**Option 2:** Use a different port
```bash
uvicorn app.main:app --reload --port 8001
```

Then access at `http://localhost:8001/docs`

### ❌ Permission denied error in PowerShell

Windows execution policy blocking scripts.

**Windows PowerShell (Admin):**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
# Then answer 'Y' or 'A' when prompted
```

### ❌ Tests fail with "Decryption failed"

Data files corrupted or keys changed. Safe to delete:
```bash
rm -r data/  # or delete 'data' folder in File Explorer
```

Tests will create fresh data files.

### ❌ Mac only: "zsh: command not found: python"

Use `python3` instead of `python`:
```bash
python3 -m venv venv
source venv/bin/activate
```

Update commands to use `python3` and `pip3`.

---

## Development Notes

### Creating an Admin User

Run the seed script to create an initial admin account:

**Windows & Mac:**
```bash
python scripts/seed_admin.py
```

Credentials printed to console. Change password immediately via API.

### Deactivating the Virtual Environment

When done working:

**Windows:**
```powershell
deactivate
```

**Mac:**
```bash
deactivate
```

### Git Best Practices

Never commit:
- `.env` files (add to `.gitignore`)
- `venv/` directories
- `data/` directories
- `htmlcov/` directories
- `__pycache__/` directories

These are already in `.gitignore`.

Do commit:
- `.gitignore`
- `requirements.txt`
- All source code in `app/`, `tests/`, `scripts/`
- `README.md` and `pyproject.toml`

---

## Performance Notes

### File-Based Storage Limitations

This system uses encrypted file storage instead of a database. It's suitable for:
- ✅ Development and testing
- ✅ Small libraries (<10k books, <1k users)
- ✅ Learning OOP & API design

For production with high load:
- 🔄 Migrate to PostgreSQL or similar
- 🔄 Add database transaction support
- 🔄 Replace file locking with proper database locks
- 🔄 Add caching layer (Redis)

### Encryption Performance

Every file read/write is encrypted with Fernet (AES-128). This adds ~1-5ms overhead per operation. For the current use case, this is negligible.

---

## Support & Contributing

For issues or questions:
1. Check [Troubleshooting](#troubleshooting) section
2. Check [CONTRIBUTING.md](CONTRIBUTING.md) for code standards
3. Check FastAPI docs: [fastapi.tiangolo.com](https://fastapi.tiangolo.com)
4. Check Pydantic docs: [docs.pydantic.dev](https://docs.pydantic.dev)

---

## License

[Specify your license here]

---

**Status**: This is a learning project. It's fully functional for development, testing, and education. The file-based storage is suitable for learning OOP and API design.

**Last Updated**: March 2026