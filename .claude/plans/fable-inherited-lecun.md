# references 사실 감사: interface over document를 구조에서 사실로

> 과거 사실 감사의 계획 기록이다. 현재 실행 지침이 아니며, 아래에서 언급하는 `tools/claims.py`, `tools/probe.py`, 퀴즈와 별도 명세 파일은 삭제되었다. 실제 변경과 검증 결과는 CHANGELOG 및 각 PR 이력을 따른다.

## Context

출발은 `.tmp/docs_claude/prompting fable 5.1.md`로 harness-creator를 개선하는 것이었다. 검토 결과 문서 16개 섹션 중 하네스 *작성자*가 파일에 쓰는 노브에 닿는 것은 셋뿐이고, 더 큰 발견은 스킬 자체의 상태였다: 네 프레임(principle over rail, interface over document, for user not developer, dense information)은 v8 재작성으로 **구조**에는 구현됐지만, references의 **사실** 층위에서는 interface over document가 아직 지켜지지 않는다. 산문이 도구가 소유한 값(컴팩션 5,000/25,000 토큰, 설명 1,536자, 리스팅 1%, import 4홉, CLAUDE.md 200줄, 메모리 200줄/25KB)과 날짜 없는 모델 행동 주장("현재 모델은 under-trigger한다")을 그대로 주장하고, 이전에 배포된 틀린 gotcha 여섯은 전부 이 부류에서 나왔다.

이 세션에서 합의한 판정 기준 셋:

1. **클라이언트 동작은 런타임에 모델이 관찰할 수 없는 것만 남긴다.** 컨텍스트에서 잘려나간 지시, `paths:` 없는 rule의 상시 로드, `@file`이 Read 호출이 아닌 것, 깨진 프런트매터가 트리거만 조용히 죽이는 것 — 어떤 지능으로도 복구 못 하는 실패 형태가 이 스킬의 핵심 가치다. 모델이 관찰할 수 있는 것(CLI `--help`, 에러 메시지, 파일 구조)과 기능 해설은 뺀다. 남기는 것도 **배치·라우팅 결정을 바꾸는 실패 형태**로 쓰지, 한도 값으로 쓰지 않는다.
2. **도구 소유 숫자는 전부 뺀다.** 숫자 목표는 줄 단위 판정("이 줄을 지우면 모델이 틀리는가")을 밀어내고 스스로 간추리게 만드는 앵커다(성진 결정, 200줄 포함). 결정을 바꾸는 것은 실패 형태이지 값이 아니다.
3. **이유 없는 방향 규칙은 이유를 찾거나 뺀다.** "트리거 쪽으로 기울여라"는 근거가 날짜 없는 모델 관찰이면, 그 관찰이 모델 기본값이라는 사실과 유통기한을 함께 적는다(아래 Fable 사례 1).

감사 도구는 이미 있다: `tools/claims.py extract`로 주장을 ID로 동결하고 `check --dispositions`로 `KEEP` / `DROP <이유>` / `REWORDED` / `TOOL` 처분을 강제한다. 처분 이유는 위 기준 번호로 쓴다. `hooks-events.md`는 `scripts/hook_event.py`의 데이터 원본이라 인터페이스 데이터로 취급해 이번 감사 대상에서 뺀다. gotcha 프로브(`tools/probe.py`, 미실행)는 삭제 근거가 "이미 안다"가 아니므로 전제가 아니다.

주장 후보 수(`claims.py extract`): SKILL.md 62, claude-md-and-rules 84, skills 78, agents 110, workflows 48, e2e-testing 67, hooks 228. 총 약 680건, hooks가 3분의 1.

## 구현 순서 — reference당 PR 1개, 세션 여러 개

각 PR 절차: 브랜치 → `claims.py extract` 동결(`.tmp/audit/<file>.claims.json`, gitignore 영역) → 파일 편집 → 처분 파일 작성 → `claims.py check` 통과 → `validate_harness.py` → `unittest` → `codex` 스킬로 `gpt-6-astra(high)` 리뷰 1회("인용 출처가 지지하지 않는 주장" 관점) → 정정 → PR → squash 머지 → graphify 리빌드. 재검증은 **이번에 손대는 주장만** 라이브 문서(`code.claude.com/docs/en/<page>`) 원문 문장 인용으로 한다(요약 fetch는 버전을 지어내므로 원문 문장을 요구하고 "그런 문장 없음"을 답으로 취급).

### PR 0 — 메모리 기록 (파일 변경 없음, 구현 세션 첫 단계)

`~/.claude/projects/-Users-seongjin-Coding-harness-creator/memory/`에 기준 셋과 성진의 판정(200줄 앵커링, 클라이언트 내부 동작은 라우팅을 바꿀 때만, 컴팩션 gotcha는 길이 지시가 아니라 배치 결정)을 feedback 메모리로, 감사 진행 상태를 project 메모리로 기록하고 `MEMORY.md`에 포인터.

### PR 1 — `SKILL.md`: 기준 + Fable 사례

- "Authoring philosophy"에 기준 1·2를 한 문단으로: 참조는 런타임에 관찰할 수 없는 클라이언트 동작을 실패 형태로 싣고, 도구 소유 값은 싣지 않는다(이유: 값은 릴리스마다 바뀌고 모델이 확인할 수단이 없으며 숫자 목표는 줄 단위 판정을 밀어낸다). 기존 "Numbers need a reason" 문장은 이것으로 대체.
- **Fable 사례 1**(같은 절): 기본값과 충돌하는 줄은 가장 가치 있는 동시에 유통기한이 모델에 묶인 줄이다 — 과잉 포매팅하던 모델을 상대로 쓴 안티-불릿 규칙은 과소 포매팅하는 모델을 더 밀어내고, "결과는 마지막에 몰아서"는 원래 말이 적은 모델을 침묵시킨다. 그런 줄은 어떤 기본값을 상대로 썼는지 핸드오프에 남기고, 모델 교체가 audit의 재검사 트리거다. 모델 버전 이름은 커밋 본문에만(for user not developer).
- **Fable 사례 3**: density 문단에 "문자 그대로의 표현이 있으면 그것을 쓴다" 한 문장. SKILL.md 내 `earns its place` 류 정리.
- "Preserve what the next change depends on"에 한 문장: 기본값을 상대로 쓴 줄은 그 기본값을 기록한다.
- 기존 "Repair"·"Verify" 절의 "removing one rule at a time" 문장은 위 원칙과 연결되는지 확인만.

### PR 2 — `references/claude-md-and-rules.md`

- `:11-15` "Target length: ~200 lines" 절 → 숫자 제거, 줄 단위 판정만 남김(기준 2, 성진 결정).
- `:52` 메모리 200줄/25KB, `:62` 4홉 → 값 제거, 실패 형태만.
- `:68-74` 컴팩션 표는 기준 1 통과(관찰 불가, 배치 결정) — 유지.
- `:17-23` 포인터 정책 세 문단 → 규칙 하나로 압축(dense).
- `:31-33` "기본값과 충돌하는 줄"에 PR 1의 유통기한 원칙을 한 절로 연결.

### PR 3 — `references/skills.md`

- `:32` "Current models under-trigger" → 모델 기본값이라는 사실과 유통기한 표식(기준 3, Fable 사례 1의 첫 적용). 삭제하지 않음 — Fable 문서는 스킬 트리거를 다루지 않아 미검증.
- `:44` 리스팅 1%, `:50` 1,536자, `:66` 5,000/25,000 토큰 → 값 제거, 실패 형태("먼저 실행된 스킬의 지시가 사라져도 모델은 따르고 있다고 믿는다")와 결정("잃으면 안 되는 행동은 루트 CLAUDE.md에")만.
- `:5,16,20`의 SKILL.md 재진술 → 스킬 고유 부분만 남김.

### PR 4 — `references/agents.md`

- **Fable 사례 2**: `:90` model 행 "싸면 `haiku`" → "같은 모델의 `effort:` 프런트매터를 먼저, 티어는 그 다음". 한 행만, effort 해설 없음. `effort:` 필드 존재는 라이브 `sub-agents` 문서 원문으로 재검증.
- `:53-55` 에이전트 본문이 시스템 프롬프트를 대체한다는 부분은 기준 1 통과 — 유지.
- 숫자 8개 판정.

### PR 5 — `references/workflows.md`, PR 6 — `references/e2e-testing.md`

- workflows `:40` 동시 16/1,000 캡 → 값 제거. e2e는 숫자 0, 재진술·수사 위주.

### PR 7 — `references/hooks.md`

- 228건, 단독 세션. 숫자 43개 중 exit code(0/2)·이벤트 계약처럼 인터페이스 자체인 값은 `TOOL`(hook_event.py·test_hook.py가 소유) 처분, 한도·버전 값은 제거.
- 이 세션에서 부분만 읽었으므로 구현 세션이 전문을 먼저 읽는다.

### 부수 발견 (감사 범위 밖, 별도 `docs:` 직접 커밋 후보)

- 레포 `CLAUDE.md`가 존재하지 않는 `docs/plan/`을 바인딩 스펙으로 가리킨다.
- `tools/gotcha-quiz.jsonl`의 `source` 줄번호가 v7 이전 기준.

## 기각한 Fable 항목 (기록)

Compact instructions 섹션(수요 미확인, Claude Code 효과 미검증), `${CLAUDE_EFFORT}`·훅 `effort.level`(기능 목록화), 생성 CLAUDE.md의 자율성·범위 블록(시스템 프롬프트가 이미 실음, 문서 스스로 "덜 묻게 되는" 트레이드오프 경고), 서브에이전트 대기·배치·append-only 히스토리·비전(클라이언트 소유), base64 훅 출력 오탐(미검증, 수요 없음).

## 각 PR의 완료 판정

- `python3 tools/claims.py check <frozen> <file> --dispositions <d>` exit 0, 모든 DROP에 기준 번호.
- `python3 .claude/skills/harness-creator/scripts/validate_harness.py --path .` 오류 0.
- `python3 -m unittest discover -s tests -q` 실패 0(기준선: 깨끗한 체크아웃 356건; 작업 폴더의 SpecRecordTests 오류 4는 기존).
- 손댄 클라이언트-동작 주장마다 PR 본문 `## 검증`에 라이브 문서 원문 문장.
- astra 리뷰 결과와 정정 내역이 PR 본문에.
- 머지 후 graphify 리빌드 커밋.

## Git

브랜치 `docs/audit-<file>`, PR 제목 `docs: <file>의 도구 소유 값을 걷어내고 실패 형태만 남긴다` 꼴. CHANGELOG `[Unreleased]`에 PR마다 한 줄.
