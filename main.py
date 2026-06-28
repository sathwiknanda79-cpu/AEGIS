from __future__ import annotations

import shutil
import subprocess
import re
from datetime import datetime
from pathlib import Path

import requests


APP_NAME = "AEGIS"
TAGLINE = "Social Media Username Intelligence Using OSINT"
RESULTS_DIR = Path("results")
USER_AGENT = "AEGIS OSINT verifier/1.0"


def print_header() -> None:
    print("=" * 62)
    print(f"{APP_NAME:^62}")
    print(f"{TAGLINE:^62}")
    print("=" * 62)


def sherlock_command() -> str | None:
    local_command = Path(".venv") / "Scripts" / "sherlock.exe"
    if local_command.exists():
        return str(local_command)
    return shutil.which("sherlock")


def extract_urls(text: str) -> list[str]:
    urls = re.findall(r"https?://[^\s,]+", text)
    return list(dict.fromkeys(url.rstrip(").]") for url in urls))


def verify_url(url: str) -> tuple[str, int | None, str]:
    try:
        response = requests.get(
            url,
            allow_redirects=True,
            headers={"User-Agent": USER_AGENT},
            timeout=12,
        )
    except requests.RequestException as error:
        return url, None, f"unreachable: {error.__class__.__name__}"

    if response.status_code == 404:
        return url, response.status_code, "not found"
    if response.status_code in {401, 403, 429}:
        return url, response.status_code, "blocked or rate limited"
    if 200 <= response.status_code < 400:
        return url, response.status_code, "reachable"
    return url, response.status_code, "needs manual check"


def write_verified_results(session_dir: Path, urls: list[str]) -> None:
    if not urls:
        print("No URLs found for verification.")
        return

    rows = [verify_url(url) for url in urls]
    text_path = session_dir / "verified_links.txt"
    csv_path = session_dir / "verified_links.csv"

    text_lines = ["url | status_code | verdict"]
    csv_lines = ["url,status_code,verdict"]
    for url, status_code, verdict in rows:
        code_text = "" if status_code is None else str(status_code)
        text_lines.append(f"{url} | {code_text} | {verdict}")
        csv_lines.append(f'"{url}","{code_text}","{verdict}"')

    text_path.write_text("\n".join(text_lines), encoding="utf-8")
    csv_path.write_text("\n".join(csv_lines), encoding="utf-8")
    print(f"Verified links saved to: {text_path.resolve()}")


def run_sherlock(usernames: list[str], output_format: str) -> None:
    RESULTS_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_dir = RESULTS_DIR / f"scan_{timestamp}"
    session_dir.mkdir(exist_ok=True)

    command_path = sherlock_command()
    if command_path is None:
        print("Sherlock is not installed or not available in PATH.")
        return

    command = [command_path, *usernames, "--folderoutput", str(session_dir)]

    if output_format == "txt":
        command.append("--txt")
    elif output_format == "csv":
        command.append("--csv")
    elif output_format == "xlsx":
        command.append("--xlsx")

    print()
    print(f"Starting AEGIS scan for: {', '.join(usernames)}")
    print(f"Results folder: {session_dir.resolve()}")
    print()

    try:
        completed = subprocess.run(command, check=True, text=True, capture_output=True)
        if completed.stdout:
            print(completed.stdout)
        if completed.stderr:
            print(completed.stderr)
        urls = extract_urls(completed.stdout)
        for result_file in session_dir.glob("*.txt"):
            urls.extend(extract_urls(result_file.read_text(encoding="utf-8", errors="replace")))
        write_verified_results(session_dir, list(dict.fromkeys(urls)))
    except subprocess.CalledProcessError as error:
        print()
        print(f"Sherlock stopped with exit code {error.returncode}.")
        if error.stdout:
            print(error.stdout)
        if error.stderr:
            print(error.stderr)
    except FileNotFoundError:
        print()
        print("Sherlock is not installed or not available in PATH.")


def ask_usernames() -> list[str]:
    raw_value = input("Enter username(s), separated by commas: ").strip()
    usernames = [name.strip() for name in raw_value.split(",") if name.strip()]
    return usernames


def ask_output_format() -> str:
    print()
    print("Choose output format:")
    print("1. Text only")
    print("2. CSV")
    print("3. Excel XLSX")
    choice = input("Select option: ").strip()

    if choice == "2":
        return "csv"
    if choice == "3":
        return "xlsx"
    return "txt"


def main() -> None:
    print_header()

    if sherlock_command() is None:
        print("Sherlock is required before AEGIS can scan usernames.")
        print("Install it with: pipx install sherlock-project")
        return

    while True:
        print()
        print("1. Start username scan")
        print("2. About AEGIS")
        print("3. Exit")
        choice = input("Select option: ").strip()

        if choice == "1":
            usernames = ask_usernames()
            if not usernames:
                print("No username entered.")
                continue
            output_format = ask_output_format()
            run_sherlock(usernames, output_format)
        elif choice == "2":
            print()
            print("AEGIS is a custom OSINT project interface.")
            print("It uses Sherlock as the public username lookup engine.")
            print("Use only for learning, self-auditing, and authorized work.")
        elif choice == "3":
            print("Exiting AEGIS.")
            break
        else:
            print("Invalid option.")


if __name__ == "__main__":
    main()
