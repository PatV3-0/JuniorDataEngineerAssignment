# Junior Data Engineer Assignment - PR Extraction and Transformation

This repository contains Python scripts to extract merged pull request (PR) data.

---

## Directory Structure

project-root/
├── .github/workflows
├── data/
│ ├── raw/ # Stores raw PR JSON files
│ └── processed/ # Stores transformed CSV files
├── source/ # Configurations for Spinx documentation
├── src/
│ ├── extract.py # Extract PR data from GitHub
│ ├── transform.py # Transform raw PR JSON data into CSV
├── build/
│ └── html/
│   └── index.html # Auto-generated documentation (Sphinx)
├── .flake8 # Flake8 configuration
├── .gitignore # Git ignore configuration
├── Makefile # Used to generate Sphinx docs
├── README.md
├── main.py # Entry point to run extraction and transformation together
└── requirements.txt

---

## Prerequisites

- Python 3.10 or higher
- Required Python packages (install via `pip`):

```bash
pip install -r requirements.txt
```

- A GitHub Personal Access Token with permissions to read repository data stored in .env:
```
GITHUB_TOKEN=your_personal_access_token_here
```

---

## Running the code