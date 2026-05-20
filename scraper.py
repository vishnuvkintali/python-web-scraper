import os
import base64
from pathlib import Path
from playwright.async_api import async_playwright, Page
import anthropic
from dotenv import load_dotenv

load_dotenv()

SCREENSHOTS_DIR = Path("screenshots")
LOGIN_URL = "https://student.russianschool.com/student-portal/login"


def describe_diagram(image_path: Path) -> str:
    """Send a diagram screenshot to Claude and get a text description back."""
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    with open(image_path, "rb") as f:
        image_data = base64.standard_b64encode(f.read()).decode("utf-8")

    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=500,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": image_data,
                    },
                },
                {
                    "type": "text",
                    "text": (
                        "Describe this math diagram precisely and concisely. "
                        "Include all labeled points, measurements, angles, and shapes. "
                        "A student should be able to reconstruct it from your description."
                    )
                }
            ],
        }]
    )
    return message.content[0].text


async def login(page: Page, username: str, password: str):
    print("  Logging in...")
    await page.goto(LOGIN_URL)
    await page.wait_for_load_state("networkidle")

    # Fill username field
    username_input = page.locator("input").first
    await username_input.fill(username)

    # Fill password field
    await page.locator('input[type="password"]').fill(password)

    # Click Sign In button
    await page.get_by_role("button", name="Sign In").click()

    await page.wait_for_load_state("networkidle")
    await page.wait_for_timeout(2000)
    print("  Logged in. Current page:", page.url)


async def get_problem_labels(page: Page) -> list[str]:
    """Read all problem labels from the left sidebar."""
    await page.wait_for_timeout(1000)

    # Grab every button in the sidebar/left panel
    buttons = page.locator("aside button, nav button, [class*='sidebar'] button, [class*='nav'] button")
    count = await buttons.count()

    labels = []
    for i in range(count):
        text = await buttons.nth(i).text_content()
        if text and text.strip():
            labels.append(text.strip())

    return labels


async def scrape_problem(page: Page, problem_index: int, label: str, base_url: str) -> dict:
    """Navigate to one problem and extract all its data."""
    await page.goto(f"{base_url}?problem={problem_index}")
    await page.wait_for_load_state("networkidle")
    await page.wait_for_timeout(500)

    # --- Problem text ---
    text = ""
    for sel in ["[class*='problem-text']", "[class*='question-text']", "[class*='task-text']", "main p"]:
        el = page.locator(sel).first
        if await el.count() > 0:
            t = await el.text_content()
            if t and t.strip():
                text = t.strip()
                break

    # --- Diagram image ---
    diagram_description = None
    for sel in ["[class*='problem'] img", "[class*='question'] img", "main img"]:
        el = page.locator(sel).first
        if await el.count() > 0:
            SCREENSHOTS_DIR.mkdir(exist_ok=True)
            shot_path = SCREENSHOTS_DIR / f"problem_{label.replace('.', '_')}.png"
            await el.screenshot(path=str(shot_path))
            print(f"    Diagram found for {label}, describing with Claude...")
            diagram_description = describe_diagram(shot_path)
            break

    # --- Student's answer ---
    answer = ""
    for sel in ['input[type="text"]', 'input[type="number"]', "[class*='answer'] input"]:
        el = page.locator(sel).first
        if await el.count() > 0:
            val = await el.input_value()
            if val:
                answer = val.strip()
                break

    # --- Correct / Incorrect status ---
    status = ""
    for sel in ["[class*='correct']", "[class*='status']", "[class*='result']"]:
        el = page.locator(sel).first
        if await el.count() > 0:
            t = await el.text_content()
            if t:
                t = t.strip().lower()
                if "incorrect" in t:
                    status = "Incorrect"
                elif "correct" in t:
                    status = "Correct"
            if status:
                break

    return {
        "label": label,
        "text": text,
        "diagram": diagram_description,
        "answer": answer,
        "status": status,
    }


async def scrape_assignment(url: str, username: str, password: str) -> dict:
    """Main entry: scrape an entire homework assignment from its URL."""
    base_url = url.split("?")[0]

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        await login(page, username, password)

        # Navigate to first problem
        await page.goto(f"{base_url}?problem=0")
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(1000)

        # Homework title — look for the heading on the page
        title = "RSM Homework"
        for sel in ["h1", "[class*='title']", "[class*='heading']"]:
            el = page.locator(sel).first
            if await el.count() > 0:
                t = await el.text_content()
                if t and t.strip():
                    title = t.strip()
                    break

        print(f"  Assignment: {title}")

        # Problem labels from sidebar
        labels = await get_problem_labels(page)
        if not labels:
            print("  WARNING: Could not find problem buttons. Trying problems 0-9...")
            labels = [str(i) for i in range(10)]

        print(f"  Found problems: {labels}")

        problems = []
        for i, label in enumerate(labels):
            print(f"  Scraping problem {label} ({i+1}/{len(labels)})...")
            data = await scrape_problem(page, i, label, base_url)
            if data["text"] or data["diagram"]:
                problems.append(data)

        await browser.close()

    return {"title": title, "url": url, "problems": problems}
