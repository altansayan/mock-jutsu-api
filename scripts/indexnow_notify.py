"""
IndexNow Notifier — Mock Jutsu
Sends all indexable HOW-TO URLs to Bing/Yandex/Seznam via IndexNow protocol.

Usage:
    python scripts/indexnow_notify.py           # dry-run (print URLs only)
    python scripts/indexnow_notify.py --send    # actually POST to IndexNow
"""

import sys
import json
import urllib.request
import urllib.error

INDEXNOW_KEY  = "ce154125f79e407bafce853146460d3a"
INDEXNOW_HOST = "altansayan.github.io"
INDEXNOW_URL  = "https://api.indexnow.org/indexnow"
BASE_URL      = "https://altansayan.github.io/mock-jutsu-api/HOW-TO"
LANGS         = ["TR", "EN", "DE", "FR", "RU"]   # UK excluded (noindex)
BATCH_SIZE    = 500                                # IndexNow max per request


def build_url_list() -> list[str]:
    """Read sitemap-howto.xml and extract all non-UK URLs."""
    import os, re
    sitemap_path = os.path.join(
        os.path.dirname(__file__), "..", "HOW-TO", "sitemap-howto.xml"
    )
    with open(sitemap_path, encoding="utf-8") as f:
        content = f.read()
    urls = re.findall(r"<loc>(https?://[^<]+)</loc>", content)
    return urls


def send_batch(urls: list[str], dry_run: bool) -> None:
    payload = {
        "host": INDEXNOW_HOST,
        "key": INDEXNOW_KEY,
        "keyLocation": f"https://{INDEXNOW_HOST}/{INDEXNOW_KEY}.txt",
        "urlList": urls,
    }
    if dry_run:
        print(f"  [dry-run] Would send {len(urls)} URLs")
        return

    data = json.dumps(payload).encode("utf-8")
    req  = urllib.request.Request(
        INDEXNOW_URL,
        data=data,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            print(f"  ✓ {len(urls)} URLs sent — HTTP {resp.status}")
    except urllib.error.HTTPError as e:
        print(f"  ✗ HTTP {e.code}: {e.reason}")
    except urllib.error.URLError as e:
        print(f"  ✗ Network error: {e.reason}")


def main() -> None:
    dry_run = "--send" not in sys.argv

    urls = build_url_list()
    print(f"IndexNow Notifier — {len(urls)} URLs found")
    print(f"Mode: {'DRY RUN (add --send to actually notify)' if dry_run else 'LIVE SEND'}")
    print()

    for i in range(0, len(urls), BATCH_SIZE):
        batch = urls[i : i + BATCH_SIZE]
        batch_num = i // BATCH_SIZE + 1
        total_batches = (len(urls) + BATCH_SIZE - 1) // BATCH_SIZE
        print(f"Batch {batch_num}/{total_batches} ({len(batch)} URLs)...")
        send_batch(batch, dry_run)

    print()
    print("Done.")
    if dry_run:
        print("Run with --send to submit to Bing/Yandex/Seznam.")


if __name__ == "__main__":
    main()
