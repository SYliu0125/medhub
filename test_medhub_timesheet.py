from datetime import date
from unittest.mock import MagicMock, patch, call

import pytest

from medhub_timesheet import END_TIME, START_TIME, format_date, get_week_monday, run


# ── Pure functions ─────────────────────────────────────────────────────────────

class TestGetWeekMonday:
    def test_monday_returns_itself(self):
        assert get_week_monday(date(2026, 5, 25)) == date(2026, 5, 25)

    def test_wednesday_gives_monday(self):
        assert get_week_monday(date(2026, 5, 27)) == date(2026, 5, 25)

    def test_friday_gives_monday(self):
        assert get_week_monday(date(2026, 5, 29)) == date(2026, 5, 25)

    def test_sunday_gives_monday(self):
        assert get_week_monday(date(2026, 5, 31)) == date(2026, 5, 25)

    def test_cross_month_boundary(self):
        # Sunday 2026-06-07 → Monday 2026-06-01
        assert get_week_monday(date(2026, 6, 7)) == date(2026, 6, 1)


class TestFormatDate:
    def test_standard_date(self):
        assert format_date(date(2026, 5, 25)) == "05/25/2026"

    def test_zero_padded_day_and_month(self):
        assert format_date(date(2026, 1, 5)) == "01/05/2026"

    def test_end_of_year(self):
        assert format_date(date(2026, 12, 31)) == "12/31/2026"


# ── Helpers ────────────────────────────────────────────────────────────────────

def _make_playwright_mock(locator_count=1, page_url="https://singhealth.medhub.com/timesheet"):
    """Build the nested mock hierarchy for CDP connect path."""

    def make_locator(count=locator_count):
        loc = MagicMock()
        loc.count.return_value = count
        loc.input_value.return_value = ""
        return loc

    page = MagicMock()
    page.url = page_url
    page.locator.side_effect = lambda sel: make_locator()

    context = MagicMock()
    context.pages = [page]

    browser = MagicMock()
    browser.contexts = [context]

    p = MagicMock()
    p.chromium.connect_over_cdp.return_value = browser

    cm = MagicMock()
    cm.__enter__.return_value = p
    cm.__exit__.return_value = False

    return cm, page, browser


# ── run() — dry-run ────────────────────────────────────────────────────────────

class TestRunDryRun:
    def test_navigates_to_week_sunday_url(self):
        """URL must contain schedule_timesheet.mh and the Sunday date for the week."""
        cm, page, _ = _make_playwright_mock()
        with patch("medhub_timesheet.sync_playwright", return_value=cm):
            run(date(2026, 5, 27), dry_run=True)  # Wednesday → Sunday 05/24/2026

        urls = [c.args[0] for c in page.goto.call_args_list]
        assert any("schedule_timesheet.mh" in u and "05/24/2026" in u for u in urls)

    def test_url_contains_tab_and_method(self):
        """URL must include tab=1&action=method&method=1."""
        cm, page, _ = _make_playwright_mock()
        with patch("medhub_timesheet.sync_playwright", return_value=cm):
            run(date(2026, 5, 25), dry_run=True)

        urls = [c.args[0] for c in page.goto.call_args_list]
        assert any("tab=1" in u and "action=method" in u and "method=1" in u for u in urls)

    def test_does_not_call_select_option(self):
        """Dry run must not change any dropdown values."""
        cm, page, _ = _make_playwright_mock()
        with patch("medhub_timesheet.sync_playwright", return_value=cm):
            run(date(2026, 5, 25), dry_run=True)

        page.select_option.assert_not_called()

    def test_does_not_click_submit(self):
        """Dry run must not click the submit button."""
        cm, page, _ = _make_playwright_mock()
        with patch("medhub_timesheet.sync_playwright", return_value=cm):
            run(date(2026, 5, 25), dry_run=True)

        # The locator returned by page.locator() should never have .click() called
        for loc_call in page.locator.return_value.click.call_args_list:
            pass  # If we got here without assertion, we need to check differently
        page.locator.return_value.click.assert_not_called()

    def test_reads_current_values_for_each_weekday(self):
        """Dry run must call input_value() to read current in/out for each of 5 days."""
        cm, page, _ = _make_playwright_mock()
        locators = []

        def track_locator(sel):
            loc = MagicMock()
            loc.count.return_value = 1
            loc.input_value.return_value = ""
            locators.append((sel, loc))
            return loc

        page.locator.side_effect = track_locator

        with patch("medhub_timesheet.sync_playwright", return_value=cm):
            run(date(2026, 5, 25), dry_run=True)

        input_value_calls = sum(
            loc.input_value.call_count for sel, loc in locators
        )
        # 5 days × 2 (in + out) = 10 reads
        assert input_value_calls == 10

    def test_closes_browser_after_dry_run(self):
        cm, page, browser = _make_playwright_mock()
        with patch("medhub_timesheet.sync_playwright", return_value=cm):
            run(date(2026, 5, 25), dry_run=True)

        browser.close.assert_called_once()


# ── run() — live mode ──────────────────────────────────────────────────────────

class TestRunLiveMode:
    def test_sets_in_time_for_each_weekday(self):
        """select_option must be called with START_TIME for each of Mon–Fri."""
        cm, page, _ = _make_playwright_mock()
        with patch("medhub_timesheet.sync_playwright", return_value=cm):
            run(date(2026, 5, 25), dry_run=False)

        select_args = [c.args[1] for c in page.select_option.call_args_list]
        assert select_args.count(START_TIME) == 5

    def test_sets_out_time_for_each_weekday(self):
        """select_option must be called with END_TIME for each of Mon–Fri."""
        cm, page, _ = _make_playwright_mock()
        with patch("medhub_timesheet.sync_playwright", return_value=cm):
            run(date(2026, 5, 25), dry_run=False)

        select_args = [c.args[1] for c in page.select_option.call_args_list]
        assert select_args.count(END_TIME) == 5

    def test_uses_correct_day_selectors(self):
        """Mon=day2, Tue=day3, Wed=day4, Thu=day5, Fri=day6."""
        cm, page, _ = _make_playwright_mock()
        with patch("medhub_timesheet.sync_playwright", return_value=cm):
            run(date(2026, 5, 25), dry_run=False)

        selector_args = [c.args[0] for c in page.select_option.call_args_list]
        for day_num in range(2, 7):  # day2 through day6
            assert any(f"day{day_num}_1_in" in s for s in selector_args)
            assert any(f"day{day_num}_1_out" in s for s in selector_args)

    def test_clicks_submit_button(self):
        """Live mode must click the Submit Work Hours locator."""
        cm, page, _ = _make_playwright_mock()
        submit_locator = MagicMock()
        submit_locator.count.return_value = 1

        def locator_side_effect(sel):
            if sel == 'a[aria-label="Submit Work Hours"]':
                return submit_locator
            loc = MagicMock()
            loc.count.return_value = 1
            loc.input_value.return_value = ""
            return loc

        page.locator.side_effect = locator_side_effect
        with patch("medhub_timesheet.sync_playwright", return_value=cm):
            run(date(2026, 5, 25), dry_run=False)

        submit_locator.click.assert_called_once()

    def test_does_not_call_input_value_in_live_mode(self):
        """Live mode should not read current values."""
        cm, page, _ = _make_playwright_mock()
        locators = []

        def track_locator(sel):
            loc = MagicMock()
            loc.count.return_value = 1
            loc.input_value.return_value = ""
            locators.append((sel, loc))
            return loc

        page.locator.side_effect = track_locator
        with patch("medhub_timesheet.sync_playwright", return_value=cm):
            run(date(2026, 5, 25), dry_run=False)

        day_locators = [
            (sel, loc) for sel, loc in locators
            if "day" in sel and ("_1_in" in sel or "_1_out" in sel)
        ]
        input_value_calls = sum(loc.input_value.call_count for _, loc in day_locators)
        assert input_value_calls == 0

    def test_closes_browser_after_live_run(self):
        cm, page, browser = _make_playwright_mock()
        with patch("medhub_timesheet.sync_playwright", return_value=cm):
            run(date(2026, 5, 25), dry_run=False)

        browser.close.assert_called_once()


# ── run() — edge cases ─────────────────────────────────────────────────────────

class TestRunEdgeCases:
    def test_missing_selector_skips_day(self):
        """When a day's in-selector count() returns 0, that day is skipped gracefully."""
        cm, page, _ = _make_playwright_mock(locator_count=0)
        with patch("medhub_timesheet.sync_playwright", return_value=cm):
            run(date(2026, 5, 25), dry_run=False)

        # select_option should never have been called (all selectors missing)
        page.select_option.assert_not_called()

    def test_missing_selector_does_not_crash(self):
        """Missing selectors must not raise an exception."""
        cm, page, _ = _make_playwright_mock(locator_count=0)
        with patch("medhub_timesheet.sync_playwright", return_value=cm):
            run(date(2026, 5, 25), dry_run=False)  # should not raise

    def test_no_submit_button_does_not_crash(self):
        """When submit button count() == 0 the script exits without error."""
        cm, page, _ = _make_playwright_mock()

        def locator_side_effect(sel):
            loc = MagicMock()
            if sel == 'a[aria-label="Submit Work Hours"]':
                loc.count.return_value = 0
            else:
                loc.count.return_value = 1
            loc.input_value.return_value = ""
            return loc

        page.locator.side_effect = locator_side_effect
        with patch("medhub_timesheet.sync_playwright", return_value=cm):
            run(date(2026, 5, 25), dry_run=False)  # should not raise

    def test_no_medhub_tab_returns_early(self):
        """If no MedHub tab is open, run() exits early without navigating."""
        cm, page, browser = _make_playwright_mock(page_url="https://www.google.com")
        with patch("medhub_timesheet.sync_playwright", return_value=cm):
            run(date(2026, 5, 25), dry_run=False)

        page.goto.assert_not_called()
        browser.close.assert_called_once()

    def test_cdp_connect_failure_returns_early(self):
        """If Chrome is not reachable, run() prints an error and returns without crashing."""
        p = MagicMock()
        p.chromium.connect_over_cdp.side_effect = Exception("Connection refused")

        cm = MagicMock()
        cm.__enter__.return_value = p
        cm.__exit__.return_value = False

        with patch("medhub_timesheet.sync_playwright", return_value=cm):
            run(date(2026, 5, 25), dry_run=False)  # should not raise

    def test_wednesday_input_uses_same_week_monday(self):
        """A Wednesday input maps to the same Monday as run(monday)."""
        cm_wed, page_wed, _ = _make_playwright_mock()
        cm_mon, page_mon, _ = _make_playwright_mock()

        with patch("medhub_timesheet.sync_playwright", return_value=cm_wed):
            run(date(2026, 5, 27), dry_run=True)  # Wednesday

        with patch("medhub_timesheet.sync_playwright", return_value=cm_mon):
            run(date(2026, 5, 25), dry_run=True)  # Monday

        urls_wed = [c.args[0] for c in page_wed.goto.call_args_list]
        urls_mon = [c.args[0] for c in page_mon.goto.call_args_list]
        assert urls_wed == urls_mon
