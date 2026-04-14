# STIgma — Usage Guide

> Step-by-step instructions for setting up, running, and using STIgma on your remote server.

---

## Prerequisites

Before you begin, ensure you have:

- Python 3.12+ installed (`python3 --version`)
- [uv](https://docs.astral.sh/uv/) installed (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- PostgreSQL 17 running (`sudo systemctl status postgresql@17-main`)
- An OpenAI API key (for CrewAI) — [platform.openai.com](https://platform.openai.com)
- A SerperDev API key (for web search) — [serper.dev](https://serper.dev) (free tier available)

---

## Day 1 — Setup & First Run

### Step 1: Clone / copy the project

```bash
# On your remote server (SSH in first)
cd ~/learning
# If starting from scratch, the project folder is already named stigma/
cd stigma
```

### Step 2: Install dependencies with uv

```bash
uv sync
```

This reads `pyproject.toml` and creates a `.venv` in the project root with all dependencies installed.

### Step 3: Configure environment variables

```bash
cp .env.example .env
nano .env   # or: vim .env
```

Fill in your values:

```env
DJANGO_SECRET_KEY=your-long-random-secret-key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=stigma
DB_USER=postgres
DB_PASSWORD=your-postgres-password
DB_HOST=localhost
DB_PORT=5432

OPENAI_API_KEY=sk-...
CREWAI_LLM_MODEL=gpt-4o-mini

SERPER_API_KEY=your-serper-key
```

> **Generating a secret key:**
> ```bash
> uv run python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
> ```

### Step 4: Create the database

```bash
# Connect as postgres superuser
sudo -u postgres psql

# Inside psql:
CREATE DATABASE stigma;
CREATE USER stigma_user WITH PASSWORD 'your-password';
GRANT ALL PRIVILEGES ON DATABASE stigma TO stigma_user;
\q
```

Then update `.env` with `DB_USER=stigma_user` and `DB_PASSWORD=your-password`.

### Step 5: Run database migrations

```bash
uv run python manage.py migrate
```

Expected output: Django applies all migrations including `blog`, `taggit`, `markdownx`.

### Step 6: Create a superuser (admin account)

```bash
uv run python manage.py createsuperuser
```

You'll be prompted for username, email, and password. This account is used for:
- Django admin (`/admin/`)
- AI post generation (`/ai/generate/`)

### Step 7: Collect static files

```bash
uv run python manage.py collectstatic --no-input
```

### Step 8: Start the development server

```bash
uv run python manage.py runserver 0.0.0.0:8000
```

Visit `http://localhost:8000` — you should see the STIgma homepage.

---

## Day 2 — Content & AI Generation

### Creating Categories

1. Go to `http://localhost:8000/admin/`
2. Log in with your superuser credentials
3. Click **Blog → Categories → Add Category**
4. Create 3–5 categories (e.g., Technology, Culture, Science, Opinion)

### Writing a Post Manually

1. Admin → **Blog → Posts → Add Post**
2. Fill in Title, Body (Markdown supported), Excerpt, Category, Tags
3. Set **Status → Published** and **Published at** to now
4. Click **Save**

The post will appear on the homepage immediately.

### Generating a Post with AI

1. Visit `http://localhost:8000/ai/generate/` (staff login required)
2. Fill in the form:
   - **Topic:** e.g. `The Hidden Cost of Microservices Architecture`
   - **Target Audience:** e.g. `Senior software engineers and engineering managers`
   - **Tone:** Choose from the dropdown
   - **Category:** Optional — assigns the generated post to a category
3. Click **✦ Generate Post with AI**
4. Wait 2–5 minutes. The three agents will run sequentially:
   - Researcher searches the web and compiles a brief
   - Writer drafts the full post
   - Editor polishes it and outputs structured JSON
5. A success message appears with a link to the draft in Admin
6. Review the draft in Admin → edit if needed → set **Status → Published**

> **If generation fails:** Check that `OPENAI_API_KEY` and `SERPER_API_KEY` are set correctly in `.env`. Restart the server after changing `.env`.

---

## Admin Reference

| URL | Purpose |
|-----|---------|
| `/admin/` | Main Django admin |
| `/admin/blog/post/` | Manage all posts |
| `/admin/blog/post/?is_ai_generated__exact=1` | Filter AI-generated drafts |
| `/admin/blog/category/` | Manage categories |
| `/admin/blog/comment/?is_approved__exact=0` | Pending comments to approve |
| `/ai/generate/` | AI post generation (staff only) |

### Approving Comments

Comments require manual approval before they appear publicly:

1. Admin → **Blog → Comments**
2. Select pending comments
3. Action → **Approve selected comments** → Go

---

## Production Deployment

### Environment changes

```env
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DJANGO_SECRET_KEY=<new-long-random-key>
```

### Run with Gunicorn

```bash
uv run gunicorn stigma.wsgi:application \
  --workers 4 \
  --bind 0.0.0.0:8000 \
  --timeout 300 \
  --log-level info
```

> `--timeout 300` is important: CrewAI generation can take up to 5 minutes.

### Nginx configuration (example)

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location /static/ {
        alias /path/to/stigma/staticfiles/;
    }

    location /media/ {
        alias /path/to/stigma/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 300s;
    }
}
```

---

## Useful Commands

```bash
# Run development server
uv run python manage.py runserver

# Create and apply new migration after model changes
uv run python manage.py makemigrations
uv run python manage.py migrate

# Open Django shell
uv run python manage.py shell

# Run tests
uv run pytest

# Check for configuration errors
uv run python manage.py check --deploy

# Load sample data (if fixture provided)
uv run python manage.py loaddata sample_data.json
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `django.db.OperationalError: connection refused` | Start PostgreSQL: `sudo systemctl start postgresql@17-main` |
| `ModuleNotFoundError: No module named 'crewai'` | Run `uv sync` — dependencies not installed |
| AI generation returns JSON parse error | The LLM wrapped JSON in markdown fences. The view strips these automatically. If persisting, try `gpt-4o` instead of `gpt-4o-mini` |
| `SERPER_API_KEY` not set error | Add `SERPER_API_KEY=your-key` to `.env` and restart server |
| Static files not loading | Run `uv run python manage.py collectstatic` |
| Admin shows no posts | Check that posts have `status=published` |
