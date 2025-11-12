import os, json, logging
import pandas as pd
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def transformPRData(df):
    if df.empty:
        logging.warning("Input DataFrame is empty. No data to transform.")
        return df
<<<<<<< Updated upstream
    
    df["CreatedAt"] = pd.to_datetime(df["CreatedAt"], errors="coerce")
    df["MergedAt"] = pd.to_datetime(df["MergedAt"], errors="coerce")
=======

    df["CreatedAt"] = pd.to_datetime(df["CreatedAt"], errors="coerce").dt.tz_localize(
        None
    )
    df["MergedAt"] = pd.to_datetime(df["MergedAt"], errors="coerce").dt.tz_localize(
        None
    )
>>>>>>> Stashed changes
    df["CR_Passed"] = df["CR_Passed"].astype(bool)
    df["Checks_Passed"] = df["Checks_Passed"].astype(bool)
    df["AllQualityGatesPassed"] = df["CR_Passed"] & df["Checks_Passed"]
    df["TimeToMerge"] = (df["MergedAt"] - df["CreatedAt"])

    return df

def processRawFiles(rawDataDir, transformedDataDir):
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
    scriptDir = os.path.dirname(os.path.abspath(__file__))
    projectRoot = os.path.abspath(os.path.join(scriptDir, ".."))
    rawDataDir = os.path.join(projectRoot, "data", "raw")
    transformedDataDir = os.path.join(projectRoot, "data", "processed")

    logging.info("Starting per-file PR data transformation...")
    processRawFiles(rawDataDir, transformedDataDir)
    logging.info("Transformation complete.")


if __name__ == "__main__":
    main()
