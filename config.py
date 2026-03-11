import os

# API Keys
CLOUDFLARE_API_TOKEN = os.getenv(
    "CLOUDFLARE_API_TOKEN",
    "aw8TKHPzRTUdVOYVZKnKLo957nKbjc1oNuYc71PY"
)

# Database configuration
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "internet_outages",
    "user": "postgres",
    "password": "postgres"
}

# API endpoints
CLOUDFLARE_BASE_URL = "https://api.cloudflare.com/client/v4/radar"

IODA_BASE_URL = "https://api.ioda.caida.org/v2"

RIPE_BASE_URL = "https://atlas.ripe.net/api/v2"

# ingestion limits
DEFAULT_LIMIT = 1000
