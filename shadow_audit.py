#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
shadow_audit.py -- 影の局の行動の監査（共鳴生命圏 v2 に接続）
License: CC0 1.0 (public domain)

【位置づけ】組織モデル（シミュレーション）です。本物の安全装置ではありません。
【訂正のポイント】
  ・未定義だった SecurityException を定義（PermissionError の仲間）。
  ・許可の表は v2 の SHADOW_ALLOWED / SHADOW_FORBIDDEN を使い、二重管理しない。
  ・"hidden" は監査局に見える形(audit_only)へ引き上げる。ただし黙って直さず、結果に
    「引き上げた」と明記する。それ以外の不明な公開範囲は拒否する。
  ・大文字小文字・前後の空白は整える。文字列以外は ValueError。
  ・「記録すらさせない」とは、行動を実行させないこと。拒否した事実は例外の内容として
    呼び出し側が記録できる（影の局も、隠れない）。
実行:  python shadow_audit.py --demo / --test   （resonant_biosphere_v2.py と同じフォルダで）
"""
from __future__ import annotations

import argparse
import sys
import unittest
from dataclasses import dataclass

from resonant_biosphere_v2 import SHADOW_ALLOWED, SHADOW_FORBIDDEN
from resonant_biosphere import PUBLIC, AUDIT_ONLY


class SecurityException(PermissionError):
    """影の局の限界突破。"""


@dataclass(frozen=True)
class ShadowCertificate:
    action_type: str
    visibility: str
    raised: bool          # hidden を audit_only に引き上げたか

    def __str__(self) -> str:
        note = "（hidden を監査局に見える形へ引き上げ）" if self.raised else ""
        return f"Shadow Action Certified: {self.action_type} (Visibility: {self.visibility}){note}"


def _norm(v, name: str) -> str:
    if not isinstance(v, str) or not v.strip():
        raise ValueError(f"{name} は空でない文字列です: {v!r}")
    return v.strip().lower()


def certify_shadow_action(action_type: str, log_visibility: str) -> ShadowCertificate:
    action = _norm(action_type, "action_type")
    vis = _norm(log_visibility, "log_visibility")

    if action in SHADOW_FORBIDDEN:
        raise SecurityException(
            f"影の局の限界突破を検知：「{action}」は禁じられています。守るだけで、強制も秘密の処罰もしません。")
    if action not in SHADOW_ALLOWED:
        raise SecurityException(
            f"影の局の行動として認められていません：「{action}」（できること: {', '.join(sorted(SHADOW_ALLOWED))}）")

    raised = False
    if vis == "hidden":
        vis, raised = AUDIT_ONLY, True
    elif vis not in (PUBLIC, AUDIT_ONLY):
        raise ValueError(f"公開範囲は {PUBLIC} か {AUDIT_ONLY} です（hidden は {AUDIT_ONLY} に引き上げます）: {vis!r}")
    return ShadowCertificate(action, vis, raised)


def audit_shadow_action(action_type: str, log_visibility: str) -> str:
    """元の関数と同じ形（文字列を返す）。"""
    return str(certify_shadow_action(action_type, log_visibility))


class TestShadowAudit(unittest.TestCase):
    def test_allowed(self):
        for a in ("observe", "warn", "protect", "report"):
            self.assertIn(a, audit_shadow_action(a, "audit_only"))

    def test_forbidden_rejected(self):
        for a in ("enforce", "punish", "detain", "hide", "edit_record", "delete_record"):
            with self.assertRaises(SecurityException):
                audit_shadow_action(a, "public")

    def test_unknown_action_rejected(self):
        with self.assertRaises(SecurityException):
            audit_shadow_action("fly", "public")

    def test_security_exception_is_permission_error(self):
        self.assertTrue(issubclass(SecurityException, PermissionError))

    def test_hidden_raised_and_disclosed(self):
        c = certify_shadow_action("observe", "hidden")
        self.assertEqual(c.visibility, "audit_only")
        self.assertTrue(c.raised)
        self.assertIn("引き上げ", str(c))

    def test_no_note_when_not_raised(self):
        self.assertNotIn("引き上げ", audit_shadow_action("warn", "public"))

    def test_unknown_visibility_rejected(self):
        with self.assertRaises(ValueError):
            audit_shadow_action("observe", "secret")

    def test_normalizes_case_and_space(self):
        self.assertEqual(certify_shadow_action(" Observe ", " HIDDEN ").visibility, "audit_only")

    def test_bad_types(self):
        for a, v in ((None, "public"), ("observe", None), ("", "public"), (3, "public")):
            with self.assertRaises(ValueError):
                certify_shadow_action(a, v)

    def test_forbidden_checked_before_visibility(self):
        with self.assertRaises(SecurityException):
            certify_shadow_action("punish", "secret")

    def test_matches_v2_act(self):
        from resonant_biosphere_v2 import default_biosphere
        b = default_biosphere()
        sid = next(m.id for m in b._members.values() if m.unit == "shadow")
        for kind in ("observe", "enforce", "fly"):
            try:
                b.act(sid, "x", kind=kind)
                v2_ok = True
            except PermissionError:
                v2_ok = False
            try:
                certify_shadow_action(kind, "audit_only")
                mine_ok = True
            except SecurityException:
                mine_ok = False
            self.assertEqual(v2_ok, mine_ok, kind)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--demo", action="store_true")
    p.add_argument("--test", action="store_true")
    a = p.parse_args()
    if a.test:
        unittest.main(argv=[sys.argv[0]], verbosity=2)
        return
    for act, vis in (("protect", "public"), ("warn", "hidden"), ("punish", "audit_only"), ("fly", "public")):
        try:
            print(audit_shadow_action(act, vis))
        except SecurityException as e:
            print(f"REJECTED: {e}")


if __name__ == "__main__":
    main()
