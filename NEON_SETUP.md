# Neon Cloud Database Configuration

## ✅ Step 1: Create Neon Account

1. Go to https://neon.tech
2. Click **Sign Up** (top right)
3. Choose authentication method:
   - Email & password, OR
   - GitHub account (recommended for easier access)
4. Verify your email
5. Create organization (optional, use default)

## ✅ Step 2: Create PostgreSQL Database on Neon

1. After signing in, click **Create a new project**
2. Fill in project details:
   - **Project name**: `internet-outage-platform`
   - **Postgres version**: 16 (or latest available)
   - **Region**: Choose closest to your server (e.g., `us-east-1`)
3. Click **Create project**

### What Neon Creates:
- ✓ PostgreSQL database instance
- ✓ Default database: `neondb`
- ✓ Default user: `neondb_owner`
- ✓ Connection pooler enabled (for serverless)

## ✅ Step 3: Get Connection String

1. On Neon dashboard, you'll see your project
2. Click **Connection string** (top right area)
3. Choose connection type: **Pooled connection** (recommended for apps)
4. Language/framework: Select **Python**
5. You'll see the connection string:

```
postgresql://neondb_owner:AbCdEfGhIjKlMnOp@ep-cool-lake-a1b2c3d4.us-east-1.neon.tech/neondb?sslmode=require
```

**Components:**
- `neondb_owner` = username
- `AbCdEfGhIjKlMnOp` = password
- `ep-cool-lake-a1b2c3d4.us-east-1.neon.tech` = host
- `5432` = port (standard PostgreSQL)
- `neondb` = database name

## ✅ Step 4: Export Connection Details

From the connection string above, extract:

```
DB_HOST: ep-cool-lake-a1b2c3d4.us-east-1.neon.tech
DB_PORT: 5432
DB_USER: neondb_owner
DB_PASSWORD: AbCdEfGhIjKlMnOp
DB_NAME: neondb
```

## ✅ Step 5: Update Local Configuration (Optional Testing)

Edit `config.py` to test locally:

```python
import os

CLOUDFLARE_API_TOKEN = os.getenv(
    "CLOUDFLARE_API_TOKEN",
    "your_api_token_here"
)

# Change to Neon credentials
DB_CONFIG = {
    "host": "ep-cool-lake-a1b2c3d4.us-east-1.neon.tech",
    "port": 5432,
    "database": "neondb",
    "user": "neondb_owner",
    "password": "AbCdEfGhIjKlMnOp",  # Use environment variable in production!
}

CLOUDFLARE_BASE_URL = "https://api.cloudflare.com/client/v4/radar"
IODA_BASE_URL = "https://api.ioda.caida.org/v2"
RIPE_BASE_URL = "https://atlas.ripe.net/api/v2"
DEFAULT_LIMIT = 1000
```

**Better approach - use environment variables:**

```python
import os

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}

CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")
CLOUDFLARE_BASE_URL = "https://api.cloudflare.com/client/v4/radar"
```

## ✅ Step 6: Update GitHub Secrets

1. Go to your GitHub repository
2. **Settings** → **Secrets and variables** → **Actions**
3. Update or create these secrets with Neon values:

| Secret Name | Value (from Neon) |
|:---|:---|
| `DB_HOST` | `ep-cool-lake-a1b2c3d4.us-east-1.neon.tech` |
| `DB_PORT` | `5432` |
| `DB_USER` | `neondb_owner` |
| `DB_PASSWORD` | `AbCdEfGhIjKlMnOp` |
| `DB_NAME` | `neondb` |
| `CLOUDFLARE_API_TOKEN` | Your Cloudflare token |

## ✅ Step 7: Migrate Data from Local (Optional)

If you want to keep existing data:

### Option A: Export from Local PostgreSQL

```bash
# Backup local database
pg_dump -U postgres internet_outages > backup.sql

# Connect to Neon and import
psql -h ep-cool-lake-a1b2c3d4.us-east-1.neon.tech \
     -U neondb_owner \
     -d neondb \
     -f backup.sql
```

### Option B: Let it Populate from Scratch
- Just point to Neon database
- Run ingestion scripts tomorrow
- New data will populate automatically

**Recommendation**: Option B (simpler, no historical baggage)

## ✅ Step 8: Test Connection Locally

Create test script `test_neon_connection.py`:

```python
#!/usr/bin/env python
"""Test Neon database connection."""

import os
from database import PostgresDB

# Set environment variables
os.environ["DB_HOST"] = "ep-cool-lake-a1b2c3d4.us-east-1.neon.tech"  # Replace with your Neon host
os.environ["DB_PORT"] = "5432"
os.environ["DB_USER"] = "neondb_owner"  # Replace with your Neon user
os.environ["DB_PASSWORD"] = "AbCdEfGhIjKlMnOp"  # Replace with your Neon password
os.environ["DB_NAME"] = "neondb"

try:
    db = PostgresDB()
    db.connect()
    cursor = db.conn.cursor()
    
    print("✓ Connected to Neon successfully!")
    
    # Test query
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print(f"✓ PostgreSQL version: {version[0]}")
    
    # Check tables exist
    cursor.execute("""
        SELECT tablename FROM pg_tables 
        WHERE schemaname = 'raw'
    """)
    tables = cursor.fetchall()
    print(f"✓ Found {len(tables)} tables in raw schema")
    
    cursor.close()
    db.close()
    
except Exception as e:
    print(f"✗ Connection failed: {e}")
    exit(1)
```

Run it:
```bash
python test_neon_connection.py
```

## ✅ Step 9: Test Ingestion with Neon

```bash
# Run one ingestion to verify
python ingest_cloudflare.py

# Then verify
python verify_cloudflare.py
```

You should see records appearing in Neon!

## ✅ Step 10: Update GitHub Actions (if needed)

The `.github/workflows/daily-ingestion.yml` already uses environment variables from secrets, so **no changes needed!**

The workflow will automatically use Neon secrets you configured.

---

## 🔒 Security Best Practices

### 1. Never Hardcode Credentials
❌ **Don't do this:**
```python
DB_CONFIG = {
    "password": "AbCdEfGhIjKlMnOp"  # EXPOSED!
}
```

✅ **Do this:**
```python
DB_CONFIG = {
    "password": os.getenv("DB_PASSWORD")  # Secure
}
```

### 2. Rotate Passwords Regularly
1. In Neon: Project settings → Roles
2. Click user (neondb_owner) → Change password
3. Update GitHub secret with new password
4. Redeploy

### 3. Use Read-Only Roles (Optional)
For extra security, create separate roles:
- `neondb_owner` - for ingestion (write access)
- `neondb_reader` - for queries (read-only)

In Neon console:
```sql
CREATE ROLE reader WITH LOGIN PASSWORD 'password';
GRANT SELECT ON ALL TABLES IN SCHEMA raw TO reader;
```

### 4. IP Whitelisting (Neon Pro only)
If on Neon Pro plan, whitelist GitHub Actions IP ranges for extra security.

---

## 📊 Neon Pricing

**Free tier includes:**
- ✓ Good for development/testing
- ✓ Monthly query limit: 50 GB
- ✓ Credits reset each month

**For production:**
- Pay-as-you-go: $0.16 per 10 GB
- Project scales automatically
- Recommended for continuous ingestion

Your use case (1,200 records/day) fits comfortably in free tier!

---

## 🔍 Monitoring Neon Database

### View Usage in Neon Console
1. Project dashboard → **Monitoring**
2. See:
   - CPU usage
   - Connections
   - Query throughput
   - Storage

### View Logs
1. **Logs** tab
2. Filter by query type
3. Debug slow queries

---

## 🆘 Troubleshooting Neon Connection

### "Connection refused"
- ❌ Check network connectivity
- ❌ Verify credentials are correct
- ✅ Copy connection string again from Neon console

### "SSL/TLS error"
- ✅ Neon requires SSL - ensure `?sslmode=require` in connection string
- ✓ Our `database.py` handles this automatically

### "Too many connections"
- ✅ Neon limits connections on free tier
- ✅ Use **Pooled connection** (which we do)
- ✓ Automatic connection pooling handles this

### "Database does not exist"
- ❌ Check database name is correct (`neondb` by default)
- ❌ Make sure you created the tables

---

## 📝 Quick Reference

### Connection Info Format
```
postgresql://[USER]:[PASSWORD]@[HOST]/[DATABASE]?sslmode=require
```

### Environment Variables to Set
```bash
export DB_HOST="your-neon-host.neon.tech"
export DB_PORT="5432"
export DB_USER="neondb_owner"
export DB_PASSWORD="your-password"
export DB_NAME="neondb"
export CLOUDFLARE_API_TOKEN="your-token"
```

### Test Connection
```bash
psql -h your-neon-host.neon.tech -U neondb_owner -d neondb -c "SELECT 1;"
```

---

## ✅ After Migration Checklist

- [ ] Created Neon account
- [ ] Created Neon project and database
- [ ] Obtained connection string
- [ ] Updated GitHub secrets (6 secrets)
- [ ] Tested local connection with `test_neon_connection.py`
- [ ] Ran one ingestion script successfully
- [ ] Verified data appears in Neon
- [ ] GitHub Actions workflow triggered (or wait for 8 AM UTC)
- [ ] Confirmed automatic daily runs work

---

## 🎉 You're Done!

Your Internet Outage Platform is now:
- ✅ Running on **Neon cloud PostgreSQL**
- ✅ Automatically ingesting daily at 8 AM UTC
- ✅ Scalable for production use
- ✅ Backed by enterprise-grade infrastructure

**No more managing local databases!** 🚀
