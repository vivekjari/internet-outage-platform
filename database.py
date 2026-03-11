from config import DB_CONFIG

try:
    import psycopg2
    from psycopg2.extras import execute_batch
except Exception:
    psycopg2 = None
    execute_batch = None
try:
    import pg8000
except Exception:
    pg8000 = None


class PostgresDB:

    def __init__(self):
        self.conn = None

    def connect(self):
        if self.conn:
            return
        # Prefer psycopg2 when available, otherwise try pg8000
        if psycopg2 is not None:
            self.conn = psycopg2.connect(
                host=DB_CONFIG["host"],
                port=DB_CONFIG["port"],
                database=DB_CONFIG["database"],
                user=DB_CONFIG["user"],
                password=DB_CONFIG.get("password")
            )
            return

        if pg8000 is not None:
            # pg8000.connect accepts keyword args host, port, database, user, password
            self.conn = pg8000.connect(
                host=DB_CONFIG["host"],
                port=DB_CONFIG["port"],
                database=DB_CONFIG["database"],
                user=DB_CONFIG["user"],
                password=DB_CONFIG.get("password")
            )
            return

        raise RuntimeError("No supported Postgres driver installed (psycopg2 or pg8000)")

    def insert_batch(self, table, columns, rows):
        self.connect()

        column_string = ",".join(columns)
        placeholder = ",".join(["%s"] * len(columns))

        # For certain raw tables, ensure a dedupe index / generated column exists
        upsert_conflict = None
        if table in ("raw.cloudflare_outages", "raw.cloudflare_bots", "raw.cloudflare_ai_bots", "raw.cloudflare_device_type"):
            try:
                # choose index name and conflict target based on table
                if table == "raw.cloudflare_outages":
                    index_name = "uq_cf_key"
                    upsert_conflict = "(location, timestamp, normalized_metric)"
                elif table == "raw.cloudflare_bots":
                    index_name = "uq_cf_bots_key"
                    upsert_conflict = "(location, timestamp, normalized_metric)"
                elif table == "raw.cloudflare_ai_bots":
                    index_name = "uq_cf_ai_key"
                    # dedupe key for AI bots: industry + timestamp + normalized_metric
                    upsert_conflict = "(industry, timestamp, normalized_metric)"
                else:  # cloudflare_device_type
                    index_name = "uq_cf_device_key"
                    # dedupe key for device type: device_type + timestamp + normalized_metric
                    upsert_conflict = "(device_type, timestamp, normalized_metric)"
                self._ensure_dedup_index(table, index_name)
            except Exception:
                # If migration fails, fall back to plain insert
                upsert_conflict = None

        query = f"INSERT INTO {table} ({column_string}) VALUES ({placeholder})"
        if upsert_conflict:
            # Update value on conflict; keep this simple and idempotent
            query = query + f" ON CONFLICT {upsert_conflict} DO UPDATE SET value = EXCLUDED.value"

        # psycopg2 path
        if psycopg2 is not None:
            cursor = self.conn.cursor()
            if execute_batch is None:
                for row in rows:
                    cursor.execute(query, row)
            else:
                execute_batch(cursor, query, rows)
            self.conn.commit()
            cursor.close()
            return

        # pg8000 path
        if pg8000 is not None:
            cursor = self.conn.cursor()
            # pg8000 uses executemany for batch inserts
            cursor.executemany(query, rows)
            self.conn.commit()
            cursor.close()
            return

        raise RuntimeError("No supported Postgres driver available for insert")

    def close(self):
        if self.conn:
            self.conn.close()

    def _ensure_dedup_index(self, table, index_name="uq_cf_key"):
        """Create a normalized metric generated column and unique index to prevent duplicates.

        `table` should be schema-qualified (e.g. 'raw.cloudflare_outages').
        This is a best-effort migration; if it fails we let the caller decide fallback behavior.
        """
        self.connect()
        cursor = self.conn.cursor()
        try:
            # Add a stored generated column that normalizes NULL metric values so the unique
            # constraint can compare a deterministic value.
            cursor.execute(
                f"""
                ALTER TABLE {table}
                ADD COLUMN IF NOT EXISTS normalized_metric text
                  GENERATED ALWAYS AS (COALESCE(metric, '<<NULL>>')) STORED;
                """
            )
        except Exception:
            # If adding the generated column fails, continue to attempting index creation
            pass

        # Create a unique index using the normalized metric to deduplicate.
        # Choose columns depending on the table shape.
        if "ai_bots" in table:
            cursor.execute(
                f"""
                CREATE UNIQUE INDEX IF NOT EXISTS {index_name}
                ON {table} (industry, timestamp, normalized_metric);
                """
            )
        elif "device_type" in table:
            cursor.execute(
                f"""
                CREATE UNIQUE INDEX IF NOT EXISTS {index_name}
                ON {table} (device_type, timestamp, normalized_metric);
                """
            )
        else:
            cursor.execute(
                f"""
                CREATE UNIQUE INDEX IF NOT EXISTS {index_name}
                ON {table} (location, timestamp, normalized_metric);
                """
            )
        self.conn.commit()
        cursor.close()