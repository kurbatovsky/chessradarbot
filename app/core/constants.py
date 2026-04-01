from app.core.countries import AVAILABLE_COUNTRIES

MAX_RESULTS = 5

FORMAT_LABELS = {
    "standard": "Classical",
    "rapid": "Rapid",
    "blitz": "Blitz",
}

ONBOARDING_TIMEZONE_OPTIONS = [
    ("(GMT+0) London", "Europe/London"),
    ("(GMT+1) Berlin", "Europe/Berlin"),
    ("(GMT+2) Athens", "Europe/Athens"),
    ("(GMT+2) Nicosia", "Asia/Nicosia"),
    ("(GMT+3) Istanbul", "Europe/Istanbul"),
    ("(GMT+3) Moscow", "Europe/Moscow"),
    ("(GMT+4) Dubai", "Asia/Dubai"),
    ("(GMT+4) Tbilisi", "Asia/Tbilisi"),
    ("(GMT+5) Tashkent", "Asia/Tashkent"),
    ("(GMT+6) Almaty", "Asia/Almaty"),
]

EXTENDED_TIMEZONE_OPTIONS = [
    ("(GMT-8) Los Angeles", "America/Los_Angeles"),
    ("(GMT-7) Denver", "America/Denver"),
    ("(GMT-6) Chicago", "America/Chicago"),
    ("(GMT-5) New York", "America/New_York"),
    ("(GMT+0) Dublin", "Europe/Dublin"),
    ("(GMT+0) Lisbon", "Europe/Lisbon"),
    ("(GMT+0) London", "Europe/London"),
    ("(GMT+1) Berlin", "Europe/Berlin"),
    ("(GMT+1) Madrid", "Europe/Madrid"),
    ("(GMT+1) Paris", "Europe/Paris"),
    ("(GMT+1) Rome", "Europe/Rome"),
    ("(GMT+2) Athens", "Europe/Athens"),
    ("(GMT+2) Bucharest", "Europe/Bucharest"),
    ("(GMT+2) Helsinki", "Europe/Helsinki"),
    ("(GMT+2) Nicosia", "Asia/Nicosia"),
    ("(GMT+3) Istanbul", "Europe/Istanbul"),
    ("(GMT+3) Jerusalem", "Asia/Jerusalem"),
    ("(GMT+3) Moscow", "Europe/Moscow"),
    ("(GMT+4) Dubai", "Asia/Dubai"),
    ("(GMT+4) Tbilisi", "Asia/Tbilisi"),
    ("(GMT+5) Karachi", "Asia/Karachi"),
    ("(GMT+5) Tashkent", "Asia/Tashkent"),
    ("(GMT+6) Almaty", "Asia/Almaty"),
    ("(GMT+8) Singapore", "Asia/Singapore"),
]

TIMEZONE_OTHER_CALLBACK = "OTHER"
TIMEZONE_BACK_TO_POPULAR_CALLBACK = "BACK_TO_POPULAR"