# harness-creator v5 — 인터페이스의 감산 절반

> v1(`docs/plan/00-*` ~ `06-*`)·v2(`docs/plan/v2/`)·v3(`docs/plan/v3/`)·v4(`docs/plan/v4/`) 계획은 원문 그대로 남는다. 이 세대는 v1 결정 하나를 **명시적으로 폐기**하고 v2 결정 하나를 **확장**한다 — 아래 개정 목록.

## 개정 목록

v2가 D16(인터페이스 교리)을 세우면서 그와 모순되는 v1 결정을 폐기하지 않았고, 그래서 두 세대의 지시가 나란히 살아남았다. 조용한 모순이 이 사태의 뿌리이므로 v5는 같은 실수를 반복하지 않고 무엇이 죽었는지 적는다.

| 대상 | 처분 | 근거 |
|---|---|---|
| **`docs/plan/02-skill-design.md:45`** (v1) — *"**Scripts** — 4개 CLI의 용도와 **호출 시그니처 요약**"* | **폐기** | v2의 D16이 "인터페이스가 유효한 것을 표현한다"를 세운 시점에 시그니처 사본은 잉여가 됐고, v4의 D43이 다섯 CLI의 `--help`를 기계적으로 완비시킨 시점에 잉여를 넘어 위험이 됐다 — `--help`는 검사되고 사본은 안 되므로 사본만 낡는다. 실제로 낡았다: 5행 중 2행이 플래그를 누락하고 1행은 하위 CLI의 플래그를 이 스크립트 것처럼 적는다. `Signature` 열은 삭제하고 `Run it when`(JUDGMENT)만 남긴다 |
| **`SKILL.md:106`**의 경계 문장 (v2, D16) | **확장 — 양방향화** | 원문은 인터페이스 작성자만 제약했다("시그니처에 when/why를 넣지 마라"). 산문 작성자에 대한 제약이 없어서 둘 다 쓰는 것이 규칙 위반이 아니었고, 스킬 자신이 그렇게 하고 있었다. 반대 방향과 반증가능성 판별식을 붙인다 |
| **`docs/plan/03-component-generators.md:21`** (v1) — *"CLAUDE.md에는 트리거 규칙·핵심 사실·harness-spec.md 포인터만"* | **부분 폐기 — 포인터만** | 트리거 규칙·핵심 사실은 유지. `harness-spec.md` 포인터는 삭제한다: 열거 금지의 근거가 *"손으로 유지하는 산문 목록은 표류한다"*인데 spec의 Behavior inventory도 손으로 유지하는 산문 목록이라(전용 드리프트 검사가 붙어 있을 만큼) 포인터는 표류를 없앤 게 아니라 한 홉 옮겼다. 작업 세션은 무엇이 존재하는지 들을 필요가 없다 — 클라이언트가 이미 알린다 |
| **`docs/plan/00-overview.md:23`** (v1 철학 #4) — *"개발 과정에서만 필요한 정보는 싣지 않는다"* | **유지, 강제 장치 신설** | 원칙은 옳고 한 번도 강제된 적이 없다. 패키지가 개발 문서 13건을 가리키고 있었다 |
| D7·D9·D12 (v1 결정 로그) | **유지, 인용 형태만 변경** | 결정 자체는 그대로다. 배포본이 풀 수 없는 ID로 인용하는 것을 그만두고 근거를 인라인한다 |

## Context — 왜 지금 이걸 하나

성진의 문제 제기는 둘이었다.

1. **배치.** 스크립트의 command·parameter 의미를 `SKILL.md`·`references`에 적는 건 사람이 일하는 방식과 동떨어진다. 클로드는 필요한 시점에 `--help`를 읽는 주체이므로, 그 정보는 `--help`에 있어야 한다.
2. **자격.** harness-creator로 만든 하네스에 개발 과정의 시행착오가 섞여 들어간다. 하네스는 *사용하는 데* 필요한 정보만 담아야 한다.

조사 결과 **둘 다 이 레포의 창립 문서에 이미 원칙으로 적혀 있고, 둘 다 강제 장치가 없다.**

- `docs/plan/00-overview.md:23` (v1 철학 #4) — *"스킬은 사용하는 클로드의 관점에서 작성한다. **개발 과정에서만 필요한 정보는 싣지 않는다.**"*
- `docs/plan/02-skill-design.md:45` (v1) — *"**Scripts** — 4개 CLI의 용도와 **호출 시그니처 요약**"*

두 번째는 v2가 인터페이스 교리(D16)를 세울 때 **폐기되지 않았다.** 두 세대의 결정이 모순인 채 공존하고, 그래서 `SKILL.md`의 Signature 열이 살아남아 낡았다.

**핵심 진단 — 교리가 한 방향으로만 적혀 있다.** `SKILL.md:106`의 경계 문장:

> "The boundary: an interface expresses what is *valid*, never when to reach for it or why this project chose it — those stay prose."

이건 **인터페이스 작성자에 대한 제약**이다("시그니처에 when/why를 넣지 마라"). **산문 작성자에 대한 제약이 없다.** 그래서 둘 다 쓰는 것이 규칙 위반이 아니고, 스킬 자신이 그렇게 하고 있다. 사본은 한 번 생기면 아무것도 지우지 않는다 — 교리도, 린터도, 프로세스도.

**그리고 이건 토큰 효율 문제가 아니다.** 실측 결과 이 결함은 이미 **거짓 서술 4건**을 낳았고 그중 하나는 안전 문제이며 둘은 **생성물이 모방하는 정본**에 있다.

## 확정된 현재 상태

### 0. 산문이 이미 거짓이 된 4건 — 최우선

시그니처 사본이 낡는 건 대조하면 드러난다. 진짜 피해는 산문이 인터페이스의 **동작**을 서술할 때 나온다 — *"기본값이다"*, *"강제한다"*, *"차단한다"*. 이건 코드에 대한 주장인데 어떤 검사도 대조하지 않아 **반증 불가능**하다.

| # | 거짓 서술 | 실제 | 결과 |
|---|---|---|---|
| **0-1** | `e2e-testing.md:159` — *"the one `run_e2e.py` implements **as its default**, is an isolated project copy (`--isolate`)"* | `run_e2e.py:184-188` — `run_dir = project_root`, `if args.isolate:` 일 때만 복사. **`store_true` opt-in** | **안전.** 산문을 믿고 플래그를 빼면 헤드리스 에이전트 세션이 사용자의 **실제 프로젝트**에서 돈다. `--isolate`의 `help=`는 정확하다 — 인터페이스는 맞고 산문만 틀렸다 |
| **0-2** | `tests/fixtures/good-harness/CLAUDE.md:15` — *"A PreToolUse hook blocks commits containing raw SQL strings"* | PreToolUse 훅은 `protect-files.sh` 하나, `*.env\|*package-lock.json`만 검사. **raw SQL 훅은 없고 PreToolUse는 커밋을 건드리지 않는다** | **상시 로드 표면**에 있는 거짓이고, **생성물이 모방하는 정본**이다 |
| **0-3** | `agents.md:99` — *"`tools:` already enforces it [read-only]"* | 예시와 픽스처 모두 `tools: Read, Grep, Bash`. 같은 스킬 `hooks.md:78`이 *"Claude can modify a file via `Bash` (`sed -i`, `echo >> file`)"*라고 명시 | 스킬이 **자기 다른 페이지로 자기를 반박**한다. read-only 에이전트가 read-only가 아니다 |
| **0-4** | `SKILL.md:79` — must-never는 hook + `permissions.deny` 결합으로 보장 | 정본 recipe(`hooks.md:202,214`)와 픽스처(`settings.json`)가 `Edit\|Write` matcher + `deny: Edit(.env)`. `hooks.md:78`이 바로 이 조합의 Bash 우회로를 문서화하고 보완책 둘을 제시한다 | **선언한 보장보다 약하다.** (기본 권한 모드에선 임의 Bash가 프롬프트를 띄우므로 "무방비"는 아니다 — 그러나 정본이 자기 gotcha 목록이 불충분하다고 지목한 형태를 시연한다) |

부수: `good-harness/.claude/hooks/check-tests.sh`는 무조건 `exit 0`인 스텁인데 `hooks.md:227`의 recipe는 *"테스트를 돌리고 실패 시 block"*이라고 설명한다. 린트 픽스처로서는 유효하나, v4가 `run.py`를 고친 근거(*"생성물은 정본 픽스처를 모방한다"*)가 그대로 적용된다.

**여기서 판별식이 나온다: 어떤 문장이 도구를 수정했을 때 거짓이 된다면, 그 문장은 도구 안에 있어야 한다.** *"격리가 기본이다"*는 기본값을 바꾸면 거짓이 된다 → `--help`. *"e2e는 사용자 동의 없이 돌리지 않는다"*는 코드 수정으로 거짓이 되지 않는다 → 산문.

### 1. 산문이 인터페이스를 베끼고, 이미 낡았다

`scripts/`의 5개 CLI는 **전부 RICH** — 모든 인자에 `help=`, 모든 파서에 `description=__doc__`. v4의 D43 검사가 이를 강제하고 통과한다. **인터페이스는 오늘 신뢰할 수 있다.** 산문 사본은 순수 잉여다.

`SKILL.md:118-124`의 Scripts 표는 두 열의 성격이 이미 깨끗하게 갈려 있다 — **절단선이 표의 열 경계로 이미 그어져 있다**:

| 열 | 성격 | 판정 |
|---|---|---|
| `Run it when` | 5행 전부 **JUDGMENT** | 교리 자신이 "those stay prose"라고 지목. **남긴다** |
| `Signature` | 5행 전부 **INTERFACE-ONLY** | `--help`가 축자적으로 출력. **삭제한다** |

그리고 그 열은 이미 틀렸다: `run_e2e.py` 행이 `--prompt-file`·`--json`·`--permission-mode` 누락, `test_hook.py` 행이 `--json` 누락, `SKILL.md:128`이 `--dangerously-skip-permissions`를 `run_e2e.py`의 플래그처럼 적지만 그건 하위 `claude` CLI의 것이다(`run_e2e.py:60-61`).

가장 아픈 건 `--permission-mode`다. **바로 그 아래 산문이 "헤드리스 권한 처리는 문서화된 추측"이라고 사과하는데, 권한 모드를 직접 지정하는 플래그가 존재하고 표가 그걸 가린다.**

**교리가 생성기에게 반대로 전달된다.** `references/skills.md:93`의 정본 예시: *"SKILL.md stays short: trigger conditions, the one gotcha that matters here, which template to open, **and the script's signature**."* 같은 파일 `:42`가 "모든 인자에 `help=`를 붙여라"고 51줄 위에서 가르친 뒤다. **반면 픽스처는 이미 옳다** — `good-harness/.claude/skills/example-skill/SKILL.md:10`은 *"`scripts/run.py` for the CLI"*라고 가리키기만 한다. 고칠 대상은 코드가 아니라 산문이다.

**이미 성공한 선례가 있다.** `docs/plan/v3/02-compression.md:337` — *"`hook_event.py` 하나가 훅 패스에서 이벤트 스키마 조회를 3,777 → ~430단어로 만든다. **인터페이스 하나가 전체 압축의 5배다.**"* 실제로 `hooks-events.md`(3,777단어)는 정상 경로에서 **파일로 읽히지 않는다** — `SKILL.md`이 한 번도 직접 호명하지 않고 `hooks.md:156`의 라우터가 `hook_event.py --event <Event>`로 보낸다. 성진이 원하는 패턴은 이미 출하되어 작동 중이다. 일반화하지 않았을 뿐이다.

### 2. 문서 그래프가 패키지 밖으로 샌다 — 전수 13건

지켜야 할 규칙은 "디렉터리 밖 경로를 쓰지 마라"가 **아니다.** 바깥 경로에는 두 종류가 있고 하나는 정당하다:

- **대상 프로젝트의 경로**(`.claude/settings.json`, `package.json`) — 스킬이 *만들고 검사할 대상*이다. 바깥에 있는 게 맞다.
- **읽으라고 가리키는 문서** — 배포본에 없으면 항상 끊긴다. **이쪽만 결함이다.**

규칙: **읽으라고 가리키는 것은 전부 `.claude/skills/harness-creator/` 안에서 닫힌다.**

| 종류 | 건수 | 위치 |
|---|---:|---|
| 결정 로그 ID | 5 | `SKILL.md:82`(D12), `e2e-testing.md:15`(D12), `interview.md:60`(D12)·`:61`(D7), `harness_common.py:418`(D9) |
| `docs/plan/` 인용 | 4 | `harness_common.py:10,22`, `validate_harness.py:11,528` |
| **`.tmp/` 인용** | 2 | `harness_common.py:21,40` |
| 맨 파일명 포인터 | 1 | `interview.md:64` → `03-component-generators.md` |
| 없는 절 제목 | 1 | `skills.md:60` → 실제 제목은 `hooks.md:37` |

`.tmp/` 두 건이 최악이다 — **gitignore된 경로라 레포를 clone한 사람에게도 없다.** `validate_harness.py:11`은 모듈 docstring이라 **`--help` 출력에 실려 최종 사용자에게 배포된다.** Hard line 1(*"실재하지 않는 컴포넌트를 광고하지 마라"*)을 건 패키지에서 13건이다.

`_SKILL_POINTER_RE`(`validate_harness.py:63-66`)가 `references/`·`scripts/` 접두사를 요구해 **맨 파일명과 ID는 구조적으로 안 보인다.** `SKILL.md:132`가 그 검사를 *"in whatever form they're written"*라고 과대 주장하는 것도 틀렸다.

**검사 설계는 실측으로 확정됐다.** `\bD[0-9]{1,2}\b`가 정확히 위 5건을 잡고 **오탐 0건**이다. 내부 식별자 계열(`I1-I5` — `interview.md:9` 정의, `V1-V4` — `e2e-testing.md:49` 정의, `B1` — `interview.md:122` 정의)은 전부 패키지 안에서 정의되므로 걸리지 않는다. 판정에 해석이 개입하지 않는 이진 사실이라 v4가 D43을 정당화한 기준을 그대로 만족한다.

### 3. CLAUDE.md → harness-spec.md 포인터가 독자를 잘못 잡는다

`claude-md-and-rules.md:21`이 한 문단 안에서 자기 근거로 자기 처방을 반박한다:

> (a) "…and **a single pointer to `.claude/harness-spec.md`** for anyone who wants the full picture of what the harness contains **and why**."
> (b) "If a future reader needs to know exactly which skills exist, **they list the `.claude/skills/` directory** — that is always correct, **unlike prose**."

열거 금지의 근거는 *"손으로 유지하는 산문 목록은 표류한다"*인데, `harness-spec.md`의 Behavior inventory도 손으로 유지하는 산문 목록이다 — 표류가 확실해서 `audit_harness.py`에 전용 드리프트 검사가 붙어 있다. 포인터는 표류를 없앤 게 아니라 한 홉 옮겼다. 그리고 배달 광고의 `and why`가 곧 Design rationale, 즉 제작 기록이다.

애초에 **작업 세션은 무엇이 존재하는지 들을 필요가 없다.** 스킬은 `description`으로 리스팅에 뜨고, 에이전트는 클라이언트가 목록으로 주고, 훅은 스스로 발화하고, 룰은 경로가 맞으면 로드된다. 클라이언트가 이미 하는 일을 산문이 중복한다.

포인터는 **세 곳**에 박혀 있다: 산문(`claude-md-and-rules.md:21`), 정본 예시(`:91-92`), **린터 실패 메시지**(`validate_harness.py:766-769`가 *"point to harness-spec.md instead of enumerating"*라고 적극 권한다). 하나만 고치면 나머지 둘이 되돌린다.

### 4. spec에 예산도 퇴거 정책도 없다

생성물 쪽 설계는 **대체로 옳다.** 제작 기록은 `.claude/harness-spec.md`로 격리되고, 그 파일은 상시 로드가 아니며(`always_loaded_report()`가 구조적으로 포함할 수 없다), CLAUDE.md 포인터도 `@import`가 아닌 백틱 형태다. 생성 CLAUDE.md·스킬·훅에 rationale을 쓰라는 지시는 한 건도 없고 기계적 가드가 넷 걸려 있다. **codex 독립 감사도 같은 결론이다** — "그 서사가 일반 작업 세션에 자동 주입된다"는 의미에서는 refuted.

문제는 목적지다.

| | 픽스처(1회 생성) | 이 레포 실물(improve 1회) |
|---|---:|---:|
| `harness-spec.md` 전체 | 122단어 | **1,624단어** |
| `## Design rationale` | 1문장 | **710단어 (44%)** |

`Change history`는 패스마다 추가되는데 오래된 항목 정리 지시가 없다. 그 710단어는 교리가 "잘라내라"고 지목한 바로 그 형태(주장을 변호하는 문장)로 채워져 있다. **harness-creator는 자기 압축 교리를 생성물 전부에 적용하면서, 매 패스마다 자기가 쓰는 단 하나의 파일에는 적용하지 않는다.** 그리고 이 레포 자신의 Change history는 2026-08-03(v2) 한 건뿐 — v3·v4 항목이 없어 **Hard line 3 위반 상태**다.

### 5. 감산은 있지만 반쪽이다

`e2e-testing.md:143,149`에 제대로 된 은퇴 교리가 있다 — *"Raise retirement as a question, never as an action… Offer `disable-model-invocation: true` before deletion."* 비어 있는 건 둘:

- **훑는 절차가 없다.** 트리거가 *"A component seems to earn nothing"* — 이미 의심해야 발동하고, 그 표는 검증 경로에서만 로드된다. `improve` 모드의 피드백 라우팅 표(`e2e-testing.md:134-143`)는 모든 화살표가 *수정 아니면 상향*이다("규칙이 무시됨 → CLAUDE.md 강화 → 훅으로 승격"). 기계를 늘리는 방향만 있다.
- **대상이 컴포넌트뿐이다.** Anthropic이 권하는 감산은 *지시문의 노후화*다 — Boris Cherny: *"every six months delete your CLAUDE.md. Delete your skills. Delete your hooks. See what the model does… for Opus 5 this is something we really do recommend."* 방법론 이름은 **ablation**. 스킬 어디에도 없다.

## 목표 (한 문장)

**교리의 감산 절반을 명문화하고, 그것이 없어서 이미 발생한 거짓 서술·끊긴 포인터·무한 증식을 세 표면(스킬 자신 / 생성 가이드 / 검사기)에서 동시에 제거한다.**

## 핵심 결정

### 결정 1 — 재작성하지 않는다 (성진의 허가에 반대)

성진은 재작성급 수정을 허가했다. **권하지 않는다.** 교리 자체는 이미 Anthropic 공식 가이드보다 날카롭게 서술돼 있고(`v2/research/audit-synthesis.md:32`가 3개 항목에서 그렇게 판정), v2의 53에이전트 감사와 v3의 실측 압축은 재현 불가능한 자산이다. 결함은 **특정 문장·특정 열·특정 검사**에 국지적이다. 재작성은 측정된 것을 추정으로 되돌린다.

바꾸는 것은 **교리 한 절, 표 한 열, 정본 예시 몇 문장, 거짓 서술 4건, 검사 메시지 하나, 새 검사 두 개**다. diff는 작고 사고 밀도는 높다 — v3가 세운 형식 그대로.

### 결정 2 — 교리를 양방향으로 만들고, 반증 가능성을 판별식으로 삼는다

`SKILL.md:106`의 경계 문장에 반대 방향을 붙인다. 초안:

> The boundary runs both ways: an interface expresses what is *valid*, never when to reach for it or why this project chose it; and prose names the tool and says when to reach for it, never restating what the tool prints or asserting how it currently behaves. If editing the tool would make the sentence false, the sentence belongs in the tool.

마지막 문장이 이 규칙을 **운영 가능**하게 만든다. 비용 논증("토큰을 아낀다")이 아니라 **오염 논증**으로 세운다 — 5행 중 2행이 이미 틀렸고 동작 서술 4건이 이미 거짓이므로 이건 관측된 사실이지 예측이 아니다.

포인터 계 한 줄:

> A pointer inherits its target's reader. Pointing a working surface at a maintenance document does not defer the cost, it gambles it.

### 결정 3 — 분량은 추정하지 말고 잰다 (v3의 교훈)

`tests/test_skill_surface.py:183`의 `WORD_BUDGET = 2650`, 현재 `SKILL.md` **2,632단어 — 여유 18단어.** v3는 정확히 여기서 넘어졌다(추정 47 → 실측 80 → 필요 257 → D34 폐기). 이번엔 **회수원이 결함 수정과 같은 곳이라** 자금이 스스로 조달된다: Signature 열 5셀, `SKILL.md:26,50,62`의 `--path .` 3회 반복, `:128`의 틀린 플래그 서술, `:132`의 과대 주장.

**절차: 교리를 온전한 문안으로 넣고 회수한 뒤 `wc -w`로 잰다.** 2,650 미만이면 진행. 넘으면 **멈추고 숫자를 들고 성진에게 묻는다** — 문안을 조일지, 예산을 올리고 사유를 남길지. 교리를 짧게 쓰려다 의미를 잃는 것이 상시 로드 50단어보다 나쁘다.

## 작업 단위와 완료 판정

완료 판정은 전부 **기계적으로 확인 가능한 것**으로 적는다.

### PR0 — 계획을 레포의 정본 위치로 옮긴다

이 레포의 `CLAUDE.md:8`이 정한다: `docs/plan/`이 구속력 있는 스펙이고, 세대마다 디렉터리 하나, 최신이 마지막. **이 문서를 `docs/plan/v5/00-overview.md`로 옮기고, 어떤 기존 결정을 개정하는지 명시한다.** v1의 `02-skill-design.md:45`(시그니처를 SKILL.md에 적으라)를 **명시적으로 폐기**하는 것이 v5의 핵심 개정이다 — v2의 D16이 조용히 모순만 만들고 폐기하지 않은 것이 이 사태의 뿌리이므로, 같은 실수를 반복하지 않는다. v1~v4 계획은 원문 그대로 둔다.

**완료 판정**: `docs/plan/v5/00-overview.md`가 존재하고, §개정 목록에 `02-skill-design.md:45`가 있다.

### PR1 — 거짓이 된 산문 4건 (최우선, 안전 포함)

| 변경 | 파일 |
|---|---|
| *"implements as its default"* → 사실대로. 격리는 opt-in이고 **e2e를 제안할 때 `--isolate`를 붙이는 것이 결정**이라고 산문에 남긴다 | `e2e-testing.md:159` |
| 존재하지 않는 raw-SQL 훅 서술 제거 또는 실제 훅과 일치시킴 | `tests/fixtures/good-harness/CLAUDE.md:14-15` |
| *"`tools:` already enforces it"* → `Bash`가 있으면 강제되지 않는다는 사실 반영. 예시에서 `Bash`를 빼거나, 왜 넣었는지와 그 결과를 명시 | `agents.md:99`, `agents.md:84`, 픽스처 `security-reviewer.md:4` |
| must-never 정본 recipe에 `hooks.md:78`의 보완책을 적용(Bash 포함 matcher 또는 Stop-time `git status`) | `hooks.md:202,214`, 픽스처 `settings.json` |
| `check-tests.sh` 스텁이 recipe 설명과 일치하도록 하거나, 스텁임을 명시 | 픽스처 `check-tests.sh` |

**완료 판정**
1. `e2e-testing.md`에 `default` 표현이 `--isolate`와 함께 등장하지 않는다. 새 문안이 `run_e2e.py --help`와 모순되지 않음을 수동 대조로 확인하고 그 대조를 테스트로 앵커한다.
2. 픽스처 CLAUDE.md의 모든 훅 서술이 `settings.json` + 실제 스크립트와 일치한다 — **이 대조를 테스트로 만든다**(픽스처 CLAUDE.md가 언급한 훅이 실재하는가).
3. `agents.md`의 read-only 주장과 예시 `tools:`가 모순되지 않는다.
4. `python3 -m unittest discover -s tests -q` 전부 통과.

### PR2 — 교리 양방향화 + 자기 적용

| 변경 | 파일 |
|---|---|
| 경계 문장 양방향화 + 반증가능성 판별식 + 포인터-독자 한 줄 | `SKILL.md:106` |
| Scripts 표에서 `Signature` 열 삭제, `Run it when` 유지, 호출 규약 1줄 + "첫 사용 전 `--help`" | `SKILL.md:118-124` |
| 틀린 `--dangerously-skip-permissions` 서술 교정 | `SKILL.md:128` |
| 포인터 검사 과대 주장 교정 | `SKILL.md:132` |
| 정본 예시의 *"and the script's signature"* → 포인터 형태(픽스처가 이미 보이는 형태) | `references/skills.md:93` |

**완료 판정**
1. Scripts 표에 `Signature` 열이 없다.
2. `wc -w SKILL.md` < 2,650 (`tests/test_skill_surface.py` 통과). 넘으면 성진과 합의한 조치와 사유가 기록됐다.
3. `grep -c "script's signature" references/skills.md` == 0.
4. 새 교리 문안을 앵커하는 `ConsequenceClauseTests` 항목이 있다.

### PR3 — 문서 그래프를 패키지 안에서 닫는다 (13건)

원칙: **ID를 지우는 게 아니라 ID가 대신하던 근거를 인라인한다.** `D12`가 나쁜 건 짧아서가 아니라 독자가 풀 수 없어서다.

| 변경 | 파일 |
|---|---|
| `D12`→내용 인라인 (3곳), `D7`→인라인, `D9`→인라인 | `SKILL.md:82`, `e2e-testing.md:15`, `interview.md:60,61`, `harness_common.py:418` |
| `docs/plan/` 인용 4건 제거. `validate_harness.py:11`은 **`--help`에 실려 배포되므로 최우선** | `harness_common.py:10,22`, `validate_harness.py:11,528` |
| `.tmp/` 인용 2건 → 로컬 스냅샷 대신 **공개 문서 URL**(출처로서도 이쪽이 낫다) | `harness_common.py:21,40` |
| `03-component-generators.md` 포인터 제거 | `interview.md:64` |
| 없는 절 제목 교정, `references/` 접두사 통일 | `skills.md:60`, `interview.md:60` |
| **새 검사 A**: 스킬 표면의 `\bD[0-9]{1,2}\b` · `docs/plan/` · `\.tmp/` → E | `validate_harness.py` |
| **새 검사 B**: `_SKILL_POINTER_RE`를 맨 파일명까지 확장 | `validate_harness.py:63-66` |

**완료 판정**
1. `grep -rnE '\bD[0-9]{1,2}\b|docs/plan/|\.tmp/' .claude/skills/harness-creator/ --include='*.md' --include='*.py'` == **0건**.
2. 검사 A가 위반 픽스처에서 E를 내고 `good-harness`·`cli-edge-cases`·현행 스킬에서 findings 0 (오탐 0 실측 완료).
3. 검사 B가 `interview.md:64` 형태를 잡는다 — 그 줄을 되돌리면 red가 되는 회귀 핀이 있다.
4. `validate_harness.py --path . --strict` exit 0.

> **구현 시 개정 (2026-08-22).** 위 문안은 검사 A를 `\bD[0-9]{1,2}\b` · `docs/plan/` · `\.tmp/` 패턴 셋으로, 검사 B를 "맨 파일명까지 확장"으로 적었다. **둘 다 그대로는 정상 하네스에서 울린다** — 이 문서가 §범위 밖에서 인용한 WS2-6 원칙("정상 하네스에서 울리는 체크는 없느니만 못하다")과 정면으로 충돌한다. `docs/plan/`은 이 레포의 경로일 뿐이고 사용자 스킬이 자기 레포의 `docs/plan/`을 가리키는 것은 정상이며, 맨 파일명은 현행 코퍼스에만 `run.py`·`template-crash.md`·`guard.sh` 등 **가상 하네스의 예시 파일명이 수십 개** 있어 전부 오탐이 된다. 목표(패키지 밖 포인터를 기계적으로 막는다)는 유지하고 수단을 바꿨다.
>
> - **검사 A → 플러그인 패키지 폐쇄.** `.claude-plugin/plugin.json`이 실제로 그 스킬을 배포할 때에만 발동하고, 스킬 디렉터리 밖의 문서 경로가 **이 레포에서 resolve되면** E — 여기서 풀리고 설치본에서 안 풀린다는 것이 곧 결함의 정의다. 프로젝트 스킬은 자기가 가리키는 레포 안에 살므로 침묵한다. **하드코딩된 패턴 없이 6건을 전부 잡고 오탐 0.**
>
>   `.gitignore`된 최상위 이름을 두 번째 조건으로 넣는 안을 만들었다가 **적대 검증에서 되돌렸다.** gitignore된 경로는 출하될 수 없으니 엄격한 개선처럼 보였는데, 실제로는 정상 하네스 셋을 잡았다 — `node_modules/some-pkg/README.md`, `dist/index.md`, `docs/notes.md`. 플러그인 레포의 `.gitignore`는 *자기* 빌드 산출물을 적고 스킬의 문장은 *독자의* 레포를 가리키기 때문이다. 대신 `.tmp/` 계열은 `tests/test_skill_surface.py`의 레포 전용 핀이 CI에서 잡는다.
> - **검사 B → 중첩 경로 + 문장 끝 마침표.** codex 적대 감사가 `_SKILL_POINTER_RE`의 실제 구멍 둘을 확인했다: `references/platform/missing.md`가 첫 세그먼트만 검사돼 통과하고, 문장 끝의 `scripts/tool.py.`가 존재하지 않는 파일로 신고된다(정상 하네스 오탐). 둘 다 일반적이고 오탐이 없다.
> - **남은 7건(D-ID 5, 맨 파일명 1, 없는 절 제목 1)은 `tests/test_skill_surface.py`의 회귀 핀으로 간다.** 이 파일이 이미 그 용도다 — `NoExternalToolNamesTests`가 `doctor|checkup` 리터럴을, `DanglingPointerTests`가 `see Hard lines` 리터럴을 막는다. 이 패키지에 대한 사실이지 사용자에게 출하할 규칙이 아니다. 계획이 검사 B의 수용 기준을 이미 "회귀 핀"이라고 적은 것과 일치한다.
>
> **추가로 닫은 2건** (codex 자기적용 감사, 같은 PR): `workflows.md:21`이 존재하지 않는 `/deep-research` 워크플로를 *"the bundled"*라고 광고했다(**Hard line 1 위반**). `hooks-events.md:3`이 *"Load this file"*이라고 자기 지시하는데 `hooks.md:156`의 라우터는 `hook_event.py --event`로 보낸다 — 그 지시를 따르면 이벤트 하나를 묻는 데 3,800단어를 낸다.

### PR4 — 포인터 독자 교정

| 변경 | 파일 |
|---|---|
| 포인터 정책에서 `harness-spec.md` 포인터 삭제, "클라이언트가 이미 컴포넌트를 알린다"로 근거 교체. 사람용이 필요하면 HTML 주석(`:69`가 이미 가르치는 무비용 메커니즘) | `claude-md-and-rules.md:21` |
| 정본 예시에서 포인터 줄 제거 | `claude-md-and-rules.md:91-92` |
| 린터 메시지에서 *"point to harness-spec.md instead"* 제거 | `validate_harness.py:766-769` |
| 픽스처 CLAUDE.md에서 포인터 줄 제거 | `good-harness/CLAUDE.md:3` |

**완료 판정**
1. `grep -rn "harness-spec.md" references/claude-md-and-rules.md` == 0건.
2. `tests/test_validate_harness.py`의 메시지 앵커 assertion이 새 문구로 갱신되고 통과.
3. 세 표면 중 하나만 고친 상태로는 테스트가 실패한다(회귀 핀).

### PR5 — spec에 예산과 퇴거를 준다

| 변경 | 파일 |
|---|---|
| `Change history` 보존 규칙: 최근 N개 유지, 이전은 한 줄 요약으로 접는다 | `interview.md:133-134` 템플릿 |
| `Design rationale`에 압축 교리 적용 — 결정과 기각안은 남기고 변호 문장은 자른다 | `interview.md:127-128` 템플릿 |
| skill `description`을 Component specs에 복제하지 않는다(이미 픽스처에서 drift — codex 발견) | `interview.md:125` |
| 이 레포 자신의 spec에 적용 + 누락된 v3·v4 Change history 보충 | `.claude/harness-spec.md` |

**완료 판정**
1. `## Design rationale`이 710단어 → 목표치 이하이며 **claim 손실 0**(D39 기준: 분량이 아니라 주장 수로 판정).
2. Change history에 v3·v4 항목이 있다(현재 v2 한 건 — Hard line 3 위반 해소).
3. `audit_harness.py --path .` 드리프트 0건.

### PR6 — 감산 스윕

| 변경 | 파일 |
|---|---|
| `improve` 모드에 감산 질문 추가 — "무엇을 더할까"와 대칭으로 "무엇이 이제 불필요한가" | `re-entry.md:11-15` |
| 지시문 노후화 교리 + ablation 절차(지우고 → 써보고 → 필요하면 되살린다) | `SKILL.md` 또는 `re-entry.md` |
| 피드백 라우팅 표에 하향 화살표 추가 | `e2e-testing.md:134-143` |

**완료 판정**
1. `improve` 진입 시 감산 질문이 대칭으로 제시된다(L5 도그푸딩으로 확인).
2. 라우팅 표에 "제거"로 끝나는 행이 최소 1개.

### PR7 — 릴리스 `v0.4.0`

**이 릴리스는 v5만 싣는 게 아니다.** `v0.3.0`(2026-08-04) 이후 미출하 커밋이 8개이고, 그중 **v4의 D43은 CHANGELOG 항목이 아예 없다.** 즉 이번 릴리스가 세 덩어리를 함께 내보낸다:

| 덩어리 | 상태 |
|---|---|
| **v4 — D43 번들 스크립트 CLI 자기서술성 검사** (`458f603`) | 머지됨, **CHANGELOG 누락** — 새로 써야 한다 |
| **discoverability 트랙** (README·wiki·CI·Issue Forms·플러그인 디렉터리 제출 등 6커밋) | `[Unreleased]`에 이미 기록됨 |
| **v5 — PR1~PR6** | 이번 작업 |

**절차** (레포에 릴리스 문서가 없으므로 기존 3회의 관례를 따른다):

1. `CHANGELOG.md`의 `[Unreleased]`를 `## [0.4.0] — <날짜>`로 확정하고, **D43 항목과 v5 항목을 추가**한다. 기존 세 릴리스가 전부 **논지 리드 문단 → Added/Changed/Fixed** 형식이므로 그대로 따른다.
2. `.claude-plugin/plugin.json:3`과 `.claude-plugin/marketplace.json:12`의 `version`을 **함께** `0.4.0`으로 올린다(두 곳이 어긋난 적 있으므로 한 커밋에서 같이).
3. `validate_harness.py --path . --strict` exit 0, 전체 테스트 통과를 확인한 뒤 `main`에서 태그 `v0.4.0`.
4. `gh release create v0.4.0` — 제목은 관례대로 **`v0.4.0 — <테마>`**. `v0.1.0 — harness-creator`, `v0.3.0 — Doctrine`의 계보. **제안: `Interface`** — D43이 인터페이스를 신뢰 가능하게 만들었고 v5가 산문이 그걸 베끼거나 오서술하지 못하게 닫는다. 성진이 다른 이름을 원하면 그대로 따른다.

**완료 판정**
1. `grep -c '"version": "0.4.0"' .claude-plugin/plugin.json .claude-plugin/marketplace.json` — 두 파일 모두 1.
2. `CHANGELOG.md`에 `[0.4.0]` 절이 있고 그 안에 D43 항목이 있다(현재 어느 절에도 없다).
3. **PR2 행동 검증 3회가 PASS**했고 그 결과가 spec의 Validation에 기록됐다(아래 검증 절 — 릴리스 게이트).
4. `[0.4.0]`의 known limitations에 **L5 풀 도그푸딩 미실행**이 명시됐다.
5. `git tag -l v0.4.0`과 `gh release list`에 항목이 뜬다. `[Unreleased]`가 비어 있다.

## 순서와 의존 — 같은 파일을 두 PR이 건드리지 않게

v3가 남긴 규칙: *"두 PR이 같은 파일을 건드리면 리뷰가 불가능해진다"*(`v3/01-doctrine.md:84`). 위 배치에 겹침이 셋 있어 다음과 같이 해소한다.

| 겹침 | 해소 |
|---|---|
| `SKILL.md` — PR2(교리·표)와 PR3(`:82`의 D12) | **`:82`의 D12 인라인을 PR2로 옮긴다.** SKILL.md는 PR2에서 한 번만 손댄다. 마침 D12를 풀어 쓰면 단어가 늘므로 PR2의 예산 실측에 함께 잡혀야 정확하다 |
| `good-harness/CLAUDE.md` — PR1(거짓 훅 서술)과 PR4(spec 포인터 줄) | **PR4의 픽스처 편집을 PR1로 옮긴다.** 픽스처 CLAUDE.md는 PR1에서 최종 형태로 만든다 |
| `e2e-testing.md` — PR1(`:159` 격리 기본값)과 PR3(`:15`의 D12) | 두 편집이 서로 멀고 독립적이다. **PR1 → PR3 순서로만 지키면 충분**하고, PR3에서 rebase 충돌이 나면 PR1이 아직 안 들어간 것이다 |

그 밖의 순서 제약:

- **PR3의 수정과 새 검사는 반드시 같은 PR에 들어간다.** 검사만 먼저 넣으면 현행 스킬에서 즉시 E 13건이 뜨고 `--strict` 게이트가 깨진다.
- **PR2는 PR1 뒤에 온다.** PR1이 `SKILL.md:128`의 인접 서술 근거를 바꾸고, PR2가 그 줄을 지운다.
- **PR5는 PR4 뒤에 온다.** 포인터 정책이 바뀌면 spec이 무엇을 담아야 하는지가 함께 바뀐다.
- **PR6은 마지막.** 감산 교리가 PR2의 교리 문안 위에 서고, SKILL.md에 들어갈 경우 예산 실측을 다시 해야 한다.

## 구현 시 쓸 도구

**`tdd` — PR1·PR3에서 연다. 나머지는 해당 없다.**

이 레포는 이미 TDD가 집 스타일이고(v4 계획 §5가 *"red를 만들 수 없어서 구현 전에 뺐다"*며 기능 2건을 삭제한 기록), 값은 **seam 합의 단계**에 있다. **v4의 선례를 따른다: seam은 `vh.run(root, strict) → (findings, exit_code)` 하나뿐이고 내부 `_check_*`를 테스트가 직접 부르지 않는다** — 슬라이스마다 내부 모양이 바뀌므로 시그니처에 테스트를 못 박으면 이후 슬라이스가 거기 갇힌다.

| PR | red를 어떻게 만드나 |
|---|---|
| PR1 | 픽스처 CLAUDE.md의 훅 서술 ↔ 실제 `settings.json`+스크립트 대조 테스트를 **먼저** 쓴다. 현재 상태에서 즉시 red(raw-SQL 훅이 없다). 그 다음 고친다 |
| PR3 | 새 검사 A를 먼저 쓰면 **현행 스킬에서 즉시 E 13건** — 자연스러운 red. 13건을 고치면 green. 검사 B는 `interview.md:64`가 red 소스 |
| PR2 | `ConsequenceClauseTests` 앵커 1건과 `WORD_BUDGET` 게이트만 해당. 산문 편집이므로 TDD는 얕게 |
| PR4 | 린터 메시지 앵커 assertion 갱신. 기존 `_assert_warning_contains` idiom 그대로 |
| PR5·PR6·PR7 | 코드가 아니다. 해당 없음 |

**테스트와 픽스처는 전부 레포 루트의 `./tests`에 둔다.** 기존 형태 그대로다 — `tests/test_*.py` 6개, 픽스처는 `tests/fixtures/`. 러너는 `python3 -m unittest discover -s tests -q`이며 `python3 tests/*.py`는 동작하지 않는다(v3 C9).

**스킬 디렉터리 안에는 절대 두지 않는다.** 레포 `CLAUDE.md`가 이유를 명시한다 — *"anything under the skill directory ships to plugin users, so dev-only fixtures stay outside it."* 픽스처를 `.claude/skills/harness-creator/` 안에 만들면 그대로 배포되고, 그건 PR3이 닫으려는 바로 그 문제(패키지가 개발용 자산을 싣는 것)를 새로 만드는 것이다.

**새 픽스처는 `good-harness`에 섞지 않는다.** v4가 세운 선례다: false-positive 가드는 `tests/fixtures/cli-edge-cases/`에 따로 뒀다 — `good-harness`는 *생성물이 모방하는 교육용 정본*이라, 거기에 고문 케이스를 섞으면 가르치는 바가 흐려진다. PR3의 위반 픽스처와 오탐 가드도 같은 규칙을 따른다.

**PR1의 대조는 lint 검사가 아니라 테스트로 만든다.** "CLAUDE.md가 존재하지 않는 훅을 서술한다"를 일반 검사로 만들려면 산문 주장과 `settings.json`을 의미 수준에서 맞춰야 하는데, 그건 어휘 신호로 갈리지 않아 WS2-6이 기각한 부류다. 픽스처 한 벌에 대한 일관성 테스트로 좁히면 이진 사실이 된다.

**`codex`(gpt-5.6-sol, xhigh) — 구현이 아니라 독립 검증에만 쓴다.**

이번 계획 단계에서 codex는 내 에이전트 3개와 내가 놓친 4건을 찾았고 그중 하나가 안전 문제였다. 값이 나온 이유는 *실행자*가 아니라 **프레임이 다른 독립 감사자**여서다. 동시에 오차도 있었다 — Bash 우회를 "무방비"로 과장했고 직접 확인해 "선언한 보장보다 약하다"로 교정했다. **찾게 하고, 판정은 이쪽에서 한다.**

| 시점 | 시킬 것 | 왜 |
|---|---|---|
| PR1 직후 | *"이 패키지의 산문 중 코드가 반박하는 동작 주장을 전부 찾아라"* — 내 진단을 주지 않고 백지에서 | 이 질문이 원래 4건을 찾아냈다. 같은 질문의 재실행이 곧 회귀 검사다 |
| PR3 검사 설계 중 | **적대적**: *"검사 A·B가 오탐을 낼 정상 하네스를 만들어 보라"* | WS2-6의 위험(*"정상 하네스에서 울리는 체크는 없느니만 못하다"*)을 실제로 두들겨 본다. 지금은 오탐 0을 현행 코퍼스에서만 확인했다 |
| PR2 문안 확정 전 | *"이 경계 문장만 읽고, 스크립트 시그니처 표를 SKILL.md에 쓰는 게 허용되나?"* | 교리가 **재도출 가능**한지의 직접 시험. 통과하면 문안이 산 것이고, 통과 못 하면 문안이 약한 것이다 |
| — | **편집 자체는 시키지 않는다** | diff가 작고 이 대화의 맥락 의존도가 높다. 브리핑 비용이 절약분보다 크다 |

`--sandbox read-only`로 돌린다. 감사에 쓰기 권한이 필요 없고, `config.toml`이 `danger-full-access`라 명시하지 않으면 상속된다.

## 검증

**기계적 (매 PR)**
```bash
python3 -m unittest discover -s tests -q            # 현재 176 tests
python3 .claude/skills/harness-creator/scripts/validate_harness.py --path . --strict   # exit 0
python3 .claude/skills/harness-creator/scripts/audit_harness.py --path .              # 드리프트 0
wc -w .claude/skills/harness-creator/SKILL.md       # < 2,650
grep -rnE '\bD[0-9]{1,2}\b|docs/plan/|\.tmp/' .claude/skills/harness-creator/   # 0건
```

**행동적 — PR7(릴리스)의 게이트. 결정됨 (성진, 2026-08-22): PR2 행동 검증만.**

`validate_harness.py`는 산문이 인터페이스를 베꼈는지 판정할 수 없다. PR2의 실제 성공 여부는 **생성 행동**으로만 확인된다:

- `run_e2e.py --isolate`로 헤드리스 세션 **3회**, "번들 스크립트가 있는 스킬을 만들어 달라" 프롬프트.
- **PASS**: 생성된 `SKILL.md`가 스크립트를 *호명*하되 플래그를 *열거하지 않는다*. 그리고 생성된 스크립트가 D43 검사를 통과한다(= `--help`가 그 정보를 실제로 담는다).
- **FAIL 신호**: 생성물이 여전히 시그니처를 적으면 문안을 조이지 말고 **정본 예시를 의심한다** — v4가 "생성물은 정본 픽스처를 모방한다"를 최고 파급으로 꼽았다.

**이 실행은 부수적으로 4세대째 열려 있는 항목을 닫는다.** `run_e2e.py`의 헤드리스 권한 처리는 v1의 위험 R3 이래 한 번도 실제 성공이 관측된 적이 없고 `SKILL.md:128`이 지금도 그렇게 고지한다. `e2e-testing.md:157`의 지시대로 **그 실행의 결과 자체가 확인**이며, 결과를 spec의 Validation에 적는다. PR1이 같은 파일의 격리-기본값 오서술을 고치므로 순서상 자연스럽다.

**남기는 부채를 명시한다.** v3의 L5 풀 인터뷰 도그푸딩(`v3/03-verification.md:271` — *"미실행 상태로 v0.3.0을 릴리즈했다… v3의 핵심 주장이 검증되지 않은 채로 나갔다"*)은 **이번에도 실행하지 않는다.** 다른 세대의 부채 때문에 v5 릴리스를 잡아두지 않는다는 판단이고, `[0.4.0]`의 known limitations에 그대로 적는다 — 조용히 넘어가지 않는다.

## 범위 밖

- **하네스 밖의 인터페이스.** D16이 하네스 내부로 한정했고 소유자가 완화안을 재확인 후 기각했다.
- **`--help` 문구 품질 채점.** v4의 기각 근거가 그대로 유효 — 어휘 신호로 좋고 나쁨을 못 가르고, 만들면 생성기가 린터를 만족시키려 글을 쓴다.
- **비-Python 스크립트.** 정상 하네스에서 울리는 체크는 없느니만 못하다(WS2-6).
- **`hooks-events.md` 삭제.** 정상 경로에서 파일로 읽히지 않아 상시 비용이 0이고, 지우면 `hook_event.py`의 데이터 소스가 사라진다(`hook_event.py:125-127`이 이 파일을 파싱해 `choices=`를 만든다).

## 위험·가정·열린 항목

1. **PR6(감산) 포함 — 결정됨 (성진, 2026-08-22).** 근거: 진단 자체가 "아무것도 제거하지 않는다"이므로 인스턴스만 고치면 v6에서 같은 계열이 다시 쌓인다. 다만 여섯 중 근거가 가장 약한 항목이라는 점은 기록해 둔다 — Anthropic의 권고는 있으나 이 레포에서의 피해 측정치는 없다. PR6이 예산이나 일정을 압박하면 **가장 먼저 잘라낼 후보**다.
2. **workflow `args` — v6으로 미룸 (성진, 2026-08-22).** v4가 *"스크립트 CLI와 같은 종류의 구멍, 아직 열려 있음"*으로 남겼다(`v4/00-overview.md:74`). **codex가 프레임을 교정했다**: 정본 예시와 픽스처에 `args` 객체가 아예 없으므로 "산문이 인터페이스를 베꼈다"가 아니라 **"비교할 인터페이스가 아직 없다"**가 정확하다. *중복 제거*가 아니라 *인터페이스 신설*이라 수용 기준이 다르고, 같은 PR 묶음에 넣으면 리뷰 기준이 섞인다.
3. **CHANGELOG·plugin 버전이 D43에 뒤처져 있다** — `plugin.json`·`marketplace.json`이 아직 `0.3.0`. 릴리스 위생 커밋으로 분리.
4. **인터페이스 교리의 근거가 연구된 적 없다** — `SKILL.md:106`의 중심 주장(*"an interface is re-read from the tool's own signature on every use"*)은 컴팩션·권한·스킬 로딩과 달리 **문서화된 제품 사실로 확인된 적이 없다**(`docs/plan/research/`·`v2/research/` 모두 0건). 이번 계획이 이 주장 위에 서므로 정직하게 기록한다. 다만 PR1·PR3의 근거는 이 주장과 독립적이다(거짓 서술과 끊긴 포인터는 그 자체로 결함이다).
5. **PR1의 훅 보완이 정본을 복잡하게 만들 위험** — Bash 포함 matcher는 명령 파싱을 요구하고, Stop-time `git status`는 턴당 1회로 거칠다. 픽스처가 교육용 정본이므로 **어느 쪽을 시연할지 자체가 교육 결정**이다. `hooks.md:78`이 이미 트레이드오프를 서술하므로 recipe는 한쪽을 고르고 이유를 한 줄 남긴다.
