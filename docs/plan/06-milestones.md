# 06 — 구현 마일스톤, 수용 기준, 리스크

## 마일스톤 (각 완료 시 main에 커밋+푸시 — D10)

### M0. 스캐폴딩 + 검증 항목 해소 — ✅ 완료 (커밋 예정)
- 디렉토리 구조 생성(01 문서 §1·2), `.claude-plugin/plugin.json` + `marketplace.json`,
  README.md(설치 2경로: 플러그인/심링크), 이 repo용 CLAUDE.md(간결 — 이 계획 문서 포인터 중심).
- **V1 검증 완료**: `claude plugin validate .` 통과 → 로컬 마켓플레이스 add → install →
  `claude plugin details harness-creator`로 `Skills (1) harness-creator` 확인. 경로 필드
  동작 확인, 폴백 불필요. 검증 후 `claude plugin uninstall`+`marketplace remove`로 정리
  (심링크만 상시 유지 — 01 문서 §패키징 참조).
- **V2 검증 완료(실측 불필요, 문서로 확정)**: 안 B 확정 — `/harness-creator:harness-creator`
  감수, 안 C는 D11(플러그인+심링크 병행)과 구조적으로 양립 불가해 기각. 근거는 01 문서 §네이밍.
- **환경 제약 발견(M2로 이관)**: 이 구현 세션의 샌드박스에서는 Bash로 스폰한 `claude` 자식
  프로세스가 인증되지 않는다(`claude -p`가 헤드리스·비헤드리스 무관 "Not logged in" 반환 —
  호스트 세션의 OAuth/키체인이 자식 프로세스에 노출되지 않음). 이는 V3(헤드리스 권한 처리
  실측)와 도그푸딩(M4)의 e2e 부분, 그리고 심링크의 "다른 디렉토리에서 스킬 목록 표시" 실측을
  이 세션에서 완전히 자동 검증할 수 없게 한다. 대신: (a) 심링크 지원은 공식 문서로 확인
  (`.tmp/docs_claude/.../01-extend-claude-with-skills.md`의 symlink 문단), (b) V3는 M2에서
  `run_e2e.py`를 문서화된 사실 기반으로 구현하되 실제 `claude -p` 실행 검증은 인증 가능한
  환경(사용자의 로컬 터미널)에서 사용자가 1회 수행하도록 안내 문구를 남긴다 — 04 문서 §4,
  06 문서 R3에 반영.
- 수용: `claude plugin validate` 통과 ✅. "심링크 설치 후 다른 디렉토리에서 스킬 목록에 표시"는
  공식 문서 확인 + 파일시스템 레벨 심링크 정합성으로 대체 검증(위 사유로 라이브 세션 실측 불가).

### M1. references/ 8개 파일
- 05 문서의 인벤토리 순서대로. 각 파일은 03 문서의 gotcha를 빠짐없이 포함하되
  1차 소스(`.tmp/docs_claude/`)에서 사실 재확인 후 작성.
- 수용: 05 문서의 "내용 개요" 항목이 전부 반영됨. gotcha 누락 0 (03 문서 대조).

### M2. scripts/ 4개 — ✅ 완료
- 순서: validate_harness → test_hook → audit_harness → run_e2e (의존성·가치 순) — 실제로
  이 순서로 작성. `harness_common.py`(공유 frontmatter 파서·canonical tool list·이벤트
  테이블)를 4개 스크립트가 공유(D9 공통 규약 — 이중 파서 불일치 방지).
- 각 스크립트에 자기 테스트: **repo 루트의** `tests/fixtures/`(good-harness/bad-harness)에
  정상/오류 하네스 픽스처를 만들어 기대 출력 대조. `tests/test_{validate_harness,test_hook,
  audit_harness,run_e2e}.py` — stdlib unittest, 총 78개 테스트, 전부 통과.
- **V3 재확인, 미해소(환경 제약)**: M0에서 발견한 샌드박스 인증 제약이 `run_e2e.py`
  완성 후 재확인됨 — `--isolate`(`--dangerously-skip-permissions` 포함) 실행도 동일하게
  "Not logged in"으로 막힘. 문서화된 사실 기준으로 구현하고 이 실패 케이스 자체로 파이프라인
  (subprocess 호출·CLAUDECODE 제거·stream-json 파싱·출력 파일 작성)은 end-to-end 검증됨.
  실제 도구-호출 시나리오에서의 권한 모드 동작만 사용자의 인증된 환경에서 최초 확인 필요
  (04 문서·e2e-testing.md에 상세 기록).
- 수용: 픽스처 테스트 전부 통과(78/78). test_hook이 대표 3레시피(보호 경로 차단 / post-edit
  포맷 / Stop 게이트) 훅을 정확히 판정 — good-harness 픽스처로 직접 검증함.

### M3. SKILL.md
- 02 문서 §1 구성대로. references와 scripts가 완성된 후에 쓴다(참조 대상이 실존해야
  정확한 라우팅 서술이 가능).
- 작성 후 validate_harness를 **이 스킬 자체에** 적용(죽은 링크·frontmatter 검사).
- 수용: 500줄 이하, 02 문서 §1(본문 섹션 7)의 hard line 3개 포함, 모든 reference/script 포인터 실존.

### M4. 도그푸딩 (성공 기준 #5) — ✅ 완료
- 샘플 대상: `chalk`(작은 실제 오픈소스 Node ESM 라이브러리)를 스크래치패드에 로컬로 clone
  (원본 GitHub repo에는 어떤 영향도 없음 — 순수 로컬 사본). 사용자가 이 방식을 확정.
- 전체 루프 실행 완료: `Skill(harness-creator)` 도구로 실제 호출(심링크 경로 확인됨) →
  Phase 0 감사(audit_harness.py, "new" 모드 제안) → 코드베이스 정찰 → 압축 인터뷰
  (사용자 참여, AskUserQuestion 3라운드 — 목표 확정 · hook 대상 확정 · 스펙 승인 게이트,
  D4의 "map, not rails" 유연성 원칙 실사용) → `.claude/harness-spec.md` 작성 →
  생성(CLAUDE.md 1개 + `source/vendor/` 보호 hook+deny 쌍 1개) →
  `validate_harness.py` 0오류/0경고(생성 직후 + Wrap-up 최종 패스 둘 다) →
  `test_hook.py`로 벤더 파일 편집 차단(exit 2)·일반 파일 편집 허용(exit 0) 둘 다 실측 확인.
  e2e는 사용자 동의 하에 의도적으로 생략(데모 하네스에 토큰 비용을 쓸 필요 없다고 판단 —
  D5의 동의 게이팅이 정확히 의도한 경로).
- **재진입 검증 완료**: 생성 후 `audit_harness.py`를 동일 경로에 재실행 →
  "extend or improve" 모드 정확히 제안(신규 아님), spec-실제 드리프트 0건 확인 —
  재호출 시 중복 생성이 아니라 확장/개선 분기로 이어짐을 확인(성공 기준 3 충족).
- **발견된 문제를 스킬에 반영**: 도그푸딩 준비 중(스펙 확정 전) 6-에이전트 신뢰성 리뷰
  워크플로우를 돌려 SKILL.md의 실제 스킵 위험 지점을 찾아 6개 수정 적용 + hooks.md/agents.md/
  skills.md에 스킬 프론트매터 `hooks:` 필드(및 `once:` 필드의 스킬 전용 스코프) 문서화 gap을
  메움 — 커밋 `993728a`. 이후 실제 생성 패스는 이 수정된 SKILL.md로 순조롭게 진행되어
  추가 개선 없이 완료됨(리뷰→수정→도그푸딩 순서가 유효했음을 보여주는 신호).
- 수용: 00 문서 §4 성공 기준 1, 2, 3, 5 충족. (기록: 이 커밋 + 구현 세션 트랜스크립트.)

### M5. 배포 마감 — ✅ 완료
- **플러그인 설치 경로 재검증**: 실제 GitHub 소스로 성공 기준 #4의 정확한 명령을 그대로 실행 —
  `claude plugin marketplace add tjdwls101010/Harness-Creator` → `claude plugin install
  harness-creator@harness-creator` → `claude plugin details harness-creator`가 `Skills (1)
  harness-creator`와 정상 토큰 비용 추정(always-on ~125, on-invoke ~3.5k)을 보고. 캐시가
  692K로 깨끗함(로컬 경로 설치 시 발견된 `.tmp/` 누출과 무관함을 실측 확정 — 01 문서 참조).
  검증 후 표준 정리(uninstall + marketplace remove + 캐시 수동 삭제)로 심링크 전용 개발
  상태로 복귀.
  - 유일하게 이 샌드박스에서 실측 불가능했던 부분: 설치 후 **다른 프로젝트 디렉토리에서 실제
    세션을 새로 띄워 호출**하는 것 — M0에서 발견한 "스폰된 `claude` 프로세스 인증 불가" 제약과
    동일한 이유. 매니페스트·설치·컴포넌트 인벤토리 레벨의 정합성은 위에서 완전히 실측했고,
    남은 것은 실제 모델 호출이 필요한 부분뿐이므로 사용자의 인증된 환경에서 1회 확인 권장.
- README.md 마감: Status 섹션을 "구현 진행 중"에서 완료 상태로 갱신, `run_e2e.py` 미검증
  사항과 로컬 경로 설치 캐시 동작을 사용자에게 미리 고지하는 문단 추가.
- **버전 태깅**: `claude plugin tag . --push` → `harness-creator--v0.1.0` 태그 생성 및
  origin에 푸시 완료(plugin.json·marketplace.json 버전 정합성 검증 통과).
- 수용: 성공 기준 #4 충족(정확한 명령으로 실측). `/plugin marketplace add` → install까지
  실측 성공 — "타 프로젝트에서 호출 성공"의 마지막 한 조각(라이브 세션 호출)만 위 사유로
  이 세션에서는 검증 불가, 사용자 확인 필요 항목으로 명시.

## 구현 세션에 주는 재량과 제약

- **재량**: 파일 내 세부 구성, 스크립트 내부 설계, reference 문구. 계획의 분량 목표는
  가이드이지 상한/하한이 아니다.
- **제약(변경 시 사용자 보고)**: 결정 로그 D1~D12, 레이어 라우팅 프레임워크의 골격,
  2층 검증 구조, hard lines, 파일 트리의 컴포넌트 구성.
- 계획-현실 충돌 시: 계획 문서를 수정하고 커밋 메시지에 사유 기록 (00 문서 §6).

## 리스크와 열린 항목

| # | 리스크/열린 항목 | 대응 |
|---|---|---|
| R1 | **V1** plugin.json skills 경로 미동작 | ✅ M0에서 실측 완료 — 동작 확인, 폴백 불필요 |
| R2 | **V2** 플러그인 스킬 네이밍 어색함 | ✅ M0에서 문서로 해소 — 안 B 확정(01 문서 §네이밍) |
| R3 | **V3** headless 권한 처리 불명 + 구현 세션 샌드박스에서 `claude` 자식 프로세스 인증 불가(M0에서 발견 — "Not logged in", 호스트 세션 자격증명이 Bash로 스폰한 프로세스에 노출 안 됨) | M2에서 `run_e2e.py`를 `.tmp/docs_claude` 문서화 사실 기반으로 구현. 유력안: --isolate 복사본 + skip-permissions. **실제 `claude -p` 실행 검증은 이 세션에서 불가하므로 사용자가 인증된 로컬 환경에서 1회 수행**하도록 스크립트 --help와 e2e-testing.md에 안내 문구 포함(자동화된 자기 테스트만으로 완결 선언 금지) |
| R4 | 문서 스냅샷(.tmp/docs_claude, ~v2.1.200 기준) 노후화 | references에 "기준 버전" 명시. 버전 민감 기능(hook if 등)은 최소 버전 주석. 재동기화는 범위 밖(필요 시 사용자가 스냅샷 갱신) |
| R5 | e2e 토큰 비용이 부담 | 기본 2~4 시나리오, 실행 전 비용 고지 + 동의(D5), 실패 시나리오만 재실행 |
| R6 | AskUserQuestion가 서브에이전트/헤드리스에서 불가 | 인터뷰는 항상 메인 스레드에서. e2e로 인터뷰 자체를 테스트할 수 없음을 e2e-testing.md에 명시 (도그푸딩=수동 검증) |
| R7 | 워크플로우 비가용 환경(무료 플랜, disableWorkflows) | 모든 워크플로우 사용처에 서브에이전트 폴백 서술 (03 문서 §6) |
| R8 | 생성 하네스가 user-scope 설정과 충돌 | audit가 ~/.claude 충돌 후보 보고 (04 문서 §2) |
| R9 | stdlib YAML 부재로 frontmatter 파싱 한계 | 보수적 파서 + 불확실 시 경고(오탐 금지) 정책 (04 문서 공통 규약) |

## v1 범위 밖 (기록용 — 요청 시 v2 후보)

- .mcp.json / output-styles / statusline / loop.md 생성 (D1)
- 플러그인 패키징 *생성*(만든 하네스를 플러그인으로 내보내기)
- description 자동 튜닝 루프(train/test 홀드아웃) — skill-creator System B의 재도입
- with/without A/B 벤치마크의 통계적 확장
