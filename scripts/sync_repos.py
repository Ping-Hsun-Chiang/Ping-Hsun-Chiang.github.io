#!/usr/bin/env python3
"""
Sync GitHub repositories to data/projects.json.

Compares GitHub repos against the 'github_repo' field in each project entry.
Appends a placeholder entry for any repo not yet tracked.
"""

import json
import os
import urllib.request
from datetime import datetime, timezone

GITHUB_USERNAME = "Ping-Hsun-Chiang"
DATA_FILE = "data/projects.json"
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


def get_known_repos(projects):
    return {p["github_repo"].lower() for p in projects if p.get("github_repo")}


def main():
    projects = load_json(DATA_FILE)
    known = get_known_repos(projects)

    repos = fetch_all_repos()
    added = []

    for repo in repos:
        if repo["name"].lower() in known:
            continue

        now = datetime.now(timezone.utc)
        projects.append({
            "date": f"{now.year}.{now.month:02d}",
            "category": "",
            "name": repo["name"],
            "desc": "",
            "url": repo["html_url"],
            "tags": [],
            "featured": False,
            "private": repo["private"],
            "github_repo": repo["name"],
        })
        known.add(repo["name"].lower())
        added.append(repo["name"])
        print(f"  + {repo['name']}")

    if added:
        save_json(DATA_FILE, projects)
        print(f"\nAdded {len(added)} new repo(s).")
    else:
        print("No new repos found.")


if __name__ == "__main__":
    main()
