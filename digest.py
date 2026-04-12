import feedparser
import os
import re
from datetime import datetime, timedelta

# ─── CONFIGURATION ─────────────────────────────────────────────────────────────
DAYS_BACK = 7

# ─── FEED STRUCTURE ────────────────────────────────────────────────────────────
# Page renders in this exact order — priority accounts first.

SECTIONS = [

    {
        "id": "home-office",
        "label": "Home Office & Border Security",
        "icon": "🔴",
        "tier": "priority",
        "tier_label": "Priority Account",
        "feeds": [
            ("Home Office – GOV.UK News",        "https://www.gov.uk/search/news-and-communications.atom?organisations[]=home-office"),
            ("Home Office – GovWire",             "https://www.govwire.co.uk/rss/home-office"),
            ("Border Force – GovWire",            "https://www.govwire.co.uk/rss/border-force"),
            ("Border Security Command – GOV.UK",  "https://www.gov.uk/search/news-and-communications.atom?keywords=border+security+command"),
            ("Home Office Media Blog",            "https://homeofficemedia.blog.gov.uk/feed/"),
            ("UK Visas & Immigration – GovWire",  "https://www.govwire.co.uk/rss/uk-visas-and-immigration"),
            ("Independent Chief Inspector Borders","https://www.govwire.co.uk/rss/independent-chief-inspector-of-borders-and-immigration-"),
            ("Home Office Science Blog",          "https://hodigital.blog.gov.uk/feed/"),
        ],
        "keywords": [
            "border force", "border security", "immigration enforcement", "home secretary",
            "policing", "counter terrorism", "passport", "visa", "asylum", "security command",
            "digital", "technology", "data", "GIS", "mapping", "location", "AI", "biometrics",
            "facial recognition", "surveillance", "drone", "UAV", "contract", "procurement",
            "tender", "framework", "award", "pilot", "deployment",
        ],
    },

    {
        "id": "ministry-of-justice",
        "label": "Ministry of Justice, HMCTS & HMPPS",
        "icon": "🔴",
        "tier": "priority",
        "tier_label": "Priority Account",
        "feeds": [
            ("Ministry of Justice – GOV.UK",      "https://www.gov.uk/search/news-and-communications.atom?organisations[]=ministry-of-justice"),
            ("Ministry of Justice – GovWire",     "https://www.govwire.co.uk/rss/ministry-of-justice"),
            ("HMCTS Blog – Inside HMCTS",         "https://insidehmcts.blog.gov.uk/feed/"),
            ("HMCTS – GOV.UK",                    "https://www.gov.uk/search/news-and-communications.atom?organisations[]=hm-courts-and-tribunals-service"),
            ("HMPPS – GOV.UK",                    "https://www.gov.uk/search/news-and-communications.atom?organisations[]=her-majestys-prison-and-probation-service"),
            ("Prison & Probation – GOV.UK",       "https://www.gov.uk/search/news-and-communications.atom?keywords=prison+probation+technology"),
            ("MoJ Digital Blog",                  "https://mojdigital.blog.gov.uk/feed/"),
        ],
        "keywords": [
            "HMCTS", "HMPPS", "prison", "probation", "court", "tribunal", "justice",
            "offender", "rehabilitation", "digital", "technology", "data", "mapping",
            "location", "GIS", "contract", "procurement", "tender", "framework", "award",
            "AI", "analytics", "reform", "transformation", "estate", "facility",
        ],
    },

    {
        "id": "policing-npcc",
        "label": "Policing – NPCC, Police.AI & Forces",
        "icon": "🟠",
        "tier": "market",
        "tier_label": "Public Safety Market",
        "feeds": [
            ("NPCC News",                         "https://news.npcc.police.uk/feed"),
            ("Police.AI / NPCC Science",          "https://science.police.uk/feed/"),
            ("College of Policing",               "https://www.college.police.uk/feed"),
            ("Police Digital Service Blog",       "https://pds.blog.gov.uk/feed/"),
            ("Police Oracle",                     "https://www.policeoracle.com/rss/news.xml"),
            ("Police Professional",               "https://www.policeprofessional.com/feed/"),
            ("GOV.UK – Policing",                 "https://www.gov.uk/search/news-and-communications.atom?keywords=policing+technology"),
            ("NDAO – GOV.UK",                     "https://www.gov.uk/search/news-and-communications.atom?keywords=national+data+analytics+office"),
            ("NCA – GOV.UK",                      "https://www.gov.uk/search/news-and-communications.atom?organisations[]=national-crime-agency"),
        ],
        "keywords": [
            "NPCC", "police", "policing", "force", "constabulary", "AI", "Police.AI",
            "facial recognition", "ANPR", "body worn", "drone", "UAV", "CAD",
            "command and control", "dispatch", "control room", "digital", "data",
            "analytics", "GIS", "mapping", "location", "NDAO", "NCA", "ESN",
            "technology", "contract", "procurement", "tender", "award", "pilot",
        ],
    },

    {
        "id": "fire-rescue",
        "label": "Fire & Rescue – NFCC & Services",
        "icon": "🟠",
        "tier": "market",
        "tier_label": "Public Safety Market",
        "feeds": [
            ("NFCC News",                         "https://nfcc.org.uk/feed/"),
            ("Fire Magazine",                     "https://www.fire-magazine.com/feed"),
            ("Emergency Services Times",          "https://www.emergencyservicestimes.com/feed/"),
            ("GOV.UK – Fire & Rescue",            "https://www.gov.uk/search/news-and-communications.atom?keywords=fire+rescue+service"),
            ("GOV.UK – NFCC",                     "https://www.gov.uk/search/news-and-communications.atom?keywords=national+fire+chiefs"),
        ],
        "keywords": [
            "fire", "fire service", "fire rescue", "NFCC", "firefighter", "appliance",
            "mobilising", "control room", "GIS", "mapping", "location", "digital",
            "technology", "data", "drone", "UAV", "contract", "procurement", "tender",
            "framework", "award", "transformation", "analytics",
        ],
    },

    {
        "id": "procurement",
        "label": "Procurement & Commercial Signals",
        "icon": "🟡",
        "tier": "commercial",
        "tier_label": "Commercial Intelligence",
        "feeds": [
            # Live tenders — public safety & geospatial
            ("Find a Tender – GIS",               "https://www.find-tender.service.gov.uk/api/1.0/Opportunities?keyword=GIS&format=RSS"),
            ("Find a Tender – Geospatial",        "https://www.find-tender.service.gov.uk/api/1.0/Opportunities?keyword=geospatial&format=RSS"),
            ("Find a Tender – Mapping",           "https://www.find-tender.service.gov.uk/api/1.0/Opportunities?keyword=mapping+software&format=RSS"),
            ("Contracts Finder – GIS",            "https://www.contractsfinder.service.gov.uk/Published/Notices/PublishedNoticeSearchResults?Page=1&Format=RSS&Keyword=GIS"),
            ("Contracts Finder – Geospatial",     "https://www.contractsfinder.service.gov.uk/Published/Notices/PublishedNoticeSearchResults?Page=1&Format=RSS&Keyword=geospatial"),
            ("Contracts Finder – Public Safety",  "https://www.contractsfinder.service.gov.uk/Published/Notices/PublishedNoticeSearchResults?Page=1&Format=RSS&Keyword=public+safety"),
            ("Contracts Finder – Policing Tech",  "https://www.contractsfinder.service.gov.uk/Published/Notices/PublishedNoticeSearchResults?Page=1&Format=RSS&Keyword=policing+technology"),
            ("Contracts Finder – Home Office",    "https://www.contractsfinder.service.gov.uk/Published/Notices/PublishedNoticeSearchResults?Page=1&Format=RSS&Keyword=home+office+mapping"),
            ("Contracts Finder – MoJ",            "https://www.contractsfinder.service.gov.uk/Published/Notices/PublishedNoticeSearchResults?Page=1&Format=RSS&Keyword=ministry+of+justice+digital"),
            # Awards
            ("Contracts Finder – Awards GIS",     "https://www.contractsfinder.service.gov.uk/Published/Notices/PublishedNoticeSearchResults?Page=1&Format=RSS&Keyword=GIS&status=awarded"),
            ("Contracts Finder – Awards Safety",  "https://www.contractsfinder.service.gov.uk/Published/Notices/PublishedNoticeSearchResults?Page=1&Format=RSS&Keyword=public+safety&status=awarded"),
        ],
        "keywords": [
            "GIS", "geospatial", "mapping", "location", "spatial", "ArcGIS",
            "police", "fire", "border", "justice", "prison", "home office",
            "tender", "contract", "award", "framework", "PIN", "prior information",
            "market engagement", "PME", "invitation to tender", "ITT", "RFP", "RFQ",
            "procurement", "lot", "call-off", "Crown Commercial",
        ],
    },

    {
        "id": "competitor-intel",
        "label": "Competitor & Partner Intelligence",
        "icon": "🔵",
        "tier": "competitive",
        "tier_label": "Competitive Intelligence",
        "feeds": [
            # Competitors — GIS / Geospatial
            ("Hexagon Safety & Geospatial",       "https://hexagon.com/company/newsroom/feed"),
            ("1Spatial News",                     "https://1spatial.com/feed/"),
            ("what3words Blog",                   "https://what3words.com/blog/feed/"),
            # Competitors — Public Safety platforms
            ("NEC Software Solutions",            "https://www.necsws.com/feed/"),
            ("Motorola Solutions Blog",           "https://www.motorolasolutions.com/en_us/blog.rss"),
            ("Frequentis News",                   "https://www.frequentis.com/en/news/feed"),
            # SI / Partners
            ("Sopra Steria UK",                   "https://www.soprasteria.co.uk/feed/"),
            ("Capita News",                       "https://www.capita.com/news/rss"),
            ("Palantir Blog",                     "https://blog.palantir.com/feed"),
            ("Microsoft UK Public Sector",        "https://www.microsoft.com/en-gb/industry/blog/feed/"),
            # Market M&A signals
            ("GeoConnexion",                      "https://www.geoconnexion.com/feed"),
            ("Geospatial World",                  "https://www.geospatialworld.net/feed/"),
        ],
        "keywords": [
            # Competitor names
            "Hexagon", "NEC Software", "Cadcorp", "1Spatial", "what3words",
            "Motorola Solutions", "Frequentis", "Sopra Steria", "Capita",
            "Palantir", "Microsoft", "Google",
            # Signal types
            "contract award", "wins contract", "awarded", "selected", "chosen",
            "partnership", "acquisition", "merger", "investment", "funding",
            "police", "fire", "border", "justice", "home office", "prison",
            "GIS", "geospatial", "mapping", "CAD", "command and control",
            "UK", "United Kingdom", "British",
        ],
    },

    {
        "id": "policy-parliament",
        "label": "Policy, Parliament & Hansard",
        "icon": "⚪",
        "tier": "context",
        "tier_label": "Sector Context",
        "feeds": [
            ("Hansard – Home Affairs",            "https://hansard.parliament.uk/rss/commons/homeaffairs"),
            ("Hansard – Justice",                 "https://hansard.parliament.uk/rss/commons/justice"),
            ("GOV.UK – DSIT",                     "https://www.gov.uk/search/news-and-communications.atom?organisations[]=department-for-science-innovation-and-technology"),
            ("Public Technology",                 "https://publictechnology.net/feed/"),
            ("LocalGov",                          "https://www.localgov.co.uk/rss/news"),
            ("Public Sector Executive",           "https://www.publicsectorexecutive.com/feed/"),
        ],
        "keywords": [
            "police", "policing", "justice", "prison", "border", "home office",
            "AI", "digital", "technology", "data", "GIS", "mapping", "geospatial",
            "public safety", "emergency services", "contract", "procurement",
            "spending", "budget", "reform", "transformation",
        ],
    },

    {
        "id": "geospatial-tech",
        "label": "Geospatial & Technology News",
        "icon": "⚪",
        "tier": "context",
        "tier_label": "Sector Context",
        "feeds": [
            ("Ordnance Survey Blog",              "https://www.ordnancesurvey.co.uk/blog/feed"),
            ("Geospatial Commission – GOV.UK",    "https://www.gov.uk/search/news-and-communications.atom?keywords=geospatial+commission"),
            ("GIS Lounge",                        "https://www.gislounge.com/feed/"),
            ("BBC Technology",                    "http://feeds.bbci.co.uk/news/technology/rss.xml"),
            ("The Register – AI",                 "https://www.theregister.com/headlines/ai/"),
            ("Wired UK",                          "https://www.wired.co.uk/rss"),
        ],
        "keywords": [
            "GIS", "geospatial", "spatial", "mapping", "location", "GPS", "satellite",
            "LiDAR", "digital twin", "AI", "machine learning", "public sector",
            "UK", "government", "police", "safety", "Esri", "ArcGIS",
        ],
    },
]

# ─── COMPETITOR NAMES for flagging ────────────────────────────────────────────
COMPETITORS = [
    "Hexagon", "NEC Software", "Cadcorp", "1Spatial", "what3words",
    "Motorola Solutions", "Frequentis",
]
PARTNERS_SI = [
    "Sopra Steria", "Capita", "Palantir", "Microsoft", "Google",
]

# ─── HELPERS ───────────────────────────────────────────────────────────────────

def strip_html(text):
    return re.sub(r'<[^>]+>', '', text or '').strip()

def is_recent(entry):
    cutoff = datetime.now() - timedelta(days=DAYS_BACK)
    for attr in ("published_parsed", "updated_parsed"):
        t = getattr(entry, attr, None)
        if t:
            try:
                return datetime(*t[:6]) >= cutoff
            except Exception:
                pass
    return True

def score_article(entry, section_keywords):
    text = f"{entry.get('title','')} {entry.get('summary','')}".lower()
    score = 0
    matched = []
    for kw in section_keywords:
        if kw.lower() in text:
            score += 1
            matched.append(kw)
    return score, matched

def is_competitor(entry):
    text = f"{entry.get('title','')} {entry.get('summary','')}".lower()
    for c in COMPETITORS:
        if c.lower() in text:
            return True, "competitor"
    for p in PARTNERS_SI:
        if p.lower() in text:
            return True, "partner"
    return False, None

def format_date(entry):
    for attr in ("published_parsed", "updated_parsed"):
        t = getattr(entry, attr, None)
        if t:
            try:
                return datetime(*t[:6]).strftime("%-d %b %Y")
            except Exception:
                pass
    return ""

def detect_notice_type(entry):
    text = f"{entry.get('title','')} {entry.get('summary','')}".lower()
    if any(x in text for x in ["prior information", "pin notice", "prior information notice"]):
        return "PIN"
    if any(x in text for x in ["preliminary market", "market engagement", "pme", "soft market"]):
        return "PME"
    if any(x in text for x in ["award", "awarded", "contract award", "winner", "wins contract"]):
        return "AWARD"
    if any(x in text for x in ["invitation to tender", "itt ", "rfp", "rfq", "open procedure"]):
        return "TENDER"
    return None

# ─── FETCH ─────────────────────────────────────────────────────────────────────

def fetch_section(section):
    articles = []
    for name, url in section["feeds"]:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                if not is_recent(entry):
                    continue
                score, matched = score_article(entry, section["keywords"])
                summary = strip_html(entry.get("summary", ""))[:240]
                flagged, flag_type = is_competitor(entry)
                notice_type = detect_notice_type(entry) if section["tier"] == "commercial" else None
                articles.append({
                    "source":      name,
                    "title":       strip_html(entry.get("title", "No title")),
                    "link":        entry.get("link", "#"),
                    "summary":     summary,
                    "date":        format_date(entry),
                    "score":       score,
                    "matched":     matched[:3],
                    "flagged":     flagged,
                    "flag_type":   flag_type,
                    "notice_type": notice_type,
                })
        except Exception as e:
            print(f"  ⚠ {name}: {e}")
    # Sort: score desc, flagged first within tier
    articles.sort(key=lambda x: (x["score"]), reverse=True)
    return articles[:20]

# ─── HTML ──────────────────────────────────────────────────────────────────────

TIER_META = {
    "priority":    {"bar": "#c0392b", "badge_bg": "#c0392b",   "badge_text": "PRIORITY ACCOUNT"},
    "market":      {"bar": "#e07b00", "badge_bg": "#e07b00",   "badge_text": "PUBLIC SAFETY MARKET"},
    "commercial":  {"bar": "#c49a00", "badge_bg": "#c49a00",   "badge_text": "COMMERCIAL INTELLIGENCE"},
    "competitive": {"bar": "#1a6fb5", "badge_bg": "#1a6fb5",   "badge_text": "COMPETITIVE INTEL"},
    "context":     {"bar": "#4a5568", "badge_bg": "#4a5568",   "badge_text": "SECTOR CONTEXT"},
}

NOTICE_BADGES = {
    "PIN":    ("#7b2d8b", "PIN NOTICE"),
    "PME":    ("#b5560f", "MARKET ENGAGEMENT"),
    "AWARD":  ("#1a6b1a", "CONTRACT AWARD"),
    "TENDER": ("#0f4c8a", "LIVE TENDER"),
}

def build_html(sections_data):
    now = datetime.now()
    generated = now.strftime("%-d %B %Y, %H:%M")
    week_label = now.strftime("w/c %-d %B %Y")
    total_articles = sum(len(s["articles"]) for s in sections_data)
    priority_count = sum(
        1 for s in sections_data
        for a in s["articles"]
        if s["section"]["tier"] == "priority"
    )
    commercial_count = sum(
        1 for s in sections_data
        if s["section"]["tier"] == "commercial"
        for a in s["articles"]
    )

    # ── Sidebar nav ──
    nav_html = ""
    current_tier = None
    tier_labels = {
        "priority":    "Priority Accounts",
        "market":      "Public Safety Market",
        "commercial":  "Commercial Signals",
        "competitive": "Competitive Intel",
        "context":     "Sector Context",
    }
    for sd in sections_data:
        sec = sd["section"]
        count = len(sd["articles"])
        tier = sec["tier"]
        if tier != current_tier:
            current_tier = tier
            nav_html += f'<div class="nav-group-label">{tier_labels[tier]}</div>'
        color = TIER_META[tier]["bar"]
        nav_html += f'''
        <a class="nav-item" href="#{sec["id"]}" style="--tier-color:{color}">
            <span class="nav-icon">{sec["icon"]}</span>
            <span class="nav-label">{sec["label"]}</span>
            <span class="nav-count">{count}</span>
        </a>'''

    # ── Sections ──
    sections_html = ""
    for sd in sections_data:
        sec = sd["section"]
        articles = sd["articles"]
        tier = sec["tier"]
        meta = TIER_META[tier]
        count = len(articles)

        cards_html = ""
        if not articles:
            cards_html = '<div class="empty-state">No new items found this week for this section.</div>'
        else:
            for a in articles:
                # Card classes
                card_class = "card"
                if tier == "priority":
                    card_class += " card-priority"
                elif a.get("flagged"):
                    card_class += " card-flagged"

                # Notice type badge
                notice_badge = ""
                if a.get("notice_type") and a["notice_type"] in NOTICE_BADGES:
                    nb_color, nb_label = NOTICE_BADGES[a["notice_type"]]
                    notice_badge = f'<span class="notice-badge" style="background:{nb_color}">{nb_label}</span>'

                # Competitor/partner badge
                comp_badge = ""
                if a.get("flagged"):
                    if a["flag_type"] == "competitor":
                        comp_badge = '<span class="comp-badge comp-rival">COMPETITOR</span>'
                    else:
                        comp_badge = '<span class="comp-badge comp-partner">SI / PARTNER</span>'

                summary_html = f'<p class="card-summary">{a["summary"]}…</p>' if a["summary"] else ""

                cards_html += f'''
                <article class="{card_class}">
                    <div class="card-badges">{notice_badge}{comp_badge}</div>
                    <a class="card-title" href="{a["link"]}" target="_blank" rel="noopener">{a["title"]}</a>
                    <div class="card-meta">
                        <span class="card-source">{a["source"]}</span>
                        {'<span class="card-dot">·</span><span class="card-date">' + a["date"] + '</span>' if a["date"] else ""}
                    </div>
                    {summary_html}
                </article>'''

        sections_html += f'''
        <section class="digest-section" id="{sec["id"]}">
            <div class="section-header" style="--tier-bar:{meta["bar"]}">
                <div class="section-header-left">
                    <span class="section-icon">{sec["icon"]}</span>
                    <h2 class="section-title">{sec["label"]}</h2>
                </div>
                <div class="section-header-right">
                    <span class="tier-badge" style="background:{meta["badge_bg"]}">{meta["badge_text"]}</span>
                    <span class="section-count">{count} items</span>
                </div>
            </div>
            <div class="cards-grid">
                {cards_html}
            </div>
        </section>'''

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Esri UK · Public Safety BD Digest</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@600;700;800&family=Libre+Franklin:ital,wght@0,300;0,400;0,500;0,600;1,300&display=swap" rel="stylesheet">
<style>
:root {{
    --ink:       #0d1117;
    --ink-2:     #1c2333;
    --ink-3:     #2d3748;
    --bg:        #f4f5f9;
    --white:     #ffffff;
    --border:    #e2e8f0;
    --muted:     #718096;
    --sidebar-w: 272px;
    --priority:  #c0392b;
    --market:    #e07b00;
    --commercial:#c49a00;
    --compet:    #1a6fb5;
    --context:   #4a5568;
    --font-h:    'Syne', sans-serif;
    --font-b:    'Libre Franklin', sans-serif;
}}
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
html {{ scroll-behavior: smooth; }}
body {{ font-family: var(--font-b); background: var(--bg); color: var(--ink); display: flex; min-height: 100vh; }}

/* ── SIDEBAR ── */
.sidebar {{
    width: var(--sidebar-w);
    background: var(--ink);
    position: fixed; top: 0; left: 0; bottom: 0;
    display: flex; flex-direction: column;
    overflow-y: auto; z-index: 200;
}}
.sidebar-brand {{
    padding: 24px 20px 18px;
    border-bottom: 1px solid rgba(255,255,255,0.07);
}}
.brand-eyebrow {{
    font-family: var(--font-h);
    font-size: 9px; font-weight: 700;
    letter-spacing: 2.5px; text-transform: uppercase;
    color: var(--priority); margin-bottom: 5px;
}}
.brand-name {{
    font-family: var(--font-h);
    font-size: 16px; font-weight: 800; color: white; line-height: 1.25;
}}
.brand-sub {{ font-size: 11px; color: rgba(255,255,255,0.35); margin-top: 3px; font-weight: 300; }}

.nav-group-label {{
    font-size: 9px; font-weight: 700;
    letter-spacing: 2px; text-transform: uppercase;
    color: rgba(255,255,255,0.2);
    padding: 14px 20px 5px;
}}
.nav-item {{
    display: flex; align-items: center; gap: 9px;
    padding: 8px 20px;
    color: rgba(255,255,255,0.55); font-size: 12px; font-weight: 400;
    text-decoration: none;
    border-left: 3px solid transparent;
    transition: all 0.15s;
}}
.nav-item:hover {{ color: white; background: rgba(255,255,255,0.04); border-left-color: var(--tier-color); }}
.nav-item.active {{ color: white; background: rgba(255,255,255,0.07); border-left-color: var(--tier-color); }}
.nav-icon {{ font-size: 13px; flex-shrink: 0; }}
.nav-label {{ flex: 1; line-height: 1.35; }}
.nav-count {{
    font-size: 10px; font-weight: 600;
    background: rgba(255,255,255,0.1); color: rgba(255,255,255,0.45);
    padding: 1px 6px; border-radius: 8px;
}}
.sidebar-footer {{
    margin-top: auto;
    padding: 14px 20px;
    border-top: 1px solid rgba(255,255,255,0.07);
    font-size: 10px; color: rgba(255,255,255,0.2);
    line-height: 1.9;
}}

/* ── MAIN ── */
.main {{ margin-left: var(--sidebar-w); flex: 1; display: flex; flex-direction: column; }}

/* ── TOPBAR ── */
.topbar {{
    background: var(--white);
    border-bottom: 1px solid var(--border);
    padding: 18px 32px;
    display: flex; align-items: center; justify-content: space-between;
    position: sticky; top: 0; z-index: 100;
}}
.topbar-title {{
    font-family: var(--font-h); font-size: 18px; font-weight: 700; color: var(--ink);
}}
.topbar-sub {{ font-size: 11px; color: var(--muted); margin-top: 2px; font-weight: 300; }}
.topbar-stats {{ display: flex; gap: 20px; align-items: center; }}
.stat {{ text-align: right; }}
.stat-num {{
    font-family: var(--font-h); font-size: 20px; font-weight: 700;
    color: var(--ink); line-height: 1;
}}
.stat-num.red {{ color: var(--priority); }}
.stat-num.amber {{ color: var(--commercial); }}
.stat-lbl {{ font-size: 9px; color: var(--muted); text-transform: uppercase; letter-spacing: 1px; margin-top: 2px; }}
.stat-divider {{ width: 1px; height: 32px; background: var(--border); }}

/* ── FILTER BAR ── */
.filter-bar {{
    background: #fafbff;
    border-bottom: 1px solid var(--border);
    padding: 10px 32px;
    display: flex; align-items: center; gap: 8px;
}}
.filter-label {{ font-size: 11px; font-weight: 600; color: var(--muted); text-transform: uppercase; letter-spacing: 1px; margin-right: 4px; }}
.fbtn {{
    padding: 4px 12px; border-radius: 14px;
    border: 1px solid var(--border);
    background: var(--white); color: var(--muted);
    font-family: var(--font-b); font-size: 11px; font-weight: 500;
    cursor: pointer; transition: all 0.15s;
}}
.fbtn:hover {{ border-color: var(--ink-3); color: var(--ink); }}
.fbtn.active {{ background: var(--ink); border-color: var(--ink); color: white; }}

/* ── CONTENT ── */
.content {{ padding: 28px 32px 60px; }}

/* ── SECTION ── */
.digest-section {{ margin-bottom: 44px; scroll-margin-top: 100px; }}
.section-header {{
    display: flex; align-items: center; justify-content: space-between;
    padding: 14px 18px;
    background: var(--white);
    border-radius: 10px 10px 0 0;
    border: 1px solid var(--border);
    border-left: 4px solid var(--tier-bar);
    margin-bottom: 0;
}}
.section-header-left {{ display: flex; align-items: center; gap: 10px; }}
.section-icon {{ font-size: 18px; }}
.section-title {{
    font-family: var(--font-h); font-size: 14px; font-weight: 700;
    color: var(--ink); letter-spacing: 0.2px;
}}
.section-header-right {{ display: flex; align-items: center; gap: 10px; }}
.tier-badge {{
    font-size: 9px; font-weight: 700; letter-spacing: 1.5px;
    text-transform: uppercase; color: white;
    padding: 3px 8px; border-radius: 4px;
}}
.section-count {{ font-size: 11px; color: var(--muted); font-weight: 500; }}

/* ── CARDS GRID ── */
.cards-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(290px, 1fr));
    gap: 10px;
    padding: 10px;
    background: var(--border);
    border-radius: 0 0 10px 10px;
    border: 1px solid var(--border);
    border-top: none;
}}

/* ── CARD ── */
.card {{
    background: var(--white);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 14px 15px;
    display: flex; flex-direction: column; gap: 7px;
    transition: box-shadow 0.15s, transform 0.15s;
}}
.card:hover {{
    box-shadow: 0 4px 16px rgba(0,0,0,0.08);
    transform: translateY(-1px);
}}
.card-priority {{
    border-left: 3px solid var(--priority);
    background: #fffafa;
}}
.card-flagged {{
    border-left: 3px solid var(--compet);
    background: #f7faff;
}}

/* ── CARD INTERNALS ── */
.card-badges {{ display: flex; gap: 5px; flex-wrap: wrap; min-height: 0; }}
.card-badges:empty {{ display: none; }}

.notice-badge, .comp-badge {{
    font-size: 8px; font-weight: 700; letter-spacing: 1px;
    text-transform: uppercase; color: white;
    padding: 2px 6px; border-radius: 3px;
}}
.comp-rival  {{ background: #8b1a1a; }}
.comp-partner {{ background: #1a4a7a; }}

.card-title {{
    font-family: var(--font-h);
    font-size: 13px; font-weight: 600;
    color: var(--ink); text-decoration: none;
    line-height: 1.4; display: block;
}}
.card-title:hover {{ color: var(--priority); }}
.card-meta {{ display: flex; align-items: center; gap: 5px; font-size: 11px; color: var(--muted); }}
.card-source {{ font-weight: 500; }}
.card-dot {{ opacity: 0.4; }}
.card-summary {{ font-size: 11.5px; color: var(--ink-3); line-height: 1.55; font-weight: 300; }}

/* ── EMPTY ── */
.empty-state {{
    grid-column: 1/-1;
    font-size: 13px; color: var(--muted);
    font-style: italic; padding: 20px;
    text-align: center;
}}

/* ── HIDDEN ── */
.card.hidden {{ display: none !important; }}
.digest-section.hidden {{ display: none !important; }}

/* ── RESPONSIVE ── */
@media (max-width: 800px) {{
    .sidebar {{ display: none; }}
    .main {{ margin-left: 0; }}
    .content {{ padding: 16px; }}
    .topbar {{ padding: 14px 16px; flex-wrap: wrap; gap: 12px; }}
    .filter-bar {{ padding: 10px 16px; flex-wrap: wrap; }}
    .cards-grid {{ grid-template-columns: 1fr; }}
}}
</style>
</head>
<body>

<nav class="sidebar">
    <div class="sidebar-brand">
        <div class="brand-eyebrow">BD Intelligence · Esri UK</div>
        <div class="brand-name">Public Safety<br>Digest</div>
        <div class="brand-sub">UK Policing · Fire · Home Office · MoJ</div>
    </div>
    {nav_html}
    <div class="sidebar-footer">
        Updated: {generated}<br>
        Auto-generated · GitHub Actions<br>
        Next update: Monday 07:00
    </div>
</nav>

<div class="main">
    <div class="topbar">
        <div>
            <div class="topbar-title">Weekly BD Intelligence Digest</div>
            <div class="topbar-sub">{week_label} · UK Public Safety &amp; Geospatial</div>
        </div>
        <div class="topbar-stats">
            <div class="stat">
                <div class="stat-num red">{priority_count}</div>
                <div class="stat-lbl">Priority</div>
            </div>
            <div class="stat-divider"></div>
            <div class="stat">
                <div class="stat-num amber">{commercial_count}</div>
                <div class="stat-lbl">Commercial</div>
            </div>
            <div class="stat-divider"></div>
            <div class="stat">
                <div class="stat-num">{total_articles}</div>
                <div class="stat-lbl">Total</div>
            </div>
        </div>
    </div>

    <div class="filter-bar">
        <span class="filter-label">Filter</span>
        <button class="fbtn active" onclick="setFilter('all', this)">All items</button>
        <button class="fbtn" onclick="setFilter('priority', this)">🔴 Priority accounts only</button>
        <button class="fbtn" onclick="setFilter('commercial', this)">🟡 Commercial signals</button>
        <button class="fbtn" onclick="setFilter('competitive', this)">🔵 Competitor intel</button>
    </div>

    <div class="content">
        {sections_html}
    </div>
</div>

<script>
function setFilter(type, btn) {{
    document.querySelectorAll('.fbtn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');

    document.querySelectorAll('.digest-section').forEach(section => {{
        const id = section.id;
        let show = false;

        if (type === 'all') {{
            show = true;
        }} else if (type === 'priority') {{
            show = ['home-office','ministry-of-justice'].includes(id);
        }} else if (type === 'commercial') {{
            show = id === 'procurement';
        }} else if (type === 'competitive') {{
            show = id === 'competitor-intel';
        }}
        section.classList.toggle('hidden', !show);
    }});
}}

// Active nav on scroll
const sections = document.querySelectorAll('.digest-section');
const navLinks  = document.querySelectorAll('.nav-item');
const observer  = new IntersectionObserver(entries => {{
    entries.forEach(e => {{
        if (e.isIntersecting) {{
            navLinks.forEach(l => l.classList.remove('active'));
            const a = document.querySelector(`.nav-item[href="#${{e.target.id}}"]`);
            if (a) a.classList.add('active');
        }}
    }});
}}, {{ rootMargin: '-15% 0px -75% 0px' }});
sections.forEach(s => observer.observe(s));
</script>
</body>
</html>"""

# ─── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    print(f"\n🔍 BD Digest — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    sections_data = []
    for section in SECTIONS:
        print(f"\n📡 {section['label']}")
        articles = fetch_section(section)
        sections_data.append({"section": section, "articles": articles})
        print(f"   → {len(articles)} articles")

    total = sum(len(s["articles"]) for s in sections_data)
    print(f"\n📰 Total: {total} articles across {len(SECTIONS)} sections")

    print("\n🔨 Building HTML page...")
    html = build_html(sections_data)

    os.makedirs("docs", exist_ok=True)
    with open("docs/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("✅ Page written → docs/index.html")

if __name__ == "__main__":
    main()
