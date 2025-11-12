"""
Module for transforming raw pull request data into a structured format.

This module reads raw JSON files containing pull request data, processes
them to compute additional fields, and saves the transformed data as CSV files.

Functions:
- transformPRData(df): Transforms a DataFrame of pull request data.
- processRawFiles(rawDataDir, transformedDataDir): Processes all raw JSON files
in the specified directory and saves transformed CSV files.
- main(): Main function to execute the transformation process.
"""

import json
import logging
import os
import pandas as pd

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def transformPRData(df):
    """
    Transforms the pull request DataFrame by converting date fields,
    computing quality gate status, and calculating time to merge.

    Parameters:
        df (pd.DataFrame): DataFrame containing raw pull request data:
            - CreatedAt (str): Creation timestamp of the PR.
            - MergedAt (str): Merge timestamp of the PR.
            - CR_Passed (bool): Code review passed status.
            - Checks_Passed (bool): Automated checks passed status.
    Returns:
        pd.DataFrame: Transformed DataFrame with additional computed fields:
            - CreatedAt (datetime): Parsed creation timestamp.
            - MergedAt (datetime): Parsed merge timestamp.
            - CR_Passed (bool): Code review passed status.
            - Checks_Passed (bool): Automated checks passed status.
            - AllQualityGatesPassed (bool): True if both CR_Passed and Checks_Passed
              are True.
            - TimeToMerge (timedelta): Time difference between MergedAt and CreatedAt.
    """

    if df.empty:
        logging.warning("Input DataFrame is empty. No data to transform.")
        return df

    df["CreatedAt"] = pd.to_datetime(df["CreatedAt"], errors="coerce").dt.tz_localize(
        None
    )
    df["MergedAt"] = pd.to_datetime(df["MergedAt"], errors="coerce").dt.tz_localize(
        None
    )
    df["CR_Passed"] = df["CR_Passed"].astype(bool)
    df["Checks_Passed"] = df["Checks_Passed"].astype(bool)
    df["AllQualityGatesPassed"] = df["CR_Passed"] & df["Checks_Passed"]
    df["TimeToMerge"] = df["MergedAt"] - df["CreatedAt"]

    return df


def processRawFiles(rawDataDir, transformedDataDir):
    """
    Processes all raw JSON files in the specified directory, transforms
    the pull request data, and saves the results as CSV files.

    Parameters:
        rawDataDir (str): Directory containing raw JSON files.
        transformedDataDir (str): Directory to save transformed CSV files.
    Returns:
        None
    """
    os.makedirs(transformedDataDir, exist_ok=True)

    for filename in os.listdir(rawDataDir):
        if not filename.endswith(".json"):
            continue

        filePath = os.path.join(rawDataDir, filename)
        try:
            with open(filePath, "r") as f:
                prs = json.load(f)
        except json.JSONDecodeError as e:
            logging.error(f"Error decoding JSON from file {filePath}: {e}")
            continue

        df = pd.DataFrame(prs)
        if df.empty:
            logging.warning(f"No data found in {filename}, skipping.")
            continue

        dfTransformed = transformPRData(df)

        baseName = os.path.splitext(filename)[0]
        outPath = os.path.join(transformedDataDir, f"{baseName}_transformed.csv")

        dfTransformed.to_csv(outPath, index=False)
        logging.info(f"Transformed data saved to {outPath}")


def main():
    """
    Main function to execute the transformation process.

    Sets up directory paths and initiates processing of raw files.
    Returns:
        None
    """
    scriptDir = os.path.dirname(os.path.abspath(__file__))
    projectRoot = os.path.abspath(os.path.join(scriptDir, ".."))
    rawDataDir = os.path.join(projectRoot, "data", "raw")
    transformedDataDir = os.path.join(projectRoot, "data", "processed")

    logging.info("Starting per-file PR data transformation...")
    processRawFiles(rawDataDir, transformedDataDir)
    logging.info("Transformation complete.")


if __name__ == "__main__":
    main()
