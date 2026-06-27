# AEGIS Project Summary

## Title

AEGIS: Social Media Username Intelligence Using OSINT

## Domain

Cybersecurity, OSINT, Digital Footprint Analysis

## Problem Statement

People often reuse the same username across multiple public platforms. This can expose a digital footprint that attackers or investigators may use to connect accounts. AEGIS demonstrates how OSINT techniques can identify public profile links associated with a username.

## Objective

The objective of AEGIS is to search public websites for accounts linked to a given username and organize the results for cybersecurity learning and analysis.

## Tools and Technologies

- Python
- Sherlock OSINT source code from GitHub
- PowerShell or terminal
- GitHub open-source resources

## Software Requirements

- Python 3.9 or newer
- Git
- Internet connection
- Sherlock project source code
- Python dependencies: certifi, colorama, PySocks, requests, requests-futures, stem, pandas, openpyxl, tomli

## Methodology

1. User enters one or more usernames.
2. AEGIS starts a Sherlock-based OSINT scan from the local GitHub source installation.
3. Sherlock checks public websites for matching usernames.
4. Results are saved into a timestamped folder under `results`.
5. The user analyzes the output for public digital footprint patterns.

## Expected Output

- Text result files
- Optional CSV output
- Optional Excel output
- List of discovered public profile URLs

## Ethical Considerations

This project must be used only for legal and ethical purposes, such as checking personal accounts, learning OSINT methods, or performing authorized cybersecurity investigation.

## Attribution

AEGIS is the custom project name and workflow. Sherlock is the open-source OSINT tool used as the username search engine.
