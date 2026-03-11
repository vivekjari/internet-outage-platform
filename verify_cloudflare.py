#!/usr/bin/env python
"""Verify the Cloudflare outages ingestion."""

from database import PostgresDB

db = PostgresDB()
db.connect()
cursor = db.conn.cursor()

# Check record count and unique locations
cursor.execute('SELECT COUNT(*) FROM raw.cloudflare_outages')
count = cursor.fetchone()[0]
print(f'✓ Total Cloudflare outage records: {count}')

cursor.execute('SELECT COUNT(DISTINCT location) FROM raw.cloudflare_outages')
location_count = cursor.fetchone()[0]
print(f'✓ Unique locations: {location_count}')

cursor.execute('''
SELECT location, COUNT(*) as record_count 
FROM raw.cloudflare_outages 
WHERE location IS NOT NULL AND location != ''
GROUP BY location 
ORDER BY record_count DESC 
LIMIT 5
''')
print('\nTop 5 locations by record count:')
for row in cursor.fetchall():
    print(f'  - {row[0]}: {row[1]} records')

# Show recent sample records
print(f'\nRecent sample records:')
cursor.execute('''
SELECT timestamp, location, metric, value 
FROM raw.cloudflare_outages 
ORDER BY timestamp DESC
LIMIT 5
''')
for row in cursor.fetchall():
    print(f'  {row[0]} | Location: {row[1]} | Metric: {row[2]} | Value: {row[3]}')

# Check date range
cursor.execute('SELECT MIN(timestamp), MAX(timestamp) FROM raw.cloudflare_outages WHERE timestamp IS NOT NULL')
min_ts, max_ts = cursor.fetchone()
print(f'\n✓ Date range: {min_ts} to {max_ts}')

cursor.close()
db.close()

print('\n✓ Cloudflare ingestion verification complete!')
