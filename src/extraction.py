from datetime import datetime
from dotenv import load_dotenv
from yaspin import yaspin
import os, requests, json, logging, argparse, itertools, threading, time

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def getReviews(repo, pr_number, headers):
    #Fetching reviews for PR
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/reviews"
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    reviews = r.json()

    logging.debug(f"PR #{pr_number} reviews: {reviews}")

    latestReviewPerUser = {}
    for review in reviews:
        user = review["user"]["login"]
        latestReviewPerUser[user] = review["state"]

    approved = any(state == "APPROVED" for state in latestReviewPerUser.values())
    numReviewers = len(latestReviewPerUser)

    return approved, numReviewers

def getCheckStatus(repo, sha, headers):
    #Fetching check runs for commit {sha}
    url = f"https://api.github.com/repos/{repo}/commits/{sha}/check-runs"
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    data = r.json()

    checkRuns = data.get("check_runs", [])

    if not checkRuns:
        return False

    logging.debug(f"Commit {sha} check runs: {json.dumps(checkRuns, indent=2)}")
    return all(run.get("conclusion") == "success" for run in checkRuns)

def getMergedPRs(repo: str, perPage: int = 100, since: str = None, until: str = None):
    #Fetching merged PRs
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN not found in environment variables") 

    headers = {"Authorization": f"token {token}"}
    baseUrl = f"https://api.github.com/repos/{repo}/pulls"
    params = {
        "state": "closed",
        "perPage": perPage
    }
    PRs = []
    page = 1

    scriptDir = os.path.dirname(os.path.abspath(__file__))
    projectRoot = os.path.abspath(os.path.join(scriptDir, ".."))
    rawDataDir = os.path.join(projectRoot, "data", "raw")
    os.makedirs(rawDataDir, exist_ok=True)

    with yaspin(text="Fetching PRs...", color="cyan") as spinner:
        try:
            while True:
                params["page"] = page
                response = requests.get(baseUrl, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()

                if not data:
                    break

                for pr in data:
                    if not pr.get("merged_at"):
                        continue

                    mergedAt = datetime.strptime(pr["merged_at"], "%Y-%m-%dT%H:%M:%SZ")

                    if since and mergedAt < datetime.strptime(since, "%Y-%m-%d"):
                        continue
                    if until and mergedAt > datetime.strptime(until, "%Y-%m-%d"):
                        continue

                    prInfo = {
                        "PRNum": pr["number"],
                        "Title": pr["title"],
                        "Author": pr["user"]["login"],
                        "CreatedAt": pr["created_at"],
                        "MergedAt": pr["merged_at"],
                    }

                    approved, num_reviewers = getReviews(repo, pr["number"], headers)
                    prInfo["Num_Reviewers"] = num_reviewers
                    prInfo["CR_Passed"] = approved
                    prInfo["Checks_Passed"] = getCheckStatus(repo, pr["merge_commit_sha"], headers)

                    PRs.append(prInfo)

                page += 1

            spinner.ok("✔")

        except requests.exceptions.RequestException as e:
            spinner.fail("✖")
            logging.error(f"Error fetching PRs: {e}")

    outPath = os.path.join(rawDataDir, f"PRs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(outPath, "w") as f:
        json.dump(PRs, f, indent=4)

    logging.info(f"Fetched {len(PRs)} merged PRs from {repo}")
    logging.info(f"Raw PR data saved to {outPath}")
    return PRs

if __name__ == "__main__":
    print("Starting PR extraction script...")
    parser = argparse.ArgumentParser(description="Fetch merged PRs from a GitHub repository.")
    parser.add_argument("--repo", type=str, required=True, help="GitHub repository in the format 'owner/repo'")
    parser.add_argument("--since", type=str, help="Fetch PRs merged since this date (YYYY-MM-DD)")
    parser.add_argument("--until", type=str, help="Fetch PRs merged until this date (YYYY-MM-DD)")
    parser.add_argument("--per_page", type=int, default=100, help="Number of PRs to fetch per page (default: 100)")

    args = parser.parse_args()

    prs = getMergedPRs(args.repo, since=args.since, until=args.until)