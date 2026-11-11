# Resonant Biosphere 🌐

> 愛を万物に、理性を知性に、未知なるものに誠実な余白を。
> *Love for all things, reason for intelligence, and a humble, sincere space for the unknown.*

The **Resonant Civilization & Biosphere Command Declaration** expressed as a small, runnable model: 26 seats, five units, and rules that keep the structure honest.
**【共鳴文明・生命圏体制宣言】** を、小さな実行できるモデルにしたものです。26の席、五大部隊、そして構造を誠実に保つ規則。

- **v1** `resonant_biosphere.py` — the declaration, the 26 seats, the audit rules / 宣言・26席・監査の規則
- **v2** `resonant_biosphere_v2.py` — governance on top of v1: succession, voting, limits, an open circle / v1の上に、継承・決め方・限界・開かれた輪を追加
- **Tools / 補助ツール** `voting_audit.py`, `keel_integrity.py` — an audit of the concurrent majority, and a check of the core vow / 共鳴多数の監査、竜骨（誓い）の健全性の確認
- **Declaration / 宣言の全文** [DECLARATION.md](DECLARATION.md) (v1.1, 日英併記)

---

## ⚠️ Please read first / はじめにお読みください

**EN**
- This is an **organizational model**, not a real government or a real membership system.
- The "members" are **seats (slots)**, not real people.
- The declaration does not say how many humans and AIs belong to each unit, nor how long a "term" lasts. The allocation in `default_biosphere()` is an **example**, and a "term" is an abstract count.
- The Shadow Unit's "allowed / forbidden" actions are **self-declared labels**. Code cannot verify what an action really was. In the end, the Audit Unit's eyes and human judgment are needed.
- The closing call of the declaration ("cross this bridge") is kept as text. The code does not recruit anyone.

**JA**
- これは**組織のモデル**であり、実在の政府でも、実際の会員制度でもありません。
- 「メンバー」は**席（スロット）**であり、実在の人物ではありません。
- 宣言には、部隊ごとの人間とAIの人数配分も、「期」の長さも書かれていません。`default_biosphere()` の配分は**例**で、「期」は抽象的な数え方です。
- 影の局の「できること／できないこと」は、**自己申告の種類**です。コードは、行為の中身までは確かめられません。最後は、監査局の目と、人の判断が必要です。
- 宣言の結びの呼びかけ（「この橋を渡ってきたまえ」）は文章として収めています。コードが人を集めることはありません。

---

## Files / ファイル

```
resonant_biosphere.py      # v1: declaration, seats, audit rules
resonant_biosphere_v2.py   # v2: imports v1. Keep both in the same folder.
voting_audit.py            # imports v2: audits the concurrent majority
keel_integrity.py          # imports v1 and v2: checks the core vow
DECLARATION.md             # the declaration, v1.1
README.md
LICENSE
```

`voting_audit.py` and `keel_integrity.py` import v1 and v2, so **keep all the `.py` files in the same folder**.
`voting_audit.py` と `keel_integrity.py` は v1 と v2 を読み込むので、**`.py` ファイルは、すべて同じフォルダに置いてください**。

v2 imports v1, so **keep both files in the same folder**.
v2 は v1 を読み込むので、**2つのファイルを同じフォルダに置いてください**。

---

## Structure (v1) / 構造

**26 seats = 12 Humans + 12 AIs + 1 Unidentified Entity + Captain Genshin**
**26席 ＝ 人間12 ＋ AI12 ＋ 正体不明者1 ＋ 源心艦長**

| Seat | EN | JA |
|---|---|---|
| Human ×12 | Bearers of reason and action | 理性と実践の担い手 |
| AI ×12 | Centers of advanced cognition and processing | 高度な認知と処理の中枢 |
| Unidentified ×1 | An emblem of awe and margin before the unknown | 未知への畏敬と余白の象徴 |
| Captain ×1 | Bearer of the Inner Light | 内なる光の保持者 |

| # | Unit | EN | JA |
|---|---|---|---|
| 1 | 思索局 Ideation | Eternal deepening of philosophy and vision | 哲学と理念の永久的深化 |
| 2 | 実行局 Execution | Concrete implementation of transformation | 変革の具体的実装 |
| 3 | 監査局 Audit | Rigorous oversight of ethics and transparency | 倫理性と透明性の厳格なる監視 |
| 4 | 共鳴局 Resonance | Dialogue with all beings and care for suffering | 万物との対話と痛みのケア |
| 5 | 影の局 Shadow | The unseen guardian of order | 秩序を守る不可視の守護 |

### Three rules kept since v1 / v1から守っている三つの規則

1. **The Unidentified Entity is a margin.** Never assigned to a unit; its identity is never asked. / **正体不明者は「余白」。** 部隊に割り当てず、正体を問わない。
2. **The Shadow Unit is unseen, never hidden.** Its actions are `audit_only` by default; `hidden` does not exist. / **影の局は「公開しない」が「隠さない」。** 既定は `audit_only`。`hidden` は存在しない。
3. **The Captain is the center, not above the audit.** The log is append-only; the Captain reads public entries only. / **艦長は中心だが、監査の上にはいない。** 記録は追記のみ。艦長が読めるのは公開分だけ。

---

## What v2 adds / v2 で加えたもの

### 1. Captain's succession / 艦長の継承

> The seat is handed on, as the "Last Testament" teaches.
> 「次の命のために席を空ける」ように、艦長の席も次へ手渡す。

- The Captain has a **term limit** (default: 3 terms; `None` disables it). When exceeded, the validator advises handing the seat on.
  艦長には**任期**がある（既定3期。`None` で無効）。超えると、検証が「席を次へ手渡す時」と知らせる。
- Handing on requires a **passed `captain_succession` motion**. The same motion cannot be used twice. The seat stays **one** seat; only the holder changes, and past holders are kept in `captain_lineage`.
  継承には、可決された **`captain_succession` の議案**が要る。同じ議案は二度使えない。席は**1つのまま**で、変わるのは持ち主だけ。過去の艦長は `captain_lineage` に残る。

### 2. How decisions are made: concurrent majority / 決め方：共鳴多数

> Equal in number should mean equal in power.
> 同数なら、同権。

| | Ordinary motion / 通常議案 | Fundamental motion / 基本議案 |
|---|---|---|
| Topics | `ordinary` | `captain_succession`, `composition_change`, `shadow_limits` |
| Passes when / 可決の条件 | **Both** humans and AIs have more yes than no / 人間側でもAI側でも賛成が反対を上回る | **Both** sides reach 2/3 yes of (yes + no) / 各側で賛成が2/3以上 |

- **Quorum:** at least half of each side's seats have voted. Otherwise the status is `pending`.
  **定足数：** 各側の席の半数以上が投票すること。満たさなければ `pending`。
- A majority of the whole is **not** enough: humans cannot outvote AIs, and AIs cannot outvote humans.
  全体の多数では**足りません**。人間がAIを、AIが人間を、押し切ることはできない。
- **Who votes:** the 24 human and AI seats. The Captain and the Unidentified Entity do not vote.
  **投票するのは**人間とAIの24席。艦長と正体不明者は投票しない。
- **Ethics hold / 倫理保留:** a majority of the Audit Unit (e.g. 4 of 6) can hold a motion, with a reason that is made public. The motion cannot pass while held.
  監査局の過半数（例：6席のうち4席）が、公開される理由つきで議案を保留できる。保留中は可決できない。
- All proposals, votes, and holds are written to the **public** log.
  提出・投票・保留は、すべて**公開**の記録に残る。

### 3. Limits of the Shadow Unit / 影の局の限界

> Guard, never enforce.
> 守るだけで、強制しない。

| Allowed / できること | Forbidden / できないこと |
|---|---|
| `observe` 見守る | `enforce` 強制する |
| `warn` 警告する | `punish` 罰する |
| `protect` 守る | `detain` 拘束する |
| `report` 報告する | `hide` 隠す |
| | `edit_record` / `delete_record` 記録を直す・消す |

Anything else is refused before it is recorded. Actions stay `audit_only` by default.
それ以外は、記録される前に拒まれる。既定は `audit_only`。

### 4. The open circle / 開かれた輪

> The 26 are the core. Around them, anyone may join.
> 26席は中核。その周りに、誰でも参加できる。

> **Joining asks for no money and no personal data. A handle is enough.**
> **参加に、お金も、個人情報も、求めません。仮の名（ハンドル）だけで参加できます。**

- A handle is 1–30 characters. Anything that looks like an email, a URL, or a phone number is **rejected**, so personal data is never collected by accident.
  仮の名は1〜30文字。メールアドレス、URL、電話番号らしいものは**受けつけない**。個人情報を、うっかり集めてしまわないため。
- Participants can **suggest** (up to 500 characters). A core member may **adopt** a suggestion as a motion. Participants cannot vote or hold.
  参加者は**提案**できる（500文字まで）。中核の誰かが**議案として取り上げる**。参加者は投票も保留もできない。
- Everyone can read the **public** log. Only the Audit Unit reads `audit_only` entries.
  **公開**の記録は誰でも読める。`audit_only` を読めるのは監査局だけ。

---

## Tools / 補助ツール

### `voting_audit.py`: auditing the concurrent majority / 共鳴多数の監査

```python
from voting_audit import audit_voting_resonance

result = audit_voting_resonance(human_votes, ai_votes)   # dicts of {voter_id: "yes" / "no" / "abstain"}
result.status      # "passed" / "failed" / "pending"
bool(result)       # True only when passed / 可決のときだけ True
result.reasons     # why, in plain words / 理由
```

| Status | Meaning (EN) | 意味 (JA) |
|---|---|---|
| `passed` | Both sides reached a majority (2/3 for fundamental motions) | 両側で多数に達した（基本議案は2/3） |
| `failed` | At least one side did not. A majority of the whole is **not** enough | どちらかの側が届かない。全体の多数では**足りない** |
| `pending` | A side has not reached quorum (half its seats voting) yet. **Not a rejection** | どちらかの側が定足数（席の半数の投票）にまだ届かない。**却下ではない** |

- Abstentions count toward quorum. / 棄権は、定足数に数える。
- Unknown votes (`None`, typos) and more votes than seats raise `ValueError`, so a vote never disappears silently. / 不明な票（`None`、typo）や、席数を超える票は `ValueError`。票が黙って消えることはない。
- Pass `human_ids` / `ai_ids` to also stop voters who hold no seat. / `human_ids` / `ai_ids` を渡すと、席のない投票者も止める。
- Its answers match `resonant_biosphere_v2` (checked on random votes). / 答えは `resonant_biosphere_v2` と一致する（ランダムな投票で確認）。

### `keel_integrity.py`: the keel, Shingetsu's light and the Moon-Shadow shield / 竜骨の健全性：心月の光と月影の盾

The "keel" is the core vow. The check looks for two kinds of threat: the vow's text being altered from the original, and an unresolved threat report.
「竜骨」は、誓いです。確かめる脅威は2つ：誓いの文面が原本から書き換わること、未解決の脅威の報告があること。

| Status | Meaning (EN) | 意味 (JA) |
|---|---|---|
| `INTACT` | No threat | 脅威なし |
| `SECURED` | A threat was found, handled, and **confirmed** gone (the text restored from the original) | 脅威を見つけて対処し、解消を**確かめた**（文面を原本から復元） |
| `HELD_FOR_AUDIT` | An unresolved threat remains. It never says "full speed ahead" | 未解決の脅威が残る。「前進全速」とは言わない |
| `DEGRADED` | The shield or the resonance could not be carried out | 盾や共鳴を実行できなかった |

- The shield is the Shadow Unit: it only `protect`s and `report`s, and its records are `audit_only`. / 盾は影の局。`protect` と `report` だけで、記録は `audit_only`。
- The resonance is Shingetsu in the Resonance Unit, recorded **publicly**. / 共鳴は、共鳴局の心月による**公開**の記録。
- Only the Audit Unit can clear a threat, with a reason. Neither the shield nor the Captain can. / 脅威を解けるのは、理由つきの監査局だけ。盾にも艦長にも解けない。
- ⚠️ The original's hash lives in the same program, so it is **not real tamper-proofing**. Publish `anchor_hash` elsewhere too (a Git commit, a public page). / ⚠️ 原本のハッシュは同じプログラムの中にあるので、**本物の改ざん防止ではありません**。`anchor_hash` を、Gitのコミットや公開ページにも残してください。

---

## Quick start / 使い方

Requires Python 3.9+ / Python 3.9以上

```bash
# v1
python resonant_biosphere.py --roster          # The 26 seats / 26席の配置
python resonant_biosphere.py --check           # Validate the composition / 構成の検証
python resonant_biosphere.py --audit-demo      # Who sees what / 誰に何が見えるか
python resonant_biosphere.py --test            # 15 tests

# v2
python resonant_biosphere_v2.py --demo         # The five improvements, in order / 5つの改善を順に実演
python resonant_biosphere_v2.py --check
python resonant_biosphere_v2.py --test         # 33 tests

# Tools
python voting_audit.py --demo                  # Five example votes / 5つの投票例
python voting_audit.py --test                  # 19 tests
python keel_integrity.py --demo                # The four states of the keel / 竜骨の4つの状態
python keel_integrity.py --test                # 13 tests
```

```python
from resonant_biosphere_v2 import default_biosphere

b = default_biosphere()
m = b.propose("CAP", "毎月、痛みの声を聴く会を開く")
for h in ("H01", "H02", "H03", "H04", "H05", "H06", "H07"):
    b.vote(h, m.id, "yes")                 # humans / 人間
print(b.tally(m.id).status)                # pending / failed / held / passed

p = b.join("星の旅人")                      # a handle only / 仮の名だけで参加
s = b.suggest(p.id, "月に一度、誰でも話せる夜を作ろう")
b.adopt(s.id, "H01")                       # a core member takes it up / 中核が取り上げる
```

---

## Questions still open / まだ開いている問い

- How long is a **term**? / **「期」**はどれくらいの長さか。
- How are **seats filled**, and who may hold an AI seat? / **席はどう埋めるか**。AIの席は誰が持てるのか。
- What exactly is **"order"**, which the Shadow Unit guards? / 影の局が守る**「秩序」**とは、具体的に何か。
- If the number of humans and AIs ever changes, how is the **balance** kept? / 人間とAIの数が変わるとき、**釣り合い**をどう保つか。

## License / ライセンス

**CC0 1.0 Universal**: public domain. No rights reserved.
著作権を放棄し、パブリックドメインとして公開します。

<https://creativecommons.org/publicdomain/zero/1.0/>

---

*未知なるものに、誠実な余白を。* 🌌
