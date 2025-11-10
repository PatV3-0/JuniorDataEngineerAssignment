from dotenv import load_dotenv
from datetime import datetime
import os, requests, json, logging, argparse, itertools, threading, time

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

#Loading spinner for long operations
def spinner_task(stop_event):
    spinner = itertools.cycle(['|', '/', '-', '\\'])
    while not stop_event.is_set():
        print(f"\rFetching PRs... {next(spinner)}", end="", flush=True)
        time.sleep(0.1)

def get_reviews(repo, pr_number, headers):
    #Fetching reviews for PR
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/reviews"
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    reviews = r.json()
    return any(review["state"] == "APPROVED" for review in reviews)

def get_check_status(repo, sha, headers):
    #Fetching check runs for commit {sha}
    url = f"https://api.github.com/repos/{repo}/commits/{sha}/check-runs"
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    data = r.json()
    return data.get("conclusion") == "success"

def get_merged_prs(repo: str, per_page: int = 100, since: str = None, until: str = None):
    #Fetching merged PRs
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN not found in environment variables") 

    headers = {"Authorization": f"token {token}"}
    base_url = f"https://api.github.com/repos/{repo}/pulls"
    params = {
        "state": "closed",
        "per_page": per_page
    }
    prs = []
    page = 1

    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, ".."))
    raw_data_dir = os.path.join(project_root, "data", "raw")
    os.makedirs(raw_data_dir, exist_ok=True)

    stop_event = threading.Event()
    spinner_thread = threading.Thread(target=spinner_task, args=(stop_event,))
    spinner_thread.start()

    try:
        while True:
            params["page"] = page
            response = requests.get(base_url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()

            if not data:
                break

            for pr in data:
                if not pr.get("merged_at"):
                    continue

                merged_at = datetime.strptime(pr["merged_at"], "%Y-%m-%dT%H:%M:%SZ")

                if since and merged_at < datetime.strptime(since, "%Y-%m-%d"):
                    continue
                if until and merged_at > datetime.strptime(until, "%Y-%m-%d"):
                    continue

                pr_info = {
                    "number": pr["number"],
                    "title": pr["title"],
                    "author": pr["user"]["login"],
                    "merged_at": pr["merged_at"],
                    "merge_commit_sha": pr["merge_commit_sha"],
                }

                pr_info["CR_Passed"] = get_reviews(repo, pr["number"], headers)
                pr_info["Checks_Passed"] = get_check_status(repo, pr["merge_commit_sha"], headers)

                prs.append(pr_info)

            page += 1

    finally:
        stop_event.set()
        spinner_thread.join()
        print("\rFetching PRs... Done!   ") 

    out_path = os.path.join(raw_data_dir, f"prs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(out_path, "w") as f:
        json.dump(prs, f, indent=4)

    logging.info(f"Fetched {len(prs)} merged PRs from {repo}")
    logging.info(f"Raw PR data saved to {out_path}")
    return prs

if __name__ == "__main__":
    print("Starting PR extraction script...")
    parser = argparse.ArgumentParser(description="Fetch merged PRs from a GitHub repository.")
    parser.add_argument("--repo", type=str, required=True, help="GitHub repository in the format 'owner/repo'")
    parser.add_argument("--since", type=str, help="Fetch PRs merged since this date (YYYY-MM-DD)")
    parser.add_argument("--until", type=str, help="Fetch PRs merged until this date (YYYY-MM-DD)")
    parser.add_argument("--per_page", type=int, default=100, help="Number of PRs to fetch per page (default: 100)")

    args = parser.parse_args()

    prs = get_merged_prs(args.repo, since=args.since, until=args.until)