import re
from datetime import datetime
from typing import Optional

import httpx
from bs4 import BeautifulSoup


BASE_HEADERS = {
    "User-Agent": "ChessRadarBot/0.1 (+contact: kurbatovsky@gmail.com)"
}


def detect_format(text: str) -> str:
    value = (text or "").lower()

    if "blitz" in value or " bz " in f" {value} ":
        return "blitz"
    if "rapid" in value or " rp " in f" {value} ":
        return "rapid"
    if "classical" in value or "standard" in value or " st " in f" {value} ":
        return "standard"

    return "standard"


def normalize_country_from_location(location: str) -> str:
    value = (location or "").lower()
    if "cyprus" in value:
        return "cyprus"
    if "greece" in value:
        return "greece"
    return "unknown"


def parse_date_value(text: str) -> Optional[str]:
    text = (text or "").strip()
    for fmt in ("%d.%m.%Y", "%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(text, fmt).date().isoformat()
        except ValueError:
            pass
    return None


def extract_tnr(url: str) -> str:
    match = re.search(r"tnr(\d+)\.aspx", url)
    if not match:
        raise ValueError(f"Could not extract tnr from URL: {url}")
    return match.group(1)


def fetch_html(url: str) -> str:
    with httpx.Client(headers=BASE_HEADERS, timeout=30.0, follow_redirects=True) as client:
        response = client.get(url)
        response.raise_for_status()
        return response.text


def parse_tournament_page(url: str) -> dict:
    html = fetch_html(url)
    soup = BeautifulSoup(html, "lxml")
    text = soup.get_text("\n", strip=True)

    title = None
    if soup.title and soup.title.text:
        title = soup.title.text.strip()

    if not title:
        h1 = soup.find("h1")
        title = h1.get_text(" ", strip=True) if h1 else "Unknown tournament"

    # Heuristics for first real importer:
    start_date = None
    end_date = None
    location = ""
    format_value = "standard"
    fide_rated = False
    entry_fee = None
    currency = "EUR"

    lines = text.splitlines()

    for i, line in enumerate(lines):
        low = line.lower()

        if "from" in low and "to" in low and not start_date:
            dates = re.findall(r"\d{2}\.\d{2}\.\d{4}", line)
            if len(dates) >= 2:
                start_date = parse_date_value(dates[0])
                end_date = parse_date_value(dates[1])

        if ("place" in low or "city" in low or "federation" in low) and len(line) < 120:
            if not location:
                location = line

        if "rapid" in low or "blitz" in low or "classical" in low or "standard" in low:
            format_value = detect_format(line)

        if "fide" in low and "rated" in low:
            fide_rated = True

        fee_match = re.search(r"(\d+(?:[.,]\d{1,2})?)\s*(eur|€)", line, re.I)
        if fee_match and entry_fee is None:
            entry_fee = float(fee_match.group(1).replace(",", "."))
            currency = "EUR"

    if not start_date:
        date_matches = re.findall(r"\d{2}\.\d{2}\.\d{4}", text)
        if date_matches:
            start_date = parse_date_value(date_matches[0])
            end_date = parse_date_value(date_matches[min(1, len(date_matches) - 1)])

    if not end_date:
        end_date = start_date

    if not location:
        location = "Unknown location"

    return {
        "source": "chess_results",
        "source_event_id": extract_tnr(url),
        "name": title,
        "location": location,
        "country": normalize_country_from_location(location),
        "start_date": start_date,
        "end_date": end_date,
        "format": format_value,
        "url": url,
        "fide_rated": fide_rated,
        "entry_fee": entry_fee,
        "currency": currency,
    }


def parse_federation_page(fed: str = "CYP", lan: int = 1, limit: int = 20) -> list[dict]:
    url = f"https://chess-results.com/fed.aspx?fed={fed}&lan={lan}"
    html = fetch_html(url)
    soup = BeautifulSoup(html, "lxml")

    results = []
    for link in soup.find_all("a", href=True):
        href = link["href"]
        text = link.get_text(" ", strip=True)

        if "tnr" not in href.lower():
            continue
        if not text:
            continue

        if href.startswith("/"):
            full_url = f"https://chess-results.com{href}"
        elif href.startswith("http"):
            full_url = href
        else:
            full_url = f"https://chess-results.com/{href}"

        try:
            source_event_id = extract_tnr(full_url)
        except ValueError:
            continue

        results.append(
            {
                "source": "chess_results",
                "source_event_id": source_event_id,
                "name": text,
                "url": full_url,
            }
        )

        if len(results) >= limit:
            break

    return results
