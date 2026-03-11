# Internet Outage Platform

A comprehensive Python-based data ingestion platform that automatically collects and analyzes internet outages and network metrics from Cloudflare Radar APIs. Data is ingested daily into a cloud-hosted Neon PostgreSQL database via GitHub Actions automation.

---

## Table of Contents

- [What This Project Does](#what-this-project-does)
- [How It Works](#how-it-works)
- [Data Structure](#data-structure)
- [Quick Start (5 Minutes)](#quick-start-5-minutes)
- [Detailed Setup](#detailed-setup)
- [GitHub Actions Automation](#github-actions-automation)
- [Monitoring & Verification](#monitoring--verification)
- [Architecture](#architecture)
- [Troubleshooting](#troubleshooting)

---

## What This Project Does

This platform **automatically collects internet outage and network metrics** from Cloudflare's global network every day and stores them in your cloud PostgreSQL database. It tracks three critical data sources:

1. **Internet Outages by Location** - Outage metrics from 10 global locations
2. **AI Bot Threats by Industry** - AI bot activity tracked across 10 industries  
3. **HTTP Traffic by Device Type** - Device-based HTTP metrics (desktop, mobile, other)

**Key Features:**
- ✅ Fully automated daily ingestion at 8 AM UTC
- ✅ Cloud-hosted (Neon serverless PostgreSQL) - no local database needed
- ✅ Automatic deduplication - no duplicate records even on re-runs
- ✅ GitHub Actions powered - runs in the cloud, no local machine required
- ✅ 30 days of historical data - fetches 30 days of metrics on each run
- ✅ Zero setup friction - 5-minute deployment with GitHub Actions

---

## How It Works

### Data Flow Pipeline

```
Cloudflare Radar API
    ↓
[ingest_cloudflare.py] → Outage data
[ingest_ai_bots.py] → AI bot threats
[ingest_device_type.py] → Device metrics
    ↓
[database.py - Deduplication Layer]
    ↓
Neon Cloud PostgreSQL (raw.cloudflare_*)
    ↓
Available for analytics, dashboards, alerting
```

### The Ingestion Process

Each ingestion script follows the same pattern:

1. **Fetch** - Calls Cloudflare Radar API with 30-day date range
2. **Parse** - Converts JSON response into structured rows
3. **Deduplicate** - ON CONFLICT clauses prevent duplicate records
4. **Store** - Batch inserts into PostgreSQL via Neon connection

### Three Data Sources

| Source | Endpoint | Records/Day | Dimensions |
|--------|----------|-------------|-----------|
| **Outages** | `/radar/netflows/timeseries_groups/location` | ~240 | 10 locations × 24 hours |
| **AI Bots** | `/radar/ai/bots/timeseries_groups/INDUSTRY` | ~240 | 10 industries × 24 hourly |
| **Device Type** | `/radar/http/timeseries_groups/DEVICE_TYPE` | ~720 | 3 device types × 240 hours |

---

## Data Structure

### raw.cloudflare_outages
Stores internet outage metrics segmented by global location.

```sql
Columns:
  id (serial primary key)
  location (varchar) - Geographic location
  timestamp (timestamptz) - Time of measurement
  metric (varchar) - Metric type (e.g., "outages")
  value (float) - Numeric value
  normalized_metric (varchar) - Generated/normalized metric name

Example record:
  location='United States', timestamp='2026-03-11 15:00:00 UTC'
  metric='outages', value=42.5, normalized_metric='outages'

Unique constraint: (location, timestamp, normalized_metric)
Records: ~7,200+ (30 days × 10 locations × 24 hours)
```

### raw.cloudflare_ai_bots
Tracks AI bot activity and threats segmented by industry vertical.

```sql
Columns:
  id (serial primary key)
  industry (varchar) - Industry category
  timestamp (timestamptz) - Time of measurement
  metric (varchar) - Metric type
  value (float) - Numeric value
  normalized_metric (varchar) - Generated/normalized metric name

Industries tracked: Retail, Internet, Telecommunications, Media, 
Financial Services, Chemicals, Automotive, Construction, Healthcare, 
Electronics

Unique constraint: (industry, timestamp, normalized_metric)
Records: ~7,930+ (30 days × 10 industries × 24-30 records)
```

### raw.cloudflare_device_type
HTTP traffic metrics segmented by client device type.

```sql
Columns:
  id (serial primary key)
  device_type (varchar) - Device category (Desktop, Mobile, Other)
  timestamp (timestamptz) - Time of measurement
  metric (varchar) - Metric type
  value (float) - Numeric value
  normalized_metric (varchar) - Generated/normalized metric name

Device types: Desktop, Mobile, Other

Unique constraint: (device_type, timestamp, normalized_metric)
Records: ~2,382+ (30 days × 3 device types × 30+ records)
```

---

## Quick Start (5 Minutes)

### Prerequisites
- Python 3.9+ (local testing only, not needed for automation)
- Neon account (free at https://neon.tech)
- Cloudflare API token
- GitHub repository

### Step 1: Create Neon Database (2 minutes)

1. Go to https://neon.tech and sign up (free tier)
2. Create a new project named "internet-outage-platform"
3. Click "Connection string" → Select "Pooled connection" → Python
4. Copy the connection string

Example:
```
postgresql://neondb_owner:AbCdEf1234@ep-cool-lake-9a8b7c.us-east-1.neon.tech/neondb?sslmode=require
```

### Step 2: Extract Credentials (1 minute)

From your connection string extract:
- `DB_HOST`: `ep-cool-lake-9a8b7c.us-east-1.neon.tech`
- `DB_PORT`: `5432`
- `DB_USER`: `neondb_owner`
- `DB_PASSWORD`: (the password part)
- `DB_NAME`: `neondb`

### Step 3: Configure GitHub Secrets (1 minute)

Go to your GitHub repository → **Settings** → **Secrets and variables** → **Actions**

Add these 6 repository secrets:

| Secret Name | Value |
|---|---|
| `DB_HOST` | Your Neon host from Step 2 |
| `DB_PORT` | `5432` |
| `DB_USER` | Your Neon user from Step 2 |
| `DB_PASSWORD` | Your Neon password from Step 2 |
| `DB_NAME` | `neondb` (or your database name) |
| `CLOUDFLARE_API_TOKEN` | Your Cloudflare API token |

### Step 4: Done! 🎉

GitHub Actions automatically starts the daily ingestion workflow. Your first run will happen at **8:00 AM UTC tomorrow**, and every day thereafter.

---

## Detailed Setup

### Option A: Automated Deployment (Recommended)

If you've already completed Quick Start above, you're done! Just wait for the 8 AM UTC run tomorrow.

### Option B: Local Testing (Before Automation)

Want to test locally before relying on automation?

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/internet-outage-platform.git
cd internet-outage-platform

# 2. Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set environment variables (use credentials from Quick Start Step 2)
export CLOUDFLARE_API_TOKEN="your_cloudflare_token_here"
export DB_HOST="ep-cool-lake-9a8b7c.us-east-1.neon.tech"
export DB_PORT="5432"
export DB_USER="neondb_owner"
export DB_PASSWORD="your_password_here"
export DB_NAME="neondb"

# 5. Test ingestion (one at a time)
python ingest_cloudflare.py       # Fetch outage data
python ingest_ai_bots.py          # Fetch AI bot threats
python ingest_device_type.py      # Fetch device metrics

# 6. Verify data ingested successfully
python verify_cloudflare.py       # Shows how many records stored
python verify_ai_bots.py
python verify_device_type.py
```

---

## GitHub Actions Automation

### How It Works

The GitHub Actions workflow (`.github/workflows/daily-ingestion.yml`) automatically:

1. Runs every day at **8:00 AM UTC**
2. Checks out your code from the repository
3. Sets up Python environment
4. Installs dependencies
5. Runs all three ingestion scripts in sequence
6. Each script connects to your Neon database using GitHub Secrets
7. Ingests 30 days of data, with automatic deduplication
8. Complete in ~30 seconds

### Changing the Schedule

To run at a different time, edit `.github/workflows/daily-ingestion.yml`:

```yaml
schedule:
  - cron: '0 8 * * *'  # Format: minute hour day month weekday
```

**Common times:**
- `'0 8 * * *'` = 8:00 AM UTC
- `'0 13 * * *'` = 1:00 PM UTC (8 AM EST)
- `'0 16 * * *'` = 4:00 PM UTC (8 AM PST)
- `'30 2 * * *'` = 2:30 AM UTC (8 AM IST)
- `'0 0 * * *'` = 12:00 AM UTC (8 AM CST)

Then commit and push the change:
```bash
git add .github/workflows/daily-ingestion.yml
git commit -m "Change ingestion schedule"
git push origin main
```

### Manual Workflow Trigger

Need to run ingestion outside of the scheduled time?

1. Go to your GitHub repository
2. Click **Actions** tab
3. Click **"Daily Data Ingestion"** workflow name
4. Click **"Run workflow"** button
5. Select branch and click **"Run workflow"**

The workflow will start immediately.

---

## Monitoring & Verification

### Check GitHub Actions Logs

1. Go to **Actions** tab in your GitHub repository
2. Click **"Daily Data Ingestion"** workflow
3. Click on any run to see detailed logs
4. Each step shows ingestion results: "Ingested 240 records", "Ingested 245 records", etc.

### Query Neon Database Directly

```bash
# Using psql
psql "postgresql://neondb_owner:password@ep-cool-lake.us-east-1.neon.tech/neondb"

# Check record counts
SELECT COUNT(*) FROM raw.cloudflare_outages;    -- Should show 7000+
SELECT COUNT(*) FROM raw.cloudflare_ai_bots;    -- Should show 7900+
SELECT COUNT(*) FROM raw.cloudflare_device_type; -- Should show 2300+

# View recent data
SELECT * FROM raw.cloudflare_outages LIMIT 5;
SELECT DISTINCT location FROM raw.cloudflare_outages;
SELECT DISTINCT industry FROM raw.cloudflare_ai_bots;
```

### Via Neon Dashboard

1. Log in to https://neon.tech
2. Open your project
3. Click **SQL Editor**
4. Write and execute queries directly in the browser

---

## Architecture

### Project Structure

```
internet-outage-platform/
├── .github/
│   └── workflows/
│       └── daily-ingestion.yml          # GitHub Actions - runs daily at 8 AM UTC
│
├── ingest_cloudflare.py                 # Fetches outage data by location
├── ingest_ai_bots.py                    # Fetches AI threat data by industry
├── ingest_device_type.py                # Fetches HTTP metrics by device type
│
├── database.py                          # PostgreSQL/Neon operations
│                                        # - Connection management
│                                        # - Batch inserts with deduplication
│                                        # - Automatic index creation
│
├── api_client.py                        # HTTP client for Cloudflare API
│                                        # - Bearer token authentication
│                                        # - Request handling
│
├── config.py                            # Configuration management
│                                        # - Environment variables
│                                        # - API endpoints
│
├── requirements.txt                     # Python dependencies
│                                        # - requests (HTTP)
│                                        # - pg8000 (PostgreSQL driver)
│
├── verify_cloudflare.py                 # Verification script for outages table
├── verify_ai_bots.py                    # Verification script for AI bots table
├── verify_device_type.py                # Verification script for device types table
│
└── README.md                            # This file
```

### Code Pattern

All three ingestion scripts follow an identical pattern:

```python
class XyzIngestor:
    """Ingests XYZ data from Cloudflare API to Neon database"""
    
    def __init__(self):
        self.client = APIClient()           # HTTP client
        self.db = PostgresDB()              # Database connection
    
    def fetch_data(self):
        """Calls Cloudflare API with 30-day date range"""
        response = self.client.get(url, params=params)
        return response.json()
    
    def parse_records(self, data):
        """Converts JSON response to list of database rows"""
        rows = []
        for entry in data['result']['timeseries']:
            rows.append([
                timestamp, dimension_value, metric, numeric_value
            ])
        return rows
    
    def save_to_db(self, rows):
        """Batch insert with ON CONFLICT deduplication"""
        self.db.insert_batch(table_name, columns, rows)
    
    def run(self):
        """Main entry point: fetch → parse → save"""
        data = self.fetch_data()
        rows = self.parse_records(data)
        self.save_to_db(rows)
```

### Database Deduplication Strategy

To prevent duplicate records when the same data is ingested multiple times:

1. Each table has a **unique constraint** on key dimensions:
   - `raw.cloudflare_outages`: (location, timestamp, normalized_metric)
   - `raw.cloudflare_ai_bots`: (industry, timestamp, normalized_metric)
   - `raw.cloudflare_device_type`: (device_type, timestamp, normalized_metric)

2. On insert conflict, the database **updates** the existing record with the new value (using `ON CONFLICT ... DO UPDATE`)

3. Result: Re-running the same ingestion never creates duplicates

---

## Troubleshooting

### "GitHub Actions workflow didn't run"

**Check 1:** Is Actions enabled?
- Go to your repo → **Settings** → **Actions** → General
- Ensure "Actions permissions" is set to "Allow all actions"

**Check 2:** Did you push to main branch?
- Workflow only triggers on main branch changes
- Verify: `git push origin main`

**Check 3:** Wait 5 minutes
- GitHub can be slow to detect new workflows
- Check after pushing

**Manual trigger:** Actions tab → "Daily Data Ingestion" → "Run workflow"

---

### "Database connection failed" in workflow logs

**Check 1:** Verify all 6 secrets are set
- Go to **Settings** → **Secrets and variables** → **Actions**
- Confirm you have: DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME, CLOUDFLARE_API_TOKEN

**Check 2:** Secrets are correct
- `DB_HOST` should NOT include "postgresql://" prefix
- `DB_PORT` should be just the number: `5432`
- `DB_USER` should be the user, usually `neondb_owner`
- `DB_PASSWORD` must match Neon password exactly (no quotes)

**Check 3:** Check Neon project status
- Log in to https://neon.tech
- Ensure your project "internet-outage-platform" is active (not paused)
- Paused projects are resumed automatically on connection, but may take a few seconds

**Check 4:** Test locally first
- Follow "Detailed Setup → Option B" to test local ingestion
- This helps isolate whether the problem is credentials or network

---

### "Ingestion ran but no data appears"

**Check 1:** Verify ingestion actually completed
- Look at GitHub Actions logs
- Each script should show "Ingested 240 records" or similar

**Check 2:** Verify `raw` schema exists
- In Neon SQL Editor:
```sql
SELECT schema_name FROM information_schema.schemata 
WHERE schema_name = 'raw';
```

**Check 3:** Check for errors in script output
- GitHub Actions logs show full stack traces if something fails
- Look for "Error:", "Exception:", or "Traceback"

**Check 4:** Verify tables exist
- In Neon SQL Editor:
```sql
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'raw';
```

---

### "Invalid Cloudflare API token" error

1. Go to https://dash.cloudflare.com → **API Tokens**
2. Create or verify an existing token has `radar:read` permission
3. Copy the token carefully (no extra spaces)
4. Update GitHub Secret: **Settings** → **Secrets and variables** → **CLOUDFLARE_API_TOKEN**
5. Paste the exact token with no extra whitespace

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Commit: `git commit -m "Add feature"`
5. Push: `git push origin feature-name`
6. Open a pull request

## License

MIT

## Support

For issues, questions, or suggestions:
1. Check the Troubleshooting section above
2. Review GitHub Actions logs for error messages
3. Open a GitHub issue with:
   - What you tried
   - What error you got
   - GitHub Actions log output (if applicable)
