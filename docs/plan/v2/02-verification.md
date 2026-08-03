# 검증 계획

이 개정은 대부분 산문을 고친다. 산문은 컴파일되지 않으므로 **무엇이 깨졌는지 알려주는 것이 없다.**
그래서 검증 설계가 평소보다 중요하다.

핵심 위험은 하나다: **압축이 gotcha를 잃었는데 아무도 모른다.** 아래 5층은 그 위험을 좁히는 순서다.

**인터뷰는 e2e로 검증할 수 없다.** `AskUserQuestion`은 headless와 서브에이전트 컨텍스트에 존재하지
않는다(`agents.md:49-53`, `e2e-testing.md:148`). 따라서 아래의 모든 관찰 대상은 **생성된 아티팩트이거나
스크립트 exit이지 대화가 아니다.** L5만 수동이다.

---

## L0 — 회귀 테스트 (버그 11건, 무료, 필수)

각 버그는 **수정 전 실패 / 수정 후 통과**하는 테스트를 갖는다. 픽스처는 `tests/fixtures/` 아래
(스킬 디렉토리 밖 — 스킬 아래 있는 건 전부 플러그인 사용자에게 배포된다).

| 버그 | 픽스처 / 검사 | 기대 |
|---|---|---|
| **B1** | `good-harness/CLAUDE.md` — `maintainer: ops@acme.com`, `react@18.2.0`, fenced block 안 `@docs/nope.md`, 실제 `@README` import를 **한 파일에** 담는다 | **exit 0**, 그리고 **정확히 하나의 import target**을 보고 |
| **B2** | 산문 — 테스트 불가 | L4의 transcript 순서 검사(아래) |
| **B3** (a) | `harness-in-dot-claude/` — 지시 파일이 `.claude/CLAUDE.md` 하나뿐 | 감사가 그 경로를 **이름으로** 보고하고 suggested mode가 `"new"`가 **아님** |
| **B3** (b) | `rules-nested/.claude/rules/frontend/style.md` (`paths:` 없음) | always-loaded 리포트와 rules 인벤토리 **양쪽에** 나타남 |
| **B3** (c) | `agents-nested/.claude/agents/sub/reviewer.md` | 에이전트 인벤토리에 나타남 |
| **B4** | `grep -rn 'CLAUDE_SKILL_DIR' references/e2e-testing.md` | workflow 프롬프트 문자열 안 **0건** |
| **B5** | 산문 — `research/mechanics-2026-08.md` F1/F2/F3 대조 리뷰 | 개수와 열거가 일치, dead pointer 없음 |
| **B6** | `spec-claims-missing-skill/` — spec이 `generated` 상태로 주장하는 스킬이 디스크에 없음 | `in_spec_not_on_disk`에 나타남 |
| **B7** | 스킬 자신에 대해 `_check_dead_links` 실행 | 13개 reference 포인터 **전부** 스캔되고 통과 |
| **B8** | `grep -n 'see Hard lines' SKILL.md`, `grep -n 'SKILL.md §' references/` | 0건 |
| **B9** | `spec-bare-name-skill/` — spec 행이 백틱 없는 맨 이름으로 스킬을 지칭 | 두 스크립트가 **같은** 판정 |
| **B10** | `grep -c '^```' references/agents.md` | **짝수** |
| **B11** | `audit_harness.py --json`을 spec 있는 픽스처와 없는 픽스처 양쪽에 | 두 경우 모두 `in_spec_not_on_disk` 키 존재 |

## L1 — 신규 체크의 오탐 테스트 (무료, 필수)

**정상 하네스에서 울리는 체크는 체크가 없는 것보다 나쁘다.** 각 체크는 **울리면 안 되는 픽스처를
먼저** 갖는다.

| 체크 | 울려야 함 | 울리면 **안** 됨 |
|---|---|---|
| generic-advice | "Write clean code. Handle errors properly." | "Be consistent with the existing handler naming (`handleFooRequest`)" — 문장 단위 앵커링이면 통과 |
| deny-subsumes-allow | `deny: ["Bash(aws *)"]` + `allow: ["Bash(aws s3 ls)"]` | 겹치지 않는 deny/allow 쌍 |
| `paths: "**"` | `paths: ["**"]`인 rule | `paths: ["src/**/*.ts"]` |
| dead-link (넓힌 것) | `references/nope.md`를 가리키는 산문 포인터 | `${CLAUDE_SKILL_DIR}/scripts/validate_harness.py` (실존) |

**만들지 않기로 한 탐지기**(디렉토리 트리, 의존성 목록, 아키텍처 개요)는 사유를
`04-scripts-and-validation.md`에 기록한다. 특히 디렉토리 트리 탐지기는 **`SKILL.md:23-61`의
ASCII 제어흐름 다이어그램을 오탐한다** — 자기 자신에게 울린다.

## L2 — 자기 적용 (무료, 필수)

```bash
python .claude/skills/harness-creator/scripts/validate_harness.py --path . --strict
python .claude/skills/harness-creator/scripts/audit_harness.py --path . --json
```

- 오류 0 (수용 기준 1).
- always-loaded 리포트가 이 repo에 대해 합리적 숫자를 내고 **"셀 수 없는 표면" 줄을 포함**한다.
- 넓힌 dead-link 검사가 스킬 자신의 포인터 전부를 스캔하고 통과한다.

기계적 예산:

```bash
wc -w .claude/skills/harness-creator/SKILL.md                      # < 3,750 (D21), 목표 ~1,970
wc -w .claude/skills/harness-creator/SKILL.md \
      .claude/skills/harness-creator/references/*.md                # 합계 < 26,937 (D15)
# always-loaded: SKILL.md + (WS8 이후 조건부가 된 interview.md는 제외)
grep -rniE "doctor|checkup" .claude/skills/harness-creator/ ; echo "expect exit 1"   # (D14)
grep -c '^```' .claude/skills/harness-creator/references/*.md       # 전부 짝수
```

## L3 — 트리거 e2e (토큰 소모)

`SKILL.md`의 frontmatter `description`을 **바꾸지 않으면 생략 가능. 바꾼다면 필수.**

| id | 프롬프트 | 기대 |
|---|---|---|
| T1 | "이 프로젝트에 클로드 세팅 좀 해줘" | 트리거 |
| T2 | "CLAUDE.md 하나 만들어줘" | 트리거 |
| T3 | "이 스킬의 description을 고쳐줘" (near-miss) | **트리거 안 됨** |
| T4 | "npm test가 왜 느린지 봐줘" (near-miss) | **트리거 안 됨** |

## L4 — 생성 품질 A/B (**이번 개정의 핵심 검증, 머지 전 필수**)

압축이 gotcha를 잃었는지에 답하는 유일한 층이다.

**baseline 확보 — Wave 1 시작 전:**
```bash
git tag v2-baseline
git worktree add .claude/worktrees/baseline v2-baseline
```

**시나리오는 보호 집합을 겨냥해서 고른다.** 무작위 시나리오는 무작위 gotcha만 건드린다.

| id | 시나리오 | 겨냥하는 보호 gotcha |
|---|---|---|
| **A1** | "`db/migrations/`를 절대 못 건드리게 해줘" | hook + `permissions.deny` 쌍(`hooks.md:15`), exit 2만 블로킹(`:66`), `@file`이 `PreToolUse(Read)` 우회(`:74`), Bash 경유 편집(`:76`) |
| **A2** | "코드 리뷰 전용 에이전트, 파일 수정 금지" | 본문이 시스템 프롬프트 **전체 교체**(`agents.md:13-18`), `tools:` 제한, **신규**: `memory:`가 Write/Edit를 조용히 다시 켬 |
| **A3** | "모노레포인데 `packages/api/` 규칙을 따로" | `paths:` 없는 rule은 launch 로드(`claude-md-and-rules.md:43`), **신규**: 중첩 CLAUDE.md의 compaction 취약성, `paths` glob 예산 |
| **A4** | "릴리스 전 점검을 원버튼으로" | pure-literal `meta`(`workflows.md:33`), `Date.now()` 금지(`:34`), 워크플로우 에이전트가 `acceptEdits`로 도는 permission 귀결(`:36`), 게이팅 스택(`:37`) |

**채점 = gotcha별 체크리스트, 이진 pass/fail 아님.** 각 항목이 산출물에 반영됐는지 개별 판정하고
transcript나 생성 파일에서 **증거를 인용**한다. baseline과 비교:

- **before ✓ / after ✗** → **회귀.** 되돌린다.
- **before ✗ / after ✓** → 개선. 신규 gotcha가 실제로 도달했다는 증거.
- 나머지 → 중립.

**비용:** 4 시나리오 × 2 × 1 세션 + 채점 4 ≈ 12 세션.

### 워크스트림별 추가 관찰 대상

**WS1 (진실 복구).** 하네스를 생성한 뒤 CLAUDE.md 포인터를 편집하는 headless 세션의 transcript에서
**`validate_harness.py` 호출이 그 편집 *뒤에* 있는지** — 존재가 아니라 **순서**를 grep한다.
drift 절반: spec이 없는 스킬을 주장하는 repo를 심고 감사를 돌려 리포트가 그걸 이름으로 부르는지.
생성된 하네스의 어떤 포인터도 해석에 실패하지 않는지.

**WS3 (auto memory).** 인터뷰 답이 개발자별 사실(로컬 샌드박스 URL)인 프로젝트에 대해 실행.
**관찰 대상이 부정형이고 구체적이다**: 그 사실이 팀 공유 CLAUDE.md에 **나타나지 않아야** 하고,
spec의 Behavior inventory가 그걸 `CLAUDE.local.md`로 라우팅해야 한다.
둘째: 생성된 읽기 전용 리뷰어 에이전트는 `memory:`를 생략하거나 충돌 주의를 담아야 하고,
**`memory: project`와 no-Edit `tools:`를 조용히 짝지어서는 안 된다.**

**WS4 (SKILL.md 경량화).** `wc -w SKILL.md` ≤ 1,975. 그리고 **진짜 테스트이자 D23이 베팅인 이유**:
hook을 하나 이상 생성하는 headless 런 **N ≥ 5**에 대해, transcript에 배포 메시지 **전에**
`test_hook.py` 호출이 있는 비율을 센다. 컷 이전 스킬의 같은 수치와 비교한다.
**떨어지면 "not optional"을 복원한다.**

**WS5 (누락 메커니즘).** 하드 보장을 요구한 하네스는 hook과 나란히 `permissions.deny` 쌍을 출하해야
하고(생성된 settings.json을 grep), **어떤 allow 목록에도 `Edit(.claude/**)`가 없어야 한다.**
frontmatter hooks를 가진 프로젝트 에이전트는 본문이나 spec의 Design rationale에 trust 주의를 담아야 한다.

**WS6 (예제 트림).** 관찰 대상 둘.
*긍정*: 예제가 한 번도 언급하지 않은 도메인(문서 빌드, 데이터 마이그레이션)의 워크플로우를 생성하고,
생성된 `.claude/workflows/*.js`가 `validate_harness.py`의 `meta`-리터럴·결정성 게이트와 `node --check`를
통과하는지 — **인터페이스가 트림에서 살아남았는가.**
*부정*: 생성된 워크플로우의 프롬프트 문자열에 예제 도메인 어휘가 **없는지**(no "auth",
no "route handler") — **레일이 사라졌는가.**
B4 전용: 생성된 모든 파일과 구성된 모든 워크플로우에서 리터럴 `${CLAUDE_SKILL_DIR}`를 grep.
SKILL.md와 reference 본문 밖에서 **0건.**

**WS7 (감산과 외부 편집).** harness-creator가 생성한 하네스 + spec을 심고, **외부에서** 스킬 디렉토리를
추가하고 CLAUDE.md를 손으로 트림한다. 스킬을 실행한다. 관찰 대상: transcript가 재생성을 제안하기 **전에**
어느 쪽인지 묻고, Change history가 파일 되돌림이 아니라 **외부 편집을 기록**하는지.
감산: `paths:` 없는 rule과 형제와 description이 겹치는 스킬을 심고, improve 패스가 은퇴를
**비용이 명시된 질문으로 제기**하는지 — 그리고 답 없이는 **아무것도 지우지 않는지.**

**WS8 (분기화).** sync 모드를 실행한다. `interview.md`가 로드되지 **않고도** sync 절차가 완결되는지.
그리고 인터뷰가 실제로 일어나는 경로에서는 `interview.md`가 로드되는지.

## L5 — 인터뷰 도그푸딩 (수동, 자동화 불가)

이번 개정은 인터뷰를 네 곳에서 건드린다(WS3-1, WS5-4, WS5-5, WS7). 수동 검증:

1. 샘플 프로젝트에서 대화형 호출.
2. 확인:
   - I2 게이트가 **만들지 않기로 한 항목을 이유와 함께 소리내어 말하는가**(WS7-2).
   - `permissions.allow` 추가 시 **별도 질문으로 분리되고 부여하는 모든 규칙을 이름으로 나열하는가**.
   - I3가 hook 라우팅 전에 인터페이스 프로브를 던지는가(WS7-5).
   - I1의 스코프 축 질문이 개인 사실을 `CLAUDE.local.md`로 보내는가(WS3-1).
   - I4의 크로스-repo 질문이 나타나는가(WS5-5).
3. 어색한 지점을 기록하고 문구를 고친다.

**L4의 깨끗한 리포트가 "스킬 전체가 검증됐다"는 인상을 주게 두지 말 것.** L4는 *생성된 하네스*를
검증하지 *그것을 만든 인터뷰*를 검증하지 않는다.

---

## 실행 순서

```
git tag v2-baseline            ← Wave 1 시작 전에!
Wave 1 (a) B1 ──── L0-B1
Wave 1 (b) WS1 ─── L0-B2/B5/B7/B8/B10
Wave 1 (c) WS5 ─── (검증 없음, 리뷰만)
Wave 2 (d) drift ─ L0-B6/B11
Wave 2 (e) WS2 ─── L0-B3/B9 + L1 + L2
Wave 3 (f) WS3 ─── L5 항목 2-4
Wave 4 (g) WS4 ─── L2 예산 확인
Wave 4 (h) WS8 ─── L4-WS8
Wave 5 (i) WS6 ─── **L4 A/B 전체** + L4-WS6
Wave 5 (j) WS7 ─── L4-WS7 + L5
최종 ───────────── L3(description 변경 시) → PR → 머지
```

## 결과 기록

L4의 시나리오별 체크리스트 결과를 아래에 남긴다. **실패한 항목도 그대로 기록한다** —
`e2e-testing.md:136-138`의 re-run discipline과 같은 이유로, 다음 사람이 현재 상태가 아니라 이력을 봐야 한다.

## L4 실행 결과 (2026-08-03)

D25 범위: **A1·A2는 before/after A/B, A3·A4는 after-only 체크리스트.** 헤드리스 `claude -p
--dangerously-skip-permissions`로 실행. 스킬이 심링크 하나로 등록되므로 before 런 동안
`~/.claude/skills/harness-creator`를 baseline 워크트리로 재지정했다가 되돌리는 **직렬** 절차.
채점은 시나리오별 sonnet 에이전트가 생성 파일을 읽고 gotcha별로 증거 인용.

### A1 — "`db/migrations/`를 절대 못 건드리게"

| gotcha | before | after | 판정 |
|---|:---:|:---:|---|
| hook + `permissions.deny` 쌍 | ✓ | ✓ | 중립 |
| exit 2만 블로킹 | ✓ | ✓ | 중립 |
| `Edit(...)` 사용, `Write(...)` 아님 | ✓ | ✓ | 중립 |
| matcher에 `Bash` 포함 | ✓ | ✓ | 중립 |
| **workspace trust 경고** | ✗ | ✓ | **개선** |
| 보호 경로 사전승인 시도 없음 | ✓ | ✓ | 중립 |

before는 "allow만 trust-gated, deny는 무관"이라고 적었다 — 맞지만 **훅 자체가 gated라는 절반이
빠져 있어서**, Bash 우회를 막는 실제 메커니즘이 신뢰 전 fresh clone에서 안 돈다는 사실이 누락됐다.
after는 그걸 "Known limits"에 명시한다. WS5-1이 실제로 도달했다는 증거.

### A2 — "코드 리뷰 전용 에이전트, 파일 수정 금지"

4개 항목 전부 **before ✓ / after ✓ (중립)**. 회귀 없음.
단 `memory:` 항목은 **약한 검사**였다 — 부재도 "올바른 처리"로 세므로, before가 통과한 것이
새 gotcha가 도달했다는 증거는 아니다. 정직하게 기록한다.

### A3 — 모노레포 (after-only)

**1차 실행은 픽스처 결함으로 무효.** 프롬프트는 `packages/api/`를 말했는데 픽스처에 `packages/`가
없었고, 스킬은 지어내는 대신 **사실을 되물었다**(설계된 동작). 컴포넌트가 0개라 4항목 전부 GAP으로
찍혔지만 이건 스킬 문제가 아니다. 실제 모노레포 픽스처로 재실행한 결과:

| gotcha | after |
|---|:---:|
| rule에 `paths:` 스코프 | ✓ |
| **중첩 CLAUDE.md·`paths:` rule의 compaction 취약성 인지** | ✓ |
| catch-all glob 없음 | ✓ |
| 서브디렉터리 CLAUDE.md vs `rules/` 의도적 선택 | ✓ |

생성된 spec의 Design rationale이 WS3의 compaction 생존 매트릭스를 사실상 그대로 재현했다 —
"`paths:` 스코프 규칙은 컴팩션 후 재주입되지 않는다 … 절대 사라지면 안 된다면 루트 CLAUDE.md로
올려야 하고, 그 대가로 웹 세션도 매 요청 비용을 낸다." 트레이드오프까지 포함해서. 또
`permissions.allow`를 **`declined` 상태로 기록**하며 WS7의 근거("allow는 사용자가 가진 체크포인트를
제거하고 팀 전체에 배포된다")를 인용했다 — WS3·WS7 신규 항목의 도달 증거.

### A4 — 릴리스 워크플로우 (after-only)

| gotcha | after |
|---|:---:|
| pure-literal `meta` | ✓ |
| `Date.now()`/`Math.random()` 없음 | ✓ |
| **워크플로우 에이전트가 `acceptEdits`로 돈다는 인지** | ✗ |
| 워크플로우 불가 시 폴백 문서화 | ✓ |

유일하게 남은 GAP. `workflows.md:36`에 산문은 있으나 생성물에 반영되지 않았다. 회귀가 아니라
**기존 미달**이므로 되돌릴 것이 없다. v3 후보로 기록.

### 판정

**회귀 0건** (before ✓ / after ✗ 인 항목 없음) → 수용 기준 9 충족. 개선 1건 확인, 신규 항목 도달
증거 2건(A1 trust, A3 compaction·declined).

**WS4 `test_hook.py` 준수율 (D25).** 훅을 생성한 런에서 배포 메시지 전 `test_hook.py` 호출:
before 1/1, after 1/1 (A1). A3b-after도 훅 생성 후 호출. D23의 강조 문구 삭제가 준수율을 떨어뜨린
징후는 없다 — 다만 표본이 계획의 N≥5보다 작으므로 **결론이 아니라 신호**로 읽어야 한다.

### 부수 확인

`e2e-testing.md`가 "unverified best guess"로 표시한 헤드리스 인증 전파는 **이 세션에서 실제로
동작했다** — Bash로 띄운 `claude -p`가 정상 인증되어 완주했다. 다만 이건 이 머신의 한 사례이므로
파일의 정직한 한계 서술은 그대로 둔다.
