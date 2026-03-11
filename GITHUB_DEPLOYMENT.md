# GitHub Deployment Instructions

## 📋 Quick Summary

Your Internet Outage Platform is ready to deploy! The project includes:
- ✅ Complete ingestion scripts for 3 data sources
- ✅ PostgreSQL database integration
- ✅ GitHub Actions workflow for daily scheduling at 8:00 AM UTC
- ✅ Full documentation and setup guides

## 🚀 Quick Start - Deploy to GitHub

### Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Enter repository name: `internet-outage-platform`
3. Description: "Python-based data ingestion platform for monitoring internet outages from Cloudflare Radar APIs"
4. Choose visibility: **Public** (recommended) or **Private**
5. **IMPORTANT**: Do NOT check "Add .gitignore" or "Add a license" (we already have them)
6. Click **Create repository**

### Step 2: Push Code to GitHub

Run these commands in your terminal:

```bash
cd /Users/vivekjariwala/Downloads/internet-outage-platform

# Replace YOURUSERNAME with your actual GitHub username
git remote add origin https://github.com/YOURUSERNAME/internet-outage-platform.git
git branch -M main
git push -u origin main
```

**If using SSH** (faster):
```bash
git remote add origin git@github.com:YOURUSERNAME/internet-outage-platform.git
git branch -M main
git push -u origin main
```

### Step 3: Configure GitHub Secrets

These secrets are required for the automated workflow to access your database:

1. Go to your GitHub repository
2. Navigate to: **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret** for each item below:

#### Required Secrets:

**CLOUDFLARE_API_TOKEN**
- Get from: https://dash.cloudflare.com/profile/api-tokens
- Click "Create Token" → "Radar API" template (or create custom with radar:read permission)
- Paste the token value

**DB_HOST**
- Your PostgreSQL server hostname
- Examples: `localhost`, `db.example.com`, RDS endpoint, Cloud SQL IP
- Default for local: `localhost`

**DB_PORT**
- PostgreSQL port number
- Default: `5432`

**DB_USER**
- PostgreSQL username
- Default: `postgres`

**DB_PASSWORD**
- PostgreSQL password (use strong password for production)

**DB_NAME**
- Database name on your PostgreSQL server
- Default: `internet_outages`

### Step 4: Verify Workflow

1. Go to your repository **Actions** tab
2. You should see **"Daily Data Ingestion"** workflow
3. Click it to see the workflow definition
4. Optionally test by clicking **"Run workflow"** → **"Run workflow"**

## 📅 Schedule Details

The workflow runs **every day at 8:00 AM UTC**.

**To adjust the time**, edit `.github/workflows/daily-ingestion.yml`:
```yaml
on:
  schedule:
    - cron: '0 8 * * *'  # minute hour day month weekday
```

**Convert UTC to your timezone:**
- For EST (UTC-5): Change `0 8` to `0 13`
- For PST (UTC-8): Change `0 8` to `0 16`
- For IST (UTC+5:30): Change `0 8` to `30 2` (2:30 AM IST = 8:00 AM UTC)
- For CST (UTC+8): Change `0 8` to `0 0`

## 🗄️ Database Setup

### Option 1: Local PostgreSQL
```bash
# Create database and schema
psql -U postgres -c "CREATE DATABASE internet_outages;"
psql -d internet_outages -c "CREATE SCHEMA raw;"

# Configure secrets with:
# DB_HOST: localhost
# DB_PORT: 5432
# DB_USER: postgres
# DB_PASSWORD: (your password)
# DB_NAME: internet_outages
```

### Option 2: AWS RDS PostgreSQL
```bash
# Create RDS instance with PostgreSQL
# Then create database:
psql -h your-rds-endpoint.amazonaws.com -U postgres -c "CREATE DATABASE internet_outages;"
psql -h your-rds-endpoint.amazonaws.com -d internet_outages -c "CREATE SCHEMA raw;"

# Configure secrets with RDS endpoint and credentials
```

### Option 3: Google Cloud SQL PostgreSQL
Similar to RDS - create instance, database, schema, then configure secrets

## ✅ Verification

### Test Locally First (Recommended)

Before scheduling:
```bash
# Activate virtual environment
source .venv/bin/activate

# Set environment variables
export CLOUDFLARE_API_TOKEN="your_token"
export DB_HOST="localhost"
export DB_USER="postgres"
export DB_PASSWORD="your_password"
export DB_NAME="internet_outages"

# Run ingestion scripts
python ingest_cloudflare.py
python ingest_ai_bots.py
python ingest_device_type.py
```

### Test GitHub Actions

1. Go to **Actions** → **Daily Data Ingestion**
2. Click **Run workflow** → **Run workflow**
3. Click the running job to see live logs
4. Wait for completion and check for any errors

### Verify Data Ingestion

After running:
```bash
# Connect to your database
psql -d internet_outages

# Check data
SELECT COUNT(*) FROM raw.cloudflare_outages;
SELECT COUNT(*) FROM raw.cloudflare_ai_bots;
SELECT COUNT(*) FROM raw.cloudflare_device_type;
```

## 🔄 Automatic Scheduling

Once GitHub secrets are configured:
- ✅ Workflow runs automatically at 8:00 AM UTC every day
- ✅ Data is automatically ingested into PostgreSQL
- ✅ Deduplication prevents duplicate records
- ✅ You can manually trigger anytime from Actions tab

## 📊 What Gets Ingested Daily

**Cloudflare Outages** (`ingest_cloudflare.py`)
- Internet outage metrics by location
- 10 locations: US, DE, IN, ID, BR, CN, VN, other
- 24 hourly data points

**AI Bots** (`ingest_ai_bots.py`)
- AI bot traffic by industry  
- 10 industries tracked
- 24 hourly data points

**Device Type** (`ingest_device_type.py`)
- HTTP traffic by device type (desktop, mobile, other)
- 3 device types
- Hourly metrics for past 30 days

## 🐛 Troubleshooting

### Workflow doesn't start
- ✅ Check Actions are enabled (repository Settings → Actions general)
- ✅ Wait up to 5 minutes after first push (GitHub can be slow to detect)
- ✅ Try manual trigger: Actions → "Run workflow" button

### "Database connection failed" error
- ✅ Verify all DB secrets are correct
- ✅ Check database is accessible (firewall rules, security groups, etc.)
- ✅ Make sure `raw` schema exists
- ✅ Test locally first

### "Invalid API token" error
- ✅ Verify Cloudflare API token is valid and not expired
- ✅ Check token has required `radar:read` permission
- ✅ Regenerate token if needed

### Workflow runs but no data appears
- ✅ Check workflow logs for errors
- ✅ Verify deduplication isn't silently skipping inserts
- ✅ Check with: `SELECT * FROM raw.cloudflare_outages LIMIT 1;`

## 📈 Next Steps

1. ✅ Deploy to GitHub (today)
2. ✅ Configure database and secrets
3. ✅ Test workflow manually
4. ✅ Monitor first automated run at 8 AM
5. 📊 Set up dashboards/analytics on accumulated data

## 📚 Additional Resources

- [Cloudflare Radar API Docs](https://developers.cloudflare.com/api/operations/radar-get-http-timeseries-groups)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- See `DEPLOYMENT.md` for more detailed deployment guide

## 🎯 Project Location

Local path: `/Users/vivekjariwala/Downloads/internet-outage-platform`
GitHub URL: `https://github.com/YOURUSERNAME/internet-outage-platform`

---

**Ready to deploy? Start with Step 1 above!** 🚀
