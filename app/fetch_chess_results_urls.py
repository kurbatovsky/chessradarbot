from app.sources.chess_results import parse_federation_page


FEDERATION = "CYP"
LIMIT = 20
OUTPUT_FILE = "data/chess_results_urls.txt"


def main():
    urls = parse_federation_page(fed=FEDERATION, limit=LIMIT)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        for url in urls:
            file.write(url + "\n")

    print(f"Saved {len(urls)} URLs to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
