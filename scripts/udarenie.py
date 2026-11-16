#!/usr/bin/env python3
"""Расставить ударения в тексте перед ИИ-озвучкой.

    echo "Сегодня катка не задалась" | python3 scripts/udarenie.py
    python3 scripts/udarenie.py --ruaccent < текст.txt

Без флага подставляются только слова из slovar.json.
С --ruaccent сначала работает модель RuAccent (pip install ruaccent),
потом словарь исправляет то, где она ошибается.
"""
import json, re, sys, pathlib

MARK = "́"
VOWELS = "аеёиоуыэюяАЕЁИОУЫЭЮЯ"
ROOT = pathlib.Path(__file__).resolve().parent.parent


def load(path=ROOT / "slovar.json"):
    return json.loads(pathlib.Path(path).read_text(encoding="utf-8"))["слова"]


def plus_to_mark(text):
    """RuAccent пишет «+» перед ударной гласной; ElevenLabs понимает знак после гласной."""
    text = re.sub(r"\+([" + VOWELS + "])", lambda m: m.group(1) + MARK, text)
    # в словах с одной гласной знак не нужен: «не́», «мы́» модель озвучки только сбивают
    return re.sub(r"[А-Яа-яЁё" + MARK + r"]+",
                  lambda m: m.group(0).replace(MARK, "")
                  if sum(c in VOWELS for c in m.group(0)) == 1 else m.group(0), text)


def _same_case(src, dst):
    if src.isupper() and len(src) > 1:
        return dst.upper()
    if src[:1].isupper():
        return dst[:1].upper() + dst[1:]
    return dst


def apply(text, slova):
    def repl(m):
        word = m.group(0)
        bare = word.replace(MARK, "")
        e = slova.get(bare.lower())
        if not e or "омограф" in e.get("заметка", ""):
            return word
        return _same_case(bare, e["ударение"])
    return re.sub(r"[А-Яа-яЁё" + MARK + r"]+", repl, text)


def main():
    text = sys.stdin.read()
    if "--ruaccent" in sys.argv:
        from ruaccent import RUAccent
        a = RUAccent()
        a.load(omograph_model_size="turbo3.1", use_dictionary=True, tiny_mode=False)
        text = "\n".join(plus_to_mark(a.process_all(line)) if line.strip() else line
                         for line in text.split("\n"))
    sys.stdout.write(apply(text, load()))


if __name__ == "__main__":
    main()
