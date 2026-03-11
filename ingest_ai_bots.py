from api_client import APIClient
from database import PostgresDB
from config import CLOUDFLARE_BASE_URL


class AIBotsIngestor:

    def __init__(self):
        self.client = APIClient()
        self.db = PostgresDB()

    def fetch_ai_bots(self):
        """Fetch AI bots timeseries data grouped by industry."""
        
        url = f"{CLOUDFLARE_BASE_URL}/ai/bots/timeseries_groups/INDUSTRY"
        params = {
            "interval": "1h",
            "dateRange": "1d"
        }

        data = self.client.get(url, params=params)

        return data

    def parse_records(self, data):
        """
        Parse AI bots timeseries response into rows for insertion.
        
        Expected structure:
        {
          "result": {
            "serie_0": {
              "timestamps": [...],
              "INDUSTRY_NAME": [...],
              "INDUSTRY_NAME2": [...]
            }
          }
        }
        
        Returns list of tuples: (timestamp, industry, metric, value)
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
                    
                    # Extract industries and their values
                    for key, arr in serie.items():
                        if key == "timestamps":
                            continue
                        if not isinstance(arr, list):
                            continue
                        # key is the industry name
                        for ts, v in zip(timestamps, arr):
                            rows.append((ts, key, None, v))
            else:
                # Fallback: try direct industry keys at result level
                timestamps = result.get("timestamps", [])
                if timestamps:
                    for key, arr in result.items():
                        if key == "timestamps":
                            continue
                        if not isinstance(arr, list):
                            continue
                        for ts, v in zip(timestamps, arr):
                            rows.append((ts, key, None, v))

        # Fallback: if result is a list of dicts with industry/timestamp/value
        if isinstance(result, list):
            for item in result:
                industry = item.get("industry")
                timestamp = item.get("timestamp")
                metric = item.get("metric")
                value = item.get("value")
                rows.append((timestamp, industry, metric, value))

        return rows

    def save_to_db(self, rows):
        """Save parsed rows to the raw.cloudflare_ai_bots table."""
        # Columns match the table structure: timestamp, industry, metric, value
        # (id and normalized_metric are auto-generated/stored)
        columns = ["timestamp", "industry", "metric", "value"]

        # Normalize rows into (timestamp, industry, metric, value)
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
                    "raw.cloudflare_ai_bots",
                    columns,
                    normalized
                )
            except RuntimeError as e:
                print(f"DB insert skipped: {e}")
            except Exception as e:
                print(f"DB insert failed: {e}")

    def run(self):
        """Execute the full ingestion pipeline."""
        
        data = self.fetch_ai_bots()

        rows = self.parse_records(data)

        self.save_to_db(rows)

        print(f"Ingested {len(rows)} records")


if __name__ == "__main__":
    ingestor = AIBotsIngestor()
    ingestor.run()
