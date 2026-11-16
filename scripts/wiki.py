#!/usr/bin/env python3
"""Как слово ударяется по Викисловарю: python3 scripts/wiki.py катка"""
import json, re, sys, time, urllib.parse, urllib.request

def variants(word):
    u = "https://ru.wiktionary.org/w/api.php?" + urllib.parse.urlencode(dict(
        action="parse", page=word, prop="wikitext", format="json", formatversion=2))
    req = urllib.request.Request(u, headers={"User-Agent": "udareniya-bot/1.0 (github.com/llamochka/udareniya)"})
    for i in range(4):
        try:
            d = json.load(urllib.request.urlopen(req, timeout=20))
            break
        except urllib.error.HTTPError as e:
            if e.code != 429 or i == 3:
                raise
            time.sleep(5 * (i + 1))
    if "error" in d:
        return []
    found = re.findall(r"\{\{по-слогам\|([^}]*)\}\}", d["parse"]["wikitext"])
    out = []
    for f in found:
        v = f.replace("|", "").replace(".", "")
        if v not in out:
            out.append(v)
    return out

if __name__ == "__main__":
    print(json.dumps(variants(sys.argv[1].strip().lower()), ensure_ascii=False))
