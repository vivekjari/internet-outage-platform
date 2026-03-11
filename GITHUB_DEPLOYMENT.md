# GitHub Actions & Neon Setup

## 📋 What You Need

This project automatically ingests data to **Neon cloud PostgreSQL** via GitHub Actions:
- ✅ Daily automatic ingestion at 8:00 AM UTC
- ✅ 3 Cloudflare APIs ingested (outages, AI bots, device type)
- ✅ Cloud-hosted database (no local setup needed)
- ✅ GitHub Actions handles all automation

## 🚀 Setup (5 Minutes)

### Step 1: Create Neon Account

1. Go to https://neon.tech
2. Click "Sign Up"
3. Choose auth method (email or GitHub)
4. Create free project named "internet-outage-platform"
5. Select region closest to you

### Step 2: Get Neon Credentials

On Neon dashboard:
1. Click "Connection string"
2. Select "Pooled connection" → Python
3. Copy the full connection string

**Example:**
```
postgresql://neondb_owner:AbCdEfGhIjKlMnOp@ep-cool-lake-a1b2c3d4.us-east-1.neon.tech/neondb?sslmode=require
```

From this string, extract:
- **DB_HOST**: ep-cool-lake-a1b2c3d4.us-east-1.neon.tech
- **DB_PORT**: 5432
- **DB_USER**: neondb_owner
- **DB_PASSWORD**: AbCdEfGhIjKlMnOp
- **DB_NAME**: neondb

### Step 3: Configure GitHub Secrets

1. Go to your GitHub repository
2. **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret** and add these 6 secrets:

| Secret | Value |
|:---|:---|
| `CLOUDFLARE_API_TOKEN` | From https://dash.cloudflare.com/profile/api-tokens |
| `DB_HOST` | From Neon connection string |
| `DB_PORT` | 5432 |
| `DB_USER` | From Neon connection string |
| `DB_PASSWORD` | From Neon connection string |
| `DB_NAME` | From Neon connection string |

### Step 4: Done!

GitHub Actions will automatically:
- ✓ Run at 8:00 AM UTC every day
- ✓ Ingest data from Cloudflare Radar APIs
- ✓ Store in your Neon database
- ✓ Verify data integrity
- ✓ Log all results

## 📊 Verify Workflow

1. Go to your repository **Actions** tab
2. Click **"Daily Data Ingestion"** workflow
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

## 🗄️ Neon Database

Your Neon serverless PostgreSQL database is already created with the required `raw` schema and tables during initial setup. No additional database configuration is needed—your Neon connection string handles everything.

## ✅ Verification

### Test GitHub Actions

1. Go to **Actions** → **Daily Data Ingestion**
2. Click **Run workflow** → **Run workflow**
3. Click the running job to see live logs
4. Wait for completion and check for any errors

### Verify Data in Neon

After the workflow runs, connect to your Neon database and verify data was ingested:

```bash
# Using psql with Neon connection string
psql "postgresql://user:password@ep-xxxx.us-west-2.aws.neon.tech/neondb"

# Check data ingestion
SELECT COUNT(*) FROM raw.cloudflare_outages;
SELECT COUNT(*) FROM raw.cloudflare_ai_bots;
SELECT COUNT(*) FROM raw.cloudflare_device_type;
```

Or check via **Neon Dashboard**:
1. Log in to [neon.tech](https://neon.tech)
2. Open your project → SQL Editor
3. Run: `SELECT COUNT(*) FROM raw.cloudflare_outages;`

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
- ✅ Verify all 6 Neon secrets are configured correctly in GitHub repo
- ✅ Check that your Neon project is **active** (sometimes paused after inactivity)
- ✅ Confirm `raw` schema exists in Neon database (check via Neon Dashboard → SQL Editor)
- ✅ Test Neon connection locally: `psql "postgresql://user:password@ep-xxxx.us-west-2.aws.neon.tech/neondb"`

### "Invalid API token" error
- ✅ Verify Cloudflare API token is valid and not expired
- ✅ Check token has required `radar:read` permission
- ✅ Regenerate token from Cloudflare Dashboard if needed

### Workflow runs but no data appears
- ✅ Check workflow logs for errors (Actions tab → workflow run)
- ✅ Verify deduplication isn't silently skipping inserts: `SELECT * FROM raw.cloudflare_outages LIMIT 1;`
- ✅ Check Neon project status (re-activate if paused)
- ✅ Ensure Neon project connection string uses correct `neondb` database name

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
