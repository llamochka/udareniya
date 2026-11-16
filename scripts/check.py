#!/usr/bin/env python3
"""Проверка slovar.json: каждое слово с одним знаком ударения на гласной."""
import json, sys, pathlib
MARK = "́"; VOWELS = "аеёиоуыэюя"
p = pathlib.Path(__file__).resolve().parent.parent / "slovar.json"
slova = json.loads(p.read_text(encoding="utf-8"))["слова"]
bad = []
for k, e in slova.items():
    u = e.get("ударение", "")
    if k != k.lower():
        bad.append(f"{k}: ключ должен быть с маленькой буквы")
    if u.count(MARK) != 1:
        bad.append(f"{k}: нужен ровно один знак ударения, а их {u.count(MARK)}")
    elif u.replace(MARK, "") != k and not e.get("пишем_иначе"):
        bad.append(f"{k}: «{u}» без знака не совпадает со словом")
    elif u[u.index(MARK) - 1] not in VOWELS:
        bad.append(f"{k}: знак ударения стоит не после гласной")
    for f in ("источник", "добавлено"):
        if not e.get(f):
            bad.append(f"{k}: нет поля «{f}»")
print("\n".join(bad) or f"ок, слов: {len(slova)}")
sys.exit(1 if bad else 0)
