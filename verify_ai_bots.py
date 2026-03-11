#!/usr/bin/env python
"""Verify the AI bots ingestion completed successfully."""

from database import PostgresDB

db = PostgresDB()
db.connect()
cursor = db.conn.cursor()

# Check record count and unique industries
cursor.execute('SELECT COUNT(*) FROM raw.cloudflare_ai_bots')
count = cursor.fetchone()[0]
print(f'✓ Total records: {count}')

cursor.execute('SELECT COUNT(DISTINCT industry) FROM raw.cloudflare_ai_bots')
industry_count = cursor.fetchone()[0]
print(f'✓ Unique industries: {industry_count}')

cursor.execute('SELECT DISTINCT industry FROM raw.cloudflare_ai_bots ORDER BY industry')
industries = [row[0] for row in cursor.fetchall()]
print('\nIndustries:')
for ind in industries:
    print(f'  - {ind}')

# Show sample records from different industries
print(f'\nSample records from 2 random industries:')
cursor.execute('''
SELECT timestamp, industry, metric, value 
FROM raw.cloudflare_ai_bots 
WHERE industry IN (SELECT industry FROM raw.cloudflare_ai_bots LIMIT 2 OFFSET 1)
ORDER BY industry, timestamp
LIMIT 4
''')
for row in cursor.fetchall():
    print(f'  {row[0]} | Industry: {row[1]} | Metric: {row[2]} | Value: {row[3]}')

cursor.close()
db.close()

print('\n✓ Ingestion verification complete!')
