"""
RSM Homework Capturer
---------------------
Run this script to scrape a homework assignment from student.russianschool.com
and save it as a markdown file in C:/work/vishnu/docs/

Usage:
    python main.py --url "https://student.russianschool.com/student-portal/content/assignment/1515979467"

Make sure you have a .env file set up (copy .env.example and fill it in).
"""

import asyncio
import argparse
import msvcrt
import sys
from scraper import scrape_assignment
from writer import write_homework


def masked_input(prompt="Password: ") -> str:
    """Show * for each character typed instead of hiding completely."""
    print(prompt, end="", flush=True)
    password = ""
    while True:
        ch = msvcrt.getwch()
        if ch in ("\r", "\n"):
            print()
            break
        elif ch == "\x08":  # backspace
            if password:
                password = password[:-1]
                print("\b \b", end="", flush=True)
        elif ch == "\x03":  # ctrl+c
            raise KeyboardInterrupt
        else:
            password += ch
            print("*", end="", flush=True)
    return password


def main():
    parser = argparse.ArgumentParser(description="Capture RSM homework to markdown.")
    parser.add_argument(
        "--url",
        required=True,
        help='The assignment URL from your browser, e.g. "https://student.russianschool.com/student-portal/content/assignment/1515979467"'
    )
    args = parser.parse_args()

    url = args.url.split("?")[0]  # strip ?problem=N if user copied it with that

    print(f"Starting RSM homework capture...")
    print(f"URL: {url}")
    print()

    username = input("RSM username: ")
    password = masked_input("RSM password: ")
    print()

    data = asyncio.run(scrape_assignment(url, username, password))

    if not data["problems"]:
        print("ERROR: No problems were found. The page selectors may need adjusting.")
        print("Check that you are logged in and the URL is correct.")
        sys.exit(1)

    output_path = write_homework(data)
    print()
    print(f"Done! Saved to: {output_path.resolve()}")
    print(f"  {len(data['problems'])} problems captured.")


if __name__ == "__main__":
    main()
