#!/usr/bin/env python3
"""Refresh the two data files that are filled automatically.

  data/auto/episodes.json     Main Branch episodes, from the YouTube channel feed
  data/auto/argocd_prs.json   the latest merged Argo CD pull requests, from the GitHub API

Uses only the Python standard library. If a source cannot be reached, the existing file is kept,
so a failed run never empties a list on the site.
"""
import json
import os
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AUTO = ROOT / "data" / "auto"

YOUTUBE_CHANNEL_ID = "UCQAHzd7CugA5rejLhkw54hw"
GITHUB_USER = "ppapapetrou76"
GITHUB_REPO = "argoproj/argo-cd"
RECENT_PRS = 8

ATOM = "{http://www.w3.org/2005/Atom}"
YT = "{http://www.youtube.com/xml/schemas/2015}"


def fetch(url, headers=None):
    req = urllib.request.Request(url, headers={"User-Agent": "pat-site-updater", **(headers or {})})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()


def write_if_changed(path, data):
    text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    if path.exists() and path.read_text(encoding="utf-8") == text:
        print(f"{path.name}: no change")
        return
    path.write_text(text, encoding="utf-8")
    print(f"{path.name}: updated, {len(data)} entries")


def update_episodes():
    feed = fetch(f"https://www.youtube.com/feeds/videos.xml?channel_id={YOUTUBE_CHANNEL_ID}")
    root = ET.fromstring(feed)
    episodes = []
    for entry in root.findall(f"{ATOM}entry"):
        video_id = entry.findtext(f"{YT}videoId")
        raw_title = entry.findtext(f"{ATOM}title") or ""
        # Titles look like "The Main Branch Video Podcast - Episode 3 : From Junior to ..."
        match = re.search(r"Episode\s+(\d+)\s*[:\-]\s*(.+)$", raw_title)
        if not match:
            continue  # shorts and clips are not episodes
        episodes.append({
            "id": video_id,
            "number": int(match.group(1)),
            "title": match.group(2).strip(),
            "url": f"https://www.youtube.com/watch?v={video_id}",
            "published": (entry.findtext(f"{ATOM}published") or "")[:10],
        })
    if not episodes:
        raise RuntimeError("the feed has no episodes")
    # The feed only lists the latest uploads, so keep older episodes we already know about.
    path = AUTO / "episodes.json"
    known = {e["id"]: e for e in json.loads(path.read_text(encoding="utf-8"))} if path.exists() else {}
    known.update({e["id"]: e for e in episodes})
    merged = sorted(known.values(), key=lambda e: e["number"], reverse=True)
    write_if_changed(path, merged)


def update_prs():
    query = f"repo:{GITHUB_REPO}+author:{GITHUB_USER}+is:pr+is:merged"
    headers = {"Accept": "application/vnd.github+json"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = fetch(f"https://api.github.com/search/issues?q={query}&sort=updated&order=desc&per_page=40", headers)
    items = json.loads(body)["items"]
    prs = []
    for item in items:
        title = item["title"].strip()
        if re.search(r"cherry[- ]pick", title, re.I):
            continue  # backports repeat the original pull request
        prs.append({
            "number": item["number"],
            "title": title,
            "url": item["html_url"],
            "merged": (item.get("pull_request", {}).get("merged_at") or item["closed_at"])[:10],
        })
    prs.sort(key=lambda p: p["merged"], reverse=True)
    if not prs:
        raise RuntimeError("the search returned no pull requests")
    write_if_changed(AUTO / "argocd_prs.json", prs[:RECENT_PRS])


def main():
    AUTO.mkdir(parents=True, exist_ok=True)
    failed = False
    for name, job in (("episodes", update_episodes), ("pull requests", update_prs)):
        try:
            job()
        except Exception as err:  # keep the old data and report it
            failed = True
            print(f"could not update {name}: {err}", file=sys.stderr)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
