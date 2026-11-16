#!/usr/bin/env python3
"""Разбор заявки на слово (Actions). Пишет otvet.md; с --add «#N» добавляет слово в slovar.json."""
import datetime, json, os, re, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from wiki import variants

MARK = "́"; VOWELS = "аеёиоуыэюя"
ROOT = pathlib.Path(__file__).resolve().parent.parent
body = os.environ.get("BODY", "")

def field(name):
    m = re.search(r"### " + re.escape(name) + r"\s*\n+(.+?)(?:\n###|\Z)", body, re.S)
    return m.group(1).strip() if m else ""

slovo = field("Слово, как пишется").lower()
ud = field("То же слово со знаком ударения")
# кАтка -> ка́тка
caps = [c for c in ud if c in VOWELS.upper()]
if MARK not in ud and len(caps) == 1:
    i = ud.index(caps[0]); ud = ud[:i] + caps[0].lower() + MARK + ud[i + 1:]
ud = ud.lower()

problems = []
if not re.fullmatch(r"[а-яё]+", slovo):
    problems.append("В поле «слово» должно быть одно русское слово без пробелов.")
if ud.count(MARK) != 1 or ud.replace(MARK, "") != slovo:
    problems.append("Ударение указано неверно: нужно то же слово с одним знаком ударения.")

try:
    wv = variants(slovo) if not problems else []
except Exception as e:
    wv = None

lines = [f"**{slovo}** → **{ud}**", ""]
if problems:
    lines += ["Не могу принять заявку:"] + [f"- {p}" for p in problems]
elif wv is None:
    lines.append("Викисловарь сейчас не ответил, сверка будет вручную.")
elif not wv:
    lines.append("В Викисловаре такого слова нет. Скорее всего жаргон или новое слово, решаем вручную.")
elif ud in wv:
    lines.append(f"Викисловарь согласен: {', '.join(wv)}.")
else:
    lines.append(f"⚠️ Викисловарь даёт другое: {', '.join(wv)}. Проверь, не опечатка ли.")
if wv and len(wv) > 1:
    lines.append("У слова несколько вариантов ударения, возможно это омограф: автозаменой его ставить нельзя.")
lines += ["", "Владелец словаря ставит метку «принято», и слово добавляется само."]
pathlib.Path("otvet.md").write_text("\n".join(lines), encoding="utf-8")

if "--add" in sys.argv:
    if problems:
        sys.exit("заявка с ошибками, не добавляю")
    p = ROOT / "slovar.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    e = {"ударение": ud, "источник": "заявка " + sys.argv[sys.argv.index("--add") + 1],
         "добавлено": datetime.date.today().isoformat()}
    if wv and len(wv) > 1:
        e["заметка"] = "омограф по Викисловарю: " + ", ".join(wv)
    d["слова"][slovo] = e
    d["слова"] = dict(sorted(d["слова"].items()))
    p.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
