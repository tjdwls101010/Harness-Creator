# 02 — SKILL.md 설계, 레이어 라우팅, 인터뷰 프로토콜, 스펙 문서

## 1. SKILL.md의 구성 (영어로 작성 — D7)

SKILL.md는 오케스트레이터다. 목표 ~350줄, 상한 500줄(공식 권장). 구성:

> **v2 개정(2026-08-03, D21/D26)**: 목표를 줄 수가 아니라 **토큰/단어 수**로 다시 정의했다.
> 상한은 5,000토큰(≈3,750단어, D21) — 넘는 부분은 auto-compaction 이후 조용히 사라진다.
> 실측 결과 SKILL.md는 2,411단어로 이 상한 안에 있다(`docs/plan/v2/00-overview.md` §4).
> **총 분량 자체는 hard gate가 아니다** — 게이트는 always-loaded 표면(< 2,500단어, D26)이다.
> "~350줄"이라는 목표는 v1 당시의 어림값으로 남겨두되, v2부터는 실측 단어 수가 기준이다.

### frontmatter

```yaml
---
name: harness-creator
description: >
  Design, generate, validate, and maintain a complete Claude Code harness
  (CLAUDE.md, rules, skills, hooks, permissions, agents, workflows) for a project
  through a structured interview. Use when the user wants to create or set up a
  harness / CLAUDE.md / skills / hooks for a project, improve or extend an
  existing .claude/ setup, or asks how Claude should be configured to work on
  their codebase. Also triggers on Korean requests like "하네스 만들어줘",
  "하네스 구성해줘", "클로드 세팅해줘".
---
```

- description이 유일한 트리거 메커니즘이다(본문의 "when to use"는 로드가 늦어 무용).
  현재 클로드는 under-trigger 경향이므로 트리거 쪽으로 기운 서술을 쓴다.
  다국어 트리거 문구(한국어)를 포함한다 — 사용자층 반영.
- `disable-model-invocation`은 두지 않는다(자동 트리거 + `/명령` 둘 다 허용).

### 본문 섹션 (순서대로)

1. **What a harness is & what this skill does** — 3~5줄. 하네스 = 모델의 지능을 유지하며
   역량을 더하는 레이어. 이 스킬은 감사→인터뷰→스펙→생성→검증→반복의 루프를 운영한다.
2. **Operating loop** — 아래 §2의 플로우. 각 단계에서 무엇을 하고 어떤 reference를 로드하는지.
3. **The layer-routing framework** — 아래 §3. 이 스킬의 심장부. SKILL.md에 직접 담는다
   (모든 경로에서 필요하므로 reference로 빼지 않는다).
4. **Authoring philosophy** — 원칙 중심 작성법의 핵심만 압축 (conviction over compliance,
   밀도, gotcha 우선, progressive disclosure는 최적점). 컴포넌트별 세부는 references로.
5. **Interview protocol summary** — 단계 목록 + 스펙 게이트 규칙 + 유연성 원칙.
   상세(단계별 질문 설계, AskUserQuestion 제약)는 `references/interview.md`.
6. **Scripts** — 4개 CLI의 용도와 호출 시그니처 요약. "언제 어떤 스크립트를 돌리는가."
   **모든 스크립트 호출은 `${CLAUDE_SKILL_DIR}/scripts/...` 기준으로 서술한다** — cwd는
   대상 프로젝트이고, 플러그인 설치 시 스크립트는 플러그인 캐시에 있으므로 상대 경로
   `scripts/...`는 심링크/플러그인 어느 쪽에서도 동작하지 않는다.
7. **Hard lines** — 광고만 하고 안 만드는 것 금지(모든 포인터는 실존 파일로),
   생성물은 반드시 validate_harness 통과 후 완료 선언, 스펙 문서와 실제 파일의 동기화 유지.

> **v2 개정(D22, WS8)**: 5번 "Interview protocol summary" 섹션은 **삭제됐다**. 근거는
> §5의 인터뷰 로드 자체가 무조건적이었다는 감사 결과(모든 호출이 `interview.md`를 로드해
> always-loaded 표면이 4,833단어였다) — 요약 섹션을 SKILL.md에 남겨두는 것 자체가 그
> 무조건 로드를 강화하는 방향이었다. 대신 SKILL.md의 **Operating loop**(§2)가 Phase 0에서
> 직접 분기한다: `new` → `references/interview.md`를 로드해 다섯 단계를 그대로 실행,
> `extend`/`improve` → 먼저 `references/re-entry.md`를 로드하고 거기서 다시 보내는 단계만
> `interview.md`를 연다, `sync` → `references/re-entry.md`만 읽고 `interview.md`는 아예
> 열지 않는다(sync에는 I1-I5 순회가 없다). 그 결과 SKILL.md의 본문 섹션은 6개로 줄었다
> (What a harness is / Operating loop / Layer-routing framework / Authoring philosophy /
> Scripts / Hard lines). 레이어 라우팅 판단 원리도 §3의 서술처럼 세 가지가 아니라
> **네 가지 질문**이 됐다 — "누가 필요로 하고 누가 쓰는가"(개인/팀 스코프, `CLAUDE.local.md`
> 목적지)가 추가됐다(D17). 상세는 `docs/plan/v2/00-overview.md` D22·D17, 그리고
> `.claude/skills/harness-creator/references/re-entry.md`(신규 9번째 reference).

### 작성 스타일 규칙 (구현 세션이 지킬 것)

- 모든 지시는 what + why + 구체적 그림을 갖춘다. why만으로 지시를 재유도할 수 있는지 테스트.
- 유능한 모델이 이미 아는 것(예: "YAML은 들여쓰기가 중요하다")은 쓰지 않는다.
- 시나리오 열거 대신 2~3개 사례를 생생하게 + 원칙 서술로 마무리.
- 숫자에는 근거와 이탈 조건을 함께 쓴다("200줄 이하 — 길수록 준수율이 떨어진다.
  단 대규모 모노레포에서 rules로 분할한 후에도 넘치면 넘겨도 된다" 식으로).
- **문장 중간 인위적 줄바꿈(하드 랩) 금지.** 줄바꿈은 문장·목록 항목·단락 경계에서만.
  근거: 컬럼 폭 맞춤 랩은 Edit 도구의 문자열 매칭과 diff 가독성을 해치고, 렌더러가 어차피
  soft wrap하므로 이득이 없다. (SKILL.md·references 전체, 그리고 생성 산출물에도 동일 적용 — 03 문서)

## 2. 운영 플로우 (Operating loop)

```
호출
 └─ Phase 0. 감사 (항상)
     ├─ python "${CLAUDE_SKILL_DIR}/scripts/audit_harness.py" --path . 실행 → 기존 컴포넌트 인벤토리
     ├─ .claude/harness-spec.md 존재 여부 확인
     ├─ 코드베이스 정찰 (빌드 시스템, 언어, 테스트 러너, 팀 규모 단서)
     └─ 분기: 신규 생성 / 확장(새 요구 추가) / 개선(기존 문제 수정) / 동기화(spec-실제 drift 해소)
        (D6의 4개 모드 — 동기화는 개선의 특수형으로, drift만 다루는 최소 인터뷰 경로)
 └─ Phase 1~N. 인터뷰 (§5, references/interview.md 로드)
     └─ 각 단계 종료 시 스펙 문서 갱신 → 사용자 승인 게이트
 └─ 생성 (references/<컴포넌트>.md 로드, 스펙 승인 후에만)
     ├─ 생성 전: protected-path 프롬프트 예고
     ├─ 컴포넌트 생성 (규모가 크면 dynamic workflow로 병렬 생성 가능 — 선택)
     └─ python "${CLAUDE_SKILL_DIR}/scripts/validate_harness.py" 실행 → 오류 0까지 수정
 └─ 검증 제안 (references/e2e-testing.md 로드)
     ├─ 훅: scripts/test_hook.py로 단위 검증 (무료, 항상 권장)
     └─ e2e: 사용자 동의 시 dynamic workflow 구성 → run_e2e.py로 headless 세션 스폰 + 채점
 └─ 마무리
     ├─ 스펙 문서에 변경 이력 기록
     ├─ CLAUDE.md 포인터 갱신 (인벤토리 나열 금지 — 03 문서)
     └─ 커밋 제안
```

- 모드별 인터뷰 차이: 개선 모드는 "무엇이 불편했나"부터, 동기화 모드는 drift 목록 확인부터.
- **유연성 원칙(D4)**: 단계는 지도다. 사용자가 이미 답한 것은 묻지 않고, 단순한 하네스(예:
  CLAUDE.md + 훅 2개)면 단계를 압축하고, "그냥 만들어줘"에는 최소 확인(목표 + 하드 제약)만
  받고 진행하되 스펙 게이트는 유지한다(스펙이 곧 합의 기록이므로 생략하지 않는다).

> **v2 개정(D22, WS8)**: 위 흐름도의 "Phase 1~N. 인터뷰"는 이제 **분기한다**, 무조건
> `interview.md`를 읽지 않는다. `신규` → `references/interview.md`를 로드해 다섯 단계
> 그대로. `확장`/`개선` → 먼저 `references/re-entry.md`를 로드하고, 거기서 재진입할
> 단계만 골라 `interview.md`로 보낸다. `동기화` → `references/re-entry.md`만 읽고
> `interview.md`는 열지 않는다 — "동기화는 개선의 특수형"이라는 위 서술은 D6에서 개정됐다:
> 동기화는 개선과 별개의 4번째 모드이고, drift를 **양방향**(스펙에 없는 파일 / 파일 없는
> `generated`·`validated` 행)으로 다룬다(`audit_harness.py` B6/B11 수정). 그리고 "마무리"
> 섹션의 순서가 실제로는 **스펙 변경 이력 → CLAUDE.md 포인터 갱신 → `validate_harness.py`
> 재실행 → 커밋 제안**이다 — 검증을 마지막에 두는 이유는 스펙·CLAUDE.md 갱신 자체가
> `@import`·200줄·인벤토리 나열 같은 린트 대상이라서, 그 편집이 만든 문제를 검증이
> 잡아내야 하기 때문이다. 위 흐름도에는 이 마지막 검증 패스가 누락돼 있었다. 상세는
> `.claude/skills/harness-creator/SKILL.md`의 Operating loop, `docs/plan/v2/00-overview.md` D22.

## 3. 레이어 라우팅 프레임워크 (스킬의 심장부)

인터뷰에서 수집한 각 "원하는 행동/지식/제약" 항목을 어느 레이어에 배치할지 결정하는 기준.
SKILL.md에 아래 표와 판단 원리를 함께 싣는다.

| 항목의 성격 | 레이어 | 이유 |
|---|---|---|
| 항상 관련 있는 프로젝트 사실·제약 (빌드 명령, 아키텍처 결정, 절대 규칙의 *존재* 고지) | CLAUDE.md | 매 요청 로드. 200줄 초과 시 준수율 하락 — 여기 넣을 자격은 "모든 세션에서 필요한가" |
| 특정 경로에서만 필요한 규칙 (예: `src/db/**`의 마이그레이션 규칙) | `.claude/rules/*.md` + `paths:` glob | 해당 파일을 만질 때만 로드 — CLAUDE.md 비대화 방지 |
| 요구가 있을 때만 필요한 절차·도메인 지식·플레이북 | skill | description으로 트리거, 본문은 호출 시 로드. 반복 프롬프트의 승격판 |
| 반드시 매번 일어나야/절대 일어나면 안 되는 행동 | hook (+ permission rule 쌍) | 권고 레이어는 강제력이 없다. hook deny는 bypassPermissions에서도 동작. 단 hook의 `if`는 fail-open이므로 하드 차단은 permission rule과 쌍으로 |
| 금지 도구·명령·경로 | `permissions.deny` | 클라이언트가 강제. 모델 행동과 무관하게 성립 |
| 컨텍스트를 많이 먹는 격리 가능한 역할 (리서치, 리뷰, QA) | `.claude/agents/*.md` | 본체 컨텍스트 보호 + 역할별 시스템 프롬프트/도구 제한 |
| 형태가 고정된 반복 오케스트레이션 (감사 파이프라인, 릴리즈 체크) | `.claude/workflows/*.js` | 결정론이 가치인 지점. 얇게: 골격만 코드, 판단은 agent 프롬프트 (D12) |
| 형태가 매번 다른 대규모 병렬 작업 | CLAUDE.md/스킬의 자연어 지침 ("이런 작업은 workflow로 fan-out하라") | 자연어 요청도 동일한 opt-in으로 인정됨. 사전 정의가 오히려 유연성 장벽 |

판단 원리(표 아래 서술로): **강제 vs 권고**(어겨도 되는 건 문서로, 어기면 안 되는 건 코드로),
**로드 시점**(항상/경로/요구/이벤트), **컨텍스트 비용**(CLAUDE.md는 매 요청, 스킬 description은
목록 예산 1%, hook은 출력이 없는 한 0 — additionalContext/stdout을 내면 그만큼 소비). 하나의 요구가 여러 레이어에 걸치면 분해한다 — 예: "커밋 전 테스트"는
훅(강제) + CLAUDE.md 한 줄(왜 그런 훅이 있는지 고지)로.

> **v2 개정(D17)**: 판단 원리에 **네 번째 질문**이 추가됐다 — "누가 필요로 하고, 누가 쓰는가"
> (모든 클론이 필요한가 vs 이 기기만 필요한가; 개발자가 쓰는가 vs 런타임에 클로드가 쓰는가).
> 이 개발자 한 명만 필요한 사실은 `CLAUDE.local.md`(gitignored, 결정론적)로 라우팅한다 —
> 팀 전체가 로드 비용을 지불하는 CLAUDE.md에는 두지 않는다. auto memory(`MEMORY.md`)는
> 이 표의 목적지가 **아니다**: 비결정적이라("Claude doesn't save something every session")
> 개발자에게 반드시 있어야 하는 사실을 거기 라우팅하는 건 안전하지 않다. 위 표와 SKILL.md의
> 라우팅 표는 이제 서로 드리프트한 채로 두지 않는다 — SKILL.md가 유일한 소스이고, 이 표는
> 그 시점의 설계 기록으로 남긴다. 상세는 `docs/plan/v2/00-overview.md` D17, D26 §4.

## 4. 스펙 문서 — `.claude/harness-spec.md` (D8)

인터뷰 중 단계마다 갱신되고, 생성 후에도 남아 재진입 감사의 기준점이 된다. 템플릿은
`references/interview.md`에 포함. 섹션:

```markdown
# Harness Spec — <project>
## Context          # 프로젝트 요약, 언어/빌드/테스트, 팀 규모, 사용자 숙련도 메모
## Goals            # 이 하네스가 달성해야 할 것 (사용자 언어 그대로 인용 포함)
## Behavior inventory
| id | behavior/knowledge/constraint | layer | component | status |
|----|-------------------------------|-------|-----------|--------|
| B1 | 커밋 전 반드시 테스트 통과     | hook  | pre-commit-test | generated |
## Component specs  # 컴포넌트별 세부 (훅: 이벤트/matcher/동작/실패정책, 스킬: 트리거/내용/스크립트, ...)
## Design rationale # 라우팅 결정의 이유, 기각한 대안
## Validation       # e2e 시나리오 목록과 마지막 실행 결과
## Change history   # 날짜, 모드(신규/확장/개선), 변경 요약
```

- status 값: `proposed` → `approved` → `generated` → `validated`.

> **v2 개정**: status 어휘에 두 값이 추가됐다 — `declined`(검토했지만 의도적으로 만들지
> 않기로 함, 행은 결정의 기록으로 남긴다)과 `retired`(존재했지만 의도적으로 제거됨). 둘 다
> 파일 존재를 주장하지 않으므로 drift로 잡히지 않는다. `generated`/`validated`만 파일
> 존재를 주장하고, 그 두 상태에서 파일이 없을 때만 audit가 drift로 보고한다(D28, WS1
> Fix B6/B11). 상세는 `references/re-entry.md`의 status 표.

- 재진입 시 audit_harness가 spec의 component 목록과 실제 파일을 대조해 drift를 보고한다
  (v2: **양방향** — 파일만 있고 spec에 없는 경우 + spec이 `generated`/`validated`라고
  주장하는데 파일이 없는 경우 둘 다. v1 설계는 전자만이었다).

## 5. 인터뷰 프로토콜 (references/interview.md의 핵심 설계)

### 단계 (신규 생성 기준)

| 단계 | 목적 | 대표 질문 소재 | 게이트 |
|---|---|---|---|
| I1. 목표와 고통 | 하네스로 뭘 개선하고 싶은가 | 클로드가 이 프로젝트에서 자주 틀리는 것, 반복 지시하는 것, 절대 하면 안 되는 것, 사용자 숙련도 | Goals 승인 |
| I2. 행동 인벤토리 | 원하는 행동·지식·제약을 항목화 | I1 답변을 항목으로 분해 + 코드베이스 정찰에서 발견한 후보 제안 (테스트 러너, lint 규칙, 위험 디렉토리...) | 인벤토리 승인 |
| I3. 레이어 라우팅 | 각 항목의 레이어 결정 | §3 프레임워크로 라우팅 제안 → 사용자 확인 (특히 강제 vs 권고 판단) | 라우팅 승인 |
| I4. 컴포넌트 세부 | 컴포넌트별 필수 정보 수집 | 훅: 실패 시 차단 vs 경고, 스킬: 참조 자료 위치, 워크플로우: 사전 정의 여부(D12), 생성 하네스의 문서 언어 | 컴포넌트 스펙 승인 |
| I5. 검증 계획 | e2e 시나리오와 예산 | 어떤 시나리오가 성공 판정 기준인가, e2e 실행 여부(토큰 비용 고지) | 최종 스펙 승인 → 생성 시작 |

### AskUserQuestion 운영 규칙 (interview.md에 명시)

- 도구 제약: 호출당 최대 4질문, 질문당 2~4옵션, 헤더 12자, 항상 "Other" 자동 제공.
- 추천이 있으면 첫 옵션에 "(Recommended)" — 근거를 description에 쓴다.
- **질문 수보다 구조**: 각 질문은 스펙의 특정 칸을 채워야 한다. 이미 답을 아는 것
  (코드베이스에서 확인 가능한 사실)은 묻지 말고 확인 결과를 제시한다.
- 사용자 숙련도에 맞춰 어휘 조정(I1에서 감지). 비개발자에게 "PreToolUse matcher"를 묻지 말고
  "위험한 명령을 실행 전에 막을까요, 실행 후에 알려드릴까요"로 묻는다.
- 열린 답이 필요한 질문(목표, 고통)은 AskUserQuestion 대신 일반 대화로 — 선택지는
  수렴에, 대화는 발산에 쓴다.

### 재진입 모드별 변형

- 확장: I1을 "새로 원하는 것"으로 축소, 기존 스펙의 Goals에 병합.
- 개선: I1 대신 "무엇이 불편했나/틀렸나" + 해당 컴포넌트의 피드백 라우팅
  (04 문서 §5의 라우팅 테이블 활용).
- 동기화: 질문 최소화 — drift 목록을 보여주고 spec을 고칠지 파일을 고칠지만 확인.

> **v2 개정(D22, WS8)**: 이 세 변형의 상세 절차(특히 동기화의 전체 drift 해소 절차)는
> `interview.md`가 아니라 신설된 `references/re-entry.md`로 옮겨졌다 — Phase 0에서
> `interview.md`를 무조건 로드하던 걸 분기시키려면, sync가 필요로 하는 절차가
> `interview.md` 밖에 있어야 했기 때문이다(순서 지키지 않으면 sync가 고립된다, D22).
> 05 문서(references 인벤토리)도 이 이동을 반영해 갱신했다.
