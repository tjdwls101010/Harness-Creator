# 변경 명세

`00-overview.md` §6의 워크스트림별 상세. 인용된 라인 번호는 2026-08-01 기준이며 앞선 워크스트림이
파일을 편집하면 이동한다 — **라인 번호가 아니라 인용된 문장으로 위치를 찾을 것.**

스킬 표면에 들어가는 텍스트는 영어로 적었다(D7). 그대로 쓰라는 뜻이 아니라 **의도와 밀도의 기준**이다.

전체 findings 원본과 가드레일 목록은 [`research/audit-synthesis.md`](research/audit-synthesis.md).
제품 메커니즘의 1차 소스는 [`research/mechanics-2026-08.md`](research/mechanics-2026-08.md).

---

## 버그 색인

| # | 위치 | 증상 | 담당 WS |
|---|---|---|---|
| **B1** | `validate_harness.py:38` | **정상 하네스를 E로 떨군다.** 이메일·핀버전을 `@import`로 오인 | WS2 |
| **B2** | `SKILL.md:51-60` | Wrap-up이 검증을 그 검증이 잡으려는 편집보다 먼저 실행 | WS1 |
| **B3** | `audit_harness.py:38`, `validate_harness.py:402`, `harness_common.py:282/:264` | CLAUDE.md 단일 경로 발견, rules·agents 비재귀 | WS2 |
| **B4** | `e2e-testing.md:50` | `${CLAUDE_SKILL_DIR}`가 workflow 에이전트 프롬프트에서 해석 안 됨 | WS6 |
| **B5** | `hooks.md:86`, `hooks-events.md:314/:330` | SessionEnd 1.5초를 per-hook 기본값으로 오기재 + 자기모순 | WS1 |
| **B6** | `interview.md:99/:103/:132` | 존재하지 않는 drift 메커니즘을 세 곳에서 주장 | WS1 |
| **B7** | `SKILL.md:111` (`:105`, `e2e-testing.md:7` 동반) | Hard line 1이 기계적 포인터 검사를 과장 | WS1 |
| **B8** | `SKILL.md:39`, `interview.md:42`, `hooks.md:86` | dangling pointer 3건 | WS1 |
| **B9** | `interview.md:117` vs `validate_harness.py:460` | spec 템플릿이 자기 drift 검사 규약과 불일치. 두 스크립트도 서로 불일치 | WS2 |
| **B10** | `agents.md:73` | ` ```markdown ` 펜스를 열고 닫지 않음 | WS1 |
| **B11** | `audit_harness.py:139` vs `:162-171` | `in_spec_not_on_disk` 키가 spec 존재 시 누락 → `--json` 소비자 파손 | WS2 |

---

## WS1 — 진실 복구

**요지.** 스킬의 가장 load-bearing한 문장들이 존재하지 않는 강제를 서술한다. 스킬 자신의 Hard line 1이
정확히 그걸 금지한다. 순수 정확성 작업이고, doctrine을 바꾸지 않으며, **더하는 것보다 빼는 게 많다.**

### WS1-1 · B2 · Wrap-up 순서 역전

`SKILL.md:52`가 `validate_harness.py`를 먼저 실행하고, `:56`/`:57`이 spec과 CLAUDE.md를 변경하고,
`:60`이 커밋을 제안한다. `:54-55`가 그 실행을 "아래 두 항목이 새 drift를 만들 수 있어서"로 정당화하고,
`:59`는 **이미 끝난 실행에 대해** "the validate_harness.py run just above will independently catch any
spec-vs-disk drift this introduces"라고 단언한다. 전달·커밋되는 상태는 검증된 적이 없다.

`:57`의 포인터 편집은 E-등급 `@`-import 검사(`:419`), 200줄 경고(`:408-414`), 맨이름 인벤토리 경고
(`:427-443`)를 새로 트립할 수 있다 — **마지막 것은 `:57`이 경계하라고 말하는 바로 그 실수다.**

**수정.** 순서를 `spec Change history` → `CLAUDE.md 포인터` → `validate_harness.py` → `커밋 제안`으로.
`:59` 삭제.

### WS1-2 · B6 · `interview.md`의 존재하지 않는 drift 메커니즘

세 곳: `:103`("this shape is what `audit_harness.py` parses and diffs against"),
`:132`("the exact mechanism… a row stuck at `approved` with no matching file"),
`:99`("spec claims component X exists, filesystem disagrees, **or vice versa**").

실제로는 원문 substring 스캔(`audit_harness.py:157-161`)이고 헤딩도 표도 `status` 열도 읽지 않는다
(4개 스크립트 전체에 "status" grep 0건). `:165-170`의 주석이 반대 방향을 명시적으로 포기하며
**"a human (or the interviewing Claude) reading the spec's Behavior inventory table"**에 위임한다.
그런데 **스킬 표면 어디에도 그 지시가 없다** — `SKILL.md:27`은 "check `.claude/harness-spec.md`"만 말한다.
그래서 D6/sync 모드의 절반을 아무도 수행하지 않는다.

**수정 = D8의 A안 (Wave 2(d)).** `check_spec_drift`에 반대 방향을 구현한다:

1. spec 텍스트에서 `## Behavior inventory` 헤딩 아래 마크다운 표 행을 읽는다.
2. `component`와 `status` 셀을 뽑는다.
3. `status`가 `generated`/`validated`인데 `component`가 on-disk 집합의 무엇과도 매치하지 않으면
   `in_spec_not_on_disk`로 보고한다.
4. **그 키를 무조건 반환한다**(B11 동시 해결).
5. `:165-170`의 포기 주석을 삭제한다.

**표 컬럼은 `02-skill-design.md:113-125`가 이미 고정했다 — spec 포맷 변경도 기존 하네스 마이그레이션도
불필요하다.** 약 15줄.

`interview.md:99`도 함께 고친다(WS7과 병합 가능): 발산은 항상 부패가 아니다.

### WS1-3 · B7 · Hard line 1의 과장

`SKILL.md:111`은 "`validate_harness.py` checks this mechanically"라고 한다.
`_check_dead_links`(`validate_harness.py:253`)는 백틱 감싼 `references/x`·`scripts/x`만 매치하고
**SKILL.md 텍스트로만** 호출된다(`:237`/`:209`). 이 스킬 자신의 명명된 reference 포인터 13개 중 **1개**만
커버하고, reference→reference 포인터 7개는 0개, 마크다운 링크 형태 0개, 스킬 이름 참조 0개다.
`04-scripts-and-validation.md`가 "본문 내 상대 링크 대상 미존재"를 명세했는데도.

**두 갈래 중 하나 — 권장은 넓히기(WS2와 함께).** `_check_dead_links`를 백틱 없는 산문 형태와
마크다운 링크 형태까지, 그리고 reference 파일들에 대해서도 돌게 한다(파일 8개뿐이라 저렴하다).
그러면 B7이 인정이 아니라 해결이 된다. 넓히지 않기로 하면 `:111`, `:105`, `e2e-testing.md:7`을
실제 커버리지로 좁혀 다시 쓴다.

### WS1-4 · B8 · dangling pointer 3건

| 위치 | 문제 | 수정 |
|---|---|---|
| `SKILL.md:39` | "(protected path, see Hard lines)" — Hard lines(`:109-113`)는 보호 경로를 언급하지 않고 메커니즘이 스킬 어디에도 없다 | WS5가 만드는 `hooks.md`의 보호 경로 절로 재지정 |
| `interview.md:42` | "the layer-routing framework from SKILL.md **§3**" — SKILL.md에 번호 매긴 절이 없다. 번호가 `02-skill-design.md:87`에서 샜다 | 절 제목으로 참조 |
| `hooks.md:86` | "the timeout column in hooks-events.md" — 그 표의 7개 헤더(`:309`)에 timeout 열이 없다 | 세 숫자를 인라인하고 포인터 삭제 (WS1-5와 동시) |

### WS1-5 · B5 · SessionEnd 타임아웃

`hooks-events.md:330`은 "Default timeout **1.5 seconds** (shortest of any event by nearly two orders of
magnitude)"라 하고 `:314`는 MessageDisplay의 10초를 "(shortest of any event)"라 한다 —
**둘 다 참일 수 없고 1.5 < 10이다.**

라이브 문서: SessionEnd hook들은 **1.5초 예산을 공유한다.** per-hook 기본 타임아웃이 아니라
공유 예산이며, 메커니즘 자체가 다른 모든 이벤트와 다르다. per-hook `timeout`을 올리면 공유 예산이
그만큼 올라간다(최대 60초).

가중: `hooks.md:86`은 "Two events break that pattern hard"라 하는데 **셋**이다
(`UserPromptSubmit` 30초, `MessageDisplay` 10초 — hooks.md에 아예 없다 —, `SessionEnd` 1.5초 공유).

**수정.** `:314`의 거짓 최상급 삭제. `:330`의 라벨을 공유 예산으로. `hooks.md:86` 문단 전체를
**개수와 열거가 어긋날 수 없게** 다시 쓰고 dead pointer 삭제.

> 근본 원인은 문서 드리프트다. 7월 스냅샷 `05-reference/07-hooks-reference.md:2623`이 문자 그대로
> "SessionEnd hooks have a default timeout of 1.5 seconds"이고 repo는 충실히 복사했다.
> **규칙을 지켰는데 틀렸다** — D24 참조.

### WS1-6 · B10 · 닫히지 않은 코드 펜스

`agents.md:73`이 ` ```markdown `을 열고 닫지 않는다(`grep -c '^```'` = 1). 렌더러와 파서에 따라
파일 나머지 전체가 코드 블록으로 먹힌다.

### WS1-7 · 라우팅 행의 reference 포인터

`SKILL.md:36`이 `references/<component>.md` 명명 규약을 넘겨주는데, 7개 컴포넌트 타입 중 3개에서
파일명이 유도되지 않는다 — CLAUDE.md와 rules는 `claude-md-and-rules.md`를 공유하고, permissions는
`hooks.md` 안에 산다. 라우팅 표 8행 중 4행(`:73`, `:74`, `:77`, `:80`)에 포인터가 없다.
**표지판 누락이지 불가능한 명령이 아니다** — SKILL.md는 통째로 로드되고 `:57`과 다른 곳에서 두 파일을
이미 이름으로 부른다. 세 행에 포인터를 붙인다(+20단어).

---

## WS2 — 스크립트 정확성

### WS2-1 · B1 · `_AT_IMPORT_RE`

현재: `(?<!\`)@([\w./\-]+\.\w+)(?!\`)`. 실행 확인: `contact ops@acme.com` → `acme.com`,
`stay on react@18.2.0` → `18.2.0`. 각각 `:419`에서 `E: @acme.com import target does not exist`가 되고
`:486`이 E를 non-zero exit으로 바꾼다. **`SKILL.md:112`의 Hard line 2가 유지보수자 이메일이나 핀 버전을
언급하는 CLAUDE.md에 대해 충족 불가능하다.**

같은 정규식의 추가 결함 2개: `See @README for overview`(메모리 문서 자신의 실제 import 예시)를
통째로 놓치고, fenced code block 안의 `@docs/nope.md`가 여전히 매치된다 — 문서는
"Import parsing skips Markdown code spans and fenced code blocks"라고 명시한다.

**수정.** fence/code-span 건너뛰기를 실제로 구현하고, 필수 점-확장자 요구를 없애고, 경로 형태를
요구한다(줄 시작 또는 공백 경계).

### WS2-2 · B3 · 발견 경로

`audit_harness.py:38`과 `validate_harness.py:402`가 `root / "CLAUDE.md"`를 하드코딩한다.
라이브 문서: "A project CLAUDE.md can be stored in either `./CLAUDE.md` or `./.claude/CLAUDE.md`."

두 번째 위치를 쓰는 프로젝트는 `audit_harness.py:244`에서 `- CLAUDE.md: absent`가 찍히고 `:205`의
`has_any_component`에서 빠져 재진입 패스에서 **`"new -- no harness components found at all."`로 분류된다** —
감사가 인터뷰하는 클로드에게 거짓말을 하고, D6의 일급 경로에서 스크립트 자신의 목적을 무너뜨린다.
`:178`의 `~/.claude/CLAUDE.md` 충돌 검사도 같은 값에 게이팅돼 조용히 안 돈다.

같은 부류: `harness_common.py:282`가 `glob("*.md")`고 `:264`의 `iter_agent_files`도 비재귀다.
`paths:`가 없는 중첩 rule 파일은 launch에 로드되는데 린터·인벤토리·drift 검사 전부에서 안 보인다.

**수정.** `harness_common.py`에 `claude_md_paths(root)` — `root/CLAUDE.md`, `root/.claude/CLAUDE.md`,
`root/CLAUDE.local.md`. `inventory_claude_md`는 리스트 반환, `check_claude_md`는 각 파일에 대해 실행.

> **`rglob` 쓰지 말 것.** Python 3.12와 3.13이 심링크 재귀에서 동작이 다르고, Claude Code는 심링크된
> rules 디렉토리를 실제로 따라간다(문서 확인). **명시적 resolved-path visited-set 워크**를 쓴다.

**공짜 경고 2개:** `./CLAUDE.md`와 `./.claude/CLAUDE.md`가 동시 존재(둘 다 로드·연결·무오버라이드),
spec에 행이 없는 중첩 CLAUDE.md.

### WS2-3 · B9 · spec 규약 불일치

`validate_harness.py:460`은 컴포넌트가 "언급됨"으로 치려면 **백틱 안의 전체 repo-상대 경로**를 요구한다.
`interview.md:117`의 예시 행은 `| B1 | ... | hook | pre-commit-test | generated |` — 맨 이름이다.
hook과 rule은 그 검사에서 면제(`:462-467`이 skills/agents/workflows만 본다)라 예시 행은 **우연히** 안전하지만,
그 맨이름 스타일을 스킬 행으로 확장한 모델은 정상 하네스에서 오탐을 받는다.
두 스크립트도 서로 다르다: 감사는 맨 stem을 받고(`:160`) 린트는 백틱 전체 경로를 요구한다.

**수정 방향 — 위로 수렴.** 산문에서 규약을 명시한다(항상 백틱 감싼 repo-상대 경로를 쓴다).
`validate_harness.py:460`을 느슨하게 풀지 않는다.

> **구현 시 개정 (2026-08-03).** 위 지시를 그대로 따르면 **이 계획 자신의 WS2-6 원칙과 충돌한다**:
> 맨이름으로 쓰인 spec은 컴포넌트가 실제로 언급돼 있는데도 "component exists on disk but isn't
> mentioned in the spec" W를 받는다 — **정상 하네스에서 울리는 체크**다. 두 목표를 모두 만족시키도록
> 소견을 **두 개로 분리**했다: 백틱 전체 경로면 통과, **맨이름이면 "규약대로 다시 쓰라"는 별개의 정확한
> W**, spec에 아예 없을 때만 기존의 drift W. 린터는 느슨해지지 않았고(여전히 규약을 요구한다),
> 거짓 보고는 사라졌으며, 두 스크립트의 판정이 일치한다. 픽스처 `spec-bare-name-skill`이 이를 고정한다.

### WS2-4 · B11 · `--json` 키 누락

`audit_harness.py:139`는 no-spec 분기에서 `in_spec_not_on_disk: []`를 반환하는데 `:162-171`에선 키를
빠뜨린다. `--json` 소비자가 그 키를 기준으로 잡으면 **spec이 존재할 때 정확히 깨진다.**
WS1-2에서 함께 해결된다.

### WS2-5 · always-loaded 예산 리포트

무조건 출력(경고가 아니라 **측정**), `--json`에도 포함:

```
Always-loaded context, project scope (every session, before the first prompt):
  CLAUDE.md                          142 lines    5.1 KB
  @docs/api-conventions.md         1,904 lines   71.0 KB   import, expands at launch
  .claude/rules/testing.md            38 lines    1.3 KB   NO paths:, loads at launch
  .claude/rules/frontend/ui.md        61 lines    2.1 KB   NO paths:, loads at launch
  ------------------------------------------------------
  TOTAL                            2,145 lines   79.5 KB
  Not counted here: user-scope (~/.claude/CLAUDE.md, ~/.claude/rules/), ancestor-directory
  CLAUDE.md files, and auto memory (machine-local).
```

**"셀 수 없는 표면"을 명시하는 줄이 필수다** — 없으면 이 숫자가 전부인 것처럼 읽힌다.
`@`-import는 4-hop 상한까지 재귀하되 visited set으로 한 번만 센다. 임계 초과 시에만 경고하고,
**임계값과 그 사유와 모노레포 예외를 같은 호흡에** 낸다(스킬 자신의 규칙).

### WS2-6 · 휴리스틱 체크 — 3개만

**만든다 (전부 W 등급):**

1. **generic-advice 문구 목록.** `claude-md-and-rules.md:25`가 산문으로만 금지하던 걸 기계화.
   **substring이 아니라 문장/불릿 전체 앵커링** — 그래야
   "Be consistent with the existing handler naming (`handleFooRequest`)"가 안 걸린다.
2. **deny-subsumes-allow.** 근-제로 오탐. 프로젝트 스코프만 보인다는 걸 메시지에 명시.
3. **`paths: "**"` 경고 — 단 메시지를 정정해서.** catch-all glob은 **launch가 아니라 첫 매칭 파일 읽기에**
   로드된다. 잘못된 메시지를 출하하면 B5를 반복한다.

**만들지 않는다 (사유 기록 필수):**

- **디렉토리 트리 탐지기.** 유일하게 작동하는 임계값이 ASCII 제어흐름 다이어그램을 잡는다 —
  **`SKILL.md:23-61`이 바로 그것이다.** 자기 자신을 오탐한다.
- **의존성 목록 / 아키텍처 개요 탐지기.** 나쁜 경우와 루브릭이 명시적으로 남기라는 경우를 가르는
  어휘 신호가 없다. 만들면 생성기가 프로젝트가 아니라 린터를 위해 글을 쓰게 된다.

> **원칙: 정상 하네스에서 울리는 체크는 체크가 없는 것보다 나쁘다.** 각 체크는 픽스처로
> false-positive 케이스를 **먼저** 갖는다.

### WS2-7 · dead-link 검사 넓히기 (WS1-3 동반)

백틱 없는 산문 형태와 마크다운 링크 형태까지, 그리고 reference 파일 8개에 대해서도.

---

## WS3 — auto memory와 개인/팀 스코프 축

**요지.** 두 번째 always-loaded·클로드-저작·머신-로컬 지시 표면이 `claude-md-and-rules.md:25`가
CLAUDE.md로 라우팅하는 것과 같은 내용 범주를 담는데 스킬 언급이 0건이다. `CLAUDE.local.md`도 0건이라
"이 개발자만 필요한 것"의 목적지가 없다.

### WS3-1 · 라우팅 축 (D17)

**행의 목적지는 `CLAUDE.local.md`다, auto memory가 아니라.** auto memory는 비결정적이므로
(문서: "Claude doesn't save something every session. It decides what's worth remembering") 개발자가
클로드에게 반드시 있어야 하는 사실을 거기 라우팅하는 건 안전하지 않다. `CLAUDE.local.md`는
결정적·저작가능·gitignore된다 — 메모리 문서 자신의 정전 사례다("Your sandbox URLs, preferred test data /
Just you").

`SKILL.md:82`의 세 질문에 **네 번째를 추가한다** — 빠진 건 목적지가 아니라 **축**이기 때문이다:

> **Who needs this — every clone, or only this machine? And who writes it — you, or Claude at runtime?**

그리고 `:82`의 비용 문장을 고친다: always-loaded 예산은 CLAUDE.md 단독이 아니라
**CLAUDE.md + `paths:` 없는 모든 rule + `@import` 전개 + `MEMORY.md` 앞 200줄/25KB**의 합이다.
MCP 도구 스키마는 기본적으로 지연 로드되므로 이름만 상주한다 — 지연된 MCP 서버에 토큰 비용을 매기지 않는다.

### WS3-2 · `claude-md-and-rules.md`

"Content eligibility test" 다음에 스코프 축을 넣고 `CLAUDE.local.md`를 이름으로 부른다. 함께:

- `MEMORY.md`는 **앞 200줄/25KB만** 매 세션 로드된다(CLAUDE.md는 길이 무관 전문 로드와 대조).
- auto memory는 통째로 꺼질 수 있다(`autoMemoryEnabled: false`, `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`) —
  **load-bearing한 것을 거기 의존시키지 않는다.**
- `:25`의 "a sandbox URL" 예시를 정정한다 — 그건 지금 `CLAUDE.local.md`의 정전 사례다.
- **compaction 생존 매트릭스**: 루트 CLAUDE.md와 `paths:` 없는 rule은 재주입, **중첩 CLAUDE.md와
  `paths:` rule은 매칭 읽기가 다시 일어날 때까지 소실.** `:44`의 모노레포 기본값이 이것과 만나면
  "절대 잃으면 안 되는" 규칙이 조용히 사라진다.
- **AGENTS.md 상호운용**: Claude Code는 `CLAUDE.md`를 읽지 `AGENTS.md`를 읽지 않는다. 병렬 본문을 쓰지 말고
  `@AGENTS.md`를 첫 줄로(또는 심링크). 기존 외부 규칙 내용은 **이미 표면화된 인터뷰 재료**다.

### WS3-3 · `agents.md`에 `memory:` 행

**함정을 먼저.** `memory: user|project|local`. `project`(문서가 "the recommended default"라 부름)는
버전 관리되는 `.claude/agent-memory/<name>/`을 만들고, memory를 켜면 **Read/Write/Edit가 자동으로 켜진다** —
`:61`과 `:73-90` 예제가 요점이라고 못 박은 읽기 전용 `tools:` 제한을 무효화할 수 있다.
**선후관계는 문서화돼 있지 않다 — 그렇게 적는다.** auto memory가 꺼져 있으면 조용히 no-op이므로
memory 존재에 의존하는 에이전트 프롬프트를 생성하지 않는다.

표는 **짧은 큐레이션 집합으로 유지한다.** `memory`가 행을 얻는 이유는 버전 관리 디렉토리를 쓰고
Write/Edit를 조용히 다시 켜기 때문이다 — `background`, `effort`, `maxTurns`, `mcpServers`,
`initialPrompt`는 그러지 않으므로 행을 얻지 못한다. `color` 행은 스스로 판단 사항이 아니라고
인정하므로 삭제한다.

### WS3-4 · 감사 확장

- `check_user_scope_conflicts`에 `~/.claude/rules/*.md` 추가(`paths:` 없는 항목은 모든 프로젝트에 로드).
- **외부 지시 파일 존재 감지**: `AGENTS.md`, `.cursor/rules/`, `.cursorrules`,
  `.github/copilot-instructions.md`, `.windsurf*`, `.clinerules`. **보고만, 파싱 금지, drift 집합에 넣지 않음.**
- **`~/.claude/projects/<project>/`를 스크립트로 만지지 않는다.** 디렉토리 슬러그 인코딩은 문서화돼
  있지 않아 리버스 엔지니어링해야 하고, 사용자의 사적 노트다. 대신 Phase 0에서 **인터뷰하는 클로드에게**
  열어보라고 지시한다.

---

## WS4 — SKILL.md 상시 로드 경량화

| 대상 | 조치 | Δ |
|---|---|---|
| "Interview protocol, summarized" `:90-92` 전체 | **삭제**(제목 포함). `:32`가 이미 로드 지시를 담고, `:92`의 "re-entry shrinks or reframes the early stages"는 sync에 대해 **이미 틀렸다**(`interview.md:99`는 I1-I5 순회가 없다고 말한다) | −126 |
| `:63` flexibility 문단 | 83 → 30단어 | −53 |
| `:65` 경로 규칙 | Scripts 절(`:96`)로 병합, 76 → 44단어. 치환 범위 절 추가(WS6의 B4와 동일 사실) | −32 |
| `:44`, `:46`, `:86`, `:105`의 순수 강조 절 | **삭제**(D23). **why 문장은 전부 남긴다** — `:45`의 "validate_harness.py cannot check this for you"는 다른 어디에도 없고(`hooks.md`에 `validate_harness.py` 언급 0건), Hard line 2의 "A checklist that isn't mechanically enforced doesn't get enforced"는 그 줄의 유일한 why다 | −41 |
| `:52-55` 부정 절 | B2 재정렬로 불필요 | −19 |
| `:59` 거짓 주장 | B2 | −13 |
| `:69` "muscle memory" | 서술 | −21 |
| `:88` "this skill's own files and" | 배포된 플러그인 사용자에게 무의미한 개발자용 5단어. **문단 자체는 유지** — 나머지 65단어는 런타임 지침이다 | −5 |
| Hard line 2 재구성 | | −10 |

**추가:** auto-memory 라우팅 축(+50), 라우팅 행 포인터(+20), `:39` 재지정(+5),
인터페이스 원칙 절(+25), Hard line 1 정확성(+5).

**`SKILL.md:86`의 교리는 압축하지 않는다**(D18). 인터뷰 단계가 보는 유일한 교리 사본이고,
hooks-only나 CLAUDE.md-only 패스에서는 어떤 reference도 복원하지 않는다.

**동반 정렬:** `skills.md:22`의 "not a direction"을 `SKILL.md:86`과 맞춘다.
`skills.md:3`을 "everything here applies to CLAUDE.md and rules too"에서
**"philosophy transfers, mechanics don't"**로 좁힌다 — 8개 reference 중 유일하게 자기 범위 선언
("Read this before…")이 없고 유일하게 다른 레이어에 대한 관할권을 주장한다.
`hooks.md:5`와 `e2e-testing.md:13`의 개발자용 서술 2건 삭제.

---

## WS5 — 조용한 실패를 갖는 누락 메커니즘

문단 4개, 전부 독립적. 각각 생성된 컴포넌트가 **조용히 무력하거나 조용히 무방비**가 되는 경우다.

### WS5-1 · workspace trust를 "capability-granting 프로젝트 설정"으로 확대

`hooks.md:104`는 지금 "project allow rules"만 말한다. 실제 게이트 대상:
프로젝트 `permissions.allow`, `additionalDirectories`, `autoMemoryDirectory`,
프로젝트 스킬의 `allowed-tools`, `statusLine`, 그리고 **(v2.1.218+) 프로젝트 서브에이전트의
frontmatter hooks** — 후자는 폴더가 신뢰되기 전까지 **디버그 로그 한 줄만 남기고 조용히 건너뛴다.**

**귀결:** 신뢰되지 않은 fresh clone에서는 **어떤 프로젝트 hook도 발화하지 않고
`permissions.deny`/`ask`만 남는다.** 같은 한 절을 `agents.md:41`에도.

`.claude/settings.local.json`도 **repo가 공급했을 수 있으면**(git 커밋됨, 또는 `.claude`가 심링크)
같은 검사를 거친다.

### WS5-2 · 보호 경로

`hooks.md`에 짧은 절, `SKILL.md:39`가 여기를 가리킨다.

- `.claude`는 **보호 디렉토리**(`.claude/worktrees` 제외). `.mcp.json`, `.claude.json`도 보호 파일.
- **`permissions.allow`는 보호 경로 쓰기를 사전 승인하지 못한다** — 안전 검사가 allow 규칙 평가보다
  먼저 돌아서 `Edit(.claude/**)`는 아무 효과가 없다. **생성기가 반사적으로 손댈 바로 그 수정이다.**
- 모드별: `default`/`acceptEdits` 프롬프트, `plan` 프롬프트, `auto` 분류기, **`dontAsk` 거부**,
  `bypassPermissions` 허용.
- 프롬프트가 뜨는 모드에서 **"Yes, and allow Claude to edit its own settings for this session"** 선택지가
  있다 — 사용자에게 실제로 알려줄 가치가 있는 유일한 디테일.

**최소 대 완전.** 최소는 `SKILL.md:39` 재지정 + 두 사실(allow가 사전 승인 못 함, 세션 승인 선택지).
완전은 전체 보호 파일 목록 + 모드별 표. **권장은 최소 + 모드별 표의 `dontAsk` 행**
(생성된 하네스가 CI에서 `dontAsk`로 돌면 조용히 거부되므로).

### WS5-3 · "기본값과 모순되는가" 검사

스킬은 기본값을 **중복**하는 규칙은 이미 잡는다(`claude-md-and-rules.md:15`, `skills.md:18`,
`SKILL.md:86`). 못 잡는 건 기본값과 **모순**되는 규칙이다 — 같은 필터들이 오히려 그걸 **남긴다**.
"이 줄을 지우면 클로드가 실수하게 되나?"는 기본값과 싸우는 줄에 대해 정확히 "예"라고 답한다.

`claude-md-and-rules.md:25` 다음에 한 문단. **"금지가 아니라 의도를 생성하라"**로 프레이밍한다.
날짜 표기된 예시를 쓰되 **날짜가 표기됐음을 명시**하고, 시스템 프롬프트 내용의 출처가
문서가 아니라 블로그임을 플래그한다. 같은 패스에서 `agents.md:15`의 미검증 기본값 목록도 고친다.

### WS5-4 · hook eligibility의 두 번째 질문

`hooks.md:9`의 "must this never be violated?"는 인터뷰받는 사용자가 거의 다 "예"라고 답하는 질문이다.
비용 측은 잘 서술돼 있으나 **테스트가 되지 못한다.** 다섯 곳이 단면적이다
(`hooks.md:9`, `SKILL.md:76`, `SKILL.md:82`, `interview.md:44`, `interview.md:117`).

두 번째 질문을 **되돌릴 수 있는가 + 이미 다른 게 잡는가**로 추가한다. 그리고 `hooks.md:228`에
Stop의 턴당 비용 주의를 붙인다 — Stop은 "once per turn" 케이던스이고, 레시피 2와 달리
`decision` 채널을 포기하지 않고는 `async`가 될 수 없다.

`interview.md:36`의 정찰 목록에 "a CI config"를 추가한다(두 단어). 게이트로 만들지는 않는다.

### WS5-5 · 배포 축 (interview.md I4)

크로스-repo/플러그인 질문 한 개. **gotcha: CLAUDE.md, rules, permissions는 플러그인 컴포넌트가 아니다.**
플러그인 패키징 생성은 여전히 범위 밖(`06-milestones.md:120`) — 인터뷰가 경로를 이름으로 부를 뿐이다.

---

## WS6 — 예제의 도메인 서사 제거 (**위험 구간**)

`00-overview.md` §5의 판별식. 블록별 측정치:

| 파일 | 블록 | 단어 | 조치 |
|---|---|---:|---|
| `hooks.md:159-183` | 레시피 1 보호 경로 | 158 | **유지** — 인터페이스 |
| `hooks.md:185-206` | 레시피 2 포매터 | 125 | JSON 형태가 레시피 1과 동일 — JSON 제거, 요점만 |
| `hooks.md:208-228` | 레시피 3 Stop 게이트 | 156 | 동상 — 요점을 Stop gotcha로 흡수 |
| `hooks.md:39-50` | 스킬 frontmatter YAML | 23 | **유지** — 다른 형태의 인터페이스 |
| `skills.md:76-91` | file-bug-report 트리 | 265 | `:80-89`의 트리는 **유지**, `:91`의 `:26` 재논증만 삭제 |
| `agents.md:69-90` | security-reviewer | 342 | frontmatter 블록 **그대로 유지** + "You read code; you never modify it" 도입부 + "keep the report short" 마무리 유지. 3단계 보안 리뷰 절차와 이슈별 리포트 형식 삭제 |
| `workflows.md:42-124` | audit-auth-routes | 606 | **→ ~280단어.** 실행 가능한 코드로 남고 **짧은 진짜 프롬프트** 유지. `:19-27`을 재진술하는 스테이지 경계 주석과 프롬프트 문자열 안의 인증 도메인 산문 삭제 |
| `e2e-testing.md:29-88` | 워크플로우 스켈레톤 | 468 | Phase-Report 블록(`:76-85`) 삭제 — workflows.md의 synthesize 스테이지와 관용구가 동일하고 repair-target 라우팅은 `:126-134`에 이미 7행 표다. **Run은 유지**(`run_e2e.py --project --prompt --out --json --isolate` 호출 형태와 V3 near-miss를 담는다). Grade는 서사만 제거 |
| `claude-md-and-rules.md:47-95` | bad/good 쌍 | 288 | Bad 블록(`:49-66`) 삭제, 제목을 "A good CLAUDE.md, concretely"로. Good 블록 유지하되 `:72`(스택 요약)와 `:82`(2-space indentation) 수정 — **둘 다 이 파일 자신의 `:15`/`:25` 테스트에 걸린다** |

### WS6-B4 · `${CLAUDE_SKILL_DIR}` (같은 패스에서)

`e2e-testing.md:50`이 `` `Run: python "\${CLAUDE_SKILL_DIR}/scripts/run_e2e.py" ...` ``를 쓴다 —
`\$`는 의도적 템플릿 리터럴 이스케이프라 **리터럴 문자열이 서브에이전트에 도달하고** Bash로 넘어간다.
치환은 스킬의 마크다운 본문과 `allowed-tools` Bash 규칙에만 적용되고, hooks 문서의 환경변수 목록에도
없다. 결과는 mid-run permission stall이거나 `python "/scripts/run_e2e.py"` file-not-found —
그리고 **`e2e-testing.md:144`가 이미 모델에게 그걸 permission 메커니즘 탓으로 오귀인하도록 준비시켜 놨다.**

**수정.** 메인 대화가 절대 경로를 해석해 JS const로 인라인한다.

> **편집 전 확인할 것:** `e2e-testing.md:68`/`:71`이 스키마 없는 `agent()` 결과에서 `run.label`을 읽는다.
> 라이브 workflows 문서에 문서화돼 있지 않다 — **그 블록의 네 번째 결함일 수 있다.**

---

## WS7 — 인터뷰 감산과 외부 편집 생존

### WS7-1 · 외부 편집은 부패가 아니다 (D14 준수 — 도구 이름 없이)

`interview.md:99`에 한 문장. 디스크에 있는데 spec이 언급하지 않는 컴포넌트, 또는 CLAUDE.md에서
스킬이나 중첩 CLAUDE.md로 옮겨간 행동은 **다른 도구나 동료의 정상적 산출물**이다. 재생성을 제안하기 전에
어느 쪽인지 묻고, 기본값은 **spec을 갱신하는 것**으로 한다.

그리고 정직한 한계를 적는다: 루트나 중첩 CLAUDE.md에 대한 편집은 **drift 목록에 아예 나타나지 않는다** —
`audit_harness.py`가 루트 파일만 인벤토리하기 때문이다.

### WS7-2 · 감산이 눈에 보이게

통합 압력은 이미 있다(`SKILL.md:34-35`, `:75`, `:78`, `skills.md:42-44`, `agents.md:9`).
빠진 건 두 가지: 무엇을 **만들지 않기로 했는지 소리내어 말하라**는 지시, 그리고 **그걸 어디에
기록하는지**. `interview.md:38`의 I2 게이트 문장을 확장하고, spec의 `status` 어휘에 `declined`를 추가한다.

### WS7-3 · 은퇴 라운드

`e2e-testing.md`의 피드백 라우팅 표에 행 하나. **제품 메커니즘으로 정당화한다** — 스킬의 description은
트리거하든 안 하든 매 세션 리스팅에 있고, `paths:` 없는 rule은 launch에 로드된다.
`disable-model-invocation: true`를 중간 설정으로 제시한다. spec `status`에 `retired` 추가.

> **위험.** 사용자가 의도적으로 추가한 걸 지우자고 제안하는 은퇴 라운드는 침묵보다 나쁘다.
> **모든 후보는 비용이 명시된 질문이어야 하고 절대 행동이어서는 안 된다.** 스킬에는 호출 텔레메트리가
> 없으므로 "미사용"은 디스크에서 측정할 수 없다.

### WS7-4 · 조건부 rubric

spec 템플릿에 assertion 타입으로 게이팅된 `rubric:`. **`:110`(Behavior compliance)과
`:112`(Artifact quality)만** 자격이 있다 — 나머지 셋은 본질적으로 이진이라 rubric이 순수 오버헤드다.

> grader 스키마를 `{dimensions, overall}`로 바꾸면 `:77`의 필터도 갱신해야 한다.
> 안 그러면 스켈레톤이 자기 자신에 대해 실행되지 않는다.

### WS7-5 · 인터페이스 원칙 착지 (D16)

`SKILL.md:86`에 한 절 + 기존 홈들: `skills.md:38-40`(번들 스크립트 CLI — **이미 있다**),
`agents.md`의 `description`/`tools`, `hooks.md`의 설정 입력, `workflows.md`의 `args`,
`skills.md`의 `description` as dispatch signal. **새로 쓰지 말고 연결한다.**

`SKILL.md` 절 초안(≈25단어 증분, 나머지는 기존 문장 재프레이밍):

> Some behaviors don't need to be told to Claude at all — the thing Claude operates can be shaped so the
> wrong move isn't available. An interface is re-read from the tool's own signature on every use: every
> session, after every compaction, inside every subagent, including the ones that skip CLAUDE.md entirely.
> The harness's own interface surfaces are a bundled script's CLI, a hook script's configuration input, a
> workflow's `args`, a skill's `description`, an agent's `tools:`. The boundary: an interface expresses what
> is valid, never when to reach for it or why this project chose it. This applies to what the harness
> contains — this skill designs harnesses, not the project's application code.

---

## WS8 — interview.md 분기화 (D22, **2단계 순서 엄수**)

**1단계 (선행 필수).** `interview.md:93-99`의 sync 절차와 `:132`의 status 진행 의미론을 옮긴다.
sync 절차는 스킬 전체에서 **여기에만** 있고, status 의미론은 `audit_harness.py:165-170`이
명시적으로 모델에게 위임하는 것이다. 목적지 후보:

- **SKILL.md** — sync는 Phase 0에서 분기하므로 상시 로드가 자연스럽다. 다만 §4의 SKILL.md 예산과 경쟁.
- **`references/re-entry.md` 신규** — sync 경로에서만 로드. 분할 축이 진짜 분기(모드)라 스킬 자신의
  기준을 통과한다.

권장: **신규 `re-entry.md`.** SKILL.md 예산을 지키고 분할 기준을 만족한다. WS1-2의 drift 방향 수정이
어차피 이 텍스트를 건드리므로 함께 한다.

**2단계.** `SKILL.md:92`의 무조건 로드 지시를 인터뷰가 실제로 일어나는 경로로 제한한다.
`SKILL.md:30-31`이 Phase 0에서 `interview.md`에 손을 뻗는 부분도 함께 정리한다.

**순서를 어기면 sync 모드가 고립된다.**
