# MedHub Timesheet Filler

Automatically fills **8am–6pm Mon–Fri** on SingHealth MedHub in one click.  
Works in any browser — Chrome, Safari, Firefox, Edge. No install required.

## Install

### 1. Open the install page

> **https://syliu0125.github.io/medhub/bookmarklet/install.html**

### 2. Show your bookmarks bar (if hidden)

| Browser | Shortcut |
|---------|----------|
| Chrome / Edge (Mac) | `Cmd+Shift+B` |
| Chrome / Edge (Windows) | `Ctrl+Shift+B` |
| Firefox | `Ctrl+Shift+B` |
| Safari | View → Show Favourites Bar |

### 3. Drag the button to your bookmarks bar

On the install page, drag the blue **"MedHub Timesheet Filler"** button onto your bookmarks bar.  
*(Can't drag? Right-click it → "Bookmark this link" / "Add to Favourites")*

That's it — one-time setup, done.

---

## Use (every week)

1. Log in to [singhealth.medhub.com](https://singhealth.medhub.com)
2. Go to your timesheet for the week you want to fill
3. Click **MedHub Timesheet Filler** in your bookmarks bar
4. Choose **Fill & Submit** or **Fill Only**

> If the page redirects on first click, just click the bookmark **once more** after it loads.

---

## Python script (command line / developers)

<details>
<summary>Click to expand</summary>

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

</details>
