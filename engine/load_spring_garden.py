import sys
sys.path.insert(0, r"c:\Users\david\Projects\PersonaLock")
from modules.task_manager import TaskManager

tm = TaskManager()

# Create the project
project_id = tm.create_project(
    name="Spring Garden 2026",
    description="Half-acre no-till market garden on post-soybean ground. Sheet mulch method: silage tarps -> cardboard -> compost cap -> direct sow. Revenue target: $8,500-18,600 season. Standing buyer at farm stand.",
    start_date="2026-03-12",
    target_end_date="2026-06-30"
)
print(f"Project created: {project_id}")

# ═══════════════════════════════════════════════════════════
# WEEK 1: March 12-18 — Tarp & Prep
# ═══════════════════════════════════════════════════════════

tasks_week1 = [
    {
        "content": "Mow target half-acre of post-soybean ground flat with riding mower",
        "category": "soil_prep",
        "priority": "critical",
        "due_date": "2026-03-13",
        "notes": "Mow as short as possible. Don't remove clippings — they become brown material under the tarp."
    },
    {
        "content": "Deploy silage tarps black-side-up on mowed area",
        "category": "soil_prep",
        "priority": "critical",
        "due_date": "2026-03-14",
        "depends_on": "mow",
        "notes": "Overlap edges 6-12 inches. Weight every 4-6 feet with cinder blocks, logs, old tires, buckets of sand. Wind will get under loose tarps."
    },
    {
        "content": "Order seeds online — mesclun mix, arugula, spinach, Sungold tomato, Black Cherry tomato, Genovese basil, parsley, cilantro, dill",
        "category": "seeds",
        "priority": "critical",
        "due_date": "2026-03-14",
        "notes": "Johnny's Selected Seeds (johnnyseeds.com) for pro grade, or Amazon for fast shipping. Ship time 5-7 days. Budget: $50-75."
    },
    {
        "content": "Start collecting cardboard from Home Depot, Lowe's, appliance stores, grocery stores",
        "category": "infrastructure",
        "priority": "high",
        "due_date": "2026-03-18",
        "notes": "Ask for cardboard recycling. Need HUNDREDS of flattened boxes. Avoid wax-coated. Start a dry stack under cover."
    },
    {
        "content": "Call 2-3 mushroom soil / bulk compost suppliers for delivery quotes",
        "category": "purchasing",
        "priority": "high",
        "due_date": "2026-03-15",
        "notes": "Chester County PA and Kennett Square for spent mushroom compost. Target $20-35/cu yd delivered. Get quotes for 30-60 cubic yards. Schedule delivery for early April."
    },
    {
        "content": "Assemble pallet compost bin — 12ft pallets for long sides, 4ft for ends, divide in half",
        "category": "compost",
        "priority": "high",
        "due_date": "2026-03-18",
        "notes": "Removable side for Magna-trac access. Start first pile with woodland browns and Similac slurry."
    },
    {
        "content": "Start first compost pile — layer woodland browns, manure, thin Similac layers",
        "category": "compost",
        "priority": "medium",
        "due_date": "2026-03-18",
        "depends_on": "pallet_bin",
        "notes": "Similac: 1 inch MAX per layer, dissolve in water first. Always cover with 4+ inches of browns. Thin layers only — thick dumps go anaerobic."
    },
    {
        "content": "Start cherry tomato and basil seeds indoors",
        "category": "seeds",
        "priority": "high",
        "due_date": "2026-03-15",
        "notes": "Sungold, Black Cherry, Yellow Pear tomatoes. Genovese, Thai, Purple basil. Need cell trays or recycled containers, seed starting mix, sunny south-facing window or shop light 2-3 inches above trays."
    },
    {
        "content": "Buy indoor seed starting supplies if needed — cell trays, seed starting mix, shop light",
        "category": "purchasing",
        "priority": "medium",
        "due_date": "2026-03-14",
        "notes": "Budget: $30-50 total. Reusable for years. Only needed if you don't already have them."
    }
]

for t in tasks_week1:
    tid = tm.add_project_task(
        project_name="Spring Garden 2026",
        content=t["content"],
        week_group="Week 1: Mar 12-18 — Tarp & Prep",
        category=t.get("category"),
        priority=t.get("priority", "medium"),
        due_date=t.get("due_date"),
        depends_on=t.get("depends_on"),
        notes=t.get("notes")
    )
    print(f"  Week 1 task added: {t['content'][:60]}...")

# ═══════════════════════════════════════════════════════════
# WEEKS 2-3: March 19 - April 1 — Tarps Cook, Prep Continues
# ═══════════════════════════════════════════════════════════

tasks_weeks23 = [
    {
        "content": "Continue cardboard collection — build stockpile of hundreds of flattened boxes",
        "category": "infrastructure",
        "priority": "medium",
        "due_date": "2026-03-28",
        "notes": "Keep dry under cover. Ongoing effort through Weeks 2-3."
    },
    {
        "content": "Check tarps weekly — re-secure any edges lifted by wind",
        "category": "soil_prep",
        "priority": "medium",
        "due_date": "2026-03-25",
        "notes": "Walk the tarp edges. Replace blown weights. Tarps need 3-4 weeks total on the ground."
    },
    {
        "content": "Turn compost pile with Magna-trac",
        "category": "compost",
        "priority": "medium",
        "due_date": "2026-03-26",
        "notes": "Turn every 1-2 weeks. Add thin Similac slurry layers and woodland browns. March/April temps will get pile cooking fast."
    },
    {
        "content": "Confirm compost/mushroom soil delivery scheduled for early April",
        "category": "purchasing",
        "priority": "high",
        "due_date": "2026-03-22",
        "notes": "Lock in the delivery date. Need 30-60 cubic yards. Mushroom soil from Kennett Square area is best option. Budget: $600-1,500."
    },
    {
        "content": "Check indoor seedlings — tomatoes and basil should be sprouting",
        "category": "seeds",
        "priority": "medium",
        "due_date": "2026-03-25",
        "notes": "Keep light 2-3 inches above seedlings. Water from bottom. Thin to strongest seedling per cell if needed."
    },
    {
        "content": "Research drip tape / irrigation supplies and pricing",
        "category": "purchasing",
        "priority": "low",
        "due_date": "2026-03-28",
        "notes": "Budget: $50-150 for drip tape and irrigation. Not needed until planting but good to have sourced."
    },
    {
        "content": "Scout neighbor's horse manure pile — check if aged 6+ months, dark and crumbly",
        "category": "compost",
        "priority": "low",
        "due_date": "2026-03-22",
        "notes": "If ready (dark, crumbly, not steaming), this is free compost. Use Magna-trac to load and haul."
    }
]

for t in tasks_weeks23:
    tid = tm.add_project_task(
        project_name="Spring Garden 2026",
        content=t["content"],
        week_group="Weeks 2-3: Mar 19 - Apr 1 — Tarps Cook",
        category=t.get("category"),
        priority=t.get("priority", "medium"),
        due_date=t.get("due_date"),
        depends_on=t.get("depends_on"),
        notes=t.get("notes")
    )
    print(f"  Weeks 2-3 task added: {t['content'][:60]}...")

# ═══════════════════════════════════════════════════════════
# WEEK 4: April 2-8 — Pull Tarps, Sheet Mulch, First Planting
# ═══════════════════════════════════════════════════════════

tasks_week4 = [
    {
        "content": "Pull tarps off first greens beds section",
        "category": "soil_prep",
        "priority": "critical",
        "due_date": "2026-04-04",
        "notes": "Should see dead vegetation and soft, worm-worked surface. This is your stale seedbed."
    },
    {
        "content": "Lay overlapping cardboard on dead vegetation where tarps were removed",
        "category": "soil_prep",
        "priority": "critical",
        "due_date": "2026-04-05",
        "depends_on": "pull_tarps",
        "notes": "Overlap edges generously. Wet cardboard thoroughly as you lay it."
    },
    {
        "content": "Receive and spread compost/mushroom soil delivery — cap cardboard beds with 4-6 inches",
        "category": "compost",
        "priority": "critical",
        "due_date": "2026-04-06",
        "depends_on": "cardboard",
        "notes": "This is your planting medium. Spread evenly 4-6 inches deep on top of wet cardboard."
    },
    {
        "content": "Direct sow salad greens and herbs into compost cap — mesclun, arugula, spinach, parsley, cilantro, dill",
        "category": "seeds",
        "priority": "critical",
        "due_date": "2026-04-08",
        "depends_on": "compost_cap",
        "notes": "No tilling. No digging. Sow right into the compost surface. These handle frost down to mid-20s."
    },
    {
        "content": "Set up drip irrigation or soaker hoses on newly planted beds",
        "category": "infrastructure",
        "priority": "high",
        "due_date": "2026-04-08",
        "notes": "Greens need consistent moisture. Drip tape is most efficient."
    },
    {
        "content": "Move remaining tarps to next bed section (tomato/pepper area) for continued occultation",
        "category": "soil_prep",
        "priority": "high",
        "due_date": "2026-04-06",
        "notes": "Tomatoes don't go out until mid-to-late May. Keep tarps cooking the next section."
    }
]

for t in tasks_week4:
    tid = tm.add_project_task(
        project_name="Spring Garden 2026",
        content=t["content"],
        week_group="Week 4: Apr 2-8 — Sheet Mulch & First Planting",
        category=t.get("category"),
        priority=t.get("priority", "medium"),
        due_date=t.get("due_date"),
        depends_on=t.get("depends_on"),
        notes=t.get("notes")
    )
    print(f"  Week 4 task added: {t['content'][:60]}...")

# ═══════════════════════════════════════════════════════════
# WEEKS 5-8: April 9 - May 6 — Growing Season Ramp
# ═══════════════════════════════════════════════════════════

tasks_weeks58 = [
    {
        "content": "Monitor greens beds — first cut expected 4 weeks after sowing (early May)",
        "category": "seeds",
        "priority": "medium",
        "due_date": "2026-04-22",
        "notes": "Watch for germination. Keep beds moist. Greens can be cut 3-5 times from same planting."
    },
    {
        "content": "Harden off tomato and basil seedlings — move outdoors during day, inside at night",
        "category": "seeds",
        "priority": "high",
        "due_date": "2026-04-25",
        "notes": "Start hardening 1-2 weeks before transplant date. Gradually increase outdoor time."
    },
    {
        "content": "Pull tarps off tomato/pepper bed section, lay cardboard, cap with compost",
        "category": "soil_prep",
        "priority": "high",
        "due_date": "2026-05-01",
        "notes": "Same sheet mulch process as greens beds. Tarps should have been on this section since early April."
    },
    {
        "content": "Buy pepper transplants — bells, banana, Italian frying",
        "category": "purchasing",
        "priority": "high",
        "due_date": "2026-05-06",
        "notes": "You missed the indoor start window for peppers (needed 8-10 weeks from January). Buy transplants instead. Budget: $60-150."
    },
    {
        "content": "Transplant tomato seedlings and pepper transplants outdoors after last frost",
        "category": "seeds",
        "priority": "critical",
        "due_date": "2026-05-15",
        "notes": "Zone 7a last frost averages mid-April, but wait until mid-to-late May for warm season crops to be safe. Nighttime temps should be consistently above 50F."
    },
    {
        "content": "First salad greens harvest — bring to farm stand buyer",
        "category": "seeds",
        "priority": "high",
        "due_date": "2026-05-08",
        "notes": "First revenue! Salad greens at $8-12/lb. Cut-and-come-again method — harvest outer leaves, plant keeps producing."
    },
    {
        "content": "Turn compost pile again — add more Similac slurry and browns",
        "category": "compost",
        "priority": "low",
        "due_date": "2026-04-15",
        "notes": "Regular turning every 1-2 weeks. This pile won't be ready until fall/next spring but building it now is essential."
    },
    {
        "content": "Succession sow more greens — plant second batch for continuous harvest",
        "category": "seeds",
        "priority": "medium",
        "due_date": "2026-04-25",
        "notes": "Stagger plantings every 2-3 weeks for continuous supply through the season."
    }
]

for t in tasks_weeks58:
    tid = tm.add_project_task(
        project_name="Spring Garden 2026",
        content=t["content"],
        week_group="Weeks 5-8: Apr 9 - May 6 — Growing Season Ramp",
        category=t.get("category"),
        priority=t.get("priority", "medium"),
        due_date=t.get("due_date"),
        depends_on=t.get("depends_on"),
        notes=t.get("notes")
    )
    print(f"  Weeks 5-8 task added: {t['content'][:60]}...")

# ═══════════════════════════════════════════════════════════
# ONGOING / BUDGET TRACKING TASKS
# ═══════════════════════════════════════════════════════════

tasks_ongoing = [
    {
        "content": "Track spending against budget — low end target $790, high end $2,195",
        "category": "purchasing",
        "priority": "medium",
        "due_date": "2026-04-30",
        "notes": "Minimum viable: $650 (seeds $50 + free cardboard + cheapest compost $600). Scale up as revenue from first greens harvests comes in."
    },
    {
        "content": "Weekly compost pile maintenance — turn with Magna-trac, add materials, monitor temp",
        "category": "compost",
        "priority": "low",
        "due_date": "2026-06-30",
        "notes": "Ongoing through the season. A few cans of Similac per turning session. Don't rush through all the Similac — pace over March through November."
    }
]

for t in tasks_ongoing:
    tid = tm.add_project_task(
        project_name="Spring Garden 2026",
        content=t["content"],
        week_group="Ongoing",
        category=t.get("category"),
        priority=t.get("priority", "medium"),
        due_date=t.get("due_date"),
        depends_on=t.get("depends_on"),
        notes=t.get("notes")
    )
    print(f"  Ongoing task added: {t['content'][:60]}...")

# ═══════════════════════════════════════════════════════════
# VERIFICATION
# ═══════════════════════════════════════════════════════════

print("\n" + "="*60)
print("SPRING GARDEN 2026 — LOAD VERIFICATION")
print("="*60)

progress = tm.get_project_progress("Spring Garden 2026")
print(f"\nTotal tasks loaded: {progress['total_tasks']}")
print(f"Pending: {progress['pending']}")
print(f"Overdue: {progress['overdue']}")
print(f"Completed: {progress['completed']}")

print(f"\nBy week:")
for week, counts in progress.get('by_week', {}).items():
    print(f"  {week}: {counts['total']} tasks ({counts['done']} done, {counts['pending']} pending)")

print(f"\nBy category:")
for cat, counts in progress.get('by_category', {}).items():
    print(f"  {cat}: {counts['total']} tasks")

overdue = tm.get_overdue_tasks("Spring Garden 2026")
print(f"\nOverdue right now: {len(overdue)}")
for t in overdue:
    print(f"  ⚠️  {t.get('content', t.get('name', 'unknown'))[:70]} (due: {t.get('due_date', 'no date')})")

upcoming = tm.get_upcoming_tasks("Spring Garden 2026", days=7)
print(f"\nDue this week: {len(upcoming)}")
for t in upcoming:
    print(f"  → {t.get('content', t.get('name', 'unknown'))[:70]} (due: {t.get('due_date', 'no date')})")

print("\n✅ Spring Garden 2026 loaded successfully.")
print("Ada now knows about your tarps, your seeds, and your deadlines.")
