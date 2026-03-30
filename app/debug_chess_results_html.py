from app.sources.chess_results import fetch_html

URL = "https://chess-results.com/tnr1371006.aspx"

def main():
    html = fetch_html(URL)
    with open("data/chess_results_sample.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Saved HTML to data/chess_results_sample.html")

if __name__ == "__main__":
    main()
