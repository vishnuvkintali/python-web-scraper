# RSM Page Reader — Build Log

**Date:** 2026-03-28
**Project folder:** `C:\work\vishnu\RSM_page_reader`

---

## Goal

Build an automation that captures RSM (Russian School of Mathematics) weekly homework from the student portal into a markdown file, so the content is preserved after the school year ends.

**Source site:** `student.russianschool.com/student-portal/content/assignment/{id}?problem={index}`

---

## What the Homework Page Looks Like

- Left sidebar: clickable problem number buttons (e.g. 6a, 6c, 7a, 7b, 15c, 16b, 11, 8201, 8202)
- Main area: problem text + geometry diagram image + student answer + Correct/Incorrect badge
- Diagrams are images (geometry shapes with labeled points and measurements) — need AI description
- URL pattern: `?problem=0`, `?problem=1`, etc. to navigate between problems

---

## Architecture

Three Python files work together:

| File | Role |
|------|------|
| `main.py` | Entry point — takes `--url` argument, runs the pipeline |
| `scraper.py` | Playwright browser bot — logs in, clicks through problems, screenshots diagrams, calls Claude API |
| `writer.py` | Converts scraped data into a `.md` file saved to `C:\work\vishnu\docs\` |

### Flow
1. User runs: `python main.py --url "https://student.russianschool.com/student-portal/content/assignment/1515979467"`
2. A real Chrome window opens and logs in automatically
3. Bot reads all problem labels from the sidebar
4. For each problem: extracts text, screenshots any diagram, sends diagram to Claude API for description, reads the student's answer and correct/incorrect status
5. Saves everything to `C:\work\vishnu\docs\Homework_26_Ch8_Area_of_Basic_Polygons.md`

### Output format (per problem)
```
## Problem 6a
Find the area of the polygon.
**Diagram:** Diamond ABCD with diagonals labeled 4 and 5, center point O
**Answer:** 40 ✓
```

---

## Tech Stack

| Tool | Purpose |
|------|---------|
| Python | Main language |
| Playwright | Controls Chrome browser |
| Anthropic SDK | Claude API for diagram descriptions |
| python-dotenv | Loads credentials from `.env` file |

---

## Files Created

```
C:\work\vishnu\RSM_page_reader\
  main.py           — entry point
  scraper.py        — browser automation + Claude API calls
  writer.py         — markdown file writer
  requirements.txt  — Python dependencies
  .env.example      — credential template
  .env              — real credentials (never share this)
  screenshots/      — auto-created, stores diagram screenshots
```

---

## Installation Steps (completed)

```bash
# 1. Install Python from python.python.org — check "Add Python to PATH"
# 2. Upgrade pip
python -m pip install --upgrade pip

# 3. Install dependencies
python -m pip install -r requirements.txt

# 4. Install Chromium browser for Playwright
python -m playwright install chromium
```

**Issues hit during install:**
- `pip` not recognized → fixed by using `python -m pip`
- `greenlet` build error (needs C++ tools) → fixed by removing version pins from `requirements.txt`
- `playwright` not recognized → fixed by using `python -m playwright`

---

## How to Run

```bash
cd C:\work\vishnu\RSM_page_reader
python main.py --url "https://student.russianschool.com/student-portal/content/assignment/1515979467"
```

---

## Known Limitations / Next Steps

- HTML selectors in `scraper.py` are best-guess estimates — may need adjustment after first run
- If "No problems were found" error appears, open browser DevTools (F12 → Elements) and check the actual class names used on the sidebar buttons and problem text
- Need Anthropic API key from `console.anthropic.com` for diagram descriptions
- `.env` file must be created manually from `.env.example` before running
