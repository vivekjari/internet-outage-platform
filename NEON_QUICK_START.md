# Neon Cloud Database - Quick Start

## 🚀 5-Minute Setup

### Step 1: Create Neon Account (2 minutes)
```
Go to: https://neon.tech
Sign up → Create free account → Verify email
```

### Step 2: Create Database (1 minute)
```
Click "Create a new project"
→ Name: internet-outage-platform
→ Region: us-east-1 (or closest to you)
→ Click "Create project"
```

### Step 3: Get Connection Details (1 minute)
```
On dashboard, click "Connection string"
→ Pooled connection
→ Python

Copy the connection string (looks like):
postgresql://neondb_owner:AbCdEfGhIjKlMnOp@ep-cool-lake-a1b2c3d4.us-east-1.neon.tech/neondb?sslmode=require
```

### Step 4: Extract & Save Credentials (1 minute)

From connection string, extract:
- **Host**: `ep-cool-lake-a1b2c3d4.us-east-1.neon.tech`
- **Port**: `5432`
- **User**: `neondb_owner`
- **Password**: `AbCdEfGhIjKlMnOp`
- **Database**: `neondb`

---

## ✅ Configure Locally (Test Before GitHub)

### Option A: Environment Variables (Recommended)

```bash
# Set environment variables
export DB_HOST="ep-cool-lake-a1b2c3d4.us-east-1.neon.tech"
export DB_PORT="5432"
export DB_USER="neondb_owner"
export DB_PASSWORD="AbCdEfGhIjKlMnOp"
export DB_NAME="neondb"

# Test connection
python test_neon_connection.py

# If successful, run ingestion
python ingest_cloudflare.py
python ingest_ai_bots.py
python ingest_device_type.py
```

### Option B: Update config.py (Not recommended for production)

```python
import os

DB_CONFIG = {
    "host": "ep-cool-lake-a1b2c3d4.us-east-1.neon.tech",
    "port": 5432,
    "database": "neondb",
    "user": "neondb_owner",
    "password": "AbCdEfGhIjKlMnOp",
}
```

---

## 🔄 Update GitHub Secrets

Go to: **Your GitHub Repo** → **Settings** → **Secrets and variables** → **Actions**

Create/Update these 6 secrets:

| Secret Name | Value |
|:---|:---|
| `DB_HOST` | `ep-cool-lake-a1b2c3d4.us-east-1.neon.tech` |
| `DB_PORT` | `5432` |
| `DB_USER` | `neondb_owner` |
| `DB_PASSWORD` | `AbCdEfGhIjKlMnOp` |
| `DB_NAME` | `neondb` |
| `CLOUDFLARE_API_TOKEN` | Your Cloudflare token |

**That's it!** GitHub Actions will automatically use Neon from now on.

---

## 📊 Optional: Migrate Existing Data

If you have data in local PostgreSQL and want to keep it:

```bash
# Set local database credentials
export LOCAL_DB_HOST="localhost"
export LOCAL_DB_PORT="5432"
export LOCAL_DB_USER="postgres"
export LOCAL_DB_NAME="internet_outages"

# Add Neon credentials (from Step 4 above)
export DB_HOST="ep-cool-lake-a1b2c3d4.us-east-1.neon.tech"
export DB_USER="neondb_owner"
export DB_PASSWORD="AbCdEfGhIjKlMnOp"
export DB_NAME="neondb"

# Run migration
python migrate_to_neon.py
```

---

## ✅ Verification Checklist

After completing steps above:

- [ ] Neon account created
- [ ] Database created in Neon
- [ ] Connection string obtained
- [ ] Environment variables set
- [ ] `python test_neon_connection.py` passed
- [ ] Ran one ingestion script successfully
- [ ] Updated GitHub secrets with Neon credentials
- [ ] (Optional) Migrated existing data

---

## 🎯 What Happens Next

### Local Testing
```bash
# Any of these commands will work with Neon
python ingest_cloudflare.py
python ingest_ai_bots.py
python ingest_device_type.py
python verify_cloudflare.py
```

### Automatic Daily Runs
- **Time**: 8:00 AM UTC every day
- **What**: Automatically fetches and ingests data into Neon
- **No action needed**: GitHub Actions handles everything

### Monitor in Neon Dashboard
1. Go to Neon console
2. Click your project
3. See "Monitoring" tab for usage stats

---

## 🆘 Quick Troubleshooting

### Connection Test Fails
```bash
# Test with psql directly
psql -h ep-cool-lake-a1b2c3d4.us-east-1.neon.tech \
     -U neondb_owner \
     -d neondb \
     -c "SELECT 1;"
```

If that fails:
- Double-check credentials
- Copy connection string again from Neon console
- Ensure password doesn't have special characters (or escape them)

### GitHub Actions Still Using Local DB
- Wait ~5 minutes for secrets to sync
- Or manually trigger: Actions → "Daily Data Ingestion" → "Run workflow"

### Data Not Appearing
- Check GitHub Actions logs: Your repo → Actions tab
- Verify Neon secrets are correct
- Check Neon database has `raw` schema

---

## 📚 Full Documentation

For more details, see:
- `NEON_SETUP.md` - Comprehensive setup guide
- `GITHUB_DEPLOYMENT.md` - GitHub Actions details
- `README.md` - Project overview

---

## 🎉 Done!

Your Internet Outage Platform now runs on **Neon cloud PostgreSQL!**

No more managing local databases. Data automatically ingests daily at 8 AM UTC. 🚀
