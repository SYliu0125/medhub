# MedHub Timesheet Filler

Automatically fills **8am–6pm Mon–Fri** on [SingHealth MedHub](https://singhealth.medhub.com) in one click.  
Works in any browser — Chrome, Safari, Firefox, Edge.

---

## Bookmarklet — Install (one-time)

1. Open the install page in your browser:  
   **https://syliu0125.github.io/medhub/bookmarklet/install.html**

2. **Show your bookmarks bar** if it's hidden:  
   - Chrome / Edge: `Cmd+Shift+B` (Mac) or `Ctrl+Shift+B` (Windows)  
   - Firefox: `Ctrl+Shift+B`  
   - Safari: View → Show Favourites Bar

3. **Drag** the blue "MedHub Timesheet Filler" button onto your bookmarks bar  
   *(or right-click it → "Bookmark this link" / "Add to Favourites")*

Done. You only need to do this once.

---

## Use (every week)

1. Log in to [singhealth.medhub.com](https://singhealth.medhub.com)
2. Navigate to your timesheet for the week you want to fill
3. Click **MedHub Timesheet Filler** in your bookmarks bar
4. Choose **Fill & Submit** or **Fill Only**

> **Tip:** If the page redirects on first click (switching to the pull-down view), click the bookmark **once more** after it loads.

---

## Python Script (developers / command line)

### Setup

```bash
pip install playwright
playwright install chromium
```

### Usage

**Step 1** — Launch Chrome with remote debugging *(quit Chrome first if open)*:
```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-medhub &
```

**Step 2** — Log in to MedHub in that Chrome window (complete MFA yourself)

**Step 3** — Run the script:
```bash
python3 medhub_timesheet.py                    # current week
python3 medhub_timesheet.py --date 2026-05-19  # specific week
python3 medhub_timesheet.py --dry-run          # preview only, no changes
```
