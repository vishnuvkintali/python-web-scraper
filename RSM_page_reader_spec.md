# RSM Page Reader — Spec

**Date:** 2026-03-28
**Project folder:** `C:\work\vishnu\RSM_page_reader`
**Status:** Built, partially working — blocked on two items (see bottom)

---

## Goal

Capture RSM (Russian School of Mathematics) weekly homework from the student portal into a markdown file so content is preserved after the school year ends.

---

## How the Homework Page Works

- URL pattern: `student.russianschool.com/student-portal/content/assignment/{id}?problem={index}`
- Left sidebar has problem buttons (e.g. 6a, 6c, 7a, 7b, 15c...)
- Each problem has: text instructions + geometry diagram image + student answer + Correct/Incorrect badge
- Diagrams need AI description since they are images, not text

---

## Architecture

| File | Role |
|------|------|
| `main.py` | Entry point — prompts for credentials, takes `--url` arg |
| `scraper.py` | Playwright browser bot — logs in, iterates problems, screenshots diagrams, calls Claude API |
| `writer.py` | Writes scraped data to a `.md` file in `C:\work\vishnu\docs\` |

### Run command
```bash
cd C:\work\vishnu\RSM_page_reader
python main.py --url "https://student.russianschool.com/student-portal/content/assignment/151597946"
```

### Output format
```
# Homework 26 | Ch8 Area of Basic Polygons

## Problem 6a
Find the area of the polygon.
**Diagram:** Diamond ABCD with diagonals labeled 4 and 5, center point O
**Answer:** 40 ✓
```

Output saved to: `C:\work\vishnu\docs\{homework title}.md`

---

## Tech Stack

| Tool | Purpose |
|------|---------|
| Python 3.14 | Main language |
| Playwright | Controls Chrome browser |
| Anthropic SDK | Claude API for diagram descriptions |
| python-dotenv | Loads API key from `.env` |

---

## Setup (already done)

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m playwright install chromium
```

---

## .env File

Only the Anthropic API key is stored — credentials are typed at runtime.

```
ANTHROPIC_API_KEY=sk-ant-...   ← paste real key here
```

Get key from: `https://platform.claude.com/settings/keys`

---

## Blocked On (resume here next session)

### 1. Anthropic API key not set
- `.env` still has placeholder `sk-ant-...`
- Fix: open `C:\work\vishnu\RSM_page_reader\.env` in Notepad, paste real key

### 2. Login not completing
- After login attempt, browser stays on `.../login` instead of redirecting
- Means the Sign In button click in `scraper.py` is not finding the right button
- Fix: take a screenshot of the RSM login page and share it so selectors can be corrected

### 3. Problem sidebar selectors are unverified
- Script fell back to trying problems 0–9 instead of reading real labels from sidebar
- Will need DevTools (F12 → Elements) inspection once login is fixed
