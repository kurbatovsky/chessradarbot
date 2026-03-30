from pprint import pprint
from app.sources.chess_results import parse_tournament_page

URL = "https://chess-results.com/tnr1371006.aspx"

def main():
    data = parse_tournament_page(URL)
    pprint(data)

if __name__ == "__main__":
    main()
