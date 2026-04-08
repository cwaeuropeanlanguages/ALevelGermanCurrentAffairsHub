from __future__ import annotations

import html
import json
import re
import ssl
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TOPICS_PATH = ROOT / "data" / "topics.json"
ARTICLES_PATH = ROOT / "data" / "articles.json"

USER_AGENT = "Mozilla/5.0 (compatible; AQA-German-Current-Affairs-Hub/1.0)"
TIMEOUT = 25
MAX_ARTICLES = 60
MAX_PER_FEED = 20

FEEDS = [
    {
        "source": "DW Deutsch",
        "country": "Germany",
        "url": "https://rss.dw.com/rdf/rss-de-all"
    },
    {
        "source": "DW Langsam gesprochene Nachrichten",
        "country": "Germany",
        "url": "https://rss.dw.com/rdf/DKfeed_lgn_de"
    },
    {
        "source": "ORF Österreich",
        "country": "Austria",
        "url": "https://rss.orf.at/oesterreich.xml"
    },
    {
        "source": "ORF Science",
        "country": "Austria",
        "url": "https://rss.orf.at/science.xml"
    },
    {
        "source": "SRF Schweiz",
        "country": "Switzerland",
        "url": "https://www.srf.ch/news/bnf/rss/19032223"
    },
    {
        "source": "SRF Kultur",
        "country": "Switzerland",
        "url": "https://www.srf.ch/kultur/bnf/rss/8774"
    }
]

DEFAULT_DISCUSSION = [
    "Was ist hier das Hauptproblem oder die Hauptchance?",
    "Welche Folgen könnte diese Entwicklung für die Gesellschaft haben?",
    "Wie könnte man dieses Thema im Unterricht oder in einer mündlichen Prüfung diskutieren?"
]

COUNTRY_KEYWORDS = {
    "Germany": ["deutschland", "deutsch", "berlin", "bundestag", "bundesregierung", "ddr", "wiedervereinigung"],
    "Austria": ["österreich", "osterreich", "wien", "övp", "fpö", "steiermark", "tirol", "salzburg"],
    "Switzerland": ["schweiz", "schweizer", "bern", "zürich", "zurich", "genf", "bundesrat", "kanton"]
}


def load_topics() -> dict[str, Any]:
    with TOPICS_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def fetch_text(url: str) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    context = ssl.create_default_context()
    with urllib.request.urlopen(request, timeout=TIMEOUT, context=context) as response:
        return response.read().decode("utf-8", errors="replace")


def strip_html(value: str) -> str:
    value = html.unescape(value or "")
    value = re.sub(r"<[^>]+>", " ", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def local_name(tag: str) -> str:
    return tag.split("}", 1)[-1] if "}" in tag else tag


def get_first_text(element: ET.Element, names: list[str]) -> str:
    for child in element.iter():
        if local_name(child.tag) in names and (child.text and child.text.strip()):
            return child.text.strip()
    return ""


def parse_date(value: str) -> str:
    if not value:
        return datetime.now(timezone.utc).isoformat()

    try:
        parsed = parsedate_to_datetime(value)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc).isoformat()
    except Exception:
        pass

    cleaned = value.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(cleaned)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc).isoformat()
    except Exception:
        return datetime.now(timezone.utc).isoformat()


def slugify(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "article"


def classify_article(text: str, topics: dict[str, Any], country: str) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    text_lower = text.lower()
    best_theme = None
    best_subtopic = None
    best_score = 0

    for theme in topics["themes"]:
        for subtopic in theme["subtopics"]:
            score = 0
            for keyword in subtopic["keywords"]:
                if keyword in text_lower:
                    score += 1
            if score > best_score:
                best_score = score
                best_theme = theme
                best_subtopic = subtopic

    if best_score < 1:
        return None, None

    # Light country relevance check for Germany feed so the tool stays tied to German-speaking places.
    if country == "Germany":
        if not any(keyword in text_lower for keyword in COUNTRY_KEYWORDS["Germany"] + ["eu", "europa"]):
            return None, None

    return best_theme, best_subtopic


def build_questions(theme_id: str, subtopic_id: str, title: str) -> list[str]:
    prompt_bank = {
        "family": [
            "Inwiefern zeigt dieser Artikel, dass sich Familienstrukturen verändern?",
            "Welche Vor- und Nachteile könnte diese Entwicklung für Familien haben?",
            "Wie wichtig ist dieses Thema für junge Menschen heute?"
        ],
        "digital-world": [
            "Welche Chancen und Risiken der Digitalisierung sieht man hier?",
            "Sollte der Staat stärker eingreifen oder nicht?",
            "Wie beeinflusst dieses Thema den Alltag Jugendlicher?"
        ],
        "youth-culture": [
            "Warum könnte dieses Thema für Jugendliche besonders wichtig sein?",
            "Wie stark beeinflussen Medien und Trends junge Menschen?",
            "Ist das eher positiv oder negativ?"
        ],
        "immigration": [
            "Welche Gründe für Migration werden hier deutlich?",
            "Welche Vorteile oder Herausforderungen werden gezeigt?",
            "Wie sollte die Politik darauf reagieren?"
        ],
        "integration": [
            "Welche Hindernisse für Integration erkennt man hier?",
            "Welche Maßnahmen könnten helfen?",
            "Ist Integration eher Aufgabe des Staates oder der Gesellschaft?"
        ],
        "racism": [
            "Welche Formen von Rassismus oder Diskriminierung stehen im Mittelpunkt?",
            "Welche Folgen könnte das für Betroffene haben?",
            "Was kann man konkret dagegen tun?"
        ],
        "festivals-traditions": [
            "Warum sind Feste und Traditionen gesellschaftlich wichtig?",
            "Sollten Traditionen bewahrt oder modernisiert werden?",
            "Welche Rolle spielen regionale Unterschiede?"
        ],
        "art-architecture": [
            "Welche Rolle spielt Kunst oder Architektur im Alltag?",
            "Warum investieren Städte in Kulturprojekte?",
            "Wie wichtig ist es, kulturelles Erbe zu schützen?"
        ],
        "berlin-culture": [
            "Wie wird Berlin in diesem Artikel dargestellt?",
            "Welche Verbindung sieht man zwischen Geschichte und Kulturleben?",
            "Warum ist Berlin kulturell so attraktiv?"
        ],
        "germany-eu": [
            "Welche Rolle spielt Deutschland hier in Europa?",
            "Welche Vorteile oder Nachteile der EU erkennt man?",
            "Wie könnte sich diese Entwicklung auf Deutschland auswirken?"
        ],
        "politics-youth": [
            "Wie engagieren sich junge Menschen politisch?",
            "Warum könnte dieses Thema für Erstwähler wichtig sein?",
            "Sollten Jugendliche mehr politischen Einfluss haben?"
        ],
        "reunification": [
            "Welche Folgen der Wiedervereinigung erkennt man hier?",
            "Gibt es noch Unterschiede zwischen Ost und West?",
            "Warum bleibt dieses Thema politisch und kulturell relevant?"
        ]
    }
    return prompt_bank.get(subtopic_id, DEFAULT_DISCUSSION)


def parse_feed(xml_text: str, source: str, country: str) -> list[dict[str, Any]]:
    root = ET.fromstring(xml_text)
    items: list[dict[str, Any]] = []

    for element in root.iter():
        if local_name(element.tag) != "item":
            continue

        title = strip_html(get_first_text(element, ["title"]))
        link = strip_html(get_first_text(element, ["link"]))
        description = strip_html(get_first_text(element, ["description", "encoded", "summary"]))
        pub_date = get_first_text(element, ["pubDate", "date", "updated", "published"])

        if not title or not link:
            continue

        items.append(
            {
                "title": title,
                "url": link,
                "summary": description,
                "publishedAt": parse_date(pub_date),
                "source": source,
                "country": country,
            }
        )

        if len(items) >= MAX_PER_FEED:
            break

    return items


def build_articles() -> list[dict[str, Any]]:
    topics = load_topics()
    seen_urls: set[str] = set()
    articles: list[dict[str, Any]] = []

    for feed in FEEDS:
        try:
            xml_text = fetch_text(feed["url"])
            entries = parse_feed(xml_text, feed["source"], feed["country"])
        except Exception as exc:
            print(f"Skipping {feed['source']}: {exc}")
            continue

        for entry in entries:
            if entry["url"] in seen_urls:
                continue

            combined_text = f"{entry['title']} {entry['summary']}"
            theme, subtopic = classify_article(combined_text, topics, entry["country"])
            if not theme or not subtopic:
                continue

            seen_urls.add(entry["url"])
            summary = entry["summary"] or entry["title"]
            summary = summary[:240].rsplit(" ", 1)[0] + "…" if len(summary) > 240 else summary

            article = {
                "id": slugify(f"{entry['source']}-{entry['title']}")[:80],
                "title": entry["title"],
                "url": entry["url"],
                "summary": summary,
                "source": entry["source"],
                "country": entry["country"],
                "publishedAt": entry["publishedAt"],
                "themeId": theme["id"],
                "themeLabel": theme["label"],
                "themeShortLabel": theme["shortLabel"],
                "subtopicId": subtopic["id"],
                "subtopicLabel": subtopic["label"],
                "keywords": subtopic["keywords"][:6],
                "discussionQuestions": build_questions(theme["id"], subtopic["id"], entry["title"]),
            }
            articles.append(article)

    articles.sort(key=lambda item: item["publishedAt"], reverse=True)
    return articles[:MAX_ARTICLES]


def main() -> None:
    articles = build_articles()
    payload = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "articles": articles,
    }
    with ARTICLES_PATH.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(f"Wrote {len(articles)} article(s) to {ARTICLES_PATH}")


if __name__ == "__main__":
    main()
