# Junior Data Engineer Assignment - PR Extraction and Transformation

This repository contains Python scripts to extract merged pull request (PR) data.

---

## Directory Structure
```
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
├── .env
├── .flake8 # Flake8 configuration
├── .gitignore # Git ignore configuration
├── Makefile # Used to generate Sphinx docs
├── README.md
├── main.py # Entry point to run extraction and transformation together
└── requirements.txt
```
---

## Prerequisites

- Python 3.10 or higher
- Required Python packages (install via `pip`):

```bash
pip install -r requirements.txt
```

- A GitHub Personal Access Token with permissions to read repository data stored in `.env`:
```bash
GITHUB_TOKEN=your_personal_access_token_here
```

---

## Running the code
### 1. Using `main.py` (recommended):

`main.py` runs both the extraction and transformation steps sequentially:
```bash
# On Windows
py main.py

# On Linux/macOS
python3 main.py
```
Filters and flags:
- Repo: Fetch PRs from this repo, formatted as `repo_owner/repo`
- Since: Fetch PRs merged on or after this date, formatted as `YYYY-MM-DD`
- Until: Fetch PRs merged on or before this date, formatted as `YYYY-MM-DD`
- Per_page: Number of PRs to fetch per GitHub API page (default: 100)

Example:
```python
repo = "Scytale-exercise/scytale-repo3"
    getMergedPRs(repo, perPage=100, since=None, until=None)
```
This will:
- Fetch merged PRs from the repository.
- Save the raw PR data to data/raw/ as JSON files.
- Transform each JSON file into CSV and save to data/processed/

### 2. Running scripts individually:

Extract PRs:
```bash
# Windows
py src/extract.py --repo owner/repo --since YYYY-MM-DD --until YYYY-MM-DD --per_page N

# Linux/macOS
python3 src/extract.py --repo owner/repo --since YYYY-MM-DD --until YYYY-MM-DD --per_page N
```

Example:
```bash
py extraction.py --repo PatV3-0/JuniorDataEngineerAssignment
```

Transform Raw Data:
```bash
# Windows
py src/transform.py

# Linux/macOS
python3 src/transform.py
```

---

## Data Output:
- Raw data: `data/raw/`
    JSON files containing PR metadata, review status, checks and timestamps
- Transformed data: `data/processed/`
  - PRNum
  - Title
  - Author
  - CreatedAt
  - MergedAt
  - Num_Reviewers
  - CR_Passed (Code Review passed)
  - Checks_Passed (CI checks passed)
  - AllQualityGatesPassed (both CR and Checks passed)
  - TimeToMerge (time from creation to merge in hours/minutes/seconds)

--- 

## Documentation:
The code is fully documented using Python docstrings and Sphinx. Documentation can be built using:
```bash
make html
```

Access the documentation in your browser at:
```bash
build/html/index.html
```

--- 
## Notes:
- All datetime values are UTC.
- The TimeToMerge field is computed as the diference between MergedAt and CreatedAt.
- The code is written to handle multiple raw JSON files independently.
- Code quality and style checks are included (Flake8 and Black)

## Example CSV:
```csv
PRNum,Title,Author,CreatedAt,MergedAt,Num_Reviewers,CR_Passed,Checks_Passed,AllQualityGatesPassed,TimeToMerge
6,Transformation step,PatV3-0,2025-11-12 10:28:52,2025-11-12 10:30:13,1,True,True,True,0 days 00:01:21
5,Extraction step,PatV3-0,2025-11-12 10:17:51,2025-11-12 10:18:38,1,True,True,True,0 days 00:00:47
4,Updating stale branch,PatV3-0,2025-11-12 10:08:02,2025-11-12 10:08:32,0,False,True,False,0 days 00:00:30
3,Code quality checks,PatV3-0,2025-11-12 10:01:02,2025-11-12 10:01:57,1,True,True,True,0 days 00:00:55
2,Transformation step,PatV3-0,2025-11-12 09:33:12,2025-11-12 09:33:50,1,True,False,False,0 days 00:00:38
1,Extraction step,PatV3-0,2025-11-12 09:31:20,2025-11-12 09:32:22,1,True,False,False,0 days 00:01:02
```
