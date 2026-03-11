# Neon Database Setup Guide

This project uses **Neon** - a serverless PostgreSQL database hosted in the cloud. No local database setup needed!

## ⚡ 5-Minute Setup

### Step 1: Create Neon Account (2 min)
```
Go to: https://neon.tech
Click "Sign Up"
Verify your email
Free tier is perfect for this project!
```

### Step 2: Create Database (1 min)
```
Click "Create a new project"
Name: internet-outage-platform
Region: us-east-1 (choose closest to you)
Click "Create"
```

### Step 3: Get Connection String (1 min)
On the dashboard:
```
Click "Connection string" button
Select "Pooled connection" 
Select "Python"
Copy entire connection string
```

Example connection string:
```
postgresql://neondb_owner:AbCdEfGhIjKlMnOp@ep-cool-lake-a1b2c3d4.us-east-1.neon.tech/neondb?sslmode=require
```

### Step 4: Extract Credentials (1 min)
From connection string above, extract these values:

| Field | Value |
|:---|:---|
| `DB_HOST` | `ep-cool-lake-a1b2c3d4.us-east-1.neon.tech` |
| `DB_PORT` | `5432` |
| `DB_USER` | `neondb_owner` |
| `DB_PASSWORD` | `AbCdEfGhIjKlMnOp` |
| `DB_NAME` | `neondb` |

---

## 🔧 Local Testing (Optional)

Test that everything works before GitHub setup:

```bash
# Set environment variables
export DB_HOST="ep-cool-lake-a1b2c3d4.us-east-1.neon.tech"
export DB_PORT="5432"
export DB_USER="neondb_owner"
export DB_PASSWORD="AbCdEfGhIjKlMnOp"
export DB_NAME="neondb"

# Run one ingestion to test
python ingest_cloudflare.py

# Should output: Ingested X records ✓
```

---

## 📝 GitHub Actions Setup (Required)

For automatic daily ingestion, configure GitHub secrets:

1. Go to your GitHub repository
2. **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret** for each item below:

| Secret Name | Value (from Step 4) |
|:---|:---|
| `DB_HOST` | ep-cool-lake-a1b2c3d4.us-east-1.neon.tech |
| `DB_PORT` | 5432 |
| `DB_USER` | neondb_owner |
| `DB_PASSWORD` | AbCdEfGhIjKlMnOp |
| `DB_NAME` | neondb |
| `CLOUDFLARE_API_TOKEN` | Your Cloudflare API token |

---

## ✅ That's It!

Your setup is complete:
- ✓ Data automatically ingests daily at **8:00 AM UTC**
- ✓ Stored in your **Neon PostgreSQL database** (cloud-hosted)
- ✓ GitHub Actions handles everything automatically
- ✓ No local database to manage

---

## 📊 Monitor Your Data

### View in Neon Dashboard
1. Log into https://neon.tech
2. Click your project
3. See "Monitoring" tab for usage stats

### Query Data Anytime
```bash
# Set environment variables (from GitHub secrets)
export PGHOST="ep-cool-lake-a1b2c3d4.us-east-1.neon.tech"
export PGUSER="neondb_owner"
export PGPASSWORD="AbCdEfGhIjKlMnOp"
export PGDATABASE="neondb"

# Query your data
psql -c "SELECT COUNT(*) FROM raw.cloudflare_outages;"
psql -c "SELECT COUNT(*) FROM raw.cloudflare_ai_bots;"
psql -c "SELECT COUNT(*) FROM raw.cloudflare_device_type;"
```

### Monitor GitHub Actions
1. Your repo → **Actions** tab
2. Click **"Daily Data Ingestion"**
3. See logs and status

---

## 🆘 Troubleshooting

**Connection fails?**
- Double-check credentials copied from Neon
- Ensure password doesn't have special characters
- Test with: `psql -h your-host.neon.tech -U your-user -d neondb -c "SELECT 1;"`

**GitHub Actions not running?**
- Verify all 6 secrets are configured
- Wait 5 minutes for secrets to sync
- Manually trigger: Actions → "Daily Data Ingestion" → "Run workflow"

**No data appearing?**
- Check GitHub Actions logs for errors
- Verify Neon database exists and is accessible
- Run locally to test: `python ingest_cloudflare.py`

---

## 💰 Neon Pricing

This project uses **free tier** of Neon:
- ✓ Unlimited databases
- ✓ 50 GB data transfer per month
- ✓ Your usage: ~1,200 records/day = **$0/month**
- ✓ Perfect for this use case!

Upgrade to paid only if you exceed limits.

---

## 📚 More Information

- **Full README**: See `README.md` for project overview
- **Deployment Details**: See `DEPLOYMENT.md`
- **GitHub Actions**: See `GITHUB_DEPLOYMENT.md`

---

## 🎉 Setup Complete!

Data automatically ingests to your Neon database every day at 8:00 AM UTC! 🚀
