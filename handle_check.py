#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
handle_check.py -- 仮の名（ハンドル）の検査
License: CC0 1.0 (public domain)

【位置づけ】うっかり個人情報を入れてしまうのを防ぐ「入口の網」です。完全ではありません。
  本名や住所のような、形のない個人情報は見分けられません。判断の最後は人です。
【訂正のポイント】
  ・文字列以外(None等)でも落ちない(False)。理由も返せる check_handle() を追加。
  ・全角の数字・＠・URL は NFKC で半角にそろえてから見る(全角すり抜けの防止)。
  ・電話番号は「ハイフン付き」だけでなく、数字が合計7桁以上でも拒否(v2と同じ基準)。
    例: 09012345678 / 090 1234 5678。
  ・www. や example.com のようなドメイン形式も拒否。
  ・前後の空白は除く。制御文字(改行など)は拒否。
  ・v2 の _check_handle が拒否するものは、すべてここでも拒否(テストで確認)。
実行:  python handle_check.py --demo / --test
"""
from __future__ import annotations

import argparse
import re
import sys
import unicodedata
import unittest
from typing import Tuple

MAX_HANDLE = 30
_EMAIL = re.compile(r"[\w.+-]+@[\w-]+(\.[\w-]+)+")
_URL = re.compile(r"http|www\.", re.I)   # v2 と同じく "http" を含むものは拒否
_DOMAIN = re.compile(r"\b[a-z0-9-]+\.(com|net|org|jp|co|io|info|me|app|dev)\b", re.I)


def check_handle(handle) -> Tuple[bool, str]:
    """(合格か, 理由)。"""
    if not isinstance(handle, str):
        return False, "文字列ではありません"
    h = unicodedata.normalize("NFKC", handle).strip()
    if not (1 <= len(h) <= MAX_HANDLE):
        return False, f"仮の名は1〜{MAX_HANDLE}文字です"
    if any(unicodedata.category(c).startswith("C") for c in h):
        return False, "制御文字は使えません"
    if "@" in h or _EMAIL.search(h):
        return False, "メールアドレスらしい文字は入れないでください"
    if _URL.search(h) or _DOMAIN.search(h):
        return False, "URLらしい文字は入れないでください"
    if len(re.sub(r"\D", "", h)) >= 7:
        return False, "電話番号らしい長い数字は入れないでください"
    return True, "OK"


def validate_participant_handle(handle: str) -> bool:
    """元の関数と同じ形(True/False)。"""
    return check_handle(handle)[0]


class TestHandle(unittest.TestCase):
    def test_good(self):
        for h in ("ありりん", "Genshin_01", "月の猫", "a"):
            self.assertTrue(validate_participant_handle(h), h)

    def test_length(self):
        self.assertFalse(validate_participant_handle(""))
        self.assertFalse(validate_participant_handle("   "))
        self.assertTrue(validate_participant_handle("a" * 30))
        self.assertFalse(validate_participant_handle("a" * 31))

    def test_email_url_phone(self):
        for h in ("a@b.com", "ａ＠ｂ.com", "http://x.y", "ＨＴＴＰＳ：//x", "www.x", "foo.com",
                  "03-1234-5678", "09012345678", "090 1234 5678", "０９０１２３４５６７８"):
            self.assertFalse(validate_participant_handle(h), h)

    def test_short_numbers_ok(self):
        self.assertTrue(validate_participant_handle("星2026"))

    def test_non_string_and_control(self):
        for h in (None, 123, b"abc", ["a"]):
            self.assertFalse(validate_participant_handle(h))
        self.assertFalse(validate_participant_handle("a\nb"))

    def test_reason(self):
        self.assertEqual(check_handle("ありりん"), (True, "OK"))
        self.assertIn("電話", check_handle("09012345678")[1])

    def test_at_least_as_strict_as_v2(self):
        try:
            from resonant_biosphere_v2 import GovernedBiosphere
        except ImportError:
            self.skipTest("v2 not found")
        samples = ["ok", "a@b", "HTTP://x", "1234567", "12345", "x" * 31, "", "ありりん", "foo https", "tel 0312345678"]
        for s in samples:
            try:
                GovernedBiosphere._check_handle(s)
                v2_ok = True
            except ValueError:
                v2_ok = False
            if not v2_ok:
                self.assertFalse(validate_participant_handle(s), s)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--demo", action="store_true")
    p.add_argument("--test", action="store_true")
    a = p.parse_args()
    if a.test:
        unittest.main(argv=[sys.argv[0]], verbosity=2)
        return
    for h in ("ありりん", "taro@example.com", "https://x.y", "090-1234-5678", "09012345678", "foo.com", ""):
        ok, why = check_handle(h)
        print(f"{'合格' if ok else '拒否'}  {h!r}: {why}")


if __name__ == "__main__":
    main()
