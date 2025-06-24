import requests
import re
import pandas as pd
import os

def main():
    url = "https://github.com/mlflow/mlflow/releases"
    response = requests.get(url)
    
    regex = r"releases/tag/([^\"<]*)"
    versions = re.findall(regex, response.text)

    if not os.path.exists("versions.csv") or os.stat("versions.csv").st_size == 0:
        stored_versions = pd.DataFrame({"version": []})
    else:
        stored_versions = pd.read_csv("versions.csv")

    new_versions = [version for version in versions if version not in stored_versions["version"].values]

    if new_versions:
        print(f"New versions found: {new_versions}")
        stored_versions = pd.concat([stored_versions, pd.DataFrame({"version": new_versions})])
        stored_versions.to_csv("versions.csv", index=False)
    else:
        print("No new versions found")


if __name__ == "__main__":
    main()