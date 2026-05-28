# MedHub Timesheet Auto-Logger

Logs 8:00am–6:00pm Mon–Fri on SingHealth MedHub automatically.

## Every session — do these steps first

**Step 1: Open Chrome with remote debugging** (quit Chrome first if it's already open)
```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-medhub &
```

**Step 2: Log in to MedHub** in that Chrome window — complete MFA when prompted.

**Step 3: Tell Claude** which week to fill, e.g.:
- "fill this week"
- "fill week May 10–16"
- "fill week June 2"

Claude will run `medhub_timesheet.py` and submit the hours.

## Run it yourself (no Claude needed)

```bash
# Current week
python3 medhub_timesheet.py

# Specific week (any date within it)
python3 medhub_timesheet.py --date 2026-06-02
```
