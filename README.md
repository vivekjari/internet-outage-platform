# Internet Outage Platform

A Python-based data ingestion platform for monitoring internet outages and network metrics from Cloudflare Radar APIs.

## Features

- **Real-time data ingestion** from Cloudflare Radar APIs
- **Multiple data sources**:
  - Outage data by location
  - AI bots threat data by industry
  - HTTP traffic data by device type
- **Automated scheduling** with GitHub Actions
- **PostgreSQL database** for persistent storage
- **Automatic deduplication** of ingested data

## Data Tables

### raw.cloudflare_outages
- Location-based internet outage metrics
- Columns: id, location, timestamp, metric, value, normalized_metric
- Updated daily with 30 days of historical data

### raw.cloudflare_ai_bots
- AI bots activity grouped by industry
- Columns: id, timestamp, industry, metric, value, normalized_metric
- 10 industries tracked: Retail, Internet, Telecommunications, etc.

### raw.cloudflare_device_type
- HTTP traffic metrics by device type (desktop, mobile, other)
- Columns: id, device_type, timestamp, metric, value, normalized_metric
- 30 days of hourly data

## Setup Instructions

### Prerequisites
- Python 3.9+
- Neon cloud PostgreSQL account (free at https://neon.tech)
- Cloudflare API token
- Git

### Neon Database Setup (2 minutes)

1. **Create Neon Account**
   - Go to https://neon.tech
   - Sign up (free tier available)
   - Create a new project named "internet-outage-platform"

2. **Get Connection Details**
   - On Neon dashboard, click "Connection string"
   - Select "Pooled connection" → Python
   - Copy the connection string (includes host, port, user, password, database)

3. **Extract Credentials**
   From the connection string, you'll need:
   - `DB_HOST`: Your Neon endpoint (e.g., ep-cool-lake-abc123.us-east-1.neon.tech)
   - `DB_PORT`: 5432
   - `DB_USER`: neondb_owner (or your user)
   - `DB_PASSWORD`: Your Neon password
   - `DB_NAME`: neondb (or your database name)

### Local Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/internet-outage-platform.git
   cd internet-outage-platform
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   export CLOUDFLARE_API_TOKEN="your_cloudflare_token"
   export DB_HOST="your-neon-host.neon.tech"
   export DB_PORT="5432"
   export DB_USER="neondb_owner"
   export DB_PASSWORD="your_neon_password"
   export DB_NAME="neondb"
   ```

5. **Test local connection**
   ```bash
   python ingest_cloudflare.py  # Test ingestion
   ```

6. **Run ingestion scripts**
   ```bash
   python ingest_cloudflare.py      # Ingest outage data
   python ingest_ai_bots.py         # Ingest AI bots data
   python ingest_device_type.py     # Ingest device type data
   ```

7. **Verify data** (optional)
   ```bash
   python verify_cloudflare.py
   python verify_ai_bots.py
   python verify_device_type.py
   ```

## Automated Scheduling

This project uses **GitHub Actions** to run ingestion scripts automatically every day at 8:00 AM UTC, storing data in your **Neon cloud database**.

### GitHub Actions Workflow

The workflow is defined in `.github/workflows/daily-ingestion.yml`:
- ✓ Runs automatically at 8:00 AM UTC daily
- ✓ Executes all three ingestion scripts in sequence
- ✓ Connects to your Neon database via secrets
- ✓ Can also be triggered manually via GitHub Actions UI

### Configure GitHub Secrets (Required)

For GitHub Actions to work, set these repository secrets:

1. Go to **GitHub Repository** → **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret** and add:
   - `CLOUDFLARE_API_TOKEN`: Your Cloudflare Radar API token
   - `DB_HOST`: Your Neon host (from connection string)
   - `DB_PORT`: `5432`
   - `DB_USER`: Your Neon user (e.g., `neondb_owner`)
   - `DB_PASSWORD`: Your Neon password
   - `DB_NAME`: Your database name (e.g., `neondb`)

All data will automatically sync to your **Neon PostgreSQL** database every day!

## Project Structure

```
.
├── ingest_cloudflare.py       # Outage data ingestion
├── ingest_ai_bots.py          # AI bots data ingestion
├── ingest_device_type.py      # Device type data ingestion
├── api_client.py              # HTTP client for API calls
├── database.py                # PostgreSQL connection & operations
├── config.py                  # Configuration settings
├── requirements.txt           # Python dependencies
├── verify_*.py                # Verification scripts
├── .github/
│   └── workflows/
│       └── daily-ingestion.yml # GitHub Actions workflow
└── README.md
```

## API Endpoints

- **Outages**: `https://api.cloudflare.com/client/v4/radar/netflows/timeseries_groups/location`
- **AI Bots**: `https://api.cloudflare.com/client/v4/radar/ai/bots/timeseries_groups/INDUSTRY`
- **Device Type**: `https://api.cloudflare.com/client/v4/radar/http/timeseries_groups/DEVICE_TYPE`

## Error Handling

- API failures are logged and reported but don't stop execution
- Database insert conflicts are handled with ON CONFLICT clauses
- Deduplication prevents duplicate records automatically

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT

## Support

For issues or questions, please open a GitHub issue.
