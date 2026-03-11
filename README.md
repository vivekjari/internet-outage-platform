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
- PostgreSQL 12+
- Git

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
   # Create .env file with:
   export CLOUDFLARE_API_TOKEN="your_token_here"
   ```

5. **Update database configuration** in `config.py`
   ```python
   DB_CONFIG = {
       "host": "your_host",
       "port": 5432,
       "database": "internet_outages",
       "user": "postgres",
       "password": "your_password"
   }
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

This project uses **GitHub Actions** to run ingestion scripts automatically every day at 8:00 AM UTC.

### Workflow Configuration

The workflow is defined in `.github/workflows/daily-ingestion.yml` and:
- Runs on schedule: `0 8 * * *` (8:00 AM UTC daily)
- Executes all three ingestion scripts in sequence
- Logs results and errors
- Can also be triggered manually via GitHub Actions UI

### Setting up GitHub Secrets

For automated execution on GitHub, you must configure the following secrets:

1. Go to your GitHub repository → Settings → Secrets and variables → Actions
2. Add the following secrets:
   - `CLOUDFLARE_API_TOKEN`: Your Cloudflare Radar API token
   - `DB_HOST`: PostgreSQL host
   - `DB_PORT`: PostgreSQL port (default: 5432)
   - `DB_USER`: PostgreSQL username
   - `DB_PASSWORD`: PostgreSQL password
   - `DB_NAME`: PostgreSQL database name (default: internet_outages)

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
