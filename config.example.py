# Cloudflare Radar API Configuration
# Get your API token from: https://dash.cloudflare.com/profile/api-tokens

import os

# API Keys
CLOUDFLARE_API_TOKEN = os.getenv(
    "CLOUDFLARE_API_TOKEN",
    "your_api_token_here"  # Replace with your actual token or set environment variable
)

# Database configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "database": os.getenv("DB_NAME", "internet_outages"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "postgres")
}

# API endpoints
CLOUDFLARE_BASE_URL = "https://api.cloudflare.com/client/v4/radar"

IODA_BASE_URL = "https://api.ioda.caida.org/v2"

RIPE_BASE_URL = "https://atlas.ripe.net/api/v2"

# ingestion limits
DEFAULT_LIMIT = 1000
