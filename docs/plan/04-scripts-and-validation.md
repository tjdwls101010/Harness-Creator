# 04 — CLI 스크립트 스펙과 검증 설계

공통 규약 (D9):
- Python 3.10+ stdlib-only (외부 의존성 0 — json, argparse, pathlib, re, subprocess, tomllib 불필요).
- 이 문서의 호출 예시는 간결성을 위해 `scripts/...`로 표기하지만, **SKILL.md에 싣는 실제
  호출 서술은 `${CLAUDE_SKILL_DIR}/scripts/...` 기준**이다 (02 문서 §1 — cwd는 대상 프로젝트).
- 모든 스크립트는 `--help` 완비, 사람용 텍스트 출력 기본 + `--json` 머신 출력 지원.
- exit code: 0 = 통과/성공, 1 = 검사 실패 발견(린트 오류 등), 2 = 스크립트 자체 오류(잘못된 인자 등).
- YAML frontmatter 파싱: 정규 YAML 파서가 stdlib에 없으므로 **단순 키:값 + 리스트만 지원하는
  보수적 파서를 utils로 공유**하고, 파싱 불확실 시 "검증 불가" 경고로 처리(오탐 금지).
  (skill-creator의 이중 파서 실수 — utils는 수제, validate는 YAML — 를 반복하지 않는다.)

## 1. `validate_harness.py` — 결정론적 린트 (1층 검증)

```
python scripts/validate_harness.py --path <target-repo> [--json] [--strict]
```

검사 항목 (오류 E / 경고 W):

| 대상 | 검사 |
|---|---|
| `.claude/settings.json`(.local 포함) | E: JSON 파스 실패. E: hooks 구조(이벤트명 실존, matcher 없는 이벤트에 matcher, 핸들러 필수 필드, 존재하지 않는 handler type). W: matcher에 정규식 문자가 있는데 앵커 없음. W: 같은 도구에 updatedInput 훅 2개. W: `if` 필드를 비도구 이벤트에 사용(절대 실행 안 됨). E: 훅 command가 참조하는 스크립트 파일 미존재 |
| permissions | E: 알 수 없는 도구명(canonical tool list 대조 — research/research-gap-report.md §2). W: auto 모드에서 드롭되는 광역 allow (`Bash(*)` 등) |
| skills | E: SKILL.md 없는 스킬 디렉토리. E: frontmatter 파스 실패(자동 트리거 사망 고지). W: description 없음/1,536자 초과. E: 본문 내 상대 링크 대상 미존재(죽은 참조). W: 500줄 초과. E: scripts/ 내 파일을 본문이 참조하는데 미존재 |
| agents | E: name/description 누락. E: 같은 scope 내 중복 name. W: 알 수 없는 model 값. E: tools의 알 수 없는 도구명 |
| workflows | E: `export const meta` 리터럴 부재/name 누락. E: `Date.now()`·`Math.random()` 호출 검출. W: node 실행 가능 시 문법 검사 — 반드시 ESM 강제로: `node --input-type=module --check < 파일` 또는 임시 `.mjs` 복사 후 `--check` (맨몸 `node --check`는 대상 프로젝트 package.json이 `"type": "commonjs"`면 유효한 워크플로우의 `export`에서 오탐) (node 불가 시 skip 고지) |
| rules | E: paths glob 문법 오류. W: paths 없는 rule(launch 로드됨을 고지) |
| CLAUDE.md | W: 200줄 초과. E: `@import` 대상 미존재. W: 컴포넌트 인벤토리 나열 감지 — 단, 03 문서가 권장하는 "핵심 스킬의 트리거 규칙 한 줄" 백업과 충돌하지 않게: 맨몸 이름 나열(불릿 목록의 연속 이름)만 플래그하고, 트리거 문구가 있는 줄("...할 때 /x를 사용")은 면제 |
| harness-spec.md | W: 부재(생성 하네스면 있어야 함). W: spec의 component 목록 vs 실제 파일 drift |
| 교차 | E: settings.json 훅이 참조하는 `.claude/hooks/*` 실행권한 없음. W: 스킬 description 총량이 목록 예산 초과 추정 |

- `--strict`: W도 exit 1로 취급 (CI용).
- harness-creator는 생성 직후 항상 이 스크립트를 돌리고 **오류 0까지 수정 후 완료를 선언**한다
  (SKILL.md hard line). revfactory의 "체크리스트만 있고 강제 없음" 실패에 대한 직접 대책.

## 2. `audit_harness.py` — 재진입 Phase 0 인벤토리

```
python scripts/audit_harness.py --path <target-repo> [--json]
```

출력 (마크다운 기본):
- 컴포넌트 인벤토리: 타입별(claude-md/rules/skills/hooks/permissions/agents/workflows)
  이름·description 요약·크기·mtime.
- harness-spec.md 유무 + spec 대비 drift(스펙에 있는데 파일 없음 / 파일 있는데 스펙에 없음).
- user-scope 충돌 후보: `~/.claude/CLAUDE.md`·`~/.claude/skills`에 같은 이름 존재 여부.
- 위생 신호: 중복 에이전트 name, 죽은 링크 수(validate 요약 재사용), 훅 스크립트 실행권한.
- 결론 힌트: "신규 / 확장 / 개선 / 동기화" 모드 제안 근거.

클로드가 직접 ls/Read로 해도 되지만, 스크립트화하면 (a) 일관된 밀도 높은 요약 (b) 컨텍스트
절약 (c) drift 계산의 정확성이 보장된다.

## 3. `test_hook.py` — 훅 단위 테스트

```
# settings에서 특정 이벤트에 매치되는 훅을 찾아 샘플 입력으로 실행
python scripts/test_hook.py --settings .claude/settings.json \
    --event PreToolUse --tool Bash --input-field command="rm -rf /" [--json]

# 또는 커맨드 직접 지정 + 입력 파일
python scripts/test_hook.py --command .claude/hooks/guard.sh --event PreToolUse --input sample.json
```

동작:
1. 이벤트별 샘플 입력 JSON 템플릿 내장(공통 필드 + 이벤트별 필드; `--input-field k=v`로 덮어씀).
2. matcher 평가 재현: 어떤 훅 그룹이 매치되는지 표시(exact vs regex 판정 로직 포함 —
   문서의 matcher 규칙 그대로 구현).
3. 훅 실행(stdin으로 JSON 주입) → exit code·stdout·stderr 수집.
4. **의미 해석 출력**: "exit 2 → 이 이벤트에서는 도구 호출이 차단되고 stderr가 클로드에게
   전달됩니다" / "exit 0 + permissionDecision: deny → 차단" / "exit 1 → 차단되지 않음(주의:
   의도가 차단이었다면 exit 2로)" 식으로 이벤트별 계약에 비춰 설명.
5. `--matrix` 모드: settings의 전체 훅 × 대표 도구명으로 매치 매트릭스만 출력(실행 없이).

훅은 실세션 없이 검증하기 어렵다는 문제의 해답이며, 생성 훅의 납품 기준
("test_hook 통과")을 SKILL.md에 명시한다.

## 4. `run_e2e.py` — headless 세션 런처

```
python scripts/run_e2e.py --project <target-repo> --prompt "..." [--prompt-file f] \
    [--model <id>] [--timeout 300] [--out <dir>] [--json] [--permission-mode acceptEdits] \
    [--isolate]   # --isolate: 프로젝트를 임시 복사본으로 격리 후 실행
```

동작:
1. `claude -p <prompt> --output-format stream-json --verbose` 를 대상 프로젝트 cwd에서 실행.
   **`CLAUDECODE` 환경변수 제거**(세션 중첩 허용 — skill-creator의 검증된 기법).
2. stream-json을 파싱해 구조화 결과 저장: 사용 도구 시퀀스, Skill 호출 여부(트리거 감지),
   훅 발화 흔적(hook error/feedback 이벤트), 최종 응답, 토큰·시간.
3. `--out`에 transcript.jsonl + summary.json 기록 → 채점 에이전트가 읽는 대상.
4. `--isolate`: 쓰기 작업이 있는 시나리오용. 임시 디렉토리에 프로젝트 복사(또는
   git worktree) 후 실행해 원본 오염 방지.

**[검증 필요-V3]** headless 모드의 권한 처리: `-p`에서 PermissionRequest 훅은 발화하지 않고,
비승인 도구는 멈추거나 실패한다. `--permission-mode`, `--dangerously-skip-permissions`,
allowlist 조합 중 어떤 것이 e2e에 적합한지 구현 세션에서 실측하고 e2e-testing.md에 기록할 것.
(격리 복사본 + skip-permissions가 유력하나 실측 우선.)

## 5. e2e 검증 설계 (2층 검증, `references/e2e-testing.md`)

### 형태

harness-creator가 스펙의 Validation 시나리오로부터 **dynamic workflow를 그 자리에서 작성**해
실행한다(고정 워크플로우 파일을 스킬에 싣지 않는다 — 시나리오가 매번 다르므로 D12 원칙상
즉석 구성이 맞다. e2e-testing.md에 워크플로우 골격 예시를 문서로 포함).

```
Phase Run:    시나리오별 agent가 Bash로 run_e2e.py 실행 (pipeline, 시나리오당 1개)
Phase Grade:  각 transcript를 채점 agent가 판정 (트리거 적중? 훅 발화? 행동 준수? 산출물 품질?)
              — 판정은 증거 인용 필수, 표면적 준수는 FAIL (skill-creator grader 독트린 승계)
Phase Report: 종합 + 실패 항목별 수리 제안
```

- 시나리오 수 기본 2~4개(작게 시작해 깊게 본다 — skill-creator 독트린), 사용자 요청 시 확장.
- 모델: 기본은 사용자의 현재 모델(행동 충실도 — 싼 모델로 테스트하면 실사용을 대표하지 못함).
  `--model`로 비용 절감 옵션 제공하되 트레이드오프 고지.
- 비교 기준선(with/without 하네스 A/B)은 v1에선 선택 기능: 신규 생성 시 "하네스 없는
  기본 동작"이 궁금할 때만. 개선 모드에선 old/new 비교가 더 유용.
- **워크플로우 불가 환경 폴백**: 같은 순서를 서브에이전트 순차 실행으로 — e2e-testing.md에
  두 경로 모두 서술.

### 검증 가능한 단언 유형 (e2e-testing.md에 수록)

| 유형 | 판정 방법 |
|---|---|
| 스킬 트리거 적중/오발 | transcript의 Skill/Read tool_use에 스킬명 등장 여부 (near-miss 프롬프트 포함) |
| 훅 발화·차단 | 훅의 부수효과(로그 파일, 차단된 도구 호출 후 클로드의 반응) + transcript의 hook 이벤트 |
| 행동 준수 | 채점 agent가 기대 행동 vs transcript 대조 (증거 인용) |
| CLAUDE.md 지식 반영 | 프로젝트 사실 질문에 대한 답의 정확성 |
| 산출물 | 파일 생성/수정 결과물 검사 (격리 복사본에서) |

### 피드백 라우팅 테이블 (실패 → 수리 대상; SKILL.md 또는 e2e-testing.md에)

| 증상 | 수리 대상 |
|---|---|
| 스킬이 트리거 안 됨 / 오발 | description (경계 서술 보강) |
| 트리거됐지만 행동이 틀림 | 스킬 본문 (why 보강 — 규칙 추가가 아니라 원칙 강화가 우선) |
| 항상 지켜야 할 규칙이 무시됨 | CLAUDE.md 문구 → 그래도 안 되면 훅으로 승격 (라우팅 재결정) |
| 훅이 안 발화 | matcher/이벤트 선택 (test_hook으로 재현) |
| 훅이 과발화(정상 작업 차단) | matcher 협소화 또는 경고로 강등 |
| 에이전트가 규칙 무시 | Explore/Plan의 CLAUDE.md 미로드 확인 → 위임 프롬프트/커스텀 에이전트로 |
| 세션이 느림/비쌈 | 훅 수·타임아웃, CLAUDE.md 길이, 스킬 description 총량 점검 |

수리 후 재실행은 실패 시나리오만(전체 재실행 비용 방지). 결과는 spec의 Validation 섹션에 기록.
