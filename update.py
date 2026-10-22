"""Update the unified FnDepot source using original authors' stable Releases."""
import copy
import json
import os
from pathlib import Path
import re
import urllib.request

ROOT = Path(__file__).resolve().parent
SOURCES = {
    "clash-for-fnos": ("chenpingonline/Clash-for-fnos", "fpk/manifest", {
        "x86": "Clash.for.fnos_{version}_x86_64.fpk",
        "arm": "Clash.for.fnos_{version}_arm64.fpk",
        "all": "Clash.for.fnos_{version}_all.fpk",
    }),
    "fnmusic-ext": ("javycoder/fnos_music_ext", "packaging/fpk/manifest.in", {
        "all": "fnmusic-ext-{version}.fpk",
    }),
}


def fetch(url):
    headers = {"User-Agent": "zunney-FnDepot", "Accept": "application/vnd.github+json"}
    # Only send the workflow token to GitHub API, never to asset/raw hosts.
    if url.startswith("https://api.github.com/") and os.environ.get("GH_TOKEN"):
        headers["Authorization"] = "Bearer " + os.environ["GH_TOKEN"]
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=60) as response:
        return response.read().decode("utf-8")


def update_app(app_id, app, release, manifest):
    repo, _, filenames = SOURCES[app_id]
    tag = release["tag_name"]
    if release.get("draft") or release.get("prerelease") or not re.fullmatch(r"v?\d+\.\d+\.\d+", tag):
        raise ValueError(f"{app_id}: expected a stable release")
    version = tag.removeprefix("v")
    fields = dict(re.findall(r"^([\w_-]+)[ \t]*=[ \t]*(.*?)[ \t]*$", manifest.replace("@VERSION@", version), re.M))
    if fields.get("appname") != app_id or fields.get("version") != version:
        raise ValueError(f"{app_id}: manifest identity/version mismatch")
    if not re.fullmatch(r"\d+(?:\.\d+)+", fields.get("os_min_version", "")):
        raise ValueError(f"{app_id}: missing minimum OS version")
    assets = {asset["name"]: asset for asset in release["assets"]}
    packages = {}
    for arch, pattern in filenames.items():
        name = pattern.format(version=version)
        asset = assets[name]  # Fail rather than publishing an incomplete architecture set.
        digest = asset.get("digest", "")
        url = f"https://github.com/{repo}/releases/download/{tag}/{name}"
        if asset["browser_download_url"] != url or not re.fullmatch(r"sha256:[0-9a-f]{64}", digest):
            raise ValueError(f"{app_id}: invalid asset URL or SHA256")
        if type(asset["size"]) is not int or asset["size"] <= 0:
            raise ValueError(f"{app_id}: invalid asset size")
        packages[arch] = {"download_url": url, "sha256": digest[7:], "size": asset["size"]}
    result = copy.deepcopy(app)
    releases = result.setdefault("releases", {})
    if version in releases and releases[version]["packages"] != packages:
        raise ValueError(f"{app_id}: published package was replaced; manual review required")
    releases[version] = {
        "updated_at": release["published_at"],
        "changelog": (release.get("body") or "")[:12000],
        "os_min_version": fields["os_min_version"],
        "packages": packages,
    }
    result["releases"] = dict(sorted(releases.items(), key=lambda p: tuple(map(int, p[0].split('.'))), reverse=True)[:100])
    result["platform"] = ["x86", "arm"] if app_id == "clash-for-fnos" else ["all"]
    return result


def main():
    path = ROOT / "fnpack.json"
    index = json.loads(path.read_text(encoding="utf-8-sig"))
    for app_id, (repo, manifest_path, _) in SOURCES.items():
        release = json.loads(fetch(f"https://api.github.com/repos/{repo}/releases/latest"))
        tag = release["tag_name"]
        if not re.fullmatch(r"v?\d+\.\d+\.\d+", tag):
            raise ValueError("Unexpected release tag")
        manifest = fetch(f"https://raw.githubusercontent.com/{repo}/{tag}/{manifest_path}")
        index["apps"][app_id] = update_app(app_id, index["apps"][app_id], release, manifest)
        print(f"{app_id}: {tag}")
    # Write only after every application has passed validation.
    path.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
