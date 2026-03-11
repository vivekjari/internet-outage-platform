from api_client import APIClient
from database import PostgresDB
from config import CLOUDFLARE_BASE_URL


class CloudflareIngestor:

    def __init__(self):
        self.client = APIClient()
        self.db = PostgresDB()

    def fetch_outages(self):

        url = f"{CLOUDFLARE_BASE_URL}/netflows/timeseries_groups/location?dateRange=1d"

        data = self.client.get(url)

        return data

    def parse_records(self, data):
        rows = []
        result = data.get("result", {})

        # 1) Summary-style responses: summary_* -> metric/value (no timestamp)
        if isinstance(result, dict):
            summary_keys = [k for k in result.keys() if k.startswith("summary_")]
            if summary_keys:
                for k in summary_keys:
                    summary = result.get(k, {})
                    if isinstance(summary, dict):
                        for metric, value in summary.items():
                            rows.append((None, None, metric, value))
                return rows

        # 2) Time-series per-location responses.
        # Possible shapes:
        # - result = { "serie_0": {"timestamps": [...], "values": [...]}, ... }
        # - result = { "LOCATION": { "serie_0": {"timestamps": [...], "values": [...]}, ... }, ... }
        if isinstance(result, dict):
            for key, val in result.items():
                if key == "meta":
                    continue

                # If the value itself contains timestamps and values, treat `key` as location
                if isinstance(val, dict) and "timestamps" in val:
                    # val may contain multiple series keyed by location (e.g. 'US', 'IN', 'other')
                    timestamps = val.get("timestamps", [])
                    for subkey, arr in val.items():
                        if subkey == "timestamps":
                            continue
                        if not isinstance(arr, list):
                            continue
                        for ts, v in zip(timestamps, arr):
                            rows.append((subkey, ts, None, v))
                    continue

                # If the value is a dict that contains serie_* entries
                if isinstance(val, dict):
                    serie_keys = [k for k in val.keys() if k.startswith("serie_")]
                    if serie_keys:
                        for sk in serie_keys:
                            serie = val.get(sk, {})
                            if not isinstance(serie, dict):
                                continue
                            if "timestamps" in serie:
                                timestamps = serie.get("timestamps", [])
                                # serie may contain multiple location series keyed by location
                                for subkey, arr in serie.items():
                                    if subkey == "timestamps":
                                        continue
                                    if not isinstance(arr, list):
                                        continue
                                    for ts, v in zip(timestamps, arr):
                                        rows.append((subkey, ts, None, v))
                            else:
                                # fallback: look for 'values' list
                                timestamps = serie.get("timestamps", [])
                                values = serie.get("values", [])
                                for ts, v in zip(timestamps, values):
                                    rows.append((key, ts, None, v))
                        continue

                # If the top-level key itself is serie_*, and values are at root
                if key.startswith("serie_") and isinstance(val, dict):
                    if "timestamps" in val:
                        timestamps = val.get("timestamps", [])
                        for subkey, arr in val.items():
                            if subkey == "timestamps":
                                continue
                            if not isinstance(arr, list):
                                continue
                            for ts, v in zip(timestamps, arr):
                                rows.append((subkey, ts, None, v))
                    else:
                        timestamps = val.get("timestamps", [])
                        values = val.get("values", [])
                        for ts, v in zip(timestamps, values):
                            rows.append((None, ts, None, v))

        # 3) Fallback: if result is a list of dicts with country/timestamp/value
        if isinstance(result, list):
            for item in result:
                country = item.get("country")
                timestamp = item.get("timestamp")
                value = item.get("value")
                rows.append((country, timestamp, None, value))

        return rows

    def save_to_db(self, rows):
        # Normalize rows into (location, timestamp, metric, value)
        columns = ["location", "timestamp", "metric", "value"]

        # Ensure rows are 4-tuples
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
                    "raw.cloudflare_outages",
                    columns,
                    normalized
                )
            except RuntimeError as e:
                print(f"DB insert skipped: {e}")
            except Exception as e:
                print(f"DB insert failed: {e}")

    def run(self):

        data = self.fetch_outages()

        rows = self.parse_records(data)

        self.save_to_db(rows)

        print(f"Ingested {len(rows)} records")