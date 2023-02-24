import requests
import json
import os
import csv
import pandas as pd
from dotenv import load_dotenv

# load environment variable from .env file
load_dotenv()

# define required variables
patToken = os.getenv("PAT_TOKEN")
branch = os.getenv("GITHUB_REF_NAME")
repositoryName = os.getenv("GITHUB_REPOSITORY")
header = {'Authorization': "Token "+patToken}
repo = repositoryName.split('/')[1]

# function to sort csv file by date
def sort_csv_by_date(file_path, sort_col):
    df = pd.read_csv(file_path)
    df.sort_values(by=[sort_col], inplace=True, ascending=False)
    df.to_csv(file_path, index=False, na_rep='None')

# get pr details from github
def get_prs(header, repositoryName, page=1, per_page=100):
    try:
        url = f"https://api.github.com/repos/{repositoryName}/pulls?state=all&per_page={per_page}&page={page}"
        response = requests.get(url, headers=header).json()
    except:
        raise Exception(f"Failed to retrive prs: {response.text}")
    return response


# get pr details from github
page = 1
per_page = 100
prList = []
while True:
    pr = get_prs(header, repositoryName, page, per_page)
    if not pr:
        break
    prList.extend(pr)
    page += 1

# Write the pr to a csv file
csvFileName = f"{repo}_pr.csv"
with open(csvFileName, "w", newline='') as prCSV:
    col_name = ["repository",
                "pr_id",
                "pr_number",
                "pr_url",
                "pr_title",
                "pr_body",
                "pr_base_branch",
                "pr_source_branch",
                "pr_state",
                "pr_created_at",
                "pr_closed_at",
                "pr_merge_at"]
    writer = csv.DictWriter(prCSV, fieldnames=col_name)
    writer.writeheader()

    # loop through prList to get all pr data
    for pr in prList:
        repository = repo
        pr_id = pr["id"]
        pr_number = pr["number"]
        pr_url = pr["html_url"]
        pr_title = pr["title"]
        pr_body = pr["body"]
        pr_base_branch = pr["base"]["ref"]
        pr_source_branch = pr["head"]["ref"]
        pr_state = pr["state"]
        pr_created_at = pr["created_at"]
        pr_closed_at = pr["closed_at"] #check_empty(pr["closed_at"])
        pr_merge_at = pr["merged_at"] #check_empty(pr["merged_at"])
        writer.writerow({"repository": repository,
                        "pr_id": pr_id,
                        "pr_number": pr_number,
                        "pr_url": pr_url,
                        "pr_title": pr_title,
                        "pr_body": pr_body,
                        "pr_base_branch": pr_base_branch,
                        "pr_source_branch": pr_source_branch,
                        "pr_state": pr_state,
                        "pr_created_at": pr_created_at,
                        "pr_closed_at": pr_closed_at,
                        "pr_merge_at": pr_merge_at})
    prCSV.close()

# sort the csv file by pr created date
sort_csv_by_date(csvFileName, "pr_created_at")
print(f"Retrieved and wrote {len(prList)} pr to the CSV file")

