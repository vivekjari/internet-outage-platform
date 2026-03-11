from ingest_cloudflare import CloudflareIngestor

def main():
    ingestor = CloudflareIngestor()

    print("Fetching data from Cloudflare Radar API...")

    data = ingestor.fetch_outages()

    print("Raw response received:")
    print(data)

    rows = ingestor.parse_records(data)

    print(f"\nParsed {len(rows)} records")

    if rows:
        print("\nSample record:")
        print(rows[0])


if __name__ == "__main__":
    main()