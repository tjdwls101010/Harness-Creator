# harness-creator 구현 계획 — 개요

> 이 문서 세트는 계획 세션(2026-07-05)에서 사용자와의 합의를 통해 확정된 구현 계획이다.
> 구현은 별도의 새 세션에서 이 문서를 읽고 진행한다. **이 계획이 곧 구현 세션의 명세다.**

## 1. 목표

`.claude/skills/harness-creator` — 사용자와 수십 회의 AskUserQuestion 논의를 통해,
사용자의 의도에 맞는 **하네스(harness)를 통째로 설계·생성·검증·유지보수해주는 메타 하네스**.

- `ai-agent = model + ai-harness`. 하네스는 모델의 지능과 창의성을 유지하면서 역량을 추가하는 레이어.
- 생성 대상: **대상 프로젝트 repo 내부**(in-repo). 루트 `CLAUDE.md` + `.claude/` 트리.
- 생성 범위: **CLAUDE.md, .claude/rules/, .claude/skills/, hooks+permissions(.claude/settings.json), .claude/agents/, .claude/workflows/**.
  (.mcp.json, output-styles, statusline, loop.md는 v1 범위 밖 — 필요 시 인터뷰에서 언급만.)

## 2. 핵심 설계 철학 (사용자 합의 사항)

1. **원칙 중심, 밀도 우선.** 규칙 나열이 아니라 "왜 그 규칙이 좋은지"를 LLM이 체화하도록 쓴다.
   LLM이 이미 아는 것은 쓰지 않는다 — 중요한 내용이 묻히고 컨텍스트가 낭비된다.
2. **Progressive disclosure는 최적점이지 방향이 아니다.** 로드 시점이 다를 때만 분할한다.
   과분할은 라우팅 실패(필요한 지식을 못 찾고 누락)를 낳는다. 트레이드오프를 명시적으로 다룬다.
3. **코드는 파라미터를 받는 CLI.** 파라미터 없는 스크립트는 클로드의 도구가 될 수 없다.
4. **스킬은 사용하는 클로드의 관점에서 작성한다.** 개발 과정에서만 필요한 정보는 싣지 않는다.
5. **유연성이 위험한 지점은 hooks로 프로그래매틱하게 보장한다.** 강제는 hooks/permissions,
   권고는 CLAUDE.md/skills. (중요 정정: CLAUDE.md는 엄밀히 시스템 프롬프트가 아니라
   시스템 프롬프트 뒤에 주입되는 advisory user message다 — 강제력이 없으므로
   가드레일은 반드시 강제 레이어에 배치해야 한다. → `03-component-generators.md`)
6. **생성된 하네스가 dynamic workflow를 잘 활용하게 한다.** 사전 정의 vs 즉석 구성은
   harness-creator가 사용자 목적에 따라 판단하되, 판단 원칙을 스킬에 담는다.

## 3. 확정 결정 로그 (계획 세션 Q&A 결과)

| # | 결정 사항 | 내용 |
|---|---|---|
| D1 | 생성 범위 | 코어 3종(CLAUDE.md·skills·hooks/permissions) + agents + workflows + rules |
| D2 | 배포 대상 | in-repo: 대상 프로젝트 루트 CLAUDE.md + `.claude/` 트리 |
| D3 | skill-creator 관계 | 폐기. 아이디어·지식만 참조. 코드 직접 재사용 안 함. eval 파이프라인 대신 dynamic workflow 기반 e2e로 대체. headless 트리거 테스트 기법은 지식으로 references에 보존 |
| D4 | 인터뷰 구조 | 단계별 + 스펙 승인 게이트. 단, harness-creator가 상황에 따라 유연하게 조정 가능(단계는 지도이지 레일이 아님) |
| D5 | 검증 | 2층: (1) 결정론적 린트 — 생성 직후 항상, 무료 (2) dynamic workflow 기반 e2e — headless `claude -p` 세션 스폰 + transcript 채점, 사용자 동의 하에 실행 |
| D6 | 재진입성 | 지원. 호출 시 항상 기존 `.claude/` 감사부터 → 신규/확장/개선/동기화 모드 분기 (동기화 = spec-실제 drift만 해소하는 개선의 특수형) |
| D7 | 문서 언어 | harness-creator 자체 문서(SKILL.md, references/)는 영어. 인터뷰 대화는 사용자 언어. 생성 하네스의 언어는 인터뷰 항목 |
| D8 | 스펙 영속화 | `.claude/harness-spec.md`를 대상 프로젝트에 커밋 — 설계 의도·라우팅 결정·변경 이력의 단일 진실 공급원, 재진입 감사의 기준점 |
| D9 | 스크립트 세트 | `validate_harness.py`, `audit_harness.py`, `test_hook.py`, `run_e2e.py` — 전부 Python stdlib-only, 파라미터 받는 CLI |
| D10 | git 정책 | main에 직접 커밋+푸시 |
| D11 | 배포 전략 | 이 repo를 마켓플레이스+플러그인으로 구조화(구현 범위 포함). 개발/일상 사용은 `~/.claude/skills/`로의 심링크(수정 즉시 반영) |
| D12 | 사전 정의 워크플로우 | harness-creator가 사용자 목적 기준으로 판단. 원칙: 오케스트레이션 자체가 반복 산출물(형태 고정, args만 가변, 원버튼 실행)이면 `.claude/workflows/*.js`로 사전 정의(얇게 — 골격만 코드, 판단은 agent 프롬프트에); 작업 형태가 매번 다르면 CLAUDE.md/스킬의 자연어 지침으로 즉석 구성 유도 |

## 4. 성공 기준

구현이 끝났을 때 다음이 모두 참이어야 한다:

1. 임의의 프로젝트에서 `/harness-creator`(또는 자동 트리거)로 호출하면, 기존 `.claude/` 감사 →
   단계별 인터뷰(스펙 게이트 포함) → 컴포넌트 생성 → 린트 통과 → (동의 시) e2e 검증까지
   한 흐름으로 진행된다.
2. 생성된 하네스가 `validate_harness.py`를 오류 0으로 통과한다.
3. 하네스가 이미 있는 프로젝트에서 재호출하면 중복 생성 없이 확장/개선/동기화 모드로 분기한다.
4. 이 repo가 `/plugin marketplace add tjdwls101010/Harness-Creator`로 설치 가능하다.
5. 샘플 프로젝트 1개에 대한 도그푸딩 실행(감사→인터뷰→생성→검증)이 성공한 기록이 남는다.
6. revfactory의 실패를 반복하지 않는다: 광고만 있고 없는 기능 0개, 생성 산출물이
   자체 체크(린트)를 통과하지 못하는 경우 0개, 실험적 API(Agent Teams 등) 하드 의존 0개.

## 5. 문서 맵

| 문서 | 내용 |
|---|---|
| `00-overview.md` | (이 문서) 목표, 결정 로그, 성공 기준, 킥오프 가이드 |
| `01-architecture.md` | repo 구조, 스킬 파일 트리, 플러그인/마켓플레이스 패키징, 심링크 |
| `02-skill-design.md` | SKILL.md 설계, 레이어 라우팅 프레임워크, 인터뷰 프로토콜, 스펙 문서 포맷 |
| `03-component-generators.md` | 컴포넌트별 생성 원칙 + 반드시 인코딩할 gotcha 인벤토리 |
| `04-scripts-and-validation.md` | 4개 CLI 스펙, e2e 워크플로우 설계, 피드백 라우팅 |
| `05-references-inventory.md` | 스킬이 실을 references/ 목록·각 파일의 내용 개요·소스 맵 |
| `06-milestones.md` | 구현 마일스톤, 수용 기준, 리스크, 열린 항목 |
| `research/*.md` | 계획 세션의 리서치 원본 (docs_claude 스윕, hooks 전체 맵, skill-creator 분석, revfactory 비판적 분석, dynamic workflows, 갭 리포트) — 구현 중 사실 확인용 1차 자료 |

## 6. 구현 세션 킥오프 가이드

새 세션에서 아래 순서를 권장한다:

1. `docs/plan/` 전체를 읽는다 (research/는 필요할 때 참조).
2. `.tmp/docs_claude/`와 `.tmp/skill-creator/`가 존재하는지 확인한다 (gitignore되어 있으나
   로컬에 있음). docs_claude가 없으면 사용자에게 요청 — references 작성 시 1차 소스로 필요하다.
   skill-creator가 없으면 `docs/plan/research/research-skill-creator.md`(밀도 요약)를
   대체 소스로 사용해도 된다.
3. `06-milestones.md`의 M0부터 순서대로 진행한다.
4. 각 마일스톤 완료 시 커밋한다 (main 직접, 푸시 포함 — D10).
5. 계획과 실제가 충돌하면(예: 플러그인 스킬 네이밍 검증 결과가 예상과 다름),
   계획 문서를 고치고 사용자에게 보고한 뒤 진행한다. 계획은 명세이지 도그마가 아니다.

킥오프 프롬프트 예시:

```
docs/plan/을 읽고 harness-creator 구현을 시작해줘.
M0부터 순서대로 진행하고, 마일스톤마다 커밋해줘.
계획과 충돌하는 사실을 발견하면 멈추지 말고 계획 문서를 수정하고 보고해줘.
```
