import logging
import os
import sys
from extract import getMergedPRs
from transform import processRawFiles

scriptDir = os.path.dirname(os.path.abspath(__file__))
srcDir = os.path.abspath(os.path.join(scriptDir, "src"))
if srcDir not in sys.path:
    sys.path.insert(0, srcDir)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def main():
    """
    Main function to orchestrate the extraction and transformation
    of pull request data.

    It first extracts merged PRs from the specified repository,
    saves the raw data as JSON files, and then processes these files
    to produce transformed CSV outputs.

    Returns:
        None
    """

    projectRoot = scriptDir
    rawDataDir = os.path.join(projectRoot, "data", "raw")
    transformedDataDir = os.path.join(projectRoot, "data", "transformed")
    os.makedirs(rawDataDir, exist_ok=True)
    os.makedirs(transformedDataDir, exist_ok=True)

    logging.info("Starting PR data extraction...")
    """
    Extract merged PRs and save as JSON files.
    Replace 'owner/repo' with the actual repository name and optional date filters
    'since' and 'until'.
    """
    repo = "Scytale-exercise/scytale-repo3"
    getMergedPRs(repo, perPage=100, since=None, until=None)

    logging.info("Starting PR data transformation...")
    processRawFiles(rawDataDir, transformedDataDir)

    logging.info("Data extraction and transformation complete.")


if __name__ == "__main__":
    main()
