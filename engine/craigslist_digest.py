# -*- coding: utf-8 -*-
"""
Craigslist South Jersey — Free Stuff Morning Digest
Fetches RSS feeds for free items in construction/trade/homestead categories
and prints a formatted daily briefing. Integrates with Ada's daily_briefing.py.
"""

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import xml.etree.ElementTree as ET
import urllib.request
import urllib.error
from datetime import datetime, timezone
import re
import json
import os

# ─────────────────────────────────────────────
# RSS FEEDS — South Jersey Craigslist Free Items
# ─────────────────────────────────────────────
FEEDS = [
    {
        "name": "🆓 Free Stuff (All)",
        "url": "https://southjersey.craigslist.org/search/zip?format=rss&sort=date",
        "all_free": True,
    },
    {
        "name": "🌱 Farm & Garden (Free)",
        "url": "https://southjersey.craigslist.org/search/gra?free=1&format=rss&sort=date",
    },
    {
        "name": "🔧 Tools (Free)",
        "url": "https://southjersey.craigslist.org/search/tla?free=1&format=rss&sort=date",
    },
    {
        "name": "🪵 Materials / Lumber (Free)",
        "url": "https://southjersey.craigslist.org/search/maa?free=1&format=rss&sort=date",
    },
    {
        "name": "🛋️ Furniture (Free)",
        "url": "https://southjersey.craigslist.org/search/fua?free=1&format=rss&sort=date",
    },
    {
        "name": "⚙️ General For Sale (Free)",
        "url": "https://southjersey.craigslist.org/search/foa?free=1&format=rss&sort=date",
    },
    {
        "name": "🏠 Household Items (Free)",
        "url": "https://southjersey.craigslist.org/search/hsa?free=1&format=rss&sort=date",
    },
    {
        "name": "🏋️ Sporting Goods (Free)",
        "url": "https://southjersey.craigslist.org/search/sga?free=1&format=rss&sort=date",
    },
    {
        "name": "🚜 Trailers (Free)",
        "url": "https://southjersey.craigslist.org/search/tra?free=1&format=rss&sort=date",
    },
    {
        "name": "🔌 Appliances (Free)",
        "url": "https://southjersey.craigslist.org/search/ppa?free=1&format=rss&sort=date",
    },
]

# ─────────────────────────────────────────────
# KEYWORD FILTERS
# Listings matching ANY of these keywords are
# flagged as HIGH PRIORITY (construction/trade)
# ─────────────────────────────────────────────
PRIORITY_KEYWORDS = [
    # Lumber / Building materials
    "lumber", "wood", "plywood", "2x4", "2x6", "4x4", "beam", "board",
    "pallet", "pallet wood", "decking", "plank", "hardwood", "firewood",
    "treated", "pressure treated", "timber", "log", "logs",
    # Concrete / Masonry
    "concrete", "block", "cinder block", "brick", "stone", "pavers",
    "tile", "gravel", "mulch", "dirt", "topsoil", "fill",
    # Tools & Equipment
    "tool", "tools", "drill", "saw", "miter", "table saw", "router",
    "generator", "compressor", "air compressor", "ladder", "scaffolding",
    "welder", "welding", "grinder", "sander", "nail gun", "nailer",
    "pressure washer", "power washer", "tiller", "chainsaw", "trimmer",
    "lawn mower", "mower", "tractor", "excavator", "skid", "backhoe",
    "pump", "hoist", "jack", "come along", "winch",
    # Plumbing / Electrical
    "pipe", "pipes", "pvc", "copper", "conduit", "wire", "wiring",
    "panel", "breaker", "electrical", "plumbing", "fitting", "fittings",
    # Doors / Windows / Structural
    "door", "doors", "window", "windows", "siding", "roofing", "shingles",
    "gutter", "fence", "fencing", "gate", "post", "railing", "framing",
    # Farm / Garden / Livestock
    "livestock", "chicken", "chickens", "goat", "goats", "sheep", "pig",
    "horse", "coop", "trough", "feeder", "hay", "straw", "feed",
    "compost", "garden bed", "raised bed", "greenhouse", "irrigation",
    "fencing", "wire mesh", "cattle panel", "t-post",
    # Containers / Storage
    "shed", "trailer", "container", "tank", "barrel", "drum", "ibc",
    "tote", "bin", "pallet rack", "shelving",
    # Metal / Scrap
    "metal", "steel", "iron", "aluminum", "pipe", "angle iron", "channel",
    "i-beam", "rebar", "scrap", "sheet metal",
]

PRIORITY_KEYWORDS_LOWER = [k.lower() for k in PRIORITY_KEYWORDS]

# ─────────────────────────────────────────────
# SEEN-ITEMS CACHE (avoid re-showing old posts)
# ─────────────────────────────────────────────
CACHE_FILE = os.path.join(os.path.dirname(__file__), "data", "craigslist_seen.json")


def load_seen() -> set:
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception:
            pass
    return set()


def save_seen(seen: set):
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    # Only keep the last 2000 IDs to prevent unbounded growth
    ids = list(seen)[-2000:]
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(ids, f)


# ─────────────────────────────────────────────
# FETCH & PARSE
# ─────────────────────────────────────────────
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

def fetch_feed(url: str) -> list[dict]:
    """Fetch and parse a Craigslist RSS feed. Returns list of item dicts."""
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = resp.read()
    except urllib.error.HTTPError as e:
        print(f"    ⚠️  HTTP {e.code} fetching feed")
        return []
    except Exception as e:
        print(f"    ⚠️  Error: {e}")
        return []

    try:
        root = ET.fromstring(raw)
    except ET.ParseError as e:
        print(f"    ⚠️  XML parse error: {e}")
        return []

    ns = {"cl": "http://www.w3.org/2005/Atom"}
    items = []

    # Try RSS 2.0 format
    for item in root.iter("item"):
        title_el = item.find("title")
        link_el = item.find("link")
        desc_el = item.find("description")
        date_el = item.find("pubDate")
        guid_el = item.find("guid")

        title = title_el.text.strip() if title_el is not None and title_el.text else ""
        link = link_el.text.strip() if link_el is not None and link_el.text else ""
        desc = desc_el.text.strip() if desc_el is not None and desc_el.text else ""
        pub_date = date_el.text.strip() if date_el is not None and date_el.text else ""
        guid = guid_el.text.strip() if guid_el is not None and guid_el.text else link

        # Strip HTML from description
        desc_clean = re.sub(r"<[^>]+>", " ", desc).strip()

        items.append({
            "title": title,
            "link": link,
            "description": desc_clean,
            "pub_date": pub_date,
            "guid": guid,
        })

    # Try Atom format if no RSS items found
    if not items:
        for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
            title_el = entry.find("{http://www.w3.org/2005/Atom}title")
            link_el = entry.find("{http://www.w3.org/2005/Atom}link")
            summary_el = entry.find("{http://www.w3.org/2005/Atom}summary")
            updated_el = entry.find("{http://www.w3.org/2005/Atom}updated")
            id_el = entry.find("{http://www.w3.org/2005/Atom}id")

            title = title_el.text.strip() if title_el is not None and title_el.text else ""
            link = link_el.get("href", "") if link_el is not None else ""
            desc_raw = summary_el.text or "" if summary_el is not None else ""
            desc_clean = re.sub(r"<[^>]+>", " ", desc_raw).strip()
            pub_date = updated_el.text.strip() if updated_el is not None and updated_el.text else ""
            guid = id_el.text.strip() if id_el is not None and id_el.text else link

            items.append({
                "title": title,
                "link": link,
                "description": desc_clean,
                "pub_date": pub_date,
                "guid": guid,
            })

    return items


def is_priority(item: dict) -> bool:
    """Return True if title or description matches a priority keyword."""
    text = (item["title"] + " " + item["description"]).lower()
    return any(kw in text for kw in PRIORITY_KEYWORDS_LOWER)


# ─────────────────────────────────────────────
# MAIN DIGEST
# ─────────────────────────────────────────────
def run_craigslist_digest(show_all: bool = False, new_only: bool = True):
    """
    Fetch all feeds and print a morning digest.

    Args:
        show_all:  If True, show ALL items (not just priority matches).
        new_only:  If True, skip items already seen in a previous run.
    """
    today = datetime.now().strftime("%A, %B %d, %Y")
    print()
    print("=" * 60)
    print(f"  🛒 CRAIGSLIST FREE STUFF DIGEST — {today}")
    print("  📍 South Jersey")
    print("=" * 60)

    seen = load_seen() if new_only else set()
    new_seen = set(seen)

    total_new = 0
    priority_items = []
    regular_items = []

    for feed in FEEDS:
        print(f"\n⏳ Fetching {feed['name']} ...")
        items = fetch_feed(feed["url"])

        feed_new = 0
        for item in items:
            guid = item["guid"]
            if new_only and guid in seen:
                continue
            new_seen.add(guid)
            feed_new += 1
            total_new += 1

            item["feed_name"] = feed["name"]

            if is_priority(item):
                priority_items.append(item)
            else:
                regular_items.append(item)

        status = f"{feed_new} new" if new_only else f"{len(items)} items"
        print(f"   ✅ {status}")

    # ── PRIORITY SECTION ─────────────────────
    print()
    print("=" * 60)
    print(f"  🏆 HIGH PRIORITY — Construction/Trade/Homestead")
    print(f"  ({len(priority_items)} matches)")
    print("=" * 60)

    if priority_items:
        for item in priority_items:
            print(f"\n  📌 {item['title']}")
            if item["description"]:
                # Trim long descriptions
                desc = item["description"][:200]
                if len(item["description"]) > 200:
                    desc += "..."
                print(f"     {desc}")
            print(f"     🔗 {item['link']}")
            print(f"     📅 {item.get('pub_date', '')[:25]}  [{item['feed_name']}]")
    else:
        print("\n  Nothing new in priority categories today.")

    # ── GENERAL SECTION ──────────────────────
    if show_all and regular_items:
        print()
        print("=" * 60)
        print(f"  📦 OTHER FREE ITEMS ({len(regular_items)} items)")
        print("=" * 60)
        for item in regular_items[:50]:  # cap at 50 to avoid wall of text
            print(f"\n  • {item['title']}")
            print(f"    🔗 {item['link']}")
            print(f"    [{item['feed_name']}]")
    elif not show_all and regular_items:
        print()
        print(f"  📦 {len(regular_items)} other free items (run with --all to see them)")

    # ── SUMMARY ──────────────────────────────
    print()
    print("=" * 60)
    print(f"  📊 SUMMARY: {total_new} new items total | "
          f"{len(priority_items)} priority matches")
    print("=" * 60)
    print()

    # Save seen IDs for next run
    if new_only:
        save_seen(new_seen)


# ─────────────────────────────────────────────
# CLI ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Craigslist South Jersey Free Stuff Morning Digest"
    )
    parser.add_argument(
        "--all", action="store_true",
        help="Show all free items, not just priority matches"
    )
    parser.add_argument(
        "--no-cache", action="store_true",
        help="Ignore seen-items cache and show everything"
    )
    args = parser.parse_args()

    run_craigslist_digest(show_all=args.all, new_only=not args.no_cache)
