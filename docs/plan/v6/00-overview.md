# harness-creator v6 — 자기 적용 감사

> v1(`docs/plan/00-*` ~ `06-*`)·v2(`docs/plan/v2/`)·v3(`docs/plan/v3/`)·v4(`docs/plan/v4/`)·v5(`docs/plan/v5/`) 계획은 원문 그대로 남는다. 이 세대는 v2 결정 하나를 **절반 폐기**하고, v3 결정 하나와 v5 결정 하나를 **이번 세대 한정으로 반전한다** — 아래 개정 목록.

## 개정 목록

| 대상 | 처분 | 근거 |
|---|---|---|
| **v2 D22**(`docs/plan/v2/00-overview.md:74`, WS8) — 2단계였다: ① sync 절차와 status 의미론을 `interview.md`에서 신설 `references/re-entry.md`로 옮긴다(`:118`) ② `interview.md` 로드를 인터뷰가 실제로 일어나는 경로로 제한한다 | **① 폐기, ② 유지** | ②가 대표 성과를 샀다 — always-loaded 4,833 → 2,411단어(`docs/plan/v2/00-overview.md:67,257`). 그 성과는 **로드 게이팅**의 것이고 파일 분할의 것이 아니다. 두 파일 다 모드 분기 뒤에 있으므로 ①이 산 것은 "재진입 경로가 인터뷰 산문을 안 읽는다" 하나뿐이고, 대가로 status 의미론이 두 파일에 중복되고(`interview.md:137` ↔ `re-entry.md:44-55`) 재진입 독자가 `interview.md`의 스테이지로 되돌려 보내진다. v6는 ①만 되돌린다. ②는 그대로 산다 — 병합 파일도 여전히 모드 분기 뒤다 |
| **v3 D37**(`docs/plan/v3/00-overview.md:83`) — *"패러프레이즈-축약은 금지 — 희석이 전부 거기서 난다"* | **이번 세대 한정 반전, PR4에 한정** | 성진의 명시 지시로 재작성 라이선스를 받는다. D37의 근거(희석은 패러프레이즈에서 난다)는 여전히 옳으므로 **폐기가 아니라 대가 지불**이다: D38/D39의 claim 추출 A/B를 PR4에 의무로 건다. **D38/D39 자체는 재작성 라이선스가 아니다** — 손실 *검증* 프로토콜이고, 그 구분을 흐리면 이 계획이 잡으려는 종류의 오인용이 된다. 라이선스는 성진에게서 오고, D38/D39는 그 라이선스가 안전해지는 조건이다 |
| **v5 결정 1**(`docs/plan/v5/00-overview.md:137`) — *"재작성하지 않는다"* | **이번 세대 한정 반전, PR4에 한정** | v5의 근거는 "감산 대상이 문장 단위로 국소적이라 재작성은 위험만 산다"였고 v5 범위에서는 옳았다. PR4는 두 문서의 **병합**이라 대상이 국소적이지 않다 — 이어붙이기는 이음새를 남긴다. PR1·PR2·PR3·PR5에는 v5 결정 1이 그대로 적용된다 |
| **`references/skills.md:26`** — *"SKILL.md crossed 400 lines"* | **드리프트 수정** | 코드는 `scripts/validate_harness.py:30`에서 `MAX_SKILL_BODY_LINES = 500`이고 `SKILL.md:99`도 500이라 적는다. 이 스킬이 스스로 경고한 *"`--help`는 드리프트할 수 없고 `--help`의 요약본은 드리프트한다"*의 자기 사례 |

## Context — 왜 지금 이걸 하나

harness-creator는 네 가지를 설파한다: principle over rail, interface over document, 사용자 관점(개발 이력 금지), dense information. v2~v5는 각각 그중 하나를 세우거나 확장했지만, **네 프레임이 스킬 자신에게 온전히 적용됐는지 총체 점검한 적이 없다.**

이번 세션에서 references 밀도 / scripts 인터페이스 / plan 이력 세 방향을 병렬로 훑었다. 이 감사는 재현 가능한 산출물을 남기지 않았으므로(중간 리포트를 커밋하지 않았다) **아래 결함 목록만이 감사의 검증 가능한 결과이고, 각 항목은 file:line으로 직접 확인된다.** 감사 자체의 커버리지 주장("무엇을 안 놓쳤나")은 근거가 없으므로 하지 않는다.

성진의 가설 셋 중 하나는 반박됐고 둘은 확인됐다.

- **e2e 삭제 가설 — 반박됨.** `run_e2e.py`가 rail이 아니냐는 문제 제기였다. 코드를 읽으면 이 스크립트가 담은 것은 재유도 불가능한 gotcha의 응축이다: 헤드리스 세션이 자기 자신을 재귀 호출하지 않도록 `CLAUDECODE` 환경변수를 제거하는 트릭, `--isolate`가 부모 디렉터리를 지웠던 회귀, skip-permissions와 `--isolate`의 우선순위. 어느 것도 클로드가 그 자리에서 재유도할 수 없다. `e2e-testing.md`도 절차서가 아니라 판단 독트린이 본체다(무엇을 시나리오로 삼을지, 실패를 어느 층으로 되돌릴지, e2e가 무엇을 절대 못 보는지). **유지.** 단 아래 결함 3의 모순은 고친다.
- **모드 분리 가설 — 확인됨.** 개정 목록 1행.
- **agents 활용법 공백 가설 — 확인됨.** 결함 5.

## 확정된 현재 상태 — 감사에서 실증된 결함

### 1. 독트린이 네 곳에 진술된다 (dense information 위반)

rail-vs-principle 논증이 정본(`SKILL.md:95`) 외에 세 곳에 있다.

- `references/skills.md:7-13` — litmus 문장이 *"16th case"*까지 거의 그대로. 정본보다 길다.
- `references/claude-md-and-rules.md:9` — enforced-vs-advisory 판별 질문을 자체 진술.
- `references/workflows.md:17` — *"the one sentence that governs every layer this skill generates is …"*로 정본을 인용 없이 재진술.

같은 형태의 양방향 중복이 하나 더 있다: `claude-md-and-rules.md:9`와 `hooks.md:7`이 **같은 판별 질문**("매번 참이어야 하나, 대개 맞으면 되나")을 상호 참조 없이 각각 진술한다.

처분: 정본은 `SKILL.md`에만 두고, 각 레퍼런스는 **컴포넌트 고유 적용례만** 남긴 뒤 정본의 앵커 구절을 가리킨다. 앵커는 `SKILL.md`에 실재하는 구절 — "Conviction over compliance" / "Don't write what a capable model already knows" / "Prefer an interface over an instruction" — 을 그대로 인용한다. **명명된 프레임 리스트를 신설하지 않는다**: 리스트 자체가 재진술이고, `SKILL.md` 예산이 5단어밖에 안 남았다.

`skills.md`의 `subscriptions` 테이블 예시는 **존치한다.** 그것은 독트린의 재진술이 아니라 생성물 대상 교보재이고, 레일과 원칙을 나란히 놓은 유일한 대조 예시다.

### 2. 런타임 표면이 이미 매 세션 전달하는 정보의 재기술 (신규 필터)

과잉 판정 기준을 정정한다. 기존 기준은 "메커니즘 서술이냐"였는데 그건 너무 넓다 — 침묵 동작(컴팩션 시 재주입 규칙, workspace trust 게이팅, 조용한 실패)의 문서화는 아무 런타임 표면도 전달하지 않으므로 유지해야 한다. **정확한 기준은 "런타임 표면(도구 스키마·`--help`·검사 실패 메시지)이 이 정보를 이미 매 세션 전달하는가"**이다.

확인된 사례 둘:

- `references/interview.md:77`의 `AskUserQuestion` 기계적 제한 재기술(질문 최대 4개, 옵션 2–4개, 헤더 12자, "Other" 자동 추가). **도구 스키마가 소유한다.** 대조 대상은 이 세션의 도구 정의다: `questions` 배열이 `minItems:1, maxItems:4`, `options`가 `minItems:2, maxItems:4`, `header`가 *"max 12 chars"*, 설명이 *"There should be no 'Other' option, that will be provided automatically."* 스킬은 그 스키마 스냅샷을 보관하지 않으므로 — 보관해도 그 사본이 드리프트한다 — 삭제 근거는 "스키마가 매 호출 전달한다"이지 "지금 스키마와 일치한다"가 아니다.
- `references/workflows.md:32`의 `Date.now()` 금지 산문. **이중 소유**: Workflow 도구 설명이 이미 진술하고, `validate_harness.py`가 검사한다. 검사 위임 한 줄로 축소한다.

같은 필터로 **삭제하지 않는 것**: 옵션 description의 품질 기준("약한 설명은 레이블을 되풀이하고 강한 설명은 이유를 준다")은 스키마가 소유하지 않는다. 스키마가 소유하는 것은 추천안을 맨 앞에 두고 `(Recommended)`를 붙이라는 *배치 규칙*뿐이다.

### 3. 드리프트와 내부 모순 (interface over document 위반)

- `skills.md:26`의 "400줄" — 개정 목록 4행.
- **"2026-08-22 3회 확인"이 세 곳에 있다** — `scripts/run_e2e.py:17`, `SKILL.md:129`, `references/e2e-testing.md:158`. `run_e2e.py` 독스트링이 단일 소유자가 되고(그것이 `--help`로 출력되는 표면이다) 나머지 둘은 포인터로 축소한다.
- **`e2e-testing.md`가 자기 자신과 모순한다(감사 이후 Gate A가 추가로 발견).** 섹션 제목 `:156`은 *"Headless permission handling: unverified in this build"*, 본문 `:158`은 *"It has one now: on 2026-08-22 … three scenarios on the first attempt"*, 그리고 `:162`는 *"That approach is reasoned, not verified. Do not present it to the user as already confirmed."* — 같은 대상에 대해 확인됨과 미확인이 나란히 산다. v5가 확인 문장을 넣으면서 둘러싼 미확인 산문을 갱신하지 않은 흔적이다. 날짜 중복만 지우면 이 모순이 남으므로 PR4가 함께 해소한다: **확인된 것(메커니즘)과 확인되지 않은 것(이 독자의 기계)의 경계를 한 번만 긋는다.**

### 4. 구조 결함

`references/agents.md`에 **본문 없는 헤더가 둘** 있다: `:24`(`## model defaults to inherit; forcing a tier needs a reason`)와 `:38`(`## Gotcha: skills: preloads full skill bodies, not descriptions`). 둘 다 헤더 직후 다음 헤더가 온다. 내용은 `:65`·`:66`의 프론트매터 표에 있으므로 정보 손실은 없지만, 목차를 훑는 독자에게 두 절이 존재한다고 알리고 빈손으로 돌려보낸다.

### 5. 커버리지 공백 — 4방향 오케스트레이션 선택 가이드 부재

Claude Code가 병렬 작업에 주는 표면은 넷이다: subagents, agent view(`claude agents`), agent teams, dynamic workflows. **무엇을 언제 쓰는가가 이 스킬 어디에도 없다.** agent teams는 `agents.md:14`의 안티패턴 언급 한 번이 전부고, 그 언급은 "teams를 기본값으로 삼지 마라"만 말한다 — teams가 *맞는* 경우를 말하지 않으므로 그 줄은 정직한 짝이 없는 반쪽이다.

## 목표 (한 문장)

네 프레임을 스킬 자신에게 적용해, 정본이 하나뿐이게 만들고(중복 제거), 산문이 런타임 표면을 베끼지 않게 하고(재기술 제거), 산문 규칙 중 기계 검사 가능한 것을 코드로 옮기고(검사 4건), 실증된 커버리지 공백 하나를 메운다(오케스트레이션 가이드).

## 핵심 결정

### 결정 1 — e2e는 유지한다. 3중 중복과 내부 모순을 함께 고친다

`run_e2e.py`가 날짜와 실행 횟수를 단독 소유하고, `SKILL.md`·`e2e-testing.md`는 그 사실이 어디 적혀 있는지만 가리킨다. 동시에 결함 3의 모순을 해소한다 — 이 둘은 같은 문단들을 건드리므로 나눠서 할 수 없다.

### 결정 2 — 모드를 전면 병합하고, 비용을 숫자로 명기한다

`interview.md`가 extend·improve(ablation 프로토콜 포함)·sync를 전부 흡수하고 `re-entry.md`는 삭제한다.

**의식적 회귀를 명기한다.** 병합 전 sync는 `re-entry.md` 1,094단어만 읽는 최저비용 모드였고, 그 속성은 `tests/test_skill_surface.py:211-218`의 `test_sync_path_does_not_require_interview_md`가 검증하고 있었다. 병합 후 sync는 통합 파일(목표 ~3,900단어)을 읽는다 — **sync 경로 기준 약 3.5배.** 실측치는 PR4 완료 시점에 확정해 CHANGELOG에 적는다. 이것은 순수 개선이 아니라 트레이드오프이고, 그렇게 기록한다.

**빈도로 정당화하지 않는다.** "sync가 가장 드물게 실행된다"는 측정된 적이 없고, 측정할 수단도 없다 — 이 스킬 자신이 `e2e-testing.md:150`에서 invocation telemetry가 없다고 적는다. 근거는 빈도가 아니라 셋이다: (a) 통합 파일은 조건부 표면이므로 **always-loaded 예산에 0의 영향**, (b) status 의미론이 한 곳에서만 진술되므로 두 사본이 어긋날 경로가 사라짐, (c) 재진입 독자의 파일 왕복 제거. sync 경로만 놓고 보면 이 거래는 손해다. 손해를 감수하는 이유는 (b)가 sync 경로 자신의 정확성 문제이기 때문이다 — 드리프트한 status 표를 읽는 저비용보다, 하나뿐인 status 표를 읽는 고비용이 낫다.

**고려 후 기각 — `interview.md`를 `SKILL.md`로 흡수하는 안.** `SKILL.md`는 스킬 호출 시 무조건 주입되고 `interview.md`는 인터뷰 스테이지에 도달했을 때만 읽는다. 비인터뷰 호출은 실재한다 — 검증만 돌리기, 훅 디버깅, e2e 실행, 이미 승인된 스펙으로 생성하기. 흡수는 조건부 표면을 무조건 표면으로 옮기는 것이므로 progressive disclosure의 역방향이다. 게다가 물리적으로 불가능하다: `SKILL.md`는 500줄 공식 상한과 자체 `WORD_BUDGET = 2650`(현재 2,644단어) 양쪽에 걸린다.

### 결정 3 — 재작성 라이선스는 claim-loss audit과 한 쌍이다

보존 단위는 문장이 아니라 **claim**이다. 라이선스의 출처는 성진의 지시이고(개정 목록 2·3행), 대가는 D38/D39 프로토콜이다: 원본에서 claim 목록을 먼저 추출 → 그 목록을 사양 삼아 빈 페이지에서 하나의 완결 문서로 집필 → 완성본을 목록과 대조해 손실 0 확인.

판단 기준: **수정 후 이음새가 보이면 그 파일은 전면 재작성한다.** 1차 재작성 확정은 `interview.md`(병합) 하나. 후보는 `skills.md`(독트린 컷 후 골격이 어색해지면), `agents.md`(헤더 수정과 섹션 신설이 겹치면 — 이 경우 PR2·PR3을 하나로 합친다).

### 결정 4 — codex 적대 검토 두 게이트

v5에서 `gpt-5.6-sol`의 독립 감사가 설계를 두 번 바꿨다(첫 독트린 초안의 unsatisfiable pair, 닫힘 검사가 실패시켰을 정상 플러그인 3건). 같은 절차를 따른다: **Gate A** — 이 계획 문서 확정 전, **Gate B** — 구현 완료 후 전체 디프.

Gate A는 실행됐고 23건을 반환했다. 이 문서의 현재 판본이 그 반영본이다. 설계를 바꾼 것 여덟: 개정 목록의 D22 절반-폐기(v6 초안은 D22 전체를 폐기한다고 썼고, D22의 실측 성과를 거꾸로 서술했다), D37/D38 구분(초안은 D38을 재작성 라이선스로 오인용했다 — 이 계획이 잡으려는 바로 그 오류), 결함 3의 `e2e-testing.md` 내부 모순(감사가 놓쳤다), 결정 2의 빈도 논거 철회, PR3의 teams 권한 주장 정정과 플러그인 workflows 주장 격하(아래), PR5의 `harness_common.py` 의존성(아래), 완료 판정 다수의 실행 가능성 수정.

### 결정 5 — red→green은 테스트 seam이 있는 모든 변경에 적용한다

`validate_harness.py` 신규 검사 4건은 픽스처와 실패 테스트를 먼저 쓴다. **PR2의 고아 헤더 검사와 PR3의 주장 고정 테스트도 마찬가지다** — 대상이 마크다운이어도 검사 대상이 파일 내용이면 red 단계가 존재한다. red 단계가 없는 것은 산문 재작성 자체(PR1·PR4의 본문)뿐이고, 거기서는 `validate_harness.py` exit 0 + pytest green + claim-loss 0을 완료 판정으로 쓴다.

### 결정 6 — `SKILL.md` 라우팅 표에 teams 행을 추가하지 않는다

잔여 예산 5단어가 첫 번째 이유지만 유일한 이유는 아니다. 라우팅 표의 각 행은 **"이것은 어느 컴포넌트 파일이 되는가"**를 답하는데, teams는 보통 아무 생성물도 만들지 않는다(런타임에 형성된다). 실험 기능이라 기본 비활성이기도 하다. 4방향 결정은 `agents.md`가 전담한다.

### 결정 7 — 출처가 "문서화되지 않음"인 주장은 그대로 "문서화되지 않음"으로 쓴다

Gate A가 잡은 오류 유형이라 규칙으로 세운다. `docs/plan/research/research-dynamic-workflows.md:55`는 플러그인 workflows 배포에 대해 *"NOT documented as able to ship workflows"*라 하고 `:115`는 같은 항목을 **OPEN QUESTION**의 *"unconfirmed"*로 분류한다. 부재의 증거를 불가능의 증거로 승격하면 안 된다.

그래서 PR3이 쓰는 문장은 "플러그인은 workflows를 배포할 수 없다"가 아니라 **"문서화된 workflow 로드 경로는 `.claude/workflows/`(프로젝트, 레포 루트까지 상향 탐색)와 `~/.claude/workflows/` 둘뿐이고, 플러그인 컴포넌트 목록에 workflows 항목이 없다"**이다. 하네스 작성자에게 주는 실무 지침은 같지만, 틀렸을 때 틀리는 방식이 다르다 — 전자는 제품이 기능을 추가하면 거짓이 되고, 후자는 문서가 바뀌면 낡을 뿐이다.

## 기계 검사 공백 — 산문 규칙을 코드로 (PR5)

넷 다 기존 산문이 이미 gotcha로 진술하는데 기계 검사 가능한 채 방치된 것이다.

| # | 검사 | 심각도 | 근거 |
|---|---|---|---|
| F1 | 프로젝트/로컬 `settings.json`의 `permissions.defaultMode: "auto"` | Warning | 프로젝트 스코프에서 무시된다. 유효한 대안 해석이 있다(사용자가 알고도 문서화 목적으로 적을 수 있음) |
| F2 | `Write(path)`·`Glob(path)`·`NotebookEdit(path)`·`MultiEdit(path)` 형태의 path-rule | **Error** | `hooks.md:110`이 *"accepted and then **never consulted**"*라고 단정한다. Edit/Read 외에는 유효한 대안 해석이 **전무**하므로 기존 missing-hook-script Error와 동형이다. 경로 없는 맨 `Write` deny는 다른 것이므로(같은 줄이 명시한다) 걸리면 안 된다 |
| F3 | `Bash(ls*)` — 후행 공백 없는 접두 규칙 | Warning | 워드 바운더리가 없어 `lsof`·`lsattr`까지 허용한다. 의도적일 수 있으므로 W |
| F4 | 스킬 프론트매터 `hooks:` 블록 검증 부재 | Error/Warning | `_check_hooks_block`이 `settings.json`에만 적용된다. 스킬 디렉터리 기준 경로 해석으로 리팩터 |

**F4에는 선언되지 않은 의존성이 있었다(Gate A #14).** `harness_common.py:218-238`은 프론트매터의 중첩 매핑을 **의도적으로** 읽지 않고 `UNPARSED_BLOCK`으로 표시한다. 그 동작은 v5가 근거를 적어 넣은 것이고(*"discarding the whole file over it is worse"*) `tests/test_interface_claims.py:140-143`이 핀으로 고정하고 있다. 그러므로 F4는 `validate_harness.py` 단독 변경이 아니다.

해법은 **가산이지 반전이 아니다**: `parse_frontmatter`가 중첩 블록을 `UNPARSED_BLOCK`으로 표시하는 것은 그대로 두고(핀 유지), 그 블록의 **원문 줄들을 함께 보존**해 `validate_harness.py`가 목적 전용 리더로 `hooks:`만 해석하게 한다. 프론트매터 분할의 단일 정본은 여전히 `harness_common.py`이고, 데이터로서의 `hooks` 값은 여전히 "이 파서가 추측하지 않는 것"이며, 새로 생기는 것은 "추측하지 않되 버리지도 않는다"뿐이다. `tests/test_interface_claims.py:140-143`은 수정 없이 통과해야 한다 — 통과하지 않으면 설계가 반전으로 미끄러진 것이므로 되돌린다.

**의도적 미구현 둘.** `stop_hook_active` 소스 grep(훅 스크립트가 그 필드를 읽는지 확인) — 파이썬이 아닌 훅 스크립트에는 파싱이 불가능하고 grep 휴리스틱은 오탐이 잦다. 복합 명령 allow-rule 분석(`Bash(cd foo && rm -rf *)` 같은 것) — 셸 파싱 없이는 불건전하다.

`once: true` 컨텍스트 오용 경고는 F4 리팩터가 공짜로 만들어주면 넣고, 리뷰에서 축소가 필요하면 1순위로 컷한다 — 이 감사가 요구한 항목이 아니라 기회적 추가다.

## 제약 수치 (설계를 구속하는 실측값)

측정 시점은 전부 2026-08-24, 쓰기 가능한 `TMPDIR`이 있는 환경이다(테스트 스위트가 `tempfile.mkdtemp()`를 쓰므로 읽기 전용 샌드박스에서는 18건이 에러로 뜬다 — 회귀가 아니라 환경 조건이다).

| 대상 | 현재 | 제약 |
|---|---|---|
| `SKILL.md` | 2,644단어 / 135줄 | `tests/test_skill_surface.py:195`가 `assertLess(words, 2650)`이므로 상한은 2,649 — **잔여 5단어.** 공식 상한 500줄. 이 세대에서 `SKILL.md`를 건드리는 PR은 감산 또는 유지만 |
| `interview.md` + `re-entry.md` | 3,222 + 1,094 = 4,316단어 | 병합 후 목표 ~3,900단어 |
| `references/*.md` | agents 3,058 / claude-md 2,795 / e2e 3,523 / hooks-events 3,801 / hooks 5,370 / skills 2,840 / workflows 2,203 | 린트 상한 없음. 500줄 규칙은 `SKILL.md` 본문 전용 |
| 이 레포의 `.claude/settings.json` | 없음 | F1–F3 자기 오탐 위험 없음 |
| 테스트 | 236건 green | 각 PR에서 유지 |
| 릴리스 | v0.4.0 | 이 세대는 **v0.5.0** |

## 작업 단위와 완료 판정

**파일 소유 규칙 — 배타가 아니라 직렬화다.** v3 규칙의 원문은 "두 PR이 같은 파일을 건드리지 않게 배열한다"이지만, 이 세대에서 그것은 문자 그대로 달성 불가능하다(Gate A #1). 실제로 지키는 것은 이것이다: **같은 파일을 건드리는 PR들은 순서가 고정되고, 뒤 PR은 앞 PR의 결과 위에서 시작한다.** 병렬로 열리는 PR 사이에만 배타가 성립한다.

- `agents.md` — PR2 → PR3 (합칠 수도 있다, 결정 3)
- `workflows.md` — PR1 → PR3
- `SKILL.md`·`interview.md`·`re-entry.md`·`e2e-testing.md` — PR4만
- `skills.md`·`claude-md-and-rules.md` — PR1만
- `validate_harness.py`·`harness_common.py` — PR5만
- `.claude/harness-spec.md` — PR6만
- `CHANGELOG.md`·`plugin.json`·`marketplace.json` — PR7만
- `tests/**` — PR2·PR3·PR4·PR5가 각각 다른 테스트 클래스를 건드린다

**Hard line 3(스펙과 디스크가 조용히 어긋나지 않는다)은 PR 단위가 아니라 패스 단위로 지킨다.** v6 전체가 하나의 improve 패스이고, 그 패스의 스펙 쓰기는 PR6 하나다. PR1–PR5가 각각 스펙을 건드리면 여섯 번의 부분 갱신이 생기고 그중 어느 것도 최종 상태가 아니다. **대신 PR6은 선택이 아니라 이 세대의 완료 조건이다** — PR5까지 머지하고 PR6을 빠뜨리면 그 순간 스펙이 거짓이 된다. 같은 이유로 PR4가 실측한 sync 비용 숫자는 PR4가 CHANGELOG에 쓰지 않고 PR 본문에 기록만 하며, CHANGELOG는 PR7이 단독으로 쓴다.

| # | 범위 | 완료 판정 |
|---|---|---|
| PR0 | 이 문서 | 파일 존재, 개정 목록에 D22·D37·v5 결정 1 각각의 처분과 근거 명기 |
| Gate A | codex(`gpt-5.6-sol`, xhigh, read-only)로 이 문서 적대 검토 | **완료** — 23건 반환, 반영본이 이 판본. 결정 4에 설계를 바꾼 항목 명기 |
| PR1 | 독트린 4중 진술 제거 + `skills.md` 400→500 + `Date.now` 산문 축소. 대상: `skills.md`, `claude-md-and-rules.md`, `workflows.md` | ① `grep -rn "re-derive" .claude/skills/harness-creator/`에서 litmus 재진술이 0건 — 남는 히트는 `SKILL.md`의 정본 문단과 무관한 용례뿐 ② `grep -n "400" references/skills.md`가 0건 ③ 세 파일 각각 `wc -w`가 before보다 작다(PR 본문에 before/after 기재) ④ `hooks.md:7`의 판별 질문이 `claude-md-and-rules.md`에서는 포인터로만 존재 ⑤ 전체 스위트 green |
| PR2 | `agents.md` 고아 헤더 2개 수정 + `NoOrphanedHeadingsTests` 신설 | 신규 테스트가 `git stash` 상태에서 red, 수정 후 green. 테스트는 `references/*.md` 전체를 스캔하고 헤더 직후 비어 있지 않은 본문 줄을 요구한다 |
| PR3 | `agents.md` 4방향 오케스트레이션 섹션 신설 + `workflows.md` 교차 포인터 1줄 | ① 다섯 주장이 각각 substring 테스트로 고정 ② **각 테스트의 docstring에 출처 file:line을 적는다** — 테스트가 고정하는 것은 제품 사실이 아니라 *이 스킬이 쓴 문장*이므로, 출처를 테스트 안에 두어야 문서가 바뀔 때 사람이 대조할 지점이 생긴다(Gate A #13) ③ 두 주장은 Gate A가 정정한 형태로만 쓴다: teams 권한은 *"리드 설정으로 시작하고, 스폰 시점에 팀원별 모드를 지정할 수는 없지만 스폰 후 개별 변경은 가능"*, 플러그인 workflows는 결정 7의 문장 ④ PR 본문에 `.tmp/docs_claude` 출처 행 명기 |
| PR4 | 모드 전면 병합 — `interview.md` 전면 재작성. `re-entry.md` 삭제, `SKILL.md` 루프 분기 축약(순감), e2e 날짜 단일 소유화 + 결함 3의 모순 해소, `AskUserQuestion` 스키마 재기술 삭제 | ① `test ! -f .claude/skills/harness-creator/references/re-entry.md` ② `grep -rn "re-entry" .claude/skills/harness-creator/ tests/`가 0건 ③ `wc -w .claude/skills/harness-creator/SKILL.md` < 2650 ④ `test_sync_path_does_not_require_interview_md` 삭제하고 **반대 방향 대체 테스트 신설** — 병합된 `interview.md`가 `sync`/`status`/`generated`/`validated`/`Change history`를 전부 담는지(원 테스트가 지키던 속성은 "sync 개념이 어딘가 있다"이고, 그것은 병합 후에도 지켜야 한다) ⑤ `SubtractionTests`의 `RE_ENTRY`/`"## Improve"` split을 병합 파일과 새 헤딩 레벨로 갱신 ⑥ `e2e-testing.md`에 "verified"와 "not verified"가 같은 대상에 대해 동시에 존재하지 않는다(PR 본문에 어느 문장이 무엇을 주장하는지 표로) ⑦ claim-loss audit 결과를 PR 본문에 첨부 — 추출한 claim 수와 대조 결과 ⑧ `validate_harness.py --path . --strict` exit 0 ⑨ 병합 파일 `wc -w` 실측값을 PR 본문에 기재(PR7이 CHANGELOG에 쓸 숫자) |
| PR5 | `validate_harness.py` 신규 검사 4건 + `harness_common.py`의 중첩 블록 원문 보존. 픽스처+red 테스트 먼저 | ① 검사 4건 각각 red→green ② 오탐 가드 픽스처 각각: `Edit(docs/**)`·맨 `Write` deny 무경고(F2), `Bash(ls *)` 무경고(F3), 사용자 스코프 `defaultMode:"auto"` 무경고(F1), 올바른 스킬 hooks 무경고(F4) ③ `tests/test_interface_claims.py:140-143` **수정 없이 통과** — 실패하면 설계가 반전으로 미끄러진 것 ④ 전체 스위트 green ⑤ 이 레포 자체에 `--strict` exit 0 |
| PR6 | `harness-spec.md` 갱신 + 위키 2줄 정정 | ① B9 행의 status가 `retired`이고 사유 셀에 B8 병합이 적혀 있다 ② B8 설명이 재진입 3모드를 포함한다 ③ Design rationale에 sync 비용 회귀가 **숫자와 함께** 1항목 ④ Change history에 `v6` 줄 존재 ⑤ `harness-spec.md:44`의 두 파일 게이팅 설명이 병합 후 사실과 일치 ⑥ `docs/wiki/explanation/architecture.md:54`와 `design-principles.md:52`가 더 이상 별도 re-entry 표면을 전제하지 않는다 ⑦ `audit_harness.py --path .` 드리프트 0 |
| Gate B | codex로 전체 디프 적대 검토: *"문서 출처가 실제로 지지하지 않는 주장, 남은 독트린 자기 재진술, 런타임 표면이 이미 전달하는 정보의 잔존 재기술, PR4의 claim 손실"* | 발견 사항 반영 후 종결. **claim-loss audit이 사람의 성실성에 의존하므로(위험 항목) Gate B가 그 항목을 명시적으로 받는다** |
| PR7 | v0.5.0 릴리스 | ① `plugin.json`·`marketplace.json` 둘 다 `0.5.0` ② `CHANGELOG.md`에 `## [0.5.0]` 헤딩과 `[0.4.0]`이 쓰는 하위 섹션 이름들이 존재 ③ Known limitations 절에 sync 비용 회귀가 **PR4 실측 숫자와 함께** 기재 ④ `git tag -l v0.5.0`이 비어 있지 않고 annotated(`git cat-file -t`가 `tag`) ⑤ `gh release list`에 표시 |

### `re-entry.md` 참조 전수 목록

PR4가 해소하는 것 — `SKILL.md:34,36`(루프 분기), `references/e2e-testing.md:144`(라우팅 표 포인터), `references/interview.md:102,139`(스텁·status 포인터), `tests/test_skill_surface.py:214-216, 220-221, 481`(테스트 3건).

PR6이 해소하는 것 — `.claude/harness-spec.md` B9 행과 `:44`의 게이팅 설명, `docs/wiki/explanation/architecture.md:54`, `docs/wiki/explanation/design-principles.md:52`.

**PR4의 grep 판정은 스킬 디렉터리와 `tests/`로 범위를 한정한다**(Gate A #23). `docs/plan/`의 역대 세대와 `CHANGELOG.md:117`은 역사 기록이라 그 문자열이 영구히 남는다 — 레포 전체 grep을 0으로 요구하면 절대 만족될 수 없는 판정이 된다. 위키 두 줄은 PR6이 고치므로 릴리스 시점에 거짓인 사용자 문서는 남지 않는다. 위키 전체 재검토는 후속 과제로 표시만 한다.

### PR3 신설 섹션 골격 (전 주장 출처 필수)

출처는 `.tmp/docs_claude/02-build-with-claude-code/01-agents-and-parallel-work/`(이하 `AGENTS/`)와 `docs/plan/research/research-dynamic-workflows.md`.

1. **판별 기준: 다음에 무엇을 실행할지 누가 결정하는가.** Claude가 턴별로(subagents) / 사용자가(agent view) / 리드 에이전트가(teams) / 스크립트가(workflows).
2. **각 선택지가 하네스에 요구하는 생성물.** subagents → `.claude/agents/*.md`; agent view → **생성물 없음**(습관이지 컴포넌트가 아니다); teams → **보통 생성물 없음**(런타임에 형성. 재사용되는 팀원 역할만 일반 subagent 파일로 미리 써 둘 값이 있다); workflows → `.claude/workflows/*.js`.
3. **teams가 실제로 맞는 경우** — `agents.md:14` 안티패턴 줄의 정직한 짝. 독립적이고 토론·반박형인 작업.
4. **비용과 역학** (`AGENTS/03-run-agent-teams.md`): 실험 기능이라 `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`로 켜야 함, 토큰 고비용, **파일 격리 없음**(소유권을 나눠 줘야 한다), 팀원 간 직접 메시지, 권한은 **리드 설정으로 시작하며 스폰 시점 팀원별 지정은 불가하되 스폰 후 개별 변경은 가능**(`:255-259, :420`), 그리고 subagent 정의의 **`skills:`·`mcpServers:` 프론트매터는 teammate로 실행될 때 적용되지 않는다**(`:250` 부근 Note) — 이것이 재사용 역할을 subagent 파일로 미리 쓰는 값의 상한이다.
5. **배포 함의.** 결정 7의 문장 + 플러그인 subagent는 `hooks`·`mcpServers`·`permissionMode`가 탈락 → 이 필드들에 의존하는 하네스는 레포 `.claude/` 트리로 배포.

## 결과 디렉터리 구조

파일 구조 변화는 `re-entry.md` 삭제 하나뿐이다(references 9 → 8개). 확장되는 파일은 `interview.md`(병합)와 `agents.md`(오케스트레이션 섹션)뿐이고, `skills.md`·`claude-md-and-rules.md`·`workflows.md`·`e2e-testing.md`·`SKILL.md`는 전부 감산이다(PR1·PR4의 완료 판정이 before/after `wc`로 이를 강제한다). `scripts/`는 파일 구성 무변경(`validate_harness.py` 검사 4건 + `harness_common.py` 원문 보존). 스킬 밖: `docs/plan/v6/` 신설, `tests/` 회귀·픽스처 추가, `harness-spec.md` B9 `retired`, 위키 2줄, CHANGELOG `[0.5.0]`.

## 검증

- 각 PR: `python3 .claude/skills/harness-creator/scripts/validate_harness.py --path . --strict` exit 0, `python3 -m unittest discover -s tests -q` green(236건 + 신규). 쓰기 가능한 `TMPDIR` 필요.
- 마크다운: 하드랩 금지.
- `harness-spec.md` 갱신은 PR6이 이 패스를 대표해 한 번 수행한다(위 Hard line 3 항목).
- codex 게이트 2회.
- 마무리: 자동 메모리의 "v3가 현행" 정보를 v6로 갱신.

## 범위 밖

- `docs/wiki/` 전체 재검토 — PR6이 거짓이 되는 두 줄만 고치고, 나머지는 후속 과제로 표시.
- `hooks.md`·`hooks-events.md` 감산 — 감사에서 중복이 나오지 않았다. `hooks-events.md`는 `hook_event.py`의 데이터 소스라 조회 전까지 비용이 0이다.
- agent teams를 `SKILL.md` 라우팅 표에 올리기 — 결정 6.
- `stop_hook_active` grep 검사와 복합 명령 allow-rule 분석 — 위 "의도적 미구현".

## 위험·가정

- **claim-loss audit이 사람의 성실성에 의존한다.** 기계 검사가 없다. 완화: 추출 목록을 PR 본문에 첨부해 대조 가능하게 만들고, Gate B가 이 항목을 명시적으로 받는다.
- **PR3의 주장 다섯이 실험 기능 문서에 근거한다.** agent teams는 기본 비활성 실험 기능이라 문서와 구현이 빠르게 바뀔 수 있다. substring 테스트는 정확성을 검증하지 못하고 *이 스킬이 쓴 문장*만 고정한다 — 그래서 각 테스트가 docstring에 출처 file:line을 들고 있어야 대조가 가능하다. Gate A가 초안의 권한 문장 하나를 이미 오서술로 잡았고, 그것이 이 위험의 실증이다.
- **sync 비용 회귀의 실측치가 아직 없다.** PR4 완료 시점에 확정한다.

## 실행 중 정정

계획이 지시한 것과 구현이 달라진 지점만 적는다. 계획을 조용히 벗어나는 것이 이 세대가 잡으려는 드리프트와 같은 종류이므로, 어긋난 곳은 어긋난 채로 기록한다.

- **PR1 ②의 판정 원문은 실행 불가능했다.** `grep "could the model.*re-derive"`가 `SKILL.md` 1건을 히트한다고 썼지만 `SKILL.md:95`의 실제 문구는 *"would let the model re-derive"*라 그 grep은 0건이다. 판정의 의도(litmus 문장이 한 곳에만 산다)는 그대로 두고 grep만 고쳤다.
- **PR4가 `harness-spec.md`를 두 줄 건드린다 — PR6 단독 소유가 아니었다.** `re-entry.md`를 지우는 순간 `audit_harness.py`의 드리프트 검사가 B9 행(`validated`, 그 경로)을 잡아 `test_this_repo_reports_no_drift`가 red가 된다. 즉 이 한 줄은 삭제와 같은 커밋에 있어야 하고, 그것이 Hard line 3이 실제로 요구하는 바다. `:44`의 게이팅 설명도 삭제 직후 거짓이 되므로 함께 고쳤다. PR6은 서술 작업(B8 확장, Design rationale, Change history, 위키)을 맡는다. Gate A #1이 이 긴장을 지적했고 당시 "전부 PR6"으로 해소했는데, 기계 검사 쪽이 더 강했다.
- **PR4 ②의 grep 범위를 `re-entry.md`(파일명)로 좁혔다.** 원문은 `grep -rn "re-entry"` 0건이었지만 "re-entry"는 개념어로도 쓰인다 — `audit_harness.py:334`가 *"references/interview.md's re-entry variants"*라고 정확히 가리키는 것까지 금지하게 된다. Hard line 1이 요구하는 것은 존재하지 않는 파일을 가리키는 포인터가 없는 것이므로 판정을 그 형태로 바꿨다. 스킬 디렉터리 내 `re-entry.md` 히트는 0건이다.
- **PR1 ②의 "500이 대신 존재"를 채택하지 않았다.** `skills.md:26`에서 숫자를 다시 쓰는 대신 검사 위임으로 갔다 — `validate_harness.py:276-280`의 메시지가 `MAX_SKILL_BODY_LINES`를 그대로 출력하므로, 숫자를 산문에 다시 적으면 *"편집하면 문장이 거짓이 되는"* 사본을 하나 더 만드는 셈이다. 결함 3이 지적한 것이 정확히 그 사본이므로, 같은 결함을 고치면서 같은 모양을 재생산하지 않는다.
