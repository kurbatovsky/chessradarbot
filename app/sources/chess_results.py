import re
from typing import Optional, Tuple
from datetime import datetime
from urllib.parse import urlencode, urlparse, urlunparse, parse_qs

import httpx
from bs4 import BeautifulSoup


BASE_HEADERS = {
    "User-Agent": "ChessRadarBot/0.1"
}


def build_full_tournament_url(url: str) -> str:
    url = url.strip()

    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url

    parsed = urlparse(url)

    query = parse_qs(parsed.query)
    query["lan"] = ["1"]
    query["turdet"] = ["YES"]
    query["SNode"] = ["S0"]

    new_query = urlencode(query, doseq=True)

    return urlunparse(
        (
            parsed.scheme or "https",
            parsed.netloc,
            parsed.path,
            parsed.params,
            new_query,
            parsed.fragment,
        )
    )


def extract_tnr(url: str) -> str:
    match = re.search(r"tnr(\d+)\.aspx", url, re.IGNORECASE)
    if not match:
        raise ValueError(f"Could not extract tnr from URL: {url}")
    return match.group(1)


def fetch_html(url: str) -> str:
    full_url = build_full_tournament_url(url)

    with httpx.Client(
        headers=BASE_HEADERS,
        timeout=30.0,
        follow_redirects=True,
    ) as client:
        response = client.get(full_url)
        response.raise_for_status()
        return response.text


def detect_format_from_time_control(value: str) -> str:
    text = (value or "").lower()

    if "rapid" in text:
        return "rapid"
    if "blitz" in text:
        return "blitz"
    return "standard"


def normalize_country(value: str) -> str:
    text = (value or "").strip().lower()

    federation_map = {
        "cyp": "cyprus",
        "gre": "greece",
        "arm": "armenia",
        "geo": "georgia",
        "srb": "serbia",
        "rus": "russia",
        "kaz": "kazakhstan",
        "uzb": "uzbekistan",
    }

    code_match = re.search(r"\(\s*([A-Z]{3})\s*\)", value or "")
    if code_match:
        code = code_match.group(1).lower()
        if code in federation_map:
            return federation_map[code]

    text_map = {
        "cyprus": "cyprus",
        "greece": "greece",
        "armenia": "armenia",
        "georgia": "georgia",
        "serbia": "serbia",
        "russia": "russia",
        "russian federation": "russia",
        "kazakhstan": "kazakhstan",
        "uzbekistan": "uzbekistan",
    }

    for key, normalized in text_map.items():
        if key in text:
            return normalized

    return "unknown"


def parse_chess_results_date(value: str) -> Tuple[Optional[str], Optional[str]]:
    text = (value or "").strip()

    try:
        dt = datetime.strptime(text, "%Y/%m/%d").date().isoformat()
        return dt, dt
    except ValueError:
        pass

    found = re.findall(r"\d{4}/\d{2}/\d{2}", text)
    if len(found) == 1:
        dt = datetime.strptime(found[0], "%Y/%m/%d").date().isoformat()
        return dt, dt
    if len(found) >= 2:
        start_dt = datetime.strptime(found[0], "%Y/%m/%d").date().isoformat()
        end_dt = datetime.strptime(found[1], "%Y/%m/%d").date().isoformat()
        return start_dt, end_dt

    return None, None


def parse_tournament_page(url: str) -> dict:
    full_url = build_full_tournament_url(url)
    html = fetch_html(full_url)
    soup = BeautifulSoup(html, "lxml")

    title = "Unknown tournament"
    title_el = soup.find("h2")
    if title_el:
        title = title_el.get_text(" ", strip=True)

    text_lines = [
        line.strip()
        for line in soup.get_text("\n", strip=True).splitlines()
        if line.strip()
    ]

    organizer = None
    federation = None
    time_control = None
    location = None
    date_value = None
    fide_rated = False

    for i, line in enumerate(text_lines):
        low = line.lower()

        if line == "Organizer(s)" and i + 1 < len(text_lines):
            organizer = text_lines[i + 1]

        elif line == "Federation" and i + 1 < len(text_lines):
            federation = text_lines[i + 1]

        elif line.startswith("Time control"):
            if i + 1 < len(text_lines) and text_lines[i + 1] not in {"Location", "Date", "Federation", "Organizer(s)"}:
                time_control = f"{line} {text_lines[i + 1]}".strip()
            else:
                time_control = line

        elif line == "Location" and i + 1 < len(text_lines):
            location = text_lines[i + 1]

        elif line == "Date" and i + 1 < len(text_lines):
            date_value = text_lines[i + 1]

        if "rating international" in low or "fide" in low:
            fide_rated = True

    start_date, end_date = parse_chess_results_date(date_value or "")
    country = normalize_country(federation or location or "")
    tournament_format = detect_format_from_time_control(time_control or "")

    return {
        "source": "chess_results",
        "source_event_id": extract_tnr(full_url),
        "name": title,
        "location": location or "Unknown location",
        "country": country,
        "start_date": start_date,
        "end_date": end_date,
        "format": tournament_format,
        "url": full_url,
        "fide_rated": fide_rated,
        "entry_fee": None,
        "currency": "EUR",
        "organizer": organizer,
        "federation_raw": federation,
        "time_control_raw": time_control,
    }
    
def parse_federation_page(fed: str = "CYP", limit: int = 20) -> list[str]:
    url = f"https://chess-results.com/fed.aspx?fed={fed}&lan=1"

    with httpx.Client(
        headers=BASE_HEADERS,
        timeout=30.0,
        follow_redirects=True,
    ) as client:
        response = client.get(url)
        response.raise_for_status()
        html = response.text

    soup = BeautifulSoup(html, "lxml")

    urls = []
    seen = set()

    for link in soup.find_all("a", href=True):
        href = link["href"].strip()

        if "tnr" not in href.lower():
            continue

        if href.startswith("http://") or href.startswith("https://"):
            full_url = href
        elif href.startswith("/"):
            full_url = "https://chess-results.com" + href
        else:
            full_url = "https://chess-results.com/" + href

        # убираем query, чтобы хранить базовый URL
        match = re.search(r"(https?://[^?]+tnr\d+\.aspx)", full_url, re.IGNORECASE)
        if not match:
            continue

        clean_url = match.group(1)

        if clean_url in seen:
            continue

        seen.add(clean_url)
        urls.append(clean_url)

        if len(urls) >= limit:
            break

    return urls