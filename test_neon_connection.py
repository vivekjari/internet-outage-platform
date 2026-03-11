#!/usr/bin/env python
"""Test Neon database connection with environment variables.

Usage:
    export DB_HOST="your-neon-host.neon.tech"
    export DB_PORT="5432"
    export DB_USER="neondb_owner"
    export DB_PASSWORD="your-password"
    export DB_NAME="neondb"
    
    python test_neon_connection.py
"""

import os
import sys
from database import PostgresDB

def test_neon_connection():
    """Test connection to Neon database."""
    
    print("=" * 60)
    print("NEON DATABASE CONNECTION TEST")
    print("=" * 60)
    print()
    
    # Check environment variables
    print("1. Checking environment variables...")
    required_vars = ["DB_HOST", "DB_PORT", "DB_USER", "DB_PASSWORD", "DB_NAME"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"   ✗ Missing variables: {', '.join(missing_vars)}")
        print("\n   Please set environment variables:")
        print('   export DB_HOST="your-neon-host.neon.tech"')
        print('   export DB_PORT="5432"')
        print('   export DB_USER="neondb_owner"')
        print('   export DB_PASSWORD="your-password"')
        print('   export DB_NAME="neondb"')
        return False
    
    print("   ✓ All required environment variables set")
    print(f"     - DB_HOST: {os.getenv('DB_HOST')}")
    print(f"     - DB_PORT: {os.getenv('DB_PORT')}")
    print(f"     - DB_USER: {os.getenv('DB_USER')}")
    print(f"     - DB_NAME: {os.getenv('DB_NAME')}")
    print()
    
    # Test connection
    print("2. Testing connection to Neon...")
    try:
        db = PostgresDB()
        db.connect()
        print("   ✓ Connected to Neon successfully!")
    except Exception as e:
        print(f"   ✗ Connection failed: {e}")
        return False
    
    print()
    
    # Get database version
    print("3. Checking PostgreSQL version...")
    try:
        cursor = db.conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"   ✓ {version}")
        print()
    except Exception as e:
        print(f"   ✗ Query failed: {e}")
        return False
    
    # Check tables in raw schema
    print("4. Checking tables in raw schema...")
    try:
        cursor.execute("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'raw'
            ORDER BY tablename
        """)
        tables = cursor.fetchall()
        
        if tables:
            print(f"   ✓ Found {len(tables)} tables:")
            for table in tables:
                print(f"     - {table[0]}")
        else:
            print("   ℹ No tables found in raw schema yet")
            print("     (This is normal if you haven't ingested data yet)")
        print()
    except Exception as e:
        print(f"   ✗ Query failed: {e}")
        return False
    
    # Check data if tables exist
    if tables:
        print("5. Checking record counts...")
        try:
            for table in tables:
                table_name = table[0]
                cursor.execute(f"SELECT COUNT(*) FROM raw.{table_name}")
                count = cursor.fetchone()[0]
                print(f"   ✓ {table_name}: {count:,} records")
            print()
        except Exception as e:
            print(f"   ✗ Query failed: {e}")
    
    # Close connection
    cursor.close()
    db.close()
    
    print("=" * 60)
    print("✓ ALL TESTS PASSED!")
    print("=" * 60)
    print()
    print("Your Neon database is ready for production use.")
    print("You can now:")
    print("  1. Run ingestion scripts: python ingest_cloudflare.py")
    print("  2. Update GitHub secrets with Neon credentials")
    print("  3. Deploy to production")
    print()
    
    return True

if __name__ == "__main__":
    success = test_neon_connection()
    sys.exit(0 if success else 1)
