# 05 — references/ 인벤토리와 소스 맵

각 파일의 목표 분량은 **밀도 기준**이지 상한이 아니다 — "이 문단이 사라지면 무엇이 달라지나"
감사를 통과하는 내용만 남긴다. 모든 파일 영어(D7). 작성 시 1차 소스에서 사실을 재확인한다.

| 파일 | 내용 개요 | 목표 분량 | 1차 소스 |
|---|---|---|---|
| `claude-md-and-rules.md` | 03 문서 §1: advisory 본질, 200줄, 포인터 정책, 내용 자격 심사, rules 라우팅(paths glob), 로딩 시맨틱(세션 시작 1회·concatenate·lazy 하위), auto 모드 상호작용, 좋은/나쁜 CLAUDE.md 대비 예시 1쌍 | ~150줄 | `.tmp/docs_claude/01-getting-started/05-use-claude-code/01-memory.md`, `06-best-practices.md`, `04-core-concepts/02-extend-claude-code.md`; research/research-docs-sweep.md §2, research-gap-report.md §4 |
| `skills.md` | 03 문서 §2: conviction over compliance(승계·압축), gotcha 독트린, PD 최적점, description=트리거 + near-miss 경계, frontmatter 필드 실무 표(전 필드 아님 — 판단이 필요한 것만), 스크립트=CLI 원칙, 스킬 수 비용, 좋은 스킬 구조 예시 1개 | ~200줄 | `.tmp/skill-creator/SKILL.md` §2·3(사상 승계), `.tmp/docs_claude/02-build-with-claude-code/03-skills/01-extend-claude-with-skills.md`; research/research-skill-creator.md, research-docs-sweep.md §1 |
| `hooks.md` | 03 문서 §3·4: 훅 자격 심사, permission 쌍 원칙, exit code 계약, matcher 함정, 우회 경로(@참조·Bash 편집)와 보완, additionalContext 작성법, 이벤트 선택 요약표(30개 이벤트 한 줄씩 — hooks-events.md로의 라우터), permissions 문법·평가 순서·trust 게이트, 대표 레시피 3개(보호 경로 차단 / post-edit 포맷 / Stop 검증 게이트) | ~250줄 | `.tmp/docs_claude/05-reference/07-hooks-reference.md`, `02-build-with-claude-code/06-automation/01-automate-with-hooks.md`, `04-configuration/01-settings-and-permissions/02-permissions.md`; research/research-hooks-reference.md |
| `hooks-events.md` | 30개 이벤트 전수 테이블(1차 소스의 이벤트 목록 전부가 기준): 발화 시점 / matcher / 주요 입력 / 결정 채널 / 대표 용도 / 버전 주의. 대표 8개 이벤트는 입출력 JSON 예시 포함 | ~300줄 (테이블 위주) | 위와 동일 |
| `agents.md` | 03 문서 §5: 에이전트 자격 심사(개수=비용), 본문=시스템 프롬프트 전체 교체, frontmatter 실무 표, Explore/Plan의 CLAUDE.md 미로드와 3가지 보완, skills 프리로드 비용, 좋은 에이전트 정의 예시 1개 | ~120줄 | `.tmp/docs_claude/02-build-with-claude-code/01-agents-and-parallel-work/01-create-custom-subagents.md`; research/research-dynamic-workflows.md §3 |
| `workflows.md` | 03 문서 §6: 사전 정의 vs 즉석 판단 기준(D12), 얇은 워크플로우 원칙, 파일 형식·결정론 제약, acceptEdits·allowlist 함정, 가용성 게이트와 폴백 서술법, fan-out→verify→synthesize 기본형, 얇은 워크플로우 예시 1개(주석 포함) | ~150줄 | `.tmp/docs_claude/02-build-with-claude-code/01-agents-and-parallel-work/04-dynamic-workflows.md`; research/research-dynamic-workflows.md |
| `interview.md` | 02 문서 §4·5: 단계별 목적·질문 소재·게이트, AskUserQuestion 제약과 운영 규칙, 숙련도 캘리브레이션, 발산은 대화·수렴은 선택지 원칙, 재진입 모드별 변형, harness-spec.md 전체 템플릿 | ~200줄 | 02-skill-design.md(이 계획), revfactory의 Phase 0·proficiency 아이디어(research/research-harness-revfactory.md) |
| `e2e-testing.md` | 04 문서 §5: 2층 검증 구조, run_e2e 사용법, 즉석 워크플로우 골격 예시, 단언 유형 표, 채점 agent 프롬프트 골격(증거 인용·표면 준수 FAIL), 피드백 라우팅 테이블, 폴백 경로, headless 권한 처리 실측 결과(V3 해소 후 기록), CLAUDECODE 제거·stream-json 파싱 등 headless 기법, **인터뷰 자체는 e2e 불가 고지**(AskUserQuestion은 headless/서브에이전트 불가 — R6, 도그푸딩=수동 검증), description 자동 튜닝(train/test 홀드아웃)은 v1 범위 밖이며 필요 시 재도입 가능하다는 한 줄 언급 | ~200줄 | `.tmp/skill-creator/scripts/run_eval.py`(기법 지식), `.tmp/skill-creator/agents/grader.md`(채점 독트린); research/research-skill-creator.md §3 (skill-creator 스냅샷 부재 시 이 요약이 대체 소스) |

## 승계 지도 (.tmp/skill-creator → harness-creator)

코드 직접 재사용은 없다(D3). 지식 승계만:

| skill-creator 자산 | 승계처 | 승계 내용 |
|---|---|---|
| SKILL.md §2 (conviction over compliance, keep/cut, gotcha) | skills.md + SKILL.md 철학 섹션 | 사상 전체 — CLAUDE.md 작성에도 동일 적용 |
| SKILL.md §3 (PD 최적점, 분할 기준) | skills.md + 본 스킬 자체 구조 | 사상 전체 |
| SKILL.md §4 (질문을 많이 하라) | interview.md | 사상 — 인터뷰 프로토콜의 근거 |
| run_eval.py의 트리거 감지 | e2e-testing.md | 기법 지식: CLAUDECODE 제거, stream-json의 tool_use 파싱, 트리거 판정 |
| grader.md | e2e-testing.md 채점 골격 | 증거 인용 의무, 표면 준수 FAIL, 단언 자체 비판 |
| run_loop.py의 train/test·홀드아웃 | (v1 범위 밖) | 필요해지면 description 튜닝 자동화로 재도입 가능하다고 e2e-testing.md에 한 줄 언급만 |

## revfactory 승계/배격 지도

| 승계 | 반영처 |
|---|---|
| Phase 0 감사 + 신규/확장/유지보수 분기 | 운영 플로우 Phase 0 (D6) |
| 중복 생성 방지(기존 컴포넌트 재사용 우선) | audit_harness + 인터뷰 I2에서 기존 컴포넌트 제시 |
| CLAUDE.md 포인터 정책 | claude-md-and-rules.md + validate 경고 |
| 재실행 키워드를 description에 | skills.md (생성 스킬의 description 지침) |
| near-miss 트리거 테스트 | e2e-testing.md 단언 유형 |
| 숙련도 기반 어휘 조정 | interview.md |

| 배격 (안티패턴) | 대책 |
|---|---|
| 광고만 있고 없는 기능 | hard line: 모든 포인터는 실존 파일 (validate가 죽은 링크 검사) |
| 체크리스트만 있고 강제 없음 | validate_harness 오류 0이 완료 조건 (프로그래매틱 강제) |
| 실험적 API 하드 의존 | Agent Teams 불사용, workflows는 폴백 동반 |
| 고정 형태 팀(항상 4-5 에이전트) | 에이전트 자격 심사 — 필요 증명된 역할만 |
| 백과사전 지식을 스킬로 재생성 | skills.md의 "모델이 이미 아는 것 금지" 원칙 |
