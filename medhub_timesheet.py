"""
MedHub Timesheet Auto-Logger
============================
Automatically logs 08:00–18:00 Mon–Fri on SingHealth MedHub.

Requirements:
    pip install playwright
    playwright install chromium

Usage:
    # Step 1: open Chrome with remote debugging (quit Chrome first if open)
    /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-medhub &

    # Step 2: log in to MedHub in that Chrome window

    # Step 3: run this script (fills the current week)
    python medhub_timesheet.py

    # Fill a specific week (any date within that week)
    python medhub_timesheet.py --date 2026-05-19

    # Dry run — show what would be selected, no changes
    python medhub_timesheet.py --dry-run
"""

import argparse
from datetime import date, timedelta
from playwright.sync_api import sync_playwright

# ── Configuration ──────────────────────────────────────────────────────────────
BASE_URL   = "https://singhealth.medhub.com"
START_TIME = "8:00am"
END_TIME   = "6:00pm"
CDP_URL    = "http://localhost:9222"
# ──────────────────────────────────────────────────────────────────────────────


def get_week_monday(reference: date) -> date:
    return reference - timedelta(days=reference.weekday())


def format_date(d: date) -> str:
    return d.strftime("%m/%d/%Y")


def run(week_start: date, dry_run: bool = False):
    monday = get_week_monday(week_start)
    sunday = monday - timedelta(days=1)
    weekdays = [monday + timedelta(days=i) for i in range(5)]  # Mon–Fri

    # Pull-down interface URL (reliable dropdown selects vs graphical drag)
    pulldown_url = (
        f"{BASE_URL}/u/r/schedule_timesheet.mh"
        f"?startDate={format_date(sunday)}&tab=1&action=method&method=1"
    )

    print(f"\n{'[DRY RUN] ' if dry_run else ''}Week of {monday.strftime('%d %b %Y')} (Mon–Fri)")
    print(f"  Days: {', '.join(d.strftime('%a %d %b') for d in weekdays)}")
    print(f"  Hours: {START_TIME} – {END_TIME}\n")

    with sync_playwright() as p:
        # ── Connect to user's Chrome ───────────────────────────────────────
        print(f"Connecting to Chrome on {CDP_URL}...")
        try:
            browser = p.chromium.connect_over_cdp(CDP_URL)
        except Exception as e:
            print(f"  ✗ Could not connect: {e}")
            print("  Start Chrome with: /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome "
                  "--remote-debugging-port=9222 --user-data-dir=/tmp/chrome-medhub &")
            return

        context = browser.contexts[0]

        # Find any MedHub tab to reuse its session
        page = None
        for pg in context.pages:
            if "singhealth.medhub.com" in pg.url:
                page = pg
                break

        if page is None:
            print("  ✗ No MedHub tab found — please open MedHub in Chrome first.")
            browser.close()
            return

        # Navigate to pull-down interface for the target week
        print(f"  Navigating to pull-down timesheet...")
        page.goto(pulldown_url)
        page.wait_for_load_state("networkidle")
        print(f"  ✓ Ready: {page.url}\n")

        # ── Fill Mon–Fri dropdowns ─────────────────────────────────────────
        # MedHub week: day1=Sun, day2=Mon, ..., day6=Fri, day7=Sat
        # Python weekday: Mon=0, Tue=1, ..., Fri=4
        # Mapping: medhub_day = python_weekday + 2
        for day in weekdays:
            day_num = day.weekday() + 2  # Mon→2, Tue→3, Wed→4, Thu→5, Fri→6
            in_sel  = f'select[name="day{day_num}_1_in"]'
            out_sel = f'select[name="day{day_num}_1_out"]'

            print(f"  {day.strftime('%A %d %b')}...", end=" ", flush=True)

            if page.locator(in_sel).count() == 0:
                print(f"✗  selector not found: {in_sel}")
                continue

            if dry_run:
                current_in  = page.locator(in_sel).input_value()
                current_out = page.locator(out_sel).input_value()
                print(f"✓  would set {in_sel}={START_TIME!r}, {out_sel}={END_TIME!r}  (currently: {current_in!r}, {current_out!r})")
                continue

            try:
                page.select_option(in_sel,  START_TIME)
                page.select_option(out_sel, END_TIME)
                print("✓")
            except Exception as e:
                print(f"✗  {e}")

        if dry_run:
            print("\n[Dry run complete — no changes made]")
            browser.close()
            return

        # ── Submit ────────────────────────────────────────────────────────
        print()
        submit = page.locator('a[aria-label="Submit Work Hours"]')
        if submit.count() > 0:
            submit.click()
            page.wait_for_load_state("networkidle")
            print("  ✓ Work hours submitted")
        else:
            print("  ⚠ Submit button not found — please submit manually.")

        browser.close()
        print("Done.")


# ── CLI entry point ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Auto-log MedHub timesheets")
    parser.add_argument(
        "--date",
        default=date.today().isoformat(),
        help="Any date within the target week (YYYY-MM-DD). Defaults to today.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be selected without submitting.",
    )
    args = parser.parse_args()

    print("MedHub Timesheet Auto-Logger")
    print("=" * 35)
    run(date.fromisoformat(args.date), dry_run=args.dry_run)
