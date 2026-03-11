# GitHub Deployment Guide

## Prerequisites
- GitHub Account
- Git installed locally
- Personal Access Token or SSH key configured with GitHub

## Step-by-Step Deployment

### 1. Create a GitHub Repository

1. Go to [github.com](https://github.com) and sign in
2. Click the "+" icon and select "New repository"
3. Name it: `internet-outage-platform`
4. Add description: "Python-based data ingestion platform for monitoring internet outages from Cloudflare Radar APIs"
5. Choose visibility: Public or Private
6. **Do NOT** initialize with README, .gitignore, or license (we already have them)
7. Click "Create repository"

### 2. Connect Local Repository to GitHub

After creating the repository on GitHub, you'll see instructions. Run these commands in your terminal:

```bash
cd /Users/vivekjariwala/Downloads/internet-outage-platform

# Add the remote origin (replace USERNAME with your GitHub username)
git remote add origin https://github.com/USERNAME/internet-outage-platform.git

# Rename branch to main if needed
git branch -M main

# Push to GitHub
git push -u origin main
```

**For SSH** (if you have SSH key configured):
```bash
git remote add origin git@github.com:USERNAME/internet-outage-platform.git
git branch -M main
git push -u origin main
```

### 3. Configure GitHub Secrets for Automated Scheduling

The GitHub Actions workflow requires database credentials to run:

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret** and add these secrets:

| Secret Name | Value | Example |
|:---|:---|:---|
| `CLOUDFLARE_API_TOKEN` | Your Cloudflare API token | `aw8TKHPzRTUdVOYVZKnKLo957nKbjc1oNuYc71PY` |
| `DB_HOST` | PostgreSQL server hostname | `db.example.com` or `localhost` |
| `DB_PORT` | PostgreSQL port | `5432` |
| `DB_USER` | PostgreSQL username | `postgres` |
| `DB_PASSWORD` | PostgreSQL password | `your_secure_password` |
| `DB_NAME` | Database name | `internet_outages` |

### 4. Enable GitHub Actions

1. Go to your repository
2. Click **Actions** tab
3. You should see "Daily Data Ingestion" workflow
4. Click "Enable workflow" if needed

### 5. Verify Workflow Setup

1. Go to **Actions** → **Daily Data Ingestion**
2. You can manually trigger it with "Run workflow" button
3. The workflow will run automatically every day at **8:00 AM UTC**

## Workflow Schedule

The workflow runs on this schedule:
- **Time**: 8:00 AM UTC every day
- **What it does**: 
  - Runs `ingest_cloudflare.py`
  - Runs `ingest_ai_bots.py`
  - Runs `ingest_device_type.py`
  - Verifies all data

To change the schedule time, edit `.github/workflows/daily-ingestion.yml`:
```yaml
on:
  schedule:
    # Change the cron time (format: minute hour day month weekday)
    - cron: '0 8 * * *'  # Current: 8:00 AM UTC
```

**Common cron examples:**
- `0 0 * * *` = Midnight UTC
- `0 12 * * *` = Noon UTC
- `0 14 * * *` = 2:00 PM UTC
- `0 20 * * *` = 8:00 PM UTC

## Database Setup on Cloud

### For AWS RDS PostgreSQL
1. Create RDS PostgreSQL instance
2. Create database: `internet_outages`
3. Create schema: `raw`
4. Set `DB_HOST` to your RDS endpoint
5. Set `DB_USER` and `DB_PASSWORD` as configured

### For Google Cloud SQL PostgreSQL
Similar steps - get the public IP and credentials, configure secrets same way

## Monitoring & Logs

1. Go to **Actions** tab in GitHub
2. Click **Daily Data Ingestion**
3. Click the latest run to see logs
4. Each ingestion step shows detailed output
5. Failed steps are clearly marked

## Making Code Changes

After making changes locally:

```bash
# Make your changes
git add .
git commit -m "Description of changes"
git push origin main
```

The workflow will automatically use the latest code.

## Troubleshooting

### Workflow won't run
- Check if Actions are enabled in repository Settings
- Verify secrets are correctly configured
- Check that `.github/workflows/daily-ingestion.yml` exists

### Database connection errors
- Verify all secrets are correct
- Check database is accessible from GitHub Actions (may need firewall rules)
- Ensure `raw` schema exists in database

### API errors
- Verify Cloudflare API token is valid and not expired
- Check API token has proper permissions
- Monitor Cloudflare API status page

## Next Steps

1. Configure your cloud database (RDS, Cloud SQL, etc.)
2. Add secrets to GitHub repository
3. Manually trigger workflow to test
4. Monitor first automated run
5. Adjust cron schedule if needed

## Support

For issues, check:
- GitHub Actions logs
- Database logs
- API status pages
