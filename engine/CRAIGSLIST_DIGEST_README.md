# 🛒 Craigslist South Jersey — Free Stuff Morning Digest

Fetches Craigslist RSS feeds every morning and filters for **construction, trade, homestead, and farm** items available **for free** in South Jersey.

---

## Files

| File | Purpose |
|---|---|
| `craigslist_digest.py` | Main Python script — fetches feeds, filters, prints digest |
| `run_craigslist_digest.bat` | Windows batch wrapper — run manually or via Task Scheduler |
| `craigslist_task_scheduler.xml` | Task Scheduler import file — sets up daily 7AM run |
| `data/craigslist_seen.json` | Auto-created cache — tracks seen listings so you only see NEW ones each day |
| `logs/craigslist_YYYY-MM-DD.txt` | Auto-created daily log files |

---

## Quick Start

### Run manually (Windows)
Double-click `run_craigslist_digest.bat`  
Or from PowerShell/CMD:
```cmd
cd C:\Users\david\projects\PersonaLock
python craigslist_digest.py
```

### Options
```
python craigslist_digest.py              # New items only (uses cache)
python craigslist_digest.py --all        # Show ALL free items, not just priority
python craigslist_digest.py --no-cache   # Ignore cache, show everything
```

---

## Schedule Daily at 7 AM (Windows Task Scheduler)

1. Open **Task Scheduler** (search in Start menu)
2. Click **Import Task...** in the right panel
3. Browse to: `C:\Users\david\projects\PersonaLock\craigslist_task_scheduler.xml`
4. Click OK — task is created and will run every day at 7:00 AM
5. Results save to `logs\craigslist_YYYY-MM-DD.txt`

---

## What Gets Flagged as PRIORITY 🏆

Any listing whose title or description contains keywords related to:

- **Lumber / Wood**: lumber, plywood, 2x4, pallet wood, hardwood, firewood, timber...
- **Building Materials**: concrete, brick, block, pavers, tile, gravel, fill dirt...
- **Tools & Equipment**: drill, saw, generator, compressor, ladder, scaffolding, welder, tiller, chainsaw, tractor...
- **Plumbing / Electrical**: pipe, PVC, copper, conduit, wire, panel, breaker...
- **Doors / Windows / Structural**: door, window, siding, roofing, shingles, fence, framing...
- **Farm / Garden / Livestock**: chicken, goat, hay, coop, greenhouse, raised bed, cattle panel...
- **Metal / Scrap**: steel, iron, rebar, angle iron, sheet metal, scrap...
- **Containers / Storage**: shed, tank, barrel, drum, IBC tote, pallet rack...

---

## Feeds Monitored

| Category | Feed |
|---|---|
| 🆓 Free Stuff (All) | `/search/zip` |
| 🌱 Farm & Garden | `/search/gra?free=1` |
| 🔧 Tools | `/search/tla?free=1` |
| 🪵 Materials / Lumber | `/search/maa?free=1` |
| 🛋️ Furniture | `/search/fua?free=1` |
| ⚙️ General For Sale | `/search/foa?free=1` |
| 🏠 Household Items | `/search/hsa?free=1` |
| 🏋️ Sporting Goods | `/search/sga?free=1` |
| 🚜 Trailers | `/search/tra?free=1` |
| 🔌 Appliances | `/search/ppa?free=1` |

---

## ⚠️ Important Note

Craigslist **blocks requests from server/cloud IPs** (datacenter blocks).  
This script must be run from your **home Windows machine** — it will work perfectly there.
Running it from WSL connected through your home internet also works.

---

## Integrate with Ada's Daily Briefing

Add this to `daily_briefing.py`:
```python
from craigslist_digest import run_craigslist_digest

# At the end of run_daily_briefing():
run_craigslist_digest(show_all=False, new_only=True)
```
