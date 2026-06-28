from __future__ import annotations

import shutil
import subprocess
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

import requests
import streamlit as st


APP_NAME = "AEGIS"
APP_SUBTITLE = "Social Media Username Intelligence Using OSINT"
BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BASE_DIR / "results"
LOGO_PATH = BASE_DIR / "assets" / "aegis-logo.png"
USER_AGENT = "AEGIS OSINT verifier/1.0"


def sherlock_command() -> str | None:
    local_command = BASE_DIR / ".venv" / "Scripts" / "sherlock.exe"
    if local_command.exists():
        return str(local_command)
    return shutil.which("sherlock")


def list_result_files() -> list[Path]:
    if not RESULTS_DIR.exists():
        return []
    return sorted(
        [path for path in RESULTS_DIR.rglob("*") if path.is_file()],
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )


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
        parsed = urlparse(str(response.url))
        if parsed.netloc:
            return url, response.status_code, "reachable"
    return url, response.status_code, "needs manual check"


def write_verified_results(session_dir: Path, urls: list[str]) -> Path | None:
    if not urls:
        return None

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
    return text_path


def run_scan(
    usernames: list[str],
    output_format: str,
    print_found: bool,
    verify_links: bool,
) -> tuple[int, str, str, Path, Path | None]:
    command_path = sherlock_command()
    if command_path is None:
        return 1, "", "Sherlock is not installed inside AEGIS.", RESULTS_DIR

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_dir = RESULTS_DIR / f"scan_{timestamp}"
    session_dir.mkdir(parents=True, exist_ok=True)

    command = [command_path, *usernames, "--folderoutput", str(session_dir)]

    if output_format == "Text":
        command.append("--txt")
    elif output_format == "CSV":
        command.append("--csv")
    elif output_format == "Excel":
        command.append("--xlsx")

    if print_found:
        command.append("--print-found")

    completed = subprocess.run(
        command,
        cwd=BASE_DIR,
        text=True,
        capture_output=True,
        check=False,
    )

    verified_path = None
    if verify_links:
        urls = extract_urls(completed.stdout)
        for result_file in session_dir.glob("*.txt"):
            urls.extend(extract_urls(result_file.read_text(encoding="utf-8", errors="replace")))
        urls = list(dict.fromkeys(urls))
        verified_path = write_verified_results(session_dir, urls)

    return completed.returncode, completed.stdout, completed.stderr, session_dir, verified_path


st.set_page_config(
    page_title="AEGIS OSINT",
    page_icon="AEGIS",
    layout="wide",
)

st.markdown(
    """
    <style>
    .main .block-container {
        padding-top: 2rem;
        max-width: 1180px;
    }
    .aegis-title {
        font-size: 2.35rem;
        font-weight: 800;
        color: #16213e;
        margin-bottom: 0.15rem;
    }
    .aegis-subtitle {
        color: #4b5563;
        font-size: 1rem;
        margin-bottom: 1.25rem;
    }
    .metric-card {
        border: 1px solid #d7dde8;
        border-radius: 8px;
        padding: 1rem;
        background: #ffffff;
    }
    .small-label {
        color: #5b6575;
        font-size: 0.85rem;
        margin-bottom: 0.25rem;
    }
    .value {
        color: #16213e;
        font-size: 1.1rem;
        font-weight: 700;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

brand_col, title_col = st.columns([0.22, 0.78], vertical_alignment="center")
with brand_col:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=150)
with title_col:
    st.markdown("<div class='aegis-title'>AEGI<span style='color:#be1c1c;'>S</span></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='aegis-subtitle'>{APP_SUBTITLE}</div>", unsafe_allow_html=True)

command_available = sherlock_command() is not None

top_left, top_mid, top_right = st.columns(3)
with top_left:
    st.markdown("<div class='metric-card'><div class='small-label'>Engine</div><div class='value'>Sherlock GitHub Source</div></div>", unsafe_allow_html=True)
with top_mid:
    status = "Ready" if command_available else "Missing"
    st.markdown(f"<div class='metric-card'><div class='small-label'>Status</div><div class='value'>{status}</div></div>", unsafe_allow_html=True)
with top_right:
    st.markdown("<div class='metric-card'><div class='small-label'>Output</div><div class='value'>TXT / CSV / XLSX</div></div>", unsafe_allow_html=True)

st.divider()

scan_col, results_col = st.columns([0.9, 1.1])

with scan_col:
    st.subheader("New Investigation")
    username_text = st.text_area(
        "Username input",
        placeholder="Enter one or more usernames, separated by commas",
        height=100,
    )
    output_format = st.segmented_control(
        "Output format",
        options=["Text", "CSV", "Excel"],
        default="Text",
    )
    print_found = st.checkbox("Show only found accounts in terminal output", value=True)
    verify_links = st.checkbox("Verify links after scan", value=True)

    start_scan = st.button("Start Scan", type="primary", use_container_width=True)

    if start_scan:
        usernames = [name.strip() for name in username_text.split(",") if name.strip()]
        if not usernames:
            st.warning("Enter at least one username.")
        elif not command_available:
            st.error("Sherlock is not available. Install project requirements first.")
        else:
            with st.spinner("Scanning public websites..."):
                code, stdout, stderr, session_dir, verified_path = run_scan(
                    usernames,
                    output_format,
                    print_found,
                    verify_links,
                )

            if code == 0:
                st.success(f"Scan completed. Results saved in {session_dir.name}.")
            else:
                st.error(f"Scan finished with exit code {code}.")

            if stdout:
                st.code(stdout, language="text")
            if stderr:
                st.code(stderr, language="text")
            if verified_path:
                st.info(f"Verified link report created: {verified_path.name}")

with results_col:
    st.subheader("Saved Results")
    result_files = list_result_files()

    if not result_files:
        st.info("No result files yet. Run a scan to create output.")
    else:
        selected_file = st.selectbox(
            "Open result file",
            options=result_files,
            format_func=lambda path: str(path.relative_to(BASE_DIR)),
        )

        st.caption(str(selected_file))
        if selected_file.suffix.lower() in {".txt", ".csv"}:
            st.code(selected_file.read_text(encoding="utf-8", errors="replace"), language="text")
        else:
            st.info("This file is saved for Excel. Open it from the results folder.")

        st.download_button(
            "Download selected file",
            data=selected_file.read_bytes(),
            file_name=selected_file.name,
            use_container_width=True,
        )

st.divider()

with st.expander("Project Notes"):
    st.write("AEGIS is your custom OSINT project wrapper. Sherlock remains credited as the open-source username lookup engine.")
    st.write("Use it only for your own accounts, lab work, learning, or authorized cybersecurity investigation.")
