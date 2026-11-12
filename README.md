# Universal Public Document Library

A lightweight, public, AI-accessible document library built with FastAPI.

## Features
- Public browsing, search (keyword + TF-IDF semantic), document pages
- REST API v1 with OpenAPI docs
- MCP server (streamable HTTP) at /mcp
- Google Drive sync (read-only) via admin dashboard
- Text extraction for PDF, DOCX, XLSX, PPTX, TXT, CSV, HTML, Markdown, EPUB, ODT, etc.
- Sitemap, robots.txt, llms.txt, RSS feed

## Run locally
```bash
cd public-doclib
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# edit .env
uvicorn app.main:app --host 0.0.0.0 --port 8000
```
Open http://localhost:8000

## Environment variables
See .env.example. Important: SECRET_KEY, ADMIN_PASSWORD, DATABASE_URL, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI, SITE_URL.

## Admin
- URL: /admin
- Password: ADMIN_PASSWORD (default "admin" — change in production)
- Connect Google Drive: /admin/google/connect
- Set folder ID in admin settings, then Sync.

## Google Drive OAuth setup (Bengali)
1. Google Cloud Console খুলুন (console.cloud.google.com)।
2. নতুন Project তৈরি করুন।
3. APIs & Services > Library থেকে "Google Drive API" Enable করুন।
4. APIs & Services > OAuth consent screen: External, app name দিন, scopes এ `.../auth/drive.readonly` যোগ করুন।
5. APIs & Services > Credentials > Create Credentials > OAuth client ID (Web application)।
6. Authorized redirect URI তে আপনার সাইটের `/admin/google/callback` URL দিন (যেমন https://your-site.com/admin/google/callback)।
7. Client ID ও Client Secret কপি করে environment variable এ সেট করুন।
8. ওয়েবসাইটের /admin পেজে গিয়ে "Connect Google Drive" বাটন চাপুন এবং আপনার Google account দিয়ে অনুমতি দিন।
9. কখনো Google password শেয়ার করবেন না।

## Deployment (Render)
1. GitHub এ code push করুন।
2. render.com এ free account খুলুন।
3. New > Web Service > connect GitHub repo।
4. Build command: `pip install -r requirements.txt`
5. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Environment variables সেট করুন (.env.example অনুযায়ী)।
7. Database: free Postgres (Render/Neon) এর DATABASE_URL ব্যবহার করুন অথবা SQLite (ephemeral)।

## Automated sync
Set up a free cron service (cron-job.org) to GET/POST `https://your-site.com/api/admin/sync?secret=YOUR_ADMIN_PASSWORD` daily.

## API
- GET /api/v1/health
- GET /api/v1/documents
- GET /api/v1/documents/{id}
- GET /api/v1/documents/{id}/content
- GET /api/v1/documents/{id}/download
- GET /api/v1/search?q=
- GET /api/v1/categories
- OpenAPI: /api/openapi.json, /api/docs

## MCP
Endpoint: /mcp (streamable HTTP). Tools: search_documents, get_document_metadata, read_document, search_document_content, list_categories, get_document_sections.

## Limitations
- SQLite on serverless is ephemeral; use Postgres for production.
- OCR requires tesseract + pdf2image (not installed by default).
- Native Google Docs export not handled (download may fail for those).
- Semantic search uses TF-IDF (lightweight), not neural embeddings.
