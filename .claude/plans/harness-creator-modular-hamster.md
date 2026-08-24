# harness-creator v6 — 자기적용 감사와 개선 계획

## Context

harness-creator는 네 가지 프레임(principle over rail, interface over document, for user not developer, dense information)을 설파하는 메타 스킬이지만, v5까지의 개선이 자기 자신에게 온전히 적용됐는지 총체 점검한 적이 없다. 이번 세션에서 3방향 병렬 감사(references 밀도, scripts 인터페이스, plan 이력)를 수행했고, 스킬이 자기 규칙을 위반하는 지점 여러 곳을 실증했다. 이 계획은 그 결과를 docs/plan/v6/ 세대로 기록하고 PR 시퀀스로 실행하는 것이다.

사용자 가설 대비 감사 결과: e2e 삭제 가설은 **반박됨**(유지 결정), 모드 분리 가설은 **확인됨**(전면 병합 결정), agents 활용법 공백 가설은 **확인됨**(4방향 오케스트레이션 가이드 추가 결정).

## 확정된 결정 (사용자 승인 완료)

1. **e2e 유지 + 중복 제거** — run_e2e.py는 rail이 아니라 재유도 불가능한 gotcha의 응축(CLAUDECODE 환경변수 제거 트릭, --isolate 부모 디렉터리 정리 회귀, skip-permissions 우선순위)이며 e2e-testing.md의 80%는 판단 독트린. 유일한 결함인 "2026-08-22 3회 확인" 3중 중복만 제거: run_e2e.py docstring이 단일 소유, SKILL.md·e2e-testing.md는 포인터로 축소.
2. **모드 전면 병합** — interview.md가 extend·improve(ablation 프로토콜 포함)·sync까지 전부 흡수, re-entry.md 삭제. sync 경로가 불필요한 인터뷰 프로토콜을 싣는 비용은 의식적 트레이드오프로 v6 결정 로그에 기록. v1의 파일 분리 결정을 revision table에서 retire. **고려 후 기각(결정 로그에 기록)**: interview.md를 SKILL.md로 흡수하는 안 — SKILL.md는 호출 시 무조건 주입되는 표면이고 interview.md는 인터뷰 스테이지에서만 읽는 조건부 표면이라(검증만·훅 디버깅·e2e·기승인 스펙 생성 등 비인터뷰 호출이 실재), 흡수는 조건부→무조건 이동으로 progressive disclosure의 역방향. 게다가 SKILL.md 500줄 공식 상한과 자체 `WORD_BUDGET=2650`(잔여 6단어)을 모두 초과해 물리적으로도 불가.
3. **codex(gpt-5.6-sol, xhigh) 두 게이트** — (a) v6 플랜 문서 확정 전 적대 검토, (b) 구현 완료 후 전체 디프 검토. v5에서 codex가 설계를 두 번 바꾼 전례(--isolate 안전 버그, package-closure 오탐)를 따름.
4. **tdd 스킬은 스크립트 변경에만** — validate_harness.py 신규 검사 4건은 픽스처+실패 테스트 먼저. 마크다운 재작성은 validate_harness.py exit 0 + pytest green을 완료 판정으로 사용.

## 감사에서 실증된 결함 (수정 대상)

### 밀도·중복 (dense information 위반)
- **독트린 4중 진술**: rail-vs-principle 논증이 SKILL.md(정본)·skills.md L5-20(“16th case”까지 거의 그대로)·claude-md-and-rules.md·workflows.md L17에 반복. → SKILL.md만 정본으로 남기고 각 레퍼런스는 컴포넌트 고유 적용례만 유지(skills.md의 subscriptions 예시는 생성물 대상 교보재로 존치).
- **status 컬럼 의미론 중복**: interview.md L137과 re-entry.md L44-55가 declined/retired 의미를 거의 그대로 반복 — 병합으로 자동 해소.
- **enforced-vs-advisory 테스트 양방향 중복**: claude-md-and-rules.md L9와 hooks.md L7이 같은 질문을 상호 참조 없이 각각 진술 — 한쪽 진술 + 포인터로.
- **interview.md 소소한 트림**: convergence/divergence 재논증(SKILL.md가 이미 진술), I2 정찰 체크리스트를 원칙 한 문장으로, "Ask open questions..." 일반 코칭 삭제.
- **런타임 재전달 메커니즘의 재기술 제거(신규 필터)**: 과잉 판정 기준은 "메커니즘이냐"가 아니라 "런타임 표면(도구 스키마·--help·검사 메시지)이 이미 그 정보를 매 세션 전달하느냐". 확인된 사례: interview.md의 AskUserQuestion 기계적 제한(질문 4개·옵션 2–4개·헤더 12자·Other 자동 추가 — 도구 스키마가 소유), workflows.md의 `Date.now()` 금지 산문(Workflow 도구 설명 + validate_harness.py 검사가 이중으로 소유 — 검사 위임 한 줄로 축소). 침묵 동작(컴팩션·trust 게이팅·조용한 실패)의 문서화는 과잉이 아니므로 유지.

### 드리프트 (interface over document 위반)
- **skills.md L26 "400줄"** vs 코드 `MAX_SKILL_BODY_LINES = 500` vs SKILL.md "500줄" — 스킬이 스스로 경고한 "아무도 검증하지 않는 사본" 사례. 500으로 수정하거나 검사 위임 문구로.
- **"2026-08-22 3회 확인" 3중 중복** — 위 결정 1.

### 구조 결함
- **agents.md 고아 헤더 2개**: L24(`model` defaults...)와 L38(`skills:` preloads...)가 본문 없이 다음 헤더로 이어짐(내용은 L65-66 표에 있음). 헤더 제거 또는 재구성.

### 커버리지 공백 (사용자 지적 확인됨)
- **4방향 오케스트레이션 선택 가이드 부재**: subagents / agent view(`claude agents`) / agent teams / dynamic workflows 중 무엇을 언제 쓰는가가 어디에도 없음. agent teams는 agents.md L14의 안티패턴 언급 1회가 전부. 판별 기준("다음에 뭘 실행할지 누가 결정하는가": Claude 턴별 / 리드 에이전트 / 스크립트)과 핵심 사실(teams는 실험 기능·파일 격리 없음·토큰 고비용, workflows는 16동시/1000총량 캡·acceptEdits 고정, **플러그인은 workflows 배포 불가** → 풀 하네스는 레포 .claude/ 트리로 배포)을 `.tmp/docs_claude/02-build-with-claude-code/01-agents-and-parallel-work/`와 `docs/plan/research/research-dynamic-workflows.md`에서 검증해 agents.md에 배치, workflows.md에서 교차 포인터, SKILL.md 라우팅 표 반영 여부 검토.

### 기계 검사 공백 (산문 규칙 → 코드로 이동, tdd 적용)
validate_harness.py에 추가할 4건 (모두 기존 산문 gotcha가 기계 검사 가능한데 방치된 것):
1. 프로젝트/로컬 settings.json의 `permissions.defaultMode: "auto"` 무시 — Warning.
2. Edit/Read 외 도구의 path-rule(`Write(path)` 등)은 파싱되지만 절대 참조 안 됨 — Warning.
3. `Bash(ls*)` 후행 공백 워드바운더리 누락 — Warning.
4. 스킬 frontmatter `hooks:` 블록 검증 부재 — `_check_hooks_block`을 스킬 frontmatter에도 적용(경로 해석은 스킬 디렉터리 기준, `once: true`는 이 위치에서만 유효).
의도적 미구현: stop_hook_active 소스 grep, 복합 명령 allow-rule 분석(불건전 휴리스틱).

## 제약 수치 (설계를 구속하는 실측값)

- `SKILL.md`는 2,644단어 / 자체 예산 `WORD_BUDGET = 2650`(`tests/test_skill_surface.py:190`) — **잔여 6단어**. SKILL.md를 건드리는 PR은 순증 불가, 순감 또는 유지만 가능.
- interview.md 3,222단어 + re-entry.md 1,094단어. 병합 후 목표 ~3,900단어(중복 제거 후). 레퍼런스 파일에는 린트 상한 없음(500줄 규칙은 SKILL.md 본문 전용).
- **병합의 의식적 회귀**: 병합 전 sync는 re-entry.md(~1,094단어)만 읽는 최저비용 모드였다(v2/WS8의 대표 성과, `test_sync_path_does_not_require_interview_md`가 그 속성을 검증). 병합 후 sync도 전체 파일(~3,900단어)을 읽는다. 이 비용은 v6 결정 로그와 CHANGELOG Known limitations에 **숫자와 함께 명기**한다 — 순수 개선으로 포장하지 않는다.
- 이 레포 자신에는 `.claude/settings.json`이 없어 신규 검사 F1–F3의 자기 오탐 위험 없음. 현재 v0.4.0 릴리스 완료, 이번 세대는 **v0.5.0**.

## 구현 계획 (PR 시퀀스)

파일 단일 소유 원칙(v3 규칙): 두 PR이 같은 파일을 건드리지 않도록 배열. `agents.md`는 PR2→PR3 순서 필수, `workflows.md`는 PR1→PR3, `SKILL.md`·`interview.md`·`re-entry.md`·`e2e-testing.md`는 PR4만, `validate_harness.py`는 PR5만, `harness-spec.md`는 PR6만.

**재작성 라이선스(사용자 지시)**: 보존 단위는 문장이 아니라 **claim**이다. 병합·트림은 이어붙이기나 부분 삭제가 아니라, v3의 claim-loss audit 기법(D38/D39)으로 진행한다 — 원본에서 claim 목록을 먼저 추출하고, 그 목록을 사양 삼아 하나의 완결된 문서로 새로 쓰고, 완성본을 목록과 대조해 손실 0을 확인. 판단 기준: **수정 후 이음새가 보이면 그 파일은 전면 재작성한다.** 1차 재작성 확정: interview.md(병합 — 신선한 빌드와 재진입이 한 생애주기로 읽히는 구조로 신규 집필). 재작성 후보: skills.md(독트린 컷 후 골격 어색 시), agents.md(헤더 수정+섹션 신설 중첩 시 — 이 경우 PR2·PR3을 하나로 합쳐도 됨, 단일 소유 원칙 유지 목적).

| # | 범위 | 완료 판정 |
|---|---|---|
| PR0 | `docs/plan/v6/00-overview.md` 골격 + revision table(한국어, v5 형식). retire 대상은 **v2의 D22**(re-entry.md 분리 — v1이 아님, v1엔 그 파일이 없었음) | 파일 존재, revision table에 D22 인용과 병합 근거 명기 |
| Gate A | codex(gpt-5.6-sol, xhigh, read-only 샌드박스)로 플랜 문서 적대 검토: "검증 소스로 추적 안 되는 주장 전부, 두 PR이 같은 파일을 건드리는 지점 전부" | 발견 사항을 PR0에 반영 후 PR1 착수 |
| PR1 | 독트린 4중 진술 제거 + skills.md 400→500 수정. 대상: skills.md, claude-md-and-rules.md, workflows.md (SKILL.md는 정본이므로 무편집). 포인터는 각 프레임의 정본 구절을 **인용 앵커**로 통일해 가리킴: "Conviction over compliance" / "Don't write what a capable model already knows"(gotcha) / "Prefer an interface over an instruction" — 명명 리스트 신설은 하지 않음(재진술 금지 + 예산 6단어; for-user-not-developer 프레임은 package-closure 검사가 소유하므로 산문 불요) | litmus 문장 고유 조각("could the model" + "re-derive") grep이 SKILL.md 1곳만 히트; skills.md:26이 500; 테스트 green; 각 파일에 컴포넌트 고유 적용례 ≤1문장 + 앵커 구절로의 SKILL.md 포인터 |
| PR2 | agents.md 고아 헤더 2개 수정 + `NoOrphanedHeadingsTests` 회귀 테스트(references/*.md 전체 스캔, red→green) 추가 | 헤더 직후 본문 없이 다음 헤더가 오는 곳 0개; 신규 테스트가 수정 전 red |
| PR3 | agents.md에 4방향 오케스트레이션 섹션 신설(인트로 제목도 orchestration 포함으로), workflows.md에 교차 포인터 1줄 | 판별 기준("누가 다음 실행을 결정하나"), `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`, 파일 격리 없음/소유권 분할, 팀원 간 직접 메시지, 플러그인 workflows 배포 불가 각각이 substring 테스트로 고정되고 PR 본문에 `.tmp/docs_claude` 출처 행 명기 |
| PR4 | **모드 전면 병합 — interview.md 전면 재작성**: 두 원본(interview.md+re-entry.md)에서 claim 목록 추출 → 빈 페이지에서 하나의 완결 문서로 신규 집필(신선한 빌드 I1–I5와 재진입 extend/improve/sync가 한 생애주기의 두 국면으로 읽히는 구조, ablation 프로토콜·status 표 포함, 문장이 아닌 claim 보존) → claim-loss audit로 손실 0 확인. re-entry.md 삭제, SKILL.md 루프 분기 축약(순감), G1(e2e 날짜 3중 중복→run_e2e.py docstring 단일 소유) + G2 트림 + **런타임 재전달 재기술 제거**(AskUserQuestion 스키마 제한 재기술 삭제; workflows.md의 Date.now 산문 정리는 파일 소유권상 PR1에 편입) 동봉 | `test -f references/re-entry.md` 실패; 스킬 디렉터리 내 "re-entry.md" grep 0건; 루프 재작성 시 남는 화살표마다 인라인 why 유지(이유 없는 라우팅 팔이 유일한 rail이었고 이번에 제거됨 — 새로 만들지 않기); `wc -w SKILL.md` < 2650; `test_sync_path_does_not_require_interview_md`는 **삭제**(반대 속성을 검증하므로 경로만 바꾸면 거짓 통과); `SubtractionTests`의 `"## Improve"` split을 `"### Improve"`로 갱신; validate --strict exit 0 |
| PR5 | validate_harness.py 신규 검사 4건, **tdd 스킬로 픽스처+red 테스트 먼저**: F1 `defaultMode:"auto"` 프로젝트 스코프 경고(W), F2 Write/Glob/NotebookEdit/MultiEdit path-rule(**Error** — 유효 해석 전무), F3 `Bash(ls*)` 후행공백(W), F4 스킬 frontmatter hooks 검증(`_check_hooks_block`에 `base_dir` 파라미터 리팩터, 스킬 디렉터리 기준 경로 해석, `${CLAUDE_PROJECT_DIR}` 리터럴 사용 시 W; 기회적 추가인 `once:true` 컨텍스트 오용 W는 리뷰에서 축소 필요 시 1순위 컷) | 검사마다 red→green 테스트 + 오탐 가드 픽스처(`Edit(docs/**)` 무경고, `Bash(ls *)` 무경고, 올바른 스킬 hooks 무경고); 전체 suite green; 이 레포 자체에 --strict exit 0 |
| PR6 | harness-spec.md 갱신: B9 행 `retired`(사유: B8로 병합), B8 설명 확장, Design rationale에 결정별 1항목(sync 비용 숫자 포함), Change history "v6 (improve)" 1줄 | `audit_harness.py` 드리프트 0 |
| Gate B | codex로 전체 디프 적대 검토: "문서 출처가 실제로 지지하지 않는 주장, 남은 독트린 자기 재진술, **런타임 표면(도구 스키마·--help·검사 메시지)이 이미 전달하는 정보의 잔존 재기술**" | 발견 사항을 PR6에 교정 반영 후 종결 |
| PR7 | v0.5.0 릴리스: CHANGELOG(`[0.4.0]` 형식 그대로 — Added/Changed/Fixed/Known limitations, sync 비용 회귀를 **명명된 수용 트레이드오프**로 기재), plugin.json·marketplace.json 버전, 태그 | 두 plugin 파일 버전 0.5.0, `gh release list`에 태그 표시 |

### re-entry.md 참조 전수 목록 (PR4에서 전부 해소 — Hard line 1)

`SKILL.md:34,36`(루프) · `e2e-testing.md:144`(라우팅 표 포인터) · `interview.md:102,139`(스텁·status 포인터) · `tests/test_skill_surface.py:214-216, 220-221, 481`(테스트 3건 — 삭제/개명/repoint) · `harness-spec.md` B9 행(PR6). `docs/plan/` 역대 세대와 `docs/wiki/reference/interview-and-reentry.md`는 역사 기록 관례상 무편집(위키는 후속 과제로 표시만).

### PR3 신설 섹션 내용 골격 (전 주장 출처 필수)

1. 판별 기준: 다음 실행 결정 주체 — Claude 턴별(subagents) / 사용자(agent view) / 리드 에이전트(teams) / 스크립트(workflows).
2. 각 선택지가 하네스에 요구하는 생성물: subagents→`.claude/agents/*.md`; agent view→**생성물 없음**(습관, CLAUDE.md 한 줄이면 충분); teams→**보통 생성물 없음**(런타임에 형성; 재사용 팀원 역할만 일반 subagent 파일로 사전 작성 가치); workflows→`.claude/workflows/*.js`.
3. teams가 실제로 맞는 경우(기존 안티패턴 줄의 정직한 짝): 독립적·토론-반박형 작업 — 다각 리서치/리뷰, 경쟁 가설 디버깅, 레이어별 소유 기능 작업.
4. 비용·역학: 실험 기능(기본 비활성), 토큰 고비용, 파일 격리 없음(소유권 분할 필요), 팀원 간 직접 메시지, 권한은 스폰 시 리드 모드로 고정.
5. 배포 함의: 플러그인은 workflows 배포 불가 + 플러그인 subagent는 hooks/mcpServers/permissionMode 탈락 → 이 필드들에 의존하는 하네스는 레포 `.claude/` 트리로 배포.

## 결과 디렉터리 구조

파일 구조 변화는 re-entry.md 삭제 하나뿐(references 9→8개). 확장되는 파일은 interview.md(병합, ~3,900단어)와 agents.md(오케스트레이션 섹션)뿐이고, skills.md·claude-md-and-rules.md·workflows.md·e2e-testing.md·SKILL.md는 전부 감산. scripts는 파일 구성 무변경(validate_harness.py만 검사 4건 확장). 스킬 밖: docs/plan/v6/ 신설, tests 회귀·픽스처 추가, harness-spec.md B9 `retired`, CHANGELOG `[0.5.0]`.

## 검증

- 각 PR: `python .claude/skills/harness-creator/scripts/validate_harness.py --path .` exit 0, `pytest` green(236+ 테스트), 새 픽스처 포함.
- 마크다운: 하드랩 금지, 삭제된 re-entry.md를 가리키는 포인터 0건(grep으로 확인 — Hard line 1).
- harness-spec.md Change history를 같은 패스에서 갱신(Hard line 3).
- codex 게이트 2회(플랜 확정 전, 구현 후 전체 디프).
- 마무리: 메모리 파일의 "v3가 현행" 정보를 v6로 갱신.

## 설계 에이전트의 브리프 반박 4건 (수용됨)

1. re-entry.md 분리는 v1이 아니라 **v2의 D22**(WS8)가 만든 것 — revision table은 D22를 인용해야 함. 오인용은 이 감사가 잡으려는 바로 그 오류.
2. F2(무효 path-rule)는 Warning이 아니라 **Error** — hooks.md가 "파싱은 되지만 아무것도 보호하지 않는다"고 단정하는, 유효한 대안 해석이 전무한 케이스. 기존 missing-hook-script Error와 동형.
3. F4의 `once:true` 컨텍스트 오용 경고는 감사 요구 밖의 기회적 추가 — 리팩터가 공짜로 만들어주면 넣되, 축소 필요 시 1순위 컷.
4. SKILL.md 라우팅 표에 teams 행 **추가 안 함** — 잔여 예산 6단어, teams는 실험 기능이고 보통 생성물이 없음. 4방향 결정은 agents.md가 전담(SKILL.md는 이번 세대에서 PR4 단일 터치 유지).
