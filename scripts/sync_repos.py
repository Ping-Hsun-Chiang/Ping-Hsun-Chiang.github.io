#!/usr/bin/env python3
"""
Sync GitHub repositories to data/projects.json.

Fetches all repos owned by the user (public + private), compares with
data/tracked_repos.json, and appends placeholder entries for any new repos.
Other fields are left blank for manual completion.
"""

import json
import os
import urllib.request
from datetime import datetime, timezone

GITHUB_USERNAME = "Ping-Hsun-Chiang"
DATA_FILE = "data/projects.json"
TRACKED_FILE = "data/tracked_repos.json"
TOKEN = os.environ["GH_PAT"]


def github_get(url):
    req = urllib.request.Request(url, headers={
        "Authorization": f"token {TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "portfolio-sync-script",
    })
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def fetch_all_repos():
    repos, page = [], 1
    while True:
        batch = github_get(
            f"https://api.github.com/user/repos"
            f"?per_page=100&page={page}&type=owner&sort=created&direction=desc"
        )
        if not batch:
            break
        repos.extend(batch)
        page += 1
    return repos


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def main():
    projects = load_json(DATA_FILE)
    tracked = load_json(TRACKED_FILE)
    tracked_lower = {name.lower() for name in tracked}

    repos = fetch_all_repos()
    added = []

    for repo in repos:
        name = repo["name"]
        if name.lower() in tracked_lower:
            continue

        now = datetime.now(timezone.utc)
        projects.append({
            "date": f"{now.year}.{now.month:02d}",
            "category": "",
            "name": name,
            "desc": "",
            "url": repo["html_url"],
            "tags": [],
            "featured": False,
            "private": repo["private"],
        })
        tracked.append(name)
        tracked_lower.add(name.lower())
        added.append(name)
        print(f"  + {name}")

    if added:
        save_json(DATA_FILE, projects)
        save_json(TRACKED_FILE, sorted(tracked, key=str.lower))
        print(f"\nAdded {len(added)} new repo(s).")
    else:
        print("No new repos found.")


if __name__ == "__main__":
    main()
