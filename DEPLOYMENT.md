# Vercel Deployment Guide

Deploy RedSea to Vercel by connecting your Git repo and setting environment variables.

---

## Option A: Deploy by Connecting Your Git Repository (Recommended)

### Step 1: Push your code to Git

1. Initialize Git (if you haven’t):
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```
2. Create a repo on **GitHub**, **GitLab**, or **Bitbucket** and push:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/RedSea.git
   git branch -M main
   git push -u origin main
   ```

### Step 2: Import the project in Vercel

1. Go to **[https://vercel.com/new](https://vercel.com/new)** and sign in.
2. Click **“Add New…” → “Project”** (or “Import Project”).
3. **Import** your Git provider (GitHub/GitLab/Bitbucket) if prompted.
4. Select the **RedSea** repository.
5. Leave **Framework Preset** as detected (or “Other”).
6. **Do not click Deploy yet** — add env vars first (Step 3).

### Step 3: Set environment variables in Vercel

1. On the same “Import Project” screen, open the **“Environment Variables”** section.
2. Add these variables (use **Production**, and optionally **Preview**):

   | Name                  | Value              | Notes                    |
   |-----------------------|--------------------|--------------------------|
   | `REDDIT_CLIENT_ID`    | your Reddit client ID | Required              |
   | `REDDIT_CLIENT_SECRET`| your Reddit secret    | Required              |
   | `REDDIT_USER_AGENT`   | `SentimentPulse`     | Optional (app default)   |

3. Get Reddit credentials from **[https://www.reddit.com/prefs/apps](https://www.reddit.com/prefs/apps)** (create an app; use the client ID and secret).
4. Click **“Deploy”**.

### Step 4: After the first deploy

- To add or change env vars later: **Project → Settings → Environment Variables**.
- Redeploys happen automatically on every push to your connected branch.

---

## Environment variables reference

| Variable               | Required | Description                          |
|------------------------|----------|--------------------------------------|
| `REDDIT_CLIENT_ID`     | Yes      | Reddit API client ID                 |
| `REDDIT_CLIENT_SECRET` | Yes      | Reddit API client secret             |
| `REDDIT_USER_AGENT`   | No       | User agent string (default: SentimentPulse) |

Local development: copy `.env.example` to `.env` and fill in the values. Never commit `.env`.

---

## Option B: Deploy with Vercel CLI

1. Install and log in:
   ```bash
   npm i -g vercel
   vercel login
   ```
2. Add env vars (when prompted, or in Dashboard later):
   ```bash
   vercel env add REDDIT_CLIENT_ID
   vercel env add REDDIT_CLIENT_SECRET
   vercel env add REDDIT_USER_AGENT
   ```
3. Deploy:
   ```bash
   vercel
   vercel --prod   # production
   ```

---

## Project structure (Vercel)

- `api/index.py` — Serverless entry for the Flask app  
- `vercel.json` — Build and routes  
- `app.py` — Main Flask app  
- `templates/`, `static/` — Front-end assets  

---

## Notes

- **NLTK**: vader_lexicon is downloaded on first run; first request may be slower.
- **Timeouts**: Free tier has a 10s function timeout; long runs may need optimization or a paid plan.
- **Static files**: Served from `static/` via `vercel.json`.

## Local test (Vercel-like)

```bash
vercel dev
```
