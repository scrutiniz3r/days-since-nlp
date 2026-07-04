"""
Rule-based entity extractor for activity name and days_ago.
Used alongside the intent classifier.
"""
import re
from datetime import date

DATE_PATTERNS = [
    (r'\btoday\b|\bthis morning\b|\bthis evening\b|\bthis afternoon\b', 0),
    (r'\byesterday\b|\blast night\b',        1),
    (r'(\d+)\s+days?\s+ago',                None),
    (r'(\d+)\s+days?\s+back',               None),
    (r'\ba week ago\b|\blast week\b',        7),
    (r'\btwo weeks ago\b|\b2 weeks ago\b',  14),
    (r'\ba month ago\b|\blast month\b',     30),
    (r'\blast\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b', None),
]

WEEKDAYS = ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"]

def days_ago_from_weekday(day_name: str) -> int:
    today = date.today()
    target = WEEKDAYS.index(day_name.lower())
    current = today.weekday()
    delta = (current - target) % 7
    return delta if delta > 0 else 7

def extract_days_ago(text: str):
    text_lower = text.lower()
    for pattern, value in DATE_PATTERNS:
        m = re.search(pattern, text_lower)
        if m:
            if value is not None:
                return value
            if m.lastindex and m.lastindex >= 1:
                try:
                    return int(m.group(1))
                except (IndexError, ValueError):
                    pass
            # weekday match
            for day in WEEKDAYS:
                if re.search(rf'\blast\s+{day}\b', text_lower):
                    return days_ago_from_weekday(day)
    return None

STRIP_PHRASES = [
    r'\b(i\s+)?(did|played|went|had|finished|completed|practiced|started|visited|called|spoke\s+to|cooked|bought|read|watched|took|made|cleaned|watered|biked|ran|hiked|swam)\b',
    r'\b(today|yesterday|this morning|this evening|this afternoon|last night)\b',
    r'\b\d+\s+days?\s+(ago|back)\b',
    r'\ba week ago\b|\blast week\b|\ba month ago\b|\blast month\b',
    r'\btwo weeks ago\b|\b2 weeks ago\b',
    r'\blast\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b',
    r'\b(for|an|a)\s+(hour|while|bit|session)\b',
    r'\bthis\s+(morning|evening|afternoon|week)\b',
    r'\bjust\b',
    r'\bto\b',  # strip stray prepositions
    r'\bmy\b',  # strip possessives
    r'\bwith\b.*$',  # strip trailing "with a friend" etc
]

def extract_activity(text: str) -> str:
    result = text
    for p in STRIP_PHRASES:
        result = re.sub(p, '', result, flags=re.IGNORECASE)
    result = re.sub(r'\s+', ' ', result).strip().strip('.,!?')
    return result.title() if result else None

def extract(text: str) -> dict:
    return {
        "activity": extract_activity(text),
        "days_ago": extract_days_ago(text),
    }

if __name__ == "__main__":
    tests = [
        "I did football 5 days ago",
        "Did cricket today",
        "Went to Chennai last week",
        "Called mom 3 days back",
        "Guitar practice this morning",
        "Played tennis yesterday",
        "Went hiking last Sunday",
    ]
    for t in tests:
        print(f"{t!r}")
        print(f"  → {extract(t)}\n")
