#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
captain_term.py -- 艦長の任期の見張り（共鳴生命圏 v2 に接続）
License: CC0 1.0 (public domain)

【位置づけ】組織モデル（シミュレーション）です。本物の統治の仕組みではありません。
【訂正のポイント】
  ・元のコードの trigger_captain_succession_protocol() は未定義だったため、実装した。
  ・「強制的に継承」ではなく、「公開の警告 + 継承議案の提出」まで。席を手渡せるのは、
    各側の2/3以上で可決された captain_succession の議案だけ（v2 の決め方を守る）。
  ・同じ任期に、警告と議案を何度も重ねない（一度だけ）。
  ・任期は「超えたら」（4期目から）。3期目はまだ正常。

実行:  python captain_term.py --demo / --test      （resonant_biosphere_v2.py と同じフォルダで）
"""
from __future__ import annotations

import argparse
import sys
import unittest
from dataclasses import dataclass
from typing import Optional

from resonant_biosphere_v2 import GovernedBiosphere, default_biosphere

OK_MSG = "STATUS: 龍骨、正常に次代へ巡航中。"
WARN_MSG = "WARNING: 席を次の命のために空ける時が来ました。Succession Motion Required."


@dataclass(frozen=True)
class TermReport:
    message: str
    over_limit: bool
    motion_id: Optional[int]    # 提出した（または既にある）継承議案
    newly_triggered: bool       # この呼び出しで警告を出したか


def _check_int(v, name, minimum):
    if isinstance(v, bool) or not isinstance(v, int) or v < minimum:
        raise ValueError(f"{name} は {minimum} 以上の整数です: {v!r}")


def check_captain_term(current_term: int, max_terms: int = 3) -> str:
    """元の関数と同じ形（文字列を返す）。副作用なし。"""
    _check_int(current_term, "current_term", 1)
    _check_int(max_terms, "max_terms", 1)
    return WARN_MSG if current_term > max_terms else OK_MSG


def trigger_captain_succession_protocol(b: GovernedBiosphere) -> Optional[int]:
    """公開の警告を記録し、継承議案を一度だけ提出する。席は動かさない。
    その任期で既に議案があれば、何もしない（None）。"""
    cap = b.captain()
    marker = f"[任期超過 第{len(b.captain_lineage) + 1}代 {b.captain_term}期目]"
    if any(marker in e.action for e in b.entries if e.actor_id == cap.id):
        return None
    b._append(cap.id, f"{marker} 任期を超えました。継承議案を提出します（可決されるまで席は動きません）", "public")
    m = b.propose(cap.id, f"{marker} 席を次へ手渡す", "captain_succession")
    return m.id


def watch_captain_term(b: GovernedBiosphere) -> TermReport:
    lim = b.captain_term_limit
    if lim is None:
        return TermReport("STATUS: 任期の定めなし。", False, None, False)
    msg = check_captain_term(b.captain_term, lim)
    if msg == OK_MSG:
        return TermReport(msg, False, None, False)
    mid = trigger_captain_succession_protocol(b)
    return TermReport(msg, True, mid, mid is not None)


class TestCaptainTerm(unittest.TestCase):
    def test_boundary(self):
        self.assertEqual(check_captain_term(3), OK_MSG)
        self.assertEqual(check_captain_term(4), WARN_MSG)

    def test_invalid(self):
        for a in [(0,), (-1,), (True,), (2.5,), (None,), (1, 0)]:
            with self.assertRaises(ValueError):
                check_captain_term(*a)

    def test_within_limit_no_action(self):
        b = default_biosphere()
        r = watch_captain_term(b)
        self.assertFalse(r.over_limit)
        self.assertIsNone(r.motion_id)

    def test_over_limit_files_motion_once(self):
        b = default_biosphere()
        for _ in range(3):
            b.advance_term()
        r1 = watch_captain_term(b)
        self.assertTrue(r1.over_limit and r1.newly_triggered)
        n = len(b.entries)
        r2 = watch_captain_term(b)
        self.assertTrue(r2.over_limit)
        self.assertFalse(r2.newly_triggered)
        self.assertEqual(len(b.entries), n)

    def test_seat_does_not_move_without_vote(self):
        b = default_biosphere()
        for _ in range(3):
            b.advance_term()
        r = watch_captain_term(b)
        before = b.captain().label
        with self.assertRaises(PermissionError):
            b.succeed_captain("次の艦長", r.motion_id)
        self.assertEqual(b.captain().label, before)

    def test_warning_is_public(self):
        b = default_biosphere()
        for _ in range(3):
            b.advance_term()
        watch_captain_term(b)
        self.assertTrue(any("任期超過" in e.action and e.visibility == "public" for e in b.entries))

    def test_no_limit(self):
        b = default_biosphere(captain_term_limit=None)
        for _ in range(9):
            b.advance_term()
        self.assertFalse(watch_captain_term(b).over_limit)

    def test_new_term_after_succession_resets(self):
        b = default_biosphere()
        for _ in range(3):
            b.advance_term()
        self.assertTrue(watch_captain_term(b).over_limit)
        b.captain_term = 1
        self.assertFalse(watch_captain_term(b).over_limit)

    def test_next_captain_gets_own_warning(self):
        b = default_biosphere()
        for _ in range(3):
            b.advance_term()
        watch_captain_term(b)
        b.captain_lineage.append("前の艦長")   # 継承後の状態（可決の流れは v2 のテストが担う）
        b.captain_term = 4
        self.assertTrue(watch_captain_term(b).newly_triggered)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--demo", action="store_true")
    p.add_argument("--test", action="store_true")
    a = p.parse_args()
    if a.test:
        unittest.main(argv=[sys.argv[0]], verbosity=2)
        return
    b = default_biosphere()
    for term in (1, 2, 3, 4):
        b.captain_term = term
        r = watch_captain_term(b)
        print(f"{term}期目: {r.message}" + (f"（議案#{r.motion_id}を提出）" if r.newly_triggered else ""))


if __name__ == "__main__":
    main()
