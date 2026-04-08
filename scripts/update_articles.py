
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

USER_AGENT = "Mozilla/5.0 (compatible; AQA-German-Current-Affairs-Hub/2.0)"
TIMEOUT = 25
MAX_ARTICLES = 48
MAX_PER_FEED = 20

FEEDS = [
    {"source": "DW Deutsch", "country": "Germany", "url": "https://rss.dw.com/rdf/rss-de-all"},
    {"source": "DW Langsam gesprochene Nachrichten", "country": "Germany", "url": "https://rss.dw.com/rdf/DKfeed_lgn_de"},
    {"source": "ORF Österreich", "country": "Austria", "url": "https://rss.orf.at/oesterreich.xml"},
    {"source": "ORF Science", "country": "Austria", "url": "https://rss.orf.at/science.xml"},
    {"source": "SRF Schweiz", "country": "Switzerland", "url": "https://www.srf.ch/news/bnf/rss/19032223"},
    {"source": "SRF Kultur", "country": "Switzerland", "url": "https://www.srf.ch/kultur/bnf/rss/8774"},
]

TOPIC_RULES = {
    "family": {
        "theme_id": "society",
        "strong": ["familie", "familien", "ehe", "heirat", "scheidung", "eltern", "kinder", "alleinerzieh", "partnerschaft", "haushalt"],
        "medium": ["pflege", "geburt", "erziehung", "betreuung", "vater", "mutter", "großeltern", "grosseltern", "haushalte"],
        "exclude": ["tierfamilie", "produktfamilie"],
        "threshold": 4,
    },
    "digital-world": {
        "theme_id": "society",
        "strong": ["digitalisierung", "soziale medien", "soziale netzwerke", "internet", "online", "app", "apps", "smartphone", "ki", "künstliche intelligenz", "cyber", "datenschutz"],
        "medium": ["plattform", "algorithm", "streaming", "influencer", "chatbot", "digital", "netz", "social media"],
        "exclude": [],
        "threshold": 4,
    },
    "youth-culture": {
        "theme_id": "society",
        "strong": ["jugendliche", "jugendkultur", "mode", "musik", "fernsehen", "tv", "streaming", "pop", "konzert", "influencer"],
        "medium": ["trend", "image", "serie", "festival", "stars", "band", "playlist", "social media"],
        "exclude": ["wahl", "wahlen", "eu", "bundestag"],
        "threshold": 4,
    },
    "immigration": {
        "theme_id": "multiculturalism",
        "strong": ["migration", "einwanderung", "zuwanderung", "asyl", "asylbewerber", "flüchtling", "fluechtling", "grenze", "visum", "abschiebung", "zuwanderer"],
        "medium": ["migranten", "ankunft", "aufnahme", "schutzsuchende", "migrationpolitik", "migrationspolitik"],
        "exclude": [],
        "threshold": 4,
    },
    "integration": {
        "theme_id": "multiculturalism",
        "strong": ["integration", "integrationskurs", "sprachkurs", "teilhabe", "inklusion", "arbeitsmarkt", "willkommenskultur"],
        "medium": ["eingliederung", "schulzugang", "wohnraum", "arbeitswelt", "teilnehmen", "hürden", "hindernisse"],
        "exclude": [],
        "threshold": 4,
    },
    "racism": {
        "theme_id": "multiculturalism",
        "strong": ["rassismus", "diskriminierung", "antisemitismus", "fremdenfeindlichkeit", "hasskriminalität", "hate speech", "rechte gewalt", "islamfeindlichkeit"],
        "medium": ["ausgrenzung", "hetze", "antirassismus", "vorurteile", "diskriminiert"],
        "exclude": [],
        "threshold": 4,
    },
    "festivals-traditions": {
        "theme_id": "culture",
        "strong": ["tradition", "traditionen", "fest", "feste", "feier", "karneval", "weihnachtsmarkt", "oktoberfest", "fastnacht", "brauch"],
        "medium": ["regional", "ritual", "umzug", "volksfest", "brauchtum", "feiertag"],
        "exclude": [],
        "threshold": 4,
    },
    "art-architecture": {
        "theme_id": "culture",
        "strong": ["kunst", "museum", "ausstellung", "galerie", "architektur", "architekt", "künstler", "kulturhaus", "denkmal"],
        "medium": ["design", "gebäude", "bauwerk", "sammlung", "installation", "skulptur", "malerei", "städtebau"],
        "exclude": [],
        "threshold": 4,
    },
    "berlin-culture": {
        "theme_id": "culture",
        "strong": ["berlin", "berliner", "hauptstadt", "clubszene", "museuminsel", "theater", "oper", "mauer", "ostberlin", "westberlin"],
        "medium": ["geschichte berlins", "kulturleben", "konzerthaus", "berghain", "gdr", "ddr"],
        "exclude": [],
        "threshold": 5,
    },
    "germany-eu": {
        "theme_id": "politics",
        "strong": ["eu", "europa", "europäische union", "europaeische union", "brüssel", "bruessel", "europaparlament", "schengen", "binnenmarkt", "eu-kommission"],
        "medium": ["eu-erweiterung", "europaweit", "mitgliedstaat", "ukraine-hilfe", "sanktionen", "nato", "eurozone"],
        "exclude": [],
        "threshold": 4,
    },
    "politics-youth": {
        "theme_id": "politics",
        "strong": ["jugendpolitik", "erstwähler", "erstwaehler", "wahl", "wahlen", "wahlrecht", "jugendparlament", "aktivismus", "demonstration", "protest"],
        "medium": ["politisches engagement", "werte", "ideale", "klimaprotest", "mitbestimmung", "wahlkampf", "politisch"],
        "exclude": [],
        "threshold": 4,
    },
    "reunification": {
        "theme_id": "politics",
        "strong": ["wiedervereinigung", "ddr", "mauerfall", "ostdeutschland", "westdeutschland", "friedliche revolution", "einheit", "ost", "west"],
        "medium": ["neue bundesländer", "alte bundesländer", "identität", "identitaet", "transformationsprozess", "ostdeutsch"],
        "exclude": [],
        "threshold": 4,
    },
}

COUNTRY_KEYWORDS = {
    "Germany": ["deutschland", "deutsch", "berlin", "hamburg", "münchen", "muenchen", "köln", "koeln", "bundestag", "bundesregierung", "ddr", "wiedervereinigung"],
    "Austria": ["österreich", "osterreich", "wien", "salzburg", "tirol", "grazer", "steiermark", "linz"],
    "Switzerland": ["schweiz", "schweizer", "bern", "zürich", "zurich", "genf", "lausanne", "basel", "kanton"],
}

THEME_FEED_BONUS = {
    ("culture", "SRF Kultur"): 2,
    ("culture", "ORF Österreich"): 1,
    ("culture", "DW Deutsch"): 1,
    ("politics", "DW Deutsch"): 1,
    ("politics", "ORF Österreich"): 1,
    ("multiculturalism", "DW Deutsch"): 1,
    ("society", "DW Langsam gesprochene Nachrichten"): 1,
}

GENERIC_EXCLUDE = [
    "sport", "fußball", "fussball", "tennis", "wetter", "aktien", "börse", "boerse", "podcastfolge", "spieltag"
]


# ---------- Helpers ----------

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


def normalise(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "").lower()).strip()


def count_hits(text: str, terms: list[str], weight: int) -> int:
    score = 0
    for term in terms:
        if term in text:
            score += weight
    return score


def get_theme_subtopic_maps(topics: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    themes = {theme["id"]: theme for theme in topics["themes"]}
    subtopics = {}
    for theme in topics["themes"]:
        for subtopic in theme["subtopics"]:
            subtopics[subtopic["id"]] = subtopic
    return themes, subtopics


def contains_country_reference(text: str, country: str) -> bool:
    return any(term in text for term in COUNTRY_KEYWORDS.get(country, []))


# ---------- Classification ----------

def classify_article(text: str, topics: dict[str, Any], country: str, source: str) -> tuple[dict[str, Any] | None, dict[str, Any] | None, int]:
    text_lower = normalise(text)

    if any(term in text_lower for term in GENERIC_EXCLUDE):
        return None, None, 0

    themes_map, subtopics_map = get_theme_subtopic_maps(topics)

    scored: list[tuple[int, str]] = []
    for subtopic_id, rule in TOPIC_RULES.items():
        score = 0
        score += count_hits(text_lower, rule["strong"], 3)
        score += count_hits(text_lower, rule["medium"], 1)
        if any(term in text_lower for term in rule["exclude"]):
            score -= 2
        score += THEME_FEED_BONUS.get((rule["theme_id"], source), 0)
        scored.append((score, subtopic_id))

    scored.sort(reverse=True)
    best_score, best_subtopic_id = scored[0]
    second_score = scored[1][0] if len(scored) > 1 else 0
    best_rule = TOPIC_RULES[best_subtopic_id]

    if best_score < best_rule["threshold"]:
        return None, None, 0

    if best_score - second_score < 2:
        return None, None, 0

    if not contains_country_reference(text_lower, country):
        # Let clearly relevant EU/German politics still pass.
        if best_subtopic_id != "germany-eu":
            return None, None, 0

    theme = themes_map[best_rule["theme_id"]]
    subtopic = subtopics_map[best_subtopic_id]
    return theme, subtopic, best_score


# ---------- Prompt generation ----------

def build_questions(subtopic_id: str, title: str, summary: str) -> list[str]:
    text = normalise(f"{title} {summary}")

    base = {
        "family": [
            "Inwiefern zeigt dieser Artikel, dass sich Familienstrukturen oder Beziehungen verändern?",
            "Welche Auswirkungen könnte diese Entwicklung auf Familien in deutschsprachigen Ländern haben?",
        ],
        "digital-world": [
            "Welche Chancen und Risiken der Digitalisierung werden hier sichtbar?",
            "Wie stark beeinflusst dieses Thema den Alltag in deutschsprachigen Ländern?",
        ],
        "youth-culture": [
            "Warum könnte dieses Thema für Jugendliche besonders relevant sein?",
            "Wie stark prägen Medien, Musik oder Trends das Verhalten junger Menschen?",
        ],
        "immigration": [
            "Welche Gründe, Probleme oder Chancen im Bereich Migration werden hier deutlich?",
            "Wie sollte ein deutschsprachiges Land auf diese Entwicklung reagieren?",
        ],
        "integration": [
            "Welche Hindernisse oder Fortschritte bei der Integration erkennt man hier?",
            "Welche Maßnahmen wären in dieser Situation besonders sinnvoll?",
        ],
        "racism": [
            "Welche Form von Diskriminierung oder Ausgrenzung steht hier im Mittelpunkt?",
            "Was könnte man gesellschaftlich oder politisch konkret dagegen tun?",
        ],
        "festivals-traditions": [
            "Warum ist dieses Fest oder diese Tradition heute noch wichtig?",
            "Sollten Traditionen eher bewahrt oder stärker modernisiert werden?",
        ],
        "art-architecture": [
            "Welche Rolle spielt Kunst oder Architektur in diesem Beispiel?",
            "Warum investieren Städte oder Regionen in Kultur und Bauprojekte?",
        ],
        "berlin-culture": [
            "Wie zeigt dieser Artikel die besondere kulturelle Rolle Berlins?",
            "Welche Verbindung zwischen Geschichte und Gegenwart erkennt man hier?",
        ],
        "germany-eu": [
            "Welche Rolle Deutschlands in Europa wird in diesem Artikel sichtbar?",
            "Welche Vorteile oder Spannungen innerhalb der EU erkennt man hier?",
        ],
        "politics-youth": [
            "Wie werden Jugendliche oder junge Erwachsene politisch angesprochen oder aktiv?",
            "Warum könnte dieses Thema für Erstwählerinnen und Erstwähler wichtig sein?",
        ],
        "reunification": [
            "Welche Folgen der Wiedervereinigung oder Unterschiede zwischen Ost und West erkennt man hier?",
            "Warum bleibt dieses Thema gesellschaftlich oder politisch relevant?",
        ],
    }.get(subtopic_id, [
        "Was ist die wichtigste Aussage dieses Artikels?",
        "Warum könnte dieses Thema für deutschsprachige Länder relevant sein?",
    ])

    angle = None
    if any(t in text for t in ["regierung", "bundesrat", "bundestag", "ministerium", "gesetz", "reform", "politik"]):
        angle = "policy"
    elif any(t in text for t in ["jugend", "jugendliche", "schüler", "schueler", "studenten", "erstwähler", "erstwaehler"]):
        angle = "youth"
    elif any(t in text for t in ["kosten", "wirtschaft", "arbeitsmarkt", "unternehmen", "teuer", "finanz"]):
        angle = "economy"
    elif any(t in text for t in ["berlin", "geschichte", "ddr", "mauer", "erinnerung"]):
        angle = "history"
    elif any(t in text for t in ["internet", "online", "ki", "digital", "plattform", "social media"]):
        angle = "digital"
    elif any(t in text for t in ["schule", "bildung", "universität", "universitaet", "ausbildung"]):
        angle = "education"

    angle_question = {
        "policy": "Findest du, dass die Politik hier richtig handelt, oder sollte man anders vorgehen?",
        "youth": "Inwiefern betrifft dieses Thema junge Menschen direkt oder indirekt?",
        "economy": "Welche wirtschaftlichen Folgen könnte diese Entwicklung haben?",
        "history": "Welche Rolle spielt der historische Hintergrund bei diesem Thema?",
        "digital": "Wie verändert die Digitalisierung die Situation in diesem Fall?",
        "education": "Welche Rolle sollten Schulen oder Universitäten bei diesem Thema spielen?",
        None: "Welche Folgen könnte diese Entwicklung für die Gesellschaft insgesamt haben?",
    }[angle]

    return [base[0], base[1], angle_question]


# ---------- Parsing ----------

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

        items.append({
            "title": title,
            "url": link,
            "summary": description,
            "publishedAt": parse_date(pub_date),
            "source": source,
            "country": country,
        })

        if len(items) >= MAX_PER_FEED:
            break

    return items


# ---------- Builder ----------

def build_articles() -> list[dict[str, Any]]:
    topics = load_topics()
    seen_urls: set[str] = set()
    built: list[dict[str, Any]] = []

    for feed in FEEDS:
        try:
            xml_text = fetch_text(feed["url"])
            feed_items = parse_feed(xml_text, feed["source"], feed["country"])
        except Exception as exc:
            print(f"Failed to fetch {feed['source']}: {exc}")
            continue

        for item in feed_items:
            if item["url"] in seen_urls:
                continue

            full_text = normalise(f"{item['title']} {item['summary']}")
            theme, subtopic, confidence = classify_article(full_text, topics, item["country"], item["source"])
            if not theme or not subtopic:
                continue

            article_id = slugify(f"{subtopic['id']}-{item['title']}")
            keywords = list(dict.fromkeys((TOPIC_RULES[subtopic["id"]]["strong"] + TOPIC_RULES[subtopic["id"]]["medium"])[:8]))
            questions = build_questions(subtopic["id"], item["title"], item["summary"])

            built.append({
                "id": article_id,
                "title": item["title"],
                "url": item["url"],
                "summary": item["summary"][:280],
                "publishedAt": item["publishedAt"],
                "source": item["source"],
                "country": item["country"],
                "themeId": theme["id"],
                "themeLabel": theme["label"],
                "themeShortLabel": theme["shortLabel"],
                "subtopicId": subtopic["id"],
                "subtopicLabel": subtopic["label"],
                "keywords": keywords,
                "discussionQuestions": questions,
                "confidence": confidence,
            })
            seen_urls.add(item["url"])

    built.sort(key=lambda a: (a["confidence"], a["publishedAt"]), reverse=True)
    return built[:MAX_ARTICLES]


# ---------- Main ----------

def main() -> None:
    articles = build_articles()
    payload = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "articles": articles,
    }
    ARTICLES_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(articles)} articles to {ARTICLES_PATH}")


if __name__ == "__main__":
    main()
