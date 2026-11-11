#!/usr/bin/env python3
"""Create or update the labels in labels.toml in the owner's repositories.

Without --apply it only reads labels.toml and, when it has a token, prints what
it would change. It never deletes a label. Reads GITHUB_API_URL,
GITHUB_REPOSITORY_OWNER and LABELS_TOKEN, which needs read:repository and
write:issue.
"""
import argparse
import json
import os
import re
import sys
import tomllib
import urllib.error
import urllib.parse
import urllib.request

COLOR = re.compile(r"^[0-9a-f]{6}$")


def load_labels(path):
    with open(path, "rb") as f:
        labels = tomllib.load(f).get("label", [])
    names = set()
    for label in labels:
        unknown = set(label) - {"name", "color", "description", "repos"}
        if unknown:
            sys.exit(f"{path}: {label.get('name')}: unknown keys {sorted(unknown)}")
        if not label.get("name") or label["name"] in names:
            sys.exit(f"{path}: a label has no name, or its name is used twice")
        if not COLOR.match(label.get("color", "")):
            sys.exit(f"{path}: {label['name']}: color must be six lower-case hex digits")
        names.add(label["name"])
    return labels


class Forge:
    def __init__(self, api, token):
        self.api, self.token = api.rstrip("/"), token

    def call(self, method, path, body=None):
        request = urllib.request.Request(
            self.api + path, method=method,
            data=None if body is None else json.dumps(body).encode(),
            headers={"Authorization": f"token {self.token}",
                     "Content-Type": "application/json", "Accept": "application/json"})
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return response.status, json.load(response)
        except urllib.error.HTTPError as error:
            if error.code == 404:
                return 404, None
            sys.exit(f"{method} {path}: HTTP {error.code}: {error.read().decode(errors='replace')}")

    def pages(self, path):
        page = 1
        while True:
            sep = "&" if "?" in path else "?"
            _, items = self.call("GET", f"{path}{sep}limit=50&page={page}")
            items = items.get("data", items) if isinstance(items, dict) else items
            if not items:
                return
            yield from items
            page += 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="make the changes")
    parser.add_argument("--labels", default="labels.toml")
    args = parser.parse_args()

    labels = load_labels(args.labels)
    print(f"{args.labels}: {len(labels)} labels")
    token = os.environ.get("LABELS_TOKEN")
    if not token:
        if args.apply:
            sys.exit("LABELS_TOKEN is not set")
        print("No LABELS_TOKEN: checked the file only.")
        return

    forge = Forge(os.environ["GITHUB_API_URL"], token)
    owner = os.environ["GITHUB_REPOSITORY_OWNER"]
    q = urllib.parse.quote
    changes = 0
    for repo in forge.pages("/repos/search?q="):
        if repo["owner"]["login"].lower() != owner.lower() or repo["archived"] or repo["mirror"]:
            continue
        name = repo["name"]
        status, _ = forge.call("GET", f"/repos/{q(owner)}/{q(name)}/contents/renovate.json")
        if status == 404:
            continue
        existing = {l["name"]: l for l in forge.pages(f"/repos/{q(owner)}/{q(name)}/labels")}
        for label in labels:
            if "repos" in label and name not in label["repos"]:
                continue
            want = {"name": label["name"], "color": "#" + label["color"],
                    "description": label.get("description", "")}
            have = existing.get(label["name"])
            if have is None:
                action, path, method = "create", f"/repos/{q(owner)}/{q(name)}/labels", "POST"
            elif (have["color"].lstrip("#").lower(), have.get("description", "")) != \
                    (label["color"], want["description"]):
                action, path, method = "update", f"/repos/{q(owner)}/{q(name)}/labels/{have['id']}", "PATCH"
            else:
                continue
            changes += 1
            print(f"{name}: {action} {label['name']}")
            if args.apply:
                forge.call(method, path, want)
    print(f"{changes} change(s){'' if args.apply else ' planned; run with --apply to make them'}")


if __name__ == "__main__":
    main()
