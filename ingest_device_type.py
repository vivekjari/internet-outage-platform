from api_client import APIClient
from database import PostgresDB
from config import CLOUDFLARE_BASE_URL


class DeviceTypeIngestor:

    def __init__(self):
        self.client = APIClient()
        self.db = PostgresDB()

    def fetch_device_type(self):
        """Fetch HTTP timeseries data grouped by device type."""
        
        url = f"{CLOUDFLARE_BASE_URL}/http/timeseries_groups/DEVICE_TYPE"
        params = {
            "interval": "1h",
            "dateRange": "1d"
        }

        data = self.client.get(url, params=params)

        return data

    def parse_records(self, data):
        """
        Parse device type timeseries response into rows for insertion.
        
        Expected structure:
        {
          "result": {
            "serie_0": {
              "timestamps": [...],
              "DEVICE_TYPE_NAME": [...],
              "DEVICE_TYPE_NAME2": [...]
            }
          }
        }
        
        Returns list of tuples: (timestamp, device_type, metric, value)
        """
        rows = []
        result = data.get("result", {})

        if isinstance(result, dict):
            # Look for serie_* keys at the top level
            serie_keys = [k for k in result.keys() if k.startswith("serie_")]
            
            if serie_keys:
                # Process each serie
                for serie_key in serie_keys:
                    serie = result.get(serie_key, {})
                    if not isinstance(serie, dict):
                        continue
                    
                    timestamps = serie.get("timestamps", [])
                    if not timestamps:
                        continue
                    
                    # Extract device types and their values
                    for key, arr in serie.items():
                        if key == "timestamps":
                            continue
                        if not isinstance(arr, list):
                            continue
                        # key is the device type
                        for ts, v in zip(timestamps, arr):
                            rows.append((ts, key, None, v))
            else:
                # Fallback: try direct device type keys at result level
                timestamps = result.get("timestamps", [])
                if timestamps:
                    for key, arr in result.items():
                        if key == "timestamps":
                            continue
                        if not isinstance(arr, list):
                            continue
                        for ts, v in zip(timestamps, arr):
                            rows.append((ts, key, None, v))

        # Fallback: if result is a list of dicts with device_type/timestamp/value
        if isinstance(result, list):
            for item in result:
                device_type = item.get("device_type")
                timestamp = item.get("timestamp")
                metric = item.get("metric")
                value = item.get("value")
                rows.append((timestamp, device_type, metric, value))

        return rows

    def save_to_db(self, rows):
        """Save parsed rows to the raw.cloudflare_device_type table."""
        # Columns match the table structure: timestamp, device_type, metric, value
        # (id and normalized_metric are auto-generated/stored)
        columns = ["timestamp", "device_type", "metric", "value"]

        # Normalize rows into (timestamp, device_type, metric, value)
        normalized = []
        for r in rows:
            if len(r) == 4:
                normalized.append(r)
            elif len(r) == 3:
                normalized.append((r[0], r[1], None, r[2]))
            elif len(r) == 2:
                normalized.append((None, None, r[0], r[1]))
            else:
                # ignore malformed
                continue

        if normalized:
            try:
                self.db.insert_batch(
                    "raw.cloudflare_device_type",
                    columns,
                    normalized
                )
            except RuntimeError as e:
                print(f"DB insert skipped: {e}")
            except Exception as e:
                print(f"DB insert failed: {e}")

    def run(self):
        """Execute the full ingestion pipeline."""
        
        data = self.fetch_device_type()

        rows = self.parse_records(data)

        self.save_to_db(rows)

        print(f"Ingested {len(rows)} records")


if __name__ == "__main__":
    ingestor = DeviceTypeIngestor()
    ingestor.run()
