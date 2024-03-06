import requests
import os
import time
import argparse


def get_member_names(api_key, base_url):
    headers = {"Authorization": "Bearer " + api_key}
    members_list = []
    page = 1
    per_page = 30  # default

    while True:
        url = f"{base_url}?per_page={per_page}&page={page}"
        response = requests.get(url, headers=headers)
        backoff_time = 1

        while response.status_code != 200:
            print(
                f"Request failed with status code {response.status_code}. Retrying in {backoff_time} seconds..."
            )
            time.sleep(backoff_time)
            backoff_time *= 2
            if backoff_time > 120:
                raise Exception("Maximum backoff time exceeded. Aborting.")
            response = requests.get(url, headers=headers)

        members_json = response.json()

        if not members_json:
            break

        for member in members_json:
            members_list.append(member["login"].lower())

        page += 1

    return members_list


def compare_team_and_org_members(api_key, org_slug, team_slug):
    try:
        organization_url = f"https://api.github.com/orgs/{org_slug}/members"
        team_url = f"https://api.github.com/orgs/{team_slug}/members"

        org_members = get_member_names(api_key, organization_url)
        team_members = get_member_names(api_key, team_url)
        return [member for member in team_members if member not in org_members]

    except Exception as e:
        print(str(e))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Compare GitHub team and organization members."
    )
    parser.add_argument("--key", required=True, help="API key for GitHub access")
    parser.add_argument("--org", required=True, help="GitHub organization slug")
    parser.add_argument("--team", required=True, help="GitHub team slug")

    args = parser.parse_args()

    result = compare_team_and_org_members(args.key, args.org, args.team)
    print(result)
