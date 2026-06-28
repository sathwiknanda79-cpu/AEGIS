# AEGIS Project Report

## Project Title

AEGIS: Social Media Username Intelligence Using OSINT

## Introduction

AEGIS is a cybersecurity project that demonstrates OSINT-based username investigation. It helps identify public social media profiles associated with a username and stores the results in organized output files.

## Problem Statement

Many users reuse the same username on multiple websites. This creates a digital footprint that can reveal public accounts across social media and online platforms. AEGIS shows how cybersecurity learners can analyze this footprint in an ethical and controlled way.

## Objective

- Build a usable OSINT investigation interface
- Search public websites for matching usernames
- Save results in text, CSV, or Excel format
- Use the official Sherlock GitHub source code as the search engine
- Present the project under a custom student project workflow

## Existing Tool Used

AEGIS uses the open-source Sherlock project as its backend username search engine.

GitHub: https://github.com/sherlock-project/sherlock

## Technologies Used

- Python
- Streamlit
- Sherlock OSINT source code
- PowerShell
- Git

## System Requirements

- Windows 10 or Windows 11
- Python 3.9 or newer
- Internet connection
- Git
- 4 GB RAM minimum, 8 GB recommended

## Project Modules

- `app.py`: Browser-based Streamlit interface
- `main.py`: Terminal-based AEGIS interface
- `third_party/sherlock`: Official Sherlock GitHub source code
- `results`: Stores scan outputs
- `run_web_app.ps1`: Runs the browser app
- `run_aegis.ps1`: Runs the terminal app

## Workflow

1. User opens AEGIS.
2. User enters one or more usernames.
3. User chooses output format.
4. AEGIS runs Sherlock from the local GitHub source installation.
5. Sherlock checks public websites.
6. AEGIS saves results in the `results` folder.
7. User reviews or downloads the saved result files.

## Output

AEGIS can generate:

- `.txt` result files
- `.csv` result files
- `.xlsx` result files
- verified link reports

## False Positives and Verification

OSINT username scanners may sometimes show false positives because websites change their response behavior, block automated requests, redirect pages, or return pages that look valid to a scanner but open as "not found" in a browser.

To reduce confusion, AEGIS performs an extra verification step. After Sherlock finds possible profile URLs, AEGIS re-checks those URLs and saves `verified_links.txt` and `verified_links.csv` with a verdict such as `reachable`, `not found`, `blocked or rate limited`, or `needs manual check`.

## Ethical Use

This project is only for learning, self-auditing, lab work, and authorized cybersecurity investigation. It must not be used for harassment, stalking, impersonation, or privacy invasion.

## Conclusion

AEGIS demonstrates how OSINT can be used to understand public digital footprints. The project combines an existing open-source OSINT engine with a custom interface, project structure, and result workflow.
