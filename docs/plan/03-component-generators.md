# 03 — 컴포넌트별 생성 원칙과 gotcha 인벤토리

각 references/ 파일에 인코딩할 내용의 핵심. **여기의 gotcha들은 리서치로 검증된 사실이며
(출처: docs/plan/research/), LLM이 사전지식으로 모르거나 자주 틀리는 것들만 추렸다 —
스킬에 담을 최고 밀도 지식이다.** 구현 세션은 이 목록을 기준으로 references를 작성하되,
research/ 원본과 `.tmp/docs_claude/`에서 세부를 보강한다.

**전 컴포넌트 공통 작성 규칙**: 생성되는 모든 마크다운 산출물(CLAUDE.md, rules, SKILL.md,
agents, harness-spec.md)에서 **문장 중간 인위적 줄바꿈(하드 랩)을 금지**한다. 줄바꿈은
문장·목록 항목·단락 경계에서만. 하드 랩은 이후 세션의 Edit 도구 문자열 매칭을 깨뜨리고
diff를 오염시키며, 렌더러의 soft wrap 앞에서 아무 이득이 없다. 이 규칙을
references/skills.md와 claude-md-and-rules.md의 작성 지침에 포함시킬 것.

## 1. CLAUDE.md + rules (`references/claude-md-and-rules.md`)

### 원칙
- **CLAUDE.md는 시스템 프롬프트가 아니다.** 시스템 프롬프트 뒤에 붙는 advisory user message.
  강제가 필요한 항목은 여기 두면 안 된다(라우팅 프레임워크로 되돌릴 것).
- **200줄 이하 목표** — 길수록 준수율이 떨어진다. 자격 심사: "모든 세션에서 필요한가?"
- **포인터 정책**: 컴포넌트 인벤토리(스킬 목록, 에이전트 목록)를 CLAUDE.md에 나열하지 않는다.
  파일시스템이 단일 진실 공급원. CLAUDE.md에는 트리거 규칙·핵심 사실·harness-spec.md 포인터만.
  (revfactory가 전체 등록 → 포인터로 회귀한 검증된 교훈.)
- 내용 자격: 코드에서 유추 불가능한 것만 — 빌드/테스트 명령, 기본값과 다른 스타일 규칙,
  아키텍처 결정, 환경 함정. "clean code를 쓰라" 류 일반론 금지.
- 구체적·검증가능하게 ("2-space indent", not "format properly"). 강조("IMPORTANT")는
  준수율을 올리지만 남용하면 무력화된다.

### gotchas
- 프로젝트 루트 CLAUDE.md는 **세션 시작 시 1회만 로드** — 수정해도 실행 중 세션에 반영 안 됨
  (`/clear`·`/compact`·재시작 필요). e2e 반복 시 세션을 새로 띄워야 하는 이유.
- 모든 CLAUDE.md는 **연결(concatenate)이며 override가 없다** — 상충 규칙은 임의 선택됨.
  user(~/.claude/CLAUDE.md)와 project가 충돌하지 않게 감사 단계에서 user 쪽도 확인.
- `@path` import는 launch 시 확장(최대 4홉), 컨텍스트 절약 효과 없음. 백틱으로 감싸면 억제.
- HTML 블록 주석은 주입 전에 제거됨 — 유지보수 메모를 공짜로 남길 수 있다.
- rules: `paths:` frontmatter 없는 rule은 launch 시 로드(CLAUDE.md와 동급) — 분할 효과를
  원하면 반드시 paths를 넣는다. glob은 `src/**/*.{ts,tsx}` 브레이스 확장 지원.
- 하위 디렉토리 CLAUDE.md는 해당 경로 파일을 만질 때 lazy 로드 — 모노레포에서 rules와
  하위 CLAUDE.md 중 선택 기준: 여러 경로 패턴에 걸치면 rules, 디렉토리 단위면 하위 CLAUDE.md.
- **auto 모드 분류기는 CLAUDE.md를 읽는다** — 생성한 CLAUDE.md 문구가 auto 모드의
  allow/block 판단에 직접 영향. 금지 사항은 CLAUDE.md 서술 + deny rule 쌍이 내구성 있는 형태.

## 2. Skills (`references/skills.md`)

### 원칙 (사용자 철학의 정수 — skill-creator SKILL.md §2·3에서 승계할 것)
- **Conviction over compliance**: 모든 지시 = what + 설득력 있는 why + 구체적 그림.
  why만 주고 지시를 재유도할 수 있으면 합격. 규칙은 예상 못 한 16번째 케이스에서 부러진다.
- 모델이 이미 아는 것은 쓰지 않는다. 최고 신호 콘텐츠는 **gotcha**(실패해봐야 아는 도메인 함정).
- Progressive disclosure는 최적점: 분할 기준은 **로드 시점(invocation pattern)**이지 분량이
  아니다. 과분할 = 조용한 라우팅 실패. references는 모델이 선택 분기하는 변형별로 조직.
- description이 유일한 트리거. 본문의 "when to use"는 무용. under-trigger 경향이므로
  트리거 쪽으로 기울인다. near-miss(비슷하지만 트리거되면 안 되는 요청)를 경계 서술로 반영.
- 스크립트는 파라미터 받는 CLI 또는 임포트 가능한 헬퍼. 동결된 단일용도 스크립트 금지.

### gotchas
- 스킬 명령 이름은 **디렉토리명**에서 온다(frontmatter `name`은 표시용).
- description+when_to_use는 목록에서 **1,536자 절단**. 스킬 목록 전체 예산은 컨텍스트의 1%
  (초과 시 저사용 스킬 설명이 이름만으로 축소) — 하네스에 스킬을 많이 만들수록 각 description이
  서로의 예산을 잠식한다. **스킬 수 자체가 비용이다** — 인터뷰에서 통합 가능성을 검토.
- `/compact` 후 스킬 목록은 재주입되지 않는다(호출했던 스킬만 보존) — 긴 세션에서
  자동 트리거가 열화됨. 핵심 스킬은 CLAUDE.md에 트리거 규칙 한 줄로 백업.
- frontmatter YAML이 깨져도 본문은 로드된다(자동 트리거만 죽음) — 조용한 실패, 린트로 잡는다.
- `context: fork` + `agent:`로 스킬 본문을 서브에이전트 프롬프트로 실행 가능,
  `allowed-tools`로 스킬 활성 중 사전 승인 도구 지정 가능(권한 프롬프트 감소).
- `!`cmd`` 동적 주입은 모델 실행이 아니라 전처리 — 세션 시작 상태 주입에 유용.
- SKILL.md 수정은 세션 내 즉시 반영(CLAUDE.md와 다름!) — 반복 개선이 빠르다.

## 3. Hooks (`references/hooks.md` + `references/hooks-events.md`)

### 설계 원칙
- 훅 자격 심사: "어기면 안 되는가?" 어겨도 되는 건 CLAUDE.md/스킬로. 훅은 결정론이 필요한
  지점에만 — 남발하면 유연성을 죽이고 세션을 느리게 한다.
- **하드 보장은 permission rule과 쌍으로**: 훅의 `if` 필드는 best-effort(파싱 불가 명령에서
  fail-open). 공식 문서도 하드 allow/deny는 permission 시스템을 쓰라고 명시.
- 훅 스크립트는 `.claude/hooks/`에 파일로 (인라인 원라이너 금지 수준의 복잡도부터),
  settings.json에서 exec form(`args` 사용) + `${CLAUDE_PROJECT_DIR}` 절대 경로로 참조.
- 모든 생성 훅은 `test_hook.py`로 검증 후 납품(04 문서).

### gotchas (hooks.md에 — 전수 이벤트 테이블은 hooks-events.md에)
- **exit 1은 차단하지 않는다.** 차단은 exit 2뿐(Unix 관행과 반대 — 최다 실수 지점).
  exit 0 + stdout JSON이 결정 채널, exit 2 + stderr가 차단 채널. 상호배타적.
- matcher에 영숫자·`_-`·공백·`,`·`|` 외 문자가 하나라도 들어가면 **unanchored 정규식**으로
  돌변 (`Edit.*`는 NotebookEdit에도 매치). 정규식 의도면 `^...$` 앵커 필수.
- MCP 도구 matcher는 `mcp__server__.*` — 맨몸 `mcp__server`는 exact-match라 아무것도 안 잡힘.
- `@`파일 참조는 도구 호출 자체가 없어 PreToolUse(Read)를 우회 — 파일 보호는 Read deny rule로.
- Bash로 한 파일 수정은 Edit|Write matcher에 안 걸림 — 보완: Bash도 matcher에 포함하거나
  Stop 훅에서 `git status --porcelain` 스캔.
- PreToolUse deny는 bypassPermissions 모드에서도 동작(강한 보장). 반대로 hook allow는
  어떤 scope의 deny rule도 뚫지 못함(훅은 조이기만 가능, 풀기 불가).
- 같은 도구에 `updatedInput` 훅 2개는 경쟁(마지막 완료가 승리, 비결정적) — 생성기는
  도구당 입력 재작성 훅을 1개로 제한.
- Stop 훅 루프 가드: `stop_hook_active` 입력 확인 필수 + 연속 8회 차단 상한.
- `additionalContext`는 **사실 서술로** 쓴다("This repo uses bun test") — 명령형 문구는
  prompt-injection 방어에 걸려 사용자에게 노출될 수 있음.
- SessionEnd 기본 타임아웃 1.5초(다른 이벤트 600초와 자릿수 다름), UserPromptSubmit 30초.
- 훅 프로세스는 tty 없음, 쉘 프로파일의 stdout 오염이 JSON 파싱을 깨뜨림.
- 버전 게이트 존재(`if`=2.1.85+, comma matcher=2.1.191+ 등) — hooks-events.md에 버전 컬럼
  포함. 생성 시 "최신 stable 가정 + 버전 민감 기능은 주석으로 최소 버전 표기" 정책.

### hooks-events.md (전 30개 이벤트)
research/research-hooks-reference.md의 이벤트별 정리를 표로 재구성: 이벤트 | 발화 시점 |
matcher | 주요 입력 필드 | 결정 채널(JSON 필드/exit 2 의미) | 대표 용도 | 버전 주의.
전 30개 이벤트 수록하되(1차 소스 기준 전수 — 개수보다 "레퍼런스의 이벤트 목록 전부"가 기준)
대표 8개(SessionStart, UserPromptSubmit, PreToolUse, PostToolUse, Stop, SubagentStart/Stop,
PreCompact)는 예시 포함 상세, 나머지는 밀도 테이블로.

## 4. Permissions (hooks.md에 통합 — 별도 파일 없음, 로드 시점이 같음)

- 평가 순서 deny → ask → allow, **첫 매치 승리, 구체성 무관**. deny는 어느 scope에 있어도 승리.
- Read/Edit rule은 gitignore 문법: `//`=절대, `/`=설정 파일 기준 상대(프로젝트 settings면
  프로젝트 루트), 맨몸 파일명은 모든 깊이 매치. `Edit` rule은 Write/NotebookEdit도 지배,
  `Read` rule은 Grep/Glob/LSP도 지배.
- **프로젝트 settings.json의 allow rule은 워크스페이스 trust 승인 후에만 적용**(deny/ask는
  항상 적용) — 클론 직후 동작 차이를 스펙에 명시.
- auto 모드 진입 시 광역 allow(`Bash(*)` 등)는 드롭됨 — 협소한 rule만 생성 가치가 있다.
- 컴파운드 명령은 각 서브커맨드가 독립 매치되어야 함. `Bash(ls *)`의 trailing `*`는
  단어 경계 강제(`lsof` 미매치).

## 5. Agents (`references/agents.md`)

### 원칙
- 에이전트 자격: 컨텍스트 격리가 가치일 때(리서치·리뷰·QA처럼 읽기가 많고 결론만 필요),
  또는 도구 제한·별도 시스템 프롬프트가 필요할 때. **개수는 비용** — revfactory의 "항상 4-5개"
  안티패턴 금지. 필요가 증명된 역할만.
- 본문 = 시스템 프롬프트 전체 교체. Claude Code 기본 시스템 프롬프트가 사라진다는 것을
  전제로 자립적으로 작성.
- `model`은 기본 inherit — 특정 티어 강제는 근거가 있을 때만 (revfactory의 전원 opus 금지).

### gotchas
- **빌트인 Explore/Plan은 CLAUDE.md와 git status를 로드하지 않는다** — 하네스 규칙이 안
  닿는다. 핵심 규칙이 서브에이전트에도 필요하면: 위임 프롬프트에 재서술 지시(CLAUDE.md에),
  또는 커스텀 에이전트로 대체, 또는 SubagentStart 훅의 additionalContext로 주입.
- `skills:` 필드는 스킬 **전체 본문**을 기동 시 주입(설명만이 아님) — 컨텍스트 비용 주의.
- agent frontmatter의 hooks는 에이전트 수명 스코프, `Stop`은 SubagentStop으로 자동 변환.
- 식별자는 frontmatter `name`(파일명 아님). 같은 scope 중복 name은 하나만 로드(조용한 실패).
- 서브에이전트에서 AskUserQuestion 사용 불가 — 인터뷰를 에이전트에 위임하면 안 되는 이유.

## 6. Workflows (`references/workflows.md`)

### 원칙 (D12)
- 사전 정의 기준: 오케스트레이션 자체가 반복 산출물인가? (형태 고정, args만 가변,
  `/이름` 원버튼, 매회 같은 품질 보장 필요) → `.claude/workflows/*.js`.
  형태가 매번 다르면 → CLAUDE.md/스킬에 자연어 지침("이런 작업은 workflow로 fan-out").
- **얇게 만든다**: 스크립트는 fan-out/수집/게이트 골격만, 판단·내용은 각 agent 프롬프트에.
  워크플로우가 두꺼우면 유연성 장벽이 된다는 사용자 우려가 근거.
- 검증 루프 내장: fan-out → adversarial verify → synthesize 패턴을 기본형으로 제시.

### gotchas
- 파일 형식: `export const meta = {name, description}` **순수 리터럴** 필수 + top-level await
  JS. `Date.now()`/`Math.random()` 호출은 검증에서 거부됨(재개 결정론).
- `.claude/workflows/<name>.js` → `/<name>` 명령 자동 등록. project가 personal에 우선.
- 워크플로우 서브에이전트는 세션 모드와 무관하게 **acceptEdits로 실행** + 도구 allowlist 상속
  — 파일 수정이 자동 승인된다. 필요한 Bash/WebFetch는 `permissions.allow`에 사전 등록해야
  중간 프롬프트로 안 멈춘다(하네스 생성 시 함께 세팅).
- 가용성 게이트: v2.1.154+, 유료 플랜, Pro는 /config 옵트인, `disableWorkflows`로 비활성 가능
  — **생성 하네스는 워크플로우 없이도 동작하는 폴백**(같은 일을 서브에이전트 순차로) 을
  스킬 지침에 함께 서술.
- launch 승인: default/acceptEdits 모드에선 실행마다 프롬프트("don't ask again" 선택 안내를
  하네스 README/CLAUDE.md에 포함).
- 스크립트 자체는 파일시스템/쉘 접근 불가(agent가 함), 동시 16 agent, 총 1,000 agent 상한.
