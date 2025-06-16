# 📊 Mutual Fund Manager

This is a backend service for a mutual fund brokerage application built using **FastAPI** and **PostgreSQL**. It allows users to:

- Register & log in securely
- Fetch mutual fund schemes via RapidAPI by fund family
- Track portfolio values based on daily NAV updates
- Run daily cron job to update portfolio values automatically

---

## ⚙️ Tech Stack

- **FastAPI** - Web framework
- **SQLModel** - ORM
- **PostgreSQL** - Database
- **APScheduler** - Scheduled tasks
- **uv** - Fast dependency manager & virtual environment handler

---

## 🚀 Features

- ✅ Secure user registration and login (hashed passwords)
- 📦 Fetch mutual fund schemes via RapidAPI
- 💼 Portfolio tracking: units, current value
- 📆 Daily background update for NAV-based portfolio values
- 🧪 E2E testing with `pytest`

---

## 🔧 Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/your-username/mutual-fund-backend.git
cd mutual-fund-backend
```

### 2. Install `uv` (if not already)

```bash
pip install uv
```

### 3. Create virtual environment & install dependencies

```bash
uv venv
source .venv/bin/activate      # On Windows: .venv\Scripts\activate
uv pip install
```

### 4. Set up environment variables

Create a `.env` file in the project root and add env variables:
Added a .env.example for reference

```ini
DATABASE_URL=postgresql://postgres:password@localhost/mutualfund
RAPIDAPI_KEY=your_rapid_api_key
RAPIDAPI_HOST=latest-mutual-fund-nav.p.rapidapi.com
```

---

### 5. Create the database

Ensure PostgreSQL is running locally, then create the `mutualfund` database:

```bash
createdb mutualfund
```

Or using psql:

```sql
CREATE DATABASE mutualfund;
```

---

### 7. Start the development server

```bash
uvicorn app.main:app --reload
```

Visit the docs at: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🧪 Running Tests

To run tests:

```bash
pytest tests
```

---

## 📁 Project Structure

```
mutual_fund_app/
├── app/
│   ├── db/              # DB engine and session
│   ├── models/          # SQLModel models
│   ├── routes/          # FastAPI route handlers
│   ├── services/        # Scheduler & API client
│   ├── utils/           # Utility functions (e.g. hashing)
│   └── main.py          # FastAPI app entrypoint
|
├── tests/               # End-to-end tests
├── pyproject.toml       # Project dependencies & metadata
├── alembic.ini
└── README.md
```

---

## 🗓️ Background NAV Updates

The app uses `APScheduler` to fetch the latest NAV for all user portfolios **once every day**.

You can customize the frequency in `app/services/scheduler.py`:

```python
scheduler.add_job(update_portfolios, "interval", days=1)
```

---


## 📄 License

MIT License
