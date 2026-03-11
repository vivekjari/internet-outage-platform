#!/usr/bin/env python
"""Verify the device type ingestion."""

from database import PostgresDB

db = PostgresDB()
db.connect()
cursor = db.conn.cursor()

# Check record count and unique device types
cursor.execute('SELECT COUNT(*) FROM raw.cloudflare_device_type')
count = cursor.fetchone()[0]
print(f'✓ Total device type records: {count}')

cursor.execute('SELECT COUNT(DISTINCT device_type) FROM raw.cloudflare_device_type')
device_count = cursor.fetchone()[0]
print(f'✓ Unique device types: {device_count}')

cursor.execute('SELECT DISTINCT device_type FROM raw.cloudflare_device_type ORDER BY device_type')
devices = [row[0] for row in cursor.fetchall()]
print('\nDevice types:')
for dev in devices:
    print(f'  - {dev}')

# Show sample records from different device types
print(f'\nSample records from different device types:')
cursor.execute('''
SELECT timestamp, device_type, metric, value 
FROM raw.cloudflare_device_type 
ORDER BY device_type, timestamp
LIMIT 6
''')
for row in cursor.fetchall():
    print(f'  {row[0]} | Device: {row[1]} | Metric: {row[2]} | Value: {row[3]}')

# Check date range
cursor.execute('SELECT MIN(timestamp), MAX(timestamp) FROM raw.cloudflare_device_type WHERE timestamp IS NOT NULL')
min_ts, max_ts = cursor.fetchone()
print(f'\n✓ Date range: {min_ts} to {max_ts}')

cursor.close()
db.close()

print('\n✓ Device type ingestion verification complete!')
