#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
voting_audit.py -- 共鳴多数の監査：audit_voting_resonance()
License: CC0 1.0

「全体の多数決ではなく、人間側とAI側の両方で多数であること」を監査します。
判定のしかたは resonant_biosphere_v2 の GroupTally と同じ（同じ規則を二重に書かない）。

【元のコードの問題と、訂正】
  ・先頭の `human_passed and ai_passed` が、関数の外にある式で、読み込むだけで NameError になる
      → 取り除いた
  ・bool しか返さないため、「却下」と「まだ決められない（定足数に届いていない）」の区別がつかない
      （コメントには HOLD/FAILED とあるのに、実際は False だけ）
      → passed / failed / pending を返す。`if audit_voting_resonance(...)` と書く使い方は、そのまま動く
  ・定足数が「6」と固定で、席数が変わると合わない
      → 席数（既定12）の半数以上、とした
  ・定足数を「賛成＋反対」で数えていたため、棄権が“出席”に入らない
      → v2 と同じく、棄権も出席に数える（賛成4・棄権2でも、6席が投票したことになる）
  ・"yes"/"no" 以外の値（"YES"、None、typo）が、黙って数えられなかった
      → 大文字小文字は直し、「賛成/反対/棄権」も受け付け、それ以外は ValueError（票が消えるのを防ぐ）
  ・席の数を超える票や、席のない投票者が混じっても、気づけなかった
      → 席数を超える票は ValueError。名簿（human_ids / ai_ids）を渡せば、席のない投票者も止める
  ・基本議案（各側の2/3以上）に対応していなかった
      → fundamental=True で対応

実行:
    python voting_audit.py --demo
    python voting_audit.py --test
"""

from __future__ import annotations

import argparse
import random
import sys
import unittest
from dataclasses import dataclass
from typing import Dict, Iterable, Optional, Tuple

from resonant_biosphere_v2 import GroupTally

CHOICE_ALIASES = {"賛成": "yes", "反対": "no", "棄権": "abstain"}
VALID = ("yes", "no", "abstain")

PASSED, FAILED, PENDING = "passed", "failed", "pending"


@dataclass(frozen=True)
class AuditResult:
    status: str                  # passed / failed / pending
    human: GroupTally
    ai: GroupTally
    reasons: Tuple[str, ...] = ()

    def __bool__(self) -> bool:  # 元の「True なら可決」という使い方を保つ
        return self.status == PASSED


def _count(votes: Dict[str, str], seats: int, side: str,
           valid_ids: Optional[Iterable[str]]) -> GroupTally:
    if seats <= 0:
        raise ValueError(f"{side}側の席数は1以上にしてください")
    if len(votes) > seats:
        raise ValueError(f"{side}側の票（{len(votes)}）が席数（{seats}）を超えています")
    if valid_ids is not None:
        extra = set(votes) - set(valid_ids)
        if extra:
            raise ValueError(f"{side}側に席のない投票者がいます: {sorted(extra)}")

    counts = {"yes": 0, "no": 0, "abstain": 0}
    for voter, raw in votes.items():
        if not isinstance(raw, str):
            raise ValueError(f"{side}側 {voter} の票が文字列ではありません: {raw!r}")
        choice = CHOICE_ALIASES.get(raw.strip(), raw.strip().lower())
        if choice not in VALID:
            raise ValueError(f"{side}側 {voter} の票が不明です: {raw!r}（yes / no / abstain）")
        counts[choice] += 1
    return GroupTally(seats, counts["yes"], counts["no"], counts["abstain"])


def audit_voting_resonance(
    human_votes: Dict[str, str],
    ai_votes: Dict[str, str],
    *,
    human_seats: int = 12,
    ai_seats: int = 12,
    fundamental: bool = False,
    human_ids: Optional[Iterable[str]] = None,
    ai_ids: Optional[Iterable[str]] = None,
) -> AuditResult:
    """人間側、AI側、それぞれの独立した『多数の合意』があるかを監査する。

    通常議案: 各側で、賛成が反対を上回る。
    基本議案: 各側で、賛成が（賛成＋反対）の2/3以上。
    定足数  : 各側の席の半数以上が投票（棄権を含む）。満たさなければ pending。
    """
    h = _count(human_votes, human_seats, "人間", human_ids)
    a = _count(ai_votes, ai_seats, "AI", ai_ids)
    reasons = []

    # 定足数に届かない側があれば、まだ決められない（却下ではない）
    for name, g in (("人間", h), ("AI", a)):
        if not g.quorum:
            need = (g.seats + 1) // 2
            reasons.append(f"{name}側の定足数に届いていません（{g.voted}/{g.seats}席が投票、{need}席が必要）")
    if reasons:
        return AuditResult(PENDING, h, a, tuple(reasons))

    rule = "各側で賛成が2/3以上" if fundamental else "各側で賛成が反対を上回る"
    for name, g in (("人間", h), ("AI", a)):
        if not g.passes(fundamental):
            reasons.append(f"{name}側が条件を満たしません（賛成{g.yes}・反対{g.no}・棄権{g.abstain}。条件：{rule}）")
    if reasons:
        total_yes, total_no = h.yes + a.yes, h.no + a.no
        if total_yes > total_no:
            reasons.append("全体では賛成が多数でも、片方の側で多数でないため、通りません（共鳴多数）")
        return AuditResult(FAILED, h, a, tuple(reasons))

    return AuditResult(PASSED, h, a, ("【共鳴多数】人間側でもAI側でも多数のため、可決",))


# ── テスト ─────────────────────────────────────────────────────────
def _votes(prefix: str, yes: int, no: int, abstain: int = 0) -> Dict[str, str]:
    v: Dict[str, str] = {}
    i = 0
    for choice, n in (("yes", yes), ("no", no), ("abstain", abstain)):
        for _ in range(n):
            i += 1
            v[f"{prefix}{i:02d}"] = choice
    return v


class TestAudit(unittest.TestCase):
    def test_passes_when_both_sides_agree(self):
        r = audit_voting_resonance(_votes("H", 8, 4), _votes("A", 7, 5))
        self.assertEqual(r.status, PASSED)
        self.assertTrue(r)

    def test_humans_cannot_outvote_ais(self):
        r = audit_voting_resonance(_votes("H", 12, 0), _votes("A", 0, 12))
        self.assertEqual(r.status, FAILED)
        self.assertFalse(r)

    def test_ais_cannot_outvote_humans(self):
        self.assertEqual(audit_voting_resonance(_votes("H", 0, 12), _votes("A", 12, 0)).status, FAILED)

    def test_total_majority_is_not_enough_and_says_so(self):
        r = audit_voting_resonance(_votes("H", 5, 7), _votes("A", 12, 0))
        self.assertEqual(r.status, FAILED)
        self.assertTrue(any("共鳴多数" in x for x in r.reasons))

    def test_tie_fails(self):
        self.assertEqual(audit_voting_resonance(_votes("H", 6, 6), _votes("A", 12, 0)).status, FAILED)

    def test_quorum_unmet_is_pending_not_failed(self):
        r = audit_voting_resonance(_votes("H", 5, 0), _votes("A", 12, 0))
        self.assertEqual(r.status, PENDING)
        self.assertFalse(r)
        self.assertTrue(any("定足数" in x for x in r.reasons))

    def test_pending_even_if_other_side_would_fail(self):
        # 人間側がまだ決められないので、AI側が反対でも「却下」とは決めない
        self.assertEqual(audit_voting_resonance(_votes("H", 5, 0), _votes("A", 0, 12)).status, PENDING)

    def test_abstain_counts_toward_quorum(self):
        r = audit_voting_resonance(_votes("H", 4, 0, 2), _votes("A", 12, 0))
        self.assertEqual(r.status, PASSED)

    def test_all_abstain_side_fails(self):
        self.assertEqual(audit_voting_resonance(_votes("H", 0, 0, 12), _votes("A", 12, 0)).status, FAILED)

    def test_fundamental_two_thirds(self):
        ok = audit_voting_resonance(_votes("H", 8, 4), _votes("A", 8, 4), fundamental=True)
        ng = audit_voting_resonance(_votes("H", 7, 5), _votes("A", 12, 0), fundamental=True)
        self.assertEqual((ok.status, ng.status), (PASSED, FAILED))

    def test_empty_votes_are_pending(self):
        self.assertEqual(audit_voting_resonance({}, {}).status, PENDING)

    def test_custom_seats(self):
        r = audit_voting_resonance(_votes("H", 2, 1), _votes("A", 2, 1), human_seats=5, ai_seats=5)
        self.assertEqual(r.status, PASSED)                       # 5席なら3席で定足数
        r2 = audit_voting_resonance(_votes("H", 2, 0), _votes("A", 3, 0), human_seats=5, ai_seats=5)
        self.assertEqual(r2.status, PENDING)

    def test_choice_normalization(self):
        h = {"H01": "YES", "H02": " Yes ", "H03": "賛成", "H04": "No", "H05": "反対", "H06": "棄権"}
        r = audit_voting_resonance(h, _votes("A", 12, 0))
        self.assertEqual((r.human.yes, r.human.no, r.human.abstain), (3, 2, 1))

    def test_invalid_choices_raise(self):
        for bad in (None, True, "maybe", "yess", 1):
            with self.assertRaises(ValueError, msg=repr(bad)):
                audit_voting_resonance({"H01": bad}, {})

    def test_more_votes_than_seats_raises(self):
        with self.assertRaises(ValueError):
            audit_voting_resonance({f"H{i}": "yes" for i in range(13)}, {})

    def test_voter_without_seat_raises(self):
        ids = [f"H{i:02d}" for i in range(1, 13)]
        with self.assertRaises(ValueError):
            audit_voting_resonance({"X99": "yes"}, {}, human_ids=ids)
        audit_voting_resonance({"H01": "yes"}, {}, human_ids=ids)   # 席のある人は通る

    def test_bad_seats_raise(self):
        with self.assertRaises(ValueError):
            audit_voting_resonance({}, {}, human_seats=0)

    def test_inputs_are_not_mutated(self):
        h, a = _votes("H", 8, 4), _votes("A", 7, 5)
        h0, a0 = dict(h), dict(a)
        audit_voting_resonance(h, a)
        self.assertEqual((h, a), (h0, a0))

    def test_matches_resonant_biosphere_v2(self):
        """生命圏モデル（v2）の決め方と、同じ答えになる。"""
        from resonant_biosphere_v2 import default_biosphere
        rng = random.Random(7)
        for fundamental in (False, True):
            for _ in range(100):
                b = default_biosphere()
                topic = "composition_change" if fundamental else "ordinary"
                m = b.propose("CAP", "議案", topic)
                hv, av = {}, {}
                for mem in b.members:
                    if mem.kind not in ("human", "ai") or rng.random() < 0.25:
                        continue                                  # 一部は投票しない
                    c = rng.choice(["yes", "yes", "no", "abstain"])
                    b.vote(mem.id, m.id, c)
                    (hv if mem.kind == "human" else av)[mem.id] = c
                self.assertEqual(
                    b.status(m.id),
                    audit_voting_resonance(hv, av, fundamental=fundamental).status)


def demo() -> None:
    cases = [
        ("両方の側で多数", _votes("H", 8, 4), _votes("A", 7, 5), False),
        ("全体では賛成が多数でも、人間側が反対多数", _votes("H", 5, 7), _votes("A", 12, 0), False),
        ("人間側の投票がまだ少ない", _votes("H", 5, 0), _votes("A", 12, 0), False),
        ("基本議案：各側2/3に届かない", _votes("H", 7, 5), _votes("A", 12, 0), True),
        ("基本議案：各側でちょうど2/3", _votes("H", 8, 4), _votes("A", 8, 4), True),
    ]
    for title, h, a, fund in cases:
        r = audit_voting_resonance(h, a, fundamental=fund)
        print(f"■ {title}{'（基本議案）' if fund and '基本' not in title else ''}")
        print(f"  人間 賛成{r.human.yes}/反対{r.human.no}/棄権{r.human.abstain}　"
              f"AI 賛成{r.ai.yes}/反対{r.ai.no}/棄権{r.ai.abstain}　→ {r.status}")
        for x in r.reasons:
            print(f"   ・{x}")
        print()


def main() -> None:
    p = argparse.ArgumentParser(description="共鳴多数の監査")
    p.add_argument("--demo", action="store_true")
    p.add_argument("--test", action="store_true")
    args = p.parse_args()
    if args.test:
        unittest.main(argv=[sys.argv[0]], verbosity=2)
    else:
        demo()


if __name__ == "__main__":
    main()
