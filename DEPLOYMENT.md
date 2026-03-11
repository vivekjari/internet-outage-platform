# GitHub Deployment Guide

## Overview

This project is designed to run on **Neon cloud PostgreSQL** with automated daily ingestion via **GitHub Actions**.

No local database setup required!

## Quick Start (5 Minutes)

### 1. Create Neon Account
- Go to https://neon.tech
- Sign up (free account)
- Create project named "internet-outage-platform"

### 2. Get Connection String
- On Neon dashboard, click "Connection string"
- Select "Pooled connection" → Python
- Copy the string

### 3. Extract Credentials
From connection string, extract:
- `DB_HOST`: Your Neon endpoint
- `DB_PORT`: 5432
- `DB_USER`: neondb_owner (or your user)
- `DB_PASSWORD`: Your password
- `DB_NAME`: neondb (or your database)

### 4. Configure GitHub Secrets
**Your GitHub Repository** → **Settings** → **Secrets and variables** → **Actions**

Add these 6 secrets:
| Secret | Value |
|:---|:---|
| `DB_HOST` | Your Neon host |
| `DB_PORT` | 5432 |
| `DB_USER` | Your Neon user |
| `DB_PASSWORD` | Your Neon password |
| `DB_NAME` | Your database name |
| `CLOUDFLARE_API_TOKEN` | Your Cloudflare API token |

### 5. Done!
GitHub Actions will automatically ingest data to Neon daily at 8:00 AM UTC.

---

## Workflow Details

The GitHub Actions workflow (`.github/workflows/daily-ingestion.yml`):
- ✓ Runs automatically every day at **8:00 AM UTC**
- ✓ Ingests data from 3 Cloudflare Radar API endpoints
- ✓ Stores in your **Neon PostgreSQL** database
- ✓ Can be manually triggered anytime via Actions tab

### Change Schedule Time

Edit `.github/workflows/daily-ingestion.yml`, line 4:
```yaml
- cron: '0 8 * * *'  # Format: minute hour day month weekday
```

Common times:
- `0 8 * * *` = 8:00 AM UTC
- `0 13 * * *` = 1:00 PM UTC  (EST: 8 AM)
- `0 16 * * *` = 4:00 PM UTC  (PST: 8 am)
- `30 2 * * *` = 2:30 AM UTC  (IST: 8 am)

---

## What Gets Ingested

### Data Updated Daily (at 8 AM UTC)

**Cloudflare Outages**
- Internet outage metrics by location
- 10 locations, 30 days of data
- ~240 records per day

**AI Bots Threats**
- AI bot traffic by industry
- 10 industries, 30 days of data
- ~240 records per day

**Device Type Metrics**
- HTTP traffic by device (desktop, mobile, other)
- 3 device types, 30 days of data
- ~720 records per day

**Total**: ~1,200 new records added daily

---

## Monitoring

### GitHub Actions Logs
1. Your repository → **Actions** tab
2. Click **"Daily Data Ingestion"**
3. Click latest run for detailed logs
4. Each step shows ingestion results

### Neon Dashboard
1. Log in to https://neon.tech
2. Click your project
3. **Monitoring** tab shows:
   - CPU usage
   - Connections
   - Data transferred

### Query Data
```bash
# Set environment variables
export PGHOST="your-neon-host"
export PGUSER="your-user"
export PGPASSWORD="your-password"
export PGDATABASE="neondb"

# Query your data
psql -c "SELECT COUNT(*) FROM raw.cloudflare_outages;"
```

---

## Troubleshooting

### "Connection Refused" in GitHub Actions
- Verify all 6 secrets are correct
- Check Neon database is running
- Test credentials locally first

### "No data appearing"
- Check GitHub Actions log for errors
- Verify secrets match Neon credentials
- Ensure `raw` schema exists in database

### "SSL/TLS error"
- Neon requires SSL (already configured)
- Connection string includes `?sslmode=require`
- No action needed, this is expected

### GitHub Actions not running
- Wait 5 minutes after first push
- Check Actions are enabled in repository Settings
- Manually trigger: Actions tab → "Run workflow"

---

## Managing the Database

### Rotate Password
If you need to change your Neon password:

1. In Neon: Project → Roles → Edit user → Change password
2. Update GitHub secrets with new password
3. Workflow will use new credentials on next run

### Backup Data
Neon automatically manages backups. To manually export:
```bash
pg_dump -h your-host.neon.tech \
        -U your-user \
        -d your-database > backup.sql
```

### Query Data Directly
Neon provides a web SQL editor in the dashboard for quick queries.

---

## Neon Pricing

**Free Tier (Perfect for this project)**
- ✓ Unlimited databases
- ✓ 50 GB data transfer/month
- ✓ No setup fees
- ✓ Your usage: ~1,200 records/day = $0/month

Upgrade only if you exceed transfer limits.

---

## Security

✅ **DO:**
- Store credentials in GitHub Secrets (never in code)
- Use strong passwords
- Rotate passwords every 3 months
- Monitor GitHub Actions logs

❌ **DON'T:**
- Commit passwords to GitHub
- Share connection strings
- Hardcode credentials in Python
- Use weak passwords

---

## Disabling Automation

To stop automatic ingestion:

1. Go to `.github/workflows/daily-ingestion.yml`
2. Comment out the schedule section:
```yaml
on:
  # schedule:
  #   - cron: '0 8 * * *'
  workflow_dispatch:
```

Can still manually trigger from Actions tab.

---

## Support

For issues:
- Check GitHub Actions logs first
- Verify Neon credentials
- Test locally with `python ingest_cloudflare.py`
- See `NEON_QUICK_START.md` for setup help

---

## Next Steps

1. ✅ Create Neon account (2 min)
2. ✅ Get connection credentials (1 min)
3. ✅ Add GitHub secrets (2 min)
4. ✅ Done! Automation is active

**Your platform is now live with automatic daily data ingestion!** 🚀
