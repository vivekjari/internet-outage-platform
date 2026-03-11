#!/usr/bin/env python
"""Migrate data from local PostgreSQL to Neon cloud database.

This script dumps data from your local database and restores it to Neon.

Prerequisites:
    - pg_dump must be installed (comes with PostgreSQL)
    - Local database must be accessible
    - Neon database must be empty or you don't mind overwriting

Usage:
    python migrate_to_neon.py
"""

import subprocess
import os
import sys
from pathlib import Path

def migrate_data():
    """Migrate data from local PostgreSQL to Neon."""
    
    print("=" * 70)
    print("DATABASE MIGRATION: Local PostgreSQL → Neon")
    print("=" * 70)
    print()
    
    # Local database config
    local_host = os.getenv("LOCAL_DB_HOST", "localhost")
    local_port = os.getenv("LOCAL_DB_PORT", "5432")
    local_user = os.getenv("LOCAL_DB_USER", "postgres")
    local_db = os.getenv("LOCAL_DB_NAME", "internet_outages")
    
    # Neon database config
    neon_host = os.getenv("DB_HOST")
    neon_port = os.getenv("DB_PORT", "5432")
    neon_user = os.getenv("DB_USER")
    neon_password = os.getenv("DB_PASSWORD")
    neon_db = os.getenv("DB_NAME")
    
    # Validate Neon config
    print("1. Checking Neon configuration...")
    if not all([neon_host, neon_user, neon_password, neon_db]):
        print("   ✗ Missing Neon environment variables!")
        print("   Please set: DB_HOST, DB_USER, DB_PASSWORD, DB_NAME")
        return False
    print("   ✓ Neon configuration OK")
    print(f"     - Host: {neon_host}")
    print(f"     - User: {neon_user}")
    print(f"     - Database: {neon_db}")
    print()
    
    # Check if pg_dump exists
    print("2. Checking for pg_dump...")
    try:
        subprocess.run(["pg_dump", "--version"], capture_output=True, check=True)
        print("   ✓ pg_dump found")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("   ✗ pg_dump not found!")
        print("   Install PostgreSQL tools: brew install postgresql@15 (macOS)")
        return False
    print()
    
    # Create backup file
    backup_file = "backup_migration.sql"
    print(f"3. Backing up local database to {backup_file}...")
    
    try:
        # Dump local database
        dump_cmd = [
            "pg_dump",
            "-h", local_host,
            "-p", local_port,
            "-U", local_user,
            "-d", local_db,
            "--no-password",
            "-v"
        ]
        
        with open(backup_file, "w") as f:
            result = subprocess.run(
                dump_cmd,
                stdout=f,
                stderr=subprocess.PIPE,
                text=True
            )
        
        if result.returncode != 0:
            print(f"   ✗ Backup failed!")
            print(f"   Error: {result.stderr}")
            return False
        
        # Check file size
        file_size = Path(backup_file).stat().st_size
        print(f"   ✓ Backup created: {file_size:,} bytes")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    print()
    
    # Restore to Neon
    print("4. Restoring data to Neon...")
    
    try:
        restore_cmd = [
            "psql",
            "-h", neon_host,
            "-p", neon_port,
            "-U", neon_user,
            "-d", neon_db,
            "-f", backup_file
        ]
        
        env = os.environ.copy()
        env["PGPASSWORD"] = neon_password
        
        result = subprocess.run(
            restore_cmd,
            env=env,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"   ✗ Restore failed!")
            print(f"   Error: {result.stderr}")
            return False
        
        print("   ✓ Data restored to Neon successfully!")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    print()
    
    # Verify migration
    print("5. Verifying migration...")
    
    try:
        from database import PostgresDB
        
        db = PostgresDB()
        db.connect()
        cursor = db.conn.cursor()
        
        cursor.execute("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'raw'
        """)
        tables = cursor.fetchall()
        
        if tables:
            print(f"   ✓ Found {len(tables)} tables in Neon:")
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM raw.{table[0]}")
                count = cursor.fetchone()[0]
                print(f"     - {table[0]}: {count:,} records")
        else:
            print("   ⚠ No tables found in Neon")
        
        cursor.close()
        db.close()
    except Exception as e:
        print(f"   ✗ Verification failed: {e}")
        return False
    
    print()
    print("=" * 70)
    print("✓ MIGRATION COMPLETE!")
    print("=" * 70)
    print()
    print("Next steps:")
    print("  1. Test with: python test_neon_connection.py")
    print("  2. Update GitHub secrets with Neon credentials")
    print("  3. Monitor ingestion tomorrow at 8 AM UTC")
    print()
    print(f"Backup file: {backup_file}")
    print("(Keep this for reference, delete after confirming migration)")
    print()
    
    return True

if __name__ == "__main__":
    # Check environment variables
    print("Setting up migration...\n")
    
    print("Environment variables required:")
    print("  Local database:")
    print('    LOCAL_DB_HOST (default: localhost)')
    print('    LOCAL_DB_PORT (default: 5432)')
    print('    LOCAL_DB_USER (default: postgres)')
    print('    LOCAL_DB_NAME (default: internet_outages)')
    print()
    print("  Neon database (REQUIRED):")
    print('    DB_HOST')
    print('    DB_PORT (default: 5432)')
    print('    DB_USER')
    print('    DB_PASSWORD')
    print('    DB_NAME')
    print()
    
    success = migrate_data()
    sys.exit(0 if success else 1)
