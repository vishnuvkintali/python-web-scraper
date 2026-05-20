from pathlib import Path
from datetime import date


OUTPUT_DIR = Path("../docs")  # saves into C:\work\vishnu\docs


def write_homework(data: dict) -> Path:
    """Convert scraped homework data into a markdown file and save it."""
    OUTPUT_DIR.mkdir(exist_ok=True)

    title = data["title"]
    # Build a safe filename from the title, e.g. "Homework_26_Ch8_Area_of_Basic_Polygons.md"
    safe_title = title.replace("|", "").replace("/", "-").strip()
    safe_title = "_".join(safe_title.split())
    filename = f"{safe_title}.md"
    output_path = OUTPUT_DIR / filename

    lines = []
    lines.append(f"# {title}")
    lines.append(f"")
    lines.append(f"**Source:** {data['url']}")
    lines.append(f"**Captured:** {date.today().isoformat()}")
    lines.append(f"")
    lines.append("---")
    lines.append("")

    for problem in data["problems"]:
        label = problem["label"]
        lines.append(f"## Problem {label}")
        lines.append("")

        if problem["text"]:
            lines.append(problem["text"])
            lines.append("")

        if problem["diagram"]:
            lines.append(f"**Diagram:** {problem['diagram']}")
            lines.append("")

        if problem["answer"]:
            status_mark = ""
            if problem["status"] == "Correct":
                status_mark = " ✓"
            elif problem["status"] == "Incorrect":
                status_mark = " ✗"
            lines.append(f"**Answer:** {problem['answer']}{status_mark}")
            lines.append("")

        lines.append("---")
        lines.append("")

    content = "\n".join(lines)
    output_path.write_text(content, encoding="utf-8")
    return output_path
