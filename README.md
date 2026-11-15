# RSM Page Reader

**Status:** In progress (half done)
All the code (login, problem walk-through, diagram descriptions, Markdown writer) is written, but the login step does not complete on the real site yet and the page selectors are unverified, so it cannot reliably capture an assignment.

A Python tool that captures an RSM (Russian School of Mathematics) homework assignment from the student portal and saves it as a Markdown file, so the problems and your answers are kept after the school year ends.

It opens a real Chromium window with Playwright, logs in, walks through every problem in the assignment, and records:

- the problem text
- a text description of any diagram (the diagram is screenshotted and described by the Claude API)
- your submitted answer
- whether it was marked Correct or Incorrect

## Setup

Requires Python 3 on Windows (the password prompt uses `msvcrt`, which is Windows only).

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m playwright install chromium
```

Then create a `.env` file from the template and add an Anthropic API key (used only for diagram descriptions):

```
ANTHROPIC_API_KEY=your-key-here
```

`.env` is gitignored. RSM login details are never stored; you type them in when the script runs.

Install tips: use `python -m pip` and `python -m playwright` if the bare `pip` or `playwright` commands are not found. The requirements are unpinned on purpose, because pinned versions caused a `greenlet` build error.

## Running it

Open the assignment in your browser, copy its URL, then from this folder run:

```bash
python main.py --url "https://student.russianschool.com/student-portal/content/assignment/<assignment-id>"
```

Any `?problem=N` on the end of the URL is stripped automatically. The script asks for your RSM username and password (the password shows as `*`), then a browser window opens and does the rest. Progress is printed to the terminal.

## Hosting

Not hosted. It is a local command-line tool that runs on your own Windows PC.

## Output

- **Markdown file:** written to `../docs/<Homework_Title>.md`, relative to the folder you run the script from. The filename comes from the assignment title with spaces turned into underscores. Each problem gets its own section:

  ```
  ## Problem 6a
  Find the area of the polygon.
  **Diagram:** Diamond ABCD with diagonals labeled 4 and 5, center point O
  **Answer:** 40 ✓
  ```

- **Screenshots:** diagram images are saved to `screenshots/problem_<label>.png` in the current folder.

## How the files fit together

| File | Role |
|------|------|
| `main.py` | Entry point. Parses `--url`, prompts for login, runs the scraper, then the writer. |
| `scraper.py` | Playwright automation. Logs in, reads problem labels from the sidebar, visits each `?problem=N` page, pulls text, answer and status, screenshots diagrams and sends them to Claude for a description. |
| `writer.py` | Turns the scraped data into a Markdown file and saves it. |
| `requirements.txt` | `playwright`, `anthropic`, `python-dotenv`. |

## Status and known limitations

The tool is built but not fully working yet.

- **Login does not complete.** After the Sign In click the browser stays on the login page, so the login selectors in `scraper.py` need fixing against the real page.
- **Selectors are best guesses.** The sidebar, problem text, answer and status selectors have not been checked against the live site. When the sidebar is not found the script falls back to problems 0 to 9. If you see "No problems were found", inspect the page with DevTools (F12, Elements tab) and update the selectors in `scraper.py`.
- **Output path is relative.** `../docs` depends on the folder you run from, so check the "Saved to" path printed at the end.
- **Windows only** because of the masked password prompt.
- **Costs API credits** for each diagram described. The model name is set in `describe_diagram()` in `scraper.py`.

Planning and spec docs live outside this repo in the owner's workspace docs folder.
