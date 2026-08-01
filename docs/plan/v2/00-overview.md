# harness-creator v2 개정 계획 — 개요

> 이 문서 세트는 계획 세션(2026-08-01)에서 사용자와의 합의로 확정된 개정 명세다.
> 구현은 별도의 새 세션에서 이 문서를 읽고 진행한다. **이 계획이 곧 구현 세션의 명세다.**
>
> v1 계획(`docs/plan/00-overview.md` ~ `06-milestones.md`)은 v1 구현의 역사적 기록으로 온전히 남는다.
> 이 문서는 v1을 대체하지 않고 **개정**한다. 충돌 지점은 §3.2에 명시했다.

## 1. 왜 이 개정을 하는가

Anthropic이 아티클
[The new rules of context engineering for Claude 5 generation models](https://claude.com/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models)
(로컬 사본 `.tmp/`)에서 Claude Code 시스템 프롬프트의 80% 이상을 평가 손실 없이 제거했다고 보고하고,
그 과정의 7개 "then → now" 전환을 공개했다.

harness-creator는 하네스를 설계·생성·검증하는 메타 스킬이다. 자기가 설파하는 원칙을 자기 자신에게
적용하지 못하면 그건 비효율이 아니라 신뢰성 붕괴다. 그래서 질문이 두 겹이다.

1. **이 스킬이 생성하도록 가르치는 하네스**가 Claude 5 세대 기준에서 옳은가.
2. **이 스킬 자신의 표면**이 그 기준을 통과하는가.

동시에 v1의 리서치는 2026-07-05 문서 스냅샷 기준이다. 오늘은 2026-08-01이고 스냅샷은 이미 여러 지점에서
낡았다 — 그중 하나는 **실제로 틀린 gotcha를 출하시켰다**(B5).

## 2. 감사 결과와 솔직한 판정

5-렌즈 × 적대적 검증 워크플로우(에이전트 53개, 오류 0). findings 47건, 생존 46건, 기각 1건.
전체 원본은 [`research/audit-synthesis.md`](research/audit-synthesis.md).

> **"doctrine 수준에서는 이미 정렬돼 있고, coverage와 truthfulness 수준에서 어긋나 있다.
> 검증된 44개 findings 중 틀린 doctrine 주장은 하나도 없었고, 재확인한 14개 제품 메커니즘은
> 14개 전부 문서와 일치했다."**

**"우리도 80% 줄여야 한다"는 잘못된 프레임이다.** Anthropic이 줄인 건 모델이 이미 아는 일반론이었고,
이 스킬의 본문은 대부분 제품 메커니즘 gotcha다. 측정 결과 do-not-cut 집합만 reference 표면의
**26.3%(6,521단어)**, `hooks.md`는 **52.9%가 보호 대상**이다. 정직한 압축 여지는 ~930단어이고
필수 추가가 ~780단어다. **총 분량 기준으로는 −154단어(−0.6%)가 천장이다.**

진짜 문제는 네 갈래이고, 그중 어느 것도 분량이 아니다.

**(a) 자기 스크립트에 대한 거짓 주장 5개.** `SKILL.md:111`(포인터 검사), `SKILL.md:59`(drift),
`interview.md:99/:103/:132`(spec 파싱). 스킬 자신의 Hard line 1이 정확히 이걸 금지한다.

**(b) 정상 하네스를 떨구는 린터 버그.** `validate_harness.py:38`의 `_AT_IMPORT_RE`가
`contact ops@acme.com` → `acme.com`, `react@18.2.0` → `18.2.0`을 import로 오인하고 **E**를 낸다.
`:486`이 E를 non-zero exit으로 바꾸므로 **유지보수자 이메일이나 핀 버전을 언급하는 CLAUDE.md는
Hard line 2를 영원히 통과할 수 없다.**

**(c) auto memory에 대한 완전한 무지.** 두 번째 always-loaded 지시 표면이 `claude-md-and-rules.md:25`가
CLAUDE.md로 라우팅하는 것과 **정확히 같은 내용 범주**를 담는데(빌드 명령, 디버깅 통찰, 클로드가 발견한
선호) 스킬 표면에 언급이 0건이다. `CLAUDE.local.md`도 0건이라 라우팅 프레임워크에
"이 개발자만 필요한 것"의 목적지가 없다.

**(d) 실제 always-loaded 표면이 알려진 것의 2배.** `SKILL.md:92`가 `interview.md`를 **모든 호출에서**
로드하라고 지시하고 `SKILL.md:30-31`이 Phase 0에서 이미 그 파일에 손을 뻗는다. 즉 실제 상시 로드는
2,185가 아니라 **4,833단어**이고, 둘 사이의 progressive-disclosure 이음매는 아무것도 사지 못한다.
이걸 진짜 분기로 만드는 것이 **이 감사 전체에서 유일하게 자릿수가 다른 레버**다(−59%).

## 3. 결정 로그

### 3.1 이번 세션의 신규 결정

| # | 결정 | 내용 |
|---|---|---|
| **D13** | 개정 야심 | **구조 재편 포함.** SKILL.md 재구성, 파일 내부 재편, 스크립트 확장. v2 전면 재작성은 하지 않는다 — 수천 시간의 교훈이 현재 문장에 암묵적으로 박혀 있어 재작성에서 소실될 위험이 실재한다. |
| **D14** | 외부 도구 무언급 | **배포되는 스킬 표면은 Claude Code UI 명령을 이름으로 언급하지 않는다.** 목표는 그것을 참조하는 스킬이 아니라 그것을 뛰어넘는 자족적 단일 메타 스킬이다. 해당 도구에서 얻은 지식은 (i) 공개 문서로 독립 검증한 뒤 스킬 자신의 목소리로 서술하거나 (ii) 버린다. 원문은 어떤 형태로도 복제하지 않는다(오픈소스 플러그인으로 배포된다). 드리프트 문제는 **도구 이름 없이 일반화**한다: "하네스는 이 흐름 밖의 도구와 사람에 의해 편집될 수 있고, sync 모드는 그걸 견뎌야 한다." |
| **D15** | 순 분량 | **줄어들어야 한다.** 다만 총량 기준 천장은 −154단어(−0.6%)다. **실질 지표는 총량이 아니라 always-loaded 표면**이고, D22가 그걸 4,833 → ~1,970으로 만든다. |
| **D16** | 인터페이스 원칙 | **교차 원칙으로 승격하되 하네스 내부로 엄격히 한정.** 대상: 번들 스크립트 CLI 시그니처, hook 스크립트의 설정 입력, workflow `args`, 스킬 `description`(디스패치 인터페이스), 에이전트 `description`·`tools:`. **사용자 애플리케이션 코드 권고는 범위 밖** — 독립 감사자가 완화형("제안만 하고 실행은 말라")을 제시했으나 소유자가 재확인 후 기각. |
| **D17** | auto memory | **예산 모델에 반영 + 라우팅 축 추가.** 단 라우팅 행의 **목적지는 `CLAUDE.local.md`이지 auto memory가 아니다** — auto memory는 비결정적이다(문서: "Claude doesn't save something every session. It decides what's worth remembering"). 개발자가 클로드에게 반드시 있어야 하는 사실을 거기 라우팅하는 건 안전하지 않다. auto memory는 *"공유 CLAUDE.md 한 줄을 쓰지 말아야 할 이유"*로 등장하고 예산 모델에 들어간다. |
| **D18** | 교리 중복 | **의도된 보험으로 유지하고 이유를 명시.** 근거는 검증된 메커니즘(`research/mechanics-2026-08.md` A1-A3): auto-compaction은 스킬 본문 앞 5,000토큰을 재부착하지만 reference를 Read한 결과는 요약되어 사라진다. `SKILL.md:86`의 교리는 **압축 대상이 아니다** — 인터뷰 단계가 보는 유일한 교리 사본이고, hooks-only나 CLAUDE.md-only 패스에서는 어떤 reference도 복원하지 않는다. |
| **D19** | 버그 처리 | **전부 수정하되 리팩토링과 분리해 개별 커밋으로 먼저.** |
| **D20** | 예제 처리 | 판별식과 측정치는 계획에 기록하고 **최종 재작성 판단은 구현 세션에 위임.** 판별식 §5. 핵심: 문제는 코드가 아니라 **도메인 서사**다. |
| **D21** | SKILL.md 토큰 상한 | **SKILL.md는 5,000토큰(≈3,750단어)을 넘지 않는다.** 넘는 부분은 compaction 이후 조용히 사라진다. |
| **D22** | interview.md 로드 게이팅 | **분기화한다(순서 엄수).** ① `interview.md:93-99`의 sync 절차와 `:132`의 status 의미론을 먼저 옮긴다 ② 그 다음에 로드를 인터뷰가 실제로 일어나는 경로로 제한한다. **순서를 어기면 sync 모드가 고립된다.** |
| **D23** | `test_hook.py` 강조 | **자른다.** 소유자 도그푸딩에서 이 단계를 건너뛰는 걸 관찰한 적 없다 — 예방적으로 들어간 문구다. **단, why 문장은 전부 남긴다**: `SKILL.md:45`의 "validate_harness.py cannot check this for you"는 다른 어디에도 없는 사실이고, Hard line 2의 "A checklist that isn't mechanically enforced doesn't get enforced"는 그 줄의 유일한 why다. WS4 검증이 실제 준수율을 측정한다. |
| **D24** | 검증 규칙 | 이 repo의 `CLAUDE.md`는 개선 대상이 아니므로 **수정하지 않는다.** 대신 **버전 민감 메커니즘**(타임아웃, matcher 값 목록, 버전 플로어, frontmatter 필드 집합)은 스냅샷이 아니라 **라이브 문서로 확인**한다는 지침을 §11 킥오프에 둔다. B5는 스킬이 기존 규칙을 지켰는데도 틀린 gotcha를 출하한 사례다. |

### 3.2 v1 결정(D1-D12)에 대한 개정

| v1 결정 | 상태 | 사유 |
|---|---|---|
| D1 생성 범위 | **개정** | auto memory가 "advisory-only, 생성물 없음"으로 §1 목록에 추가된다. `.mcp.json`/output-styles/statusline은 생성 범위 밖 유지. |
| D2 배포 대상 | **개정** | in-repo 유지. 단 **감사 범위가 생성 범위를 넘어선다** — 감사는 `CLAUDE.local.md`와 외부 지시 파일(AGENTS.md 등)을 *충돌 신호*로 읽되 spec 추적 컴포넌트로 삼지 않는다. 이 구분을 기록해야 한다. |
| D3 skill-creator 관계 | **유지** | |
| D4 인터뷰 구조 | **개정** | 5단계 유지. **감산 단계·권한 확대 게이트·은퇴 라운드** 추가(WS7). |
| D5 검증 2층 | **개정** | 린트에 **always-loaded 예산 리포트**(프로젝트 스코프, 무조건 출력) + 3개 W-등급 휴리스틱 추가. 이는 v1 명세를 넘는 확장이므로 `04-scripts-and-validation.md`의 체크 표를 고쳐야 한다. |
| D6 재진입성 | **개정** | sync 모드를 **"이 흐름 밖에서 하네스가 편집됐을 수 있다"**를 일급 시나리오로 승격. drift 방향 결정(A안) 반영. |
| D7 문서 언어 | **유지** | |
| D8 스펙 영속화 | **개정 — A안 확정** | `check_spec_drift`가 Behavior inventory 표 행을 파싱해 `status`가 `generated`/`validated`인데 디스크에 없는 컴포넌트를 보고한다. **표 컬럼은 이미 `02-skill-design.md:113-125`가 고정해 놓았으므로 포맷 변경도 기존 spec 마이그레이션도 불필요.** Hard line 3의 헤드라인 방향이 처음으로 실제 검사가 된다. |
| D9 스크립트 세트 | **유지, 확장** | 4개 CLI 유지. `harness_common.py`에 `claude_md_paths()`. **`rglob` 금지 — 명시적 visited-set 워크**(Python 3.12/3.13이 심링크 재귀에서 다르고 Claude Code는 심링크된 rules 디렉토리를 실제로 따라간다). |
| D10 git 정책 | **개정 — 브랜치+PR** | §8. |
| D11 배포 전략 | **유지** | |
| D12 사전 정의 워크플로우 | **유지** | |

## 4. 분량 예산

측정치(`wc -w`, 2026-08-01)와 항목별 목표. 상세 근거는
[`research/audit-synthesis.md`](research/audit-synthesis.md) §1b.

| 파일 | 현재 | 목표 | Δ |
|---|---:|---:|---:|
| `SKILL.md` | 2,185 | **1,970** | −215 |
| `references/agents.md` | 3,003 | **2,928** | −75 |
| `references/claude-md-and-rules.md` | 1,885 | **2,161** | **+276** |
| `references/e2e-testing.md` | 3,160 | **3,132** | −28 |
| `references/hooks-events.md` | 3,766 | **3,790** | +24 |
| `references/hooks.md` | 4,760 | **4,860** | **+100** |
| `references/interview.md` | 2,648 | **2,758** | +110 |
| `references/skills.md` | 3,085 | **2,975** | −110 |
| `references/workflows.md` | 2,445 | **2,209** | −236 |
| **합계** | **26,937** | **26,783** | **−154 (−0.6%)** |

**총량은 지표가 아니다.** 실제 비용을 지배하는 건 always-loaded 표면이다.

| | 현재 | 위 예산만 적용 | D22까지 적용 |
|---|---:|---:|---:|
| always-loaded | **4,833** | 4,618 | **~1,970 (−59%)** |

압축 천장이 구조적인 이유: reference 표면의 26.3%가 보호된 non-derivable 메커니즘이고,
`hooks.md`는 52.9%가 보호 대상이라 압축 예산에서 면제이며, `hooks-events.md`는 사실상 100% 인터페이스다.

## 5. 예제 판별식 (D20)

**아티클을 다시 읽어야 한다.** anti-example 전환은 **도구 사용법 예제에만** 한정된다(line 60:
"The number one rule for **tool usage** was to give Claude examples on how to use them"). 같은 아티클이
line 102와 134에서 **코드를 레퍼런스로 쓰는 것을 적극 권장**한다. 잘라야 할 건 코드가 아니라
**코드를 감싼 도메인 서사**다.

> 606단어짜리 `audit-auth-routes`는 `agent()`/`pipeline()`/`schema`를 **약 120단어로** 가르치고,
> 나머지를 "무엇이 누락된 인증 검사인가"를 가르치는 데 쓴다.

판별식, 순서대로:

1. **필수 인터페이스를 문서화하는가?** 틀리면 조용히 no-op 되는 것들 — settings.json의 정확한 중첩,
   workflow의 pure-literal `meta`. **유지.**
2. **도메인을 완전히 다른 것으로 바꿔도 독자가 배우는 게 그대로인가?** 그렇다면 도메인은 장식이다.
3. **같은 파일의 산문이 이미 말한 것을 반복하는가?**
4. **`skills.md:14`에 맞는가?** — "원칙을 한 번 말하고, 2-3개의 짧은 사례로 생생하게 하고, 멈춰라."

**절대 하면 안 되는 것: 실행 가능한 코드를 시그니처 블록 + `'<placeholder>'` 프롬프트로 바꾸는 것.**
아티클 line 134가 정확히 그 반대를 말한다 — 코드에서 산문으로의 다운그레이드다. 짧은 **진짜** 프롬프트를
유지한다.

측정치와 블록별 1차 분류는 [`01-changes.md`](01-changes.md) WS6.

## 6. 워크스트림

상세는 [`01-changes.md`](01-changes.md). 순서는 §7.

| # | 워크스트림 | 규모 | 위험 | 요지 |
|---|---|---|---|---|
| **WS1** | 진실 복구 | M | 낮음 | 스킬이 자기 스크립트에 대해 하는 모든 주장을 참으로 만든다. 순 감소. |
| **WS2** | 스크립트 정확성 | L | 중간 | 정상 하네스를 떨구는 걸 멈추고, 감사 대상 파일을 실제로 보게 한다. |
| **WS3** | auto memory + 개인/팀 스코프 축 | M | 중간 | D17. |
| **WS4** | SKILL.md 상시 로드 경량화 | S-M | 중간 | D21/D23. |
| **WS5** | 조용한 실패를 갖는 누락 메커니즘 | S | 낮음 | 문단 4개. |
| **WS6** | 예제의 도메인 서사 제거 | M | **높음** | D20. 과잉 트림 위험 구간. |
| **WS7** | 인터뷰 감산 + 외부 편집 생존 | M | 중간 | D4/D6 개정. D14에 따라 도구 이름 없이. |
| **WS8** | interview.md 분기화 | M | **높음** | D22. 2단계, 순서 엄수. |

## 7. 실행 순서 (웨이브)

**Wave 1 — 병렬, 의존성 없음**
- (a) **WS2의 B1만** — `_AT_IMPORT_RE`. 단독으로 먼저 출하한다. 정상 하네스가 배포 게이트를 통과 못 하게
  만드는 유일한 결함이다. 계획 문서 수정 불필요.
- (b) **WS1의 dangling-pointer / 거짓 주장 수정** — `SKILL.md:39/:59/:105/:111`, `interview.md:42`,
  `hooks.md:86`, `hooks-events.md:314/:330`, `agents.md:73`의 닫히지 않은 펜스.
- (c) **WS5 전체** — 독립적인 단문단 추가 4개.

**Wave 2 — Wave 1(b) 이후**
- (d) **WS1의 drift 방향 결정 구현**(A안). **D6 영향.** `04-scripts-and-validation.md:46`과
  `02-skill-design.md:128`이 양방향을 *요구*하므로, 어느 쪽을 택하든 계획 문서 수정이 필수다 —
  **코드가 미기록 이탈이지 산문이 아니다.**
- (e) **WS2의 나머지 스크립트 작업.** **D5·D2 영향.** `04`의 체크 표 수정 필요.

**Wave 3 — Wave 2(e) 이후**
- (f) **WS3** — auto memory. (e)에 의존한다(예산 리포트가 먼저 있거나, "셀 수 없는 표면" 명시 줄과 함께
  출하해야 한다). **D1 영향.** `05-references-inventory.md:8` 수정 필요.

**Wave 4 — Wave 3 이후**
- (g) **WS4** — SKILL.md 경량화. WS1의 Wrap-up 재정렬(B2) **이후**여야 한다(아니면 깨진 순서를 압축해
  보존한다). WS3의 라우팅 축 이후여야 표를 한 번만 편집한다. `02-skill-design.md:5, :28-44` 수정 필요.
- (h) **WS8** — interview.md 분기화. (g) 이후. **자체 2단계 순서는 협상 불가.**

**Wave 5 — 마지막, 단독**
- (i) **WS6** — 예제 트림. 의도적으로 마지막: 과잉 트림 위험이 가장 높고, 안정화된 가드레일 목록에
  대고 해야 하며, 리뷰어가 나머지 변경 전부를 앞에 두고 봐야 하는 유일한 워크스트림이다.
  `05-references-inventory.md:8-15`가 예제를 이름으로 명시하므로 수정 필요.
- (j) **WS7** — 감산과 외부 편집 생존. **D4 영향.** `02-skill-design.md:130-141` 수정 필요.

### 함께 수정해야 하는 계획 문서와 위키

**계획 문서:** `00-overview.md` §1·§3(D1, D2, D5, D6); `02-skill-design.md` :5, :28-44, :50, :92-101,
:113-128, :130-141; `03-component-generators.md` :11-12(하드랩 규칙이 두 reference로 지시됐으나 배치되지
않았다 — 배치하거나 이탈을 기록); `04-scripts-and-validation.md` :29, :46, 체크 표;
`05-references-inventory.md` :8-15; `06-milestones.md` :51.

**위키:** `Architecture.md:77`("~110 lines" 하드코딩), `Layer-Routing.md:15-17, :23-32, :42-43`,
`The-Interview.md:15-21`, `Validation.md`, `Re-entry-Modes.md`.

> **라우팅 테이블이 세 곳에 복사돼 있고 이미 드리프트했다** — `SKILL.md:76`,
> `02-skill-design.md:97`, `docs/wiki/Layer-Routing.md:43`이 `bypassPermissions` 하에서 hook과 deny 규칙 중
> 무엇이 살아남는지에 대해 서로 다르게 말한다. 이번 패스에서 단일 진실 공급원으로 정리한다.

## 8. git 정책 (D10 개정 — 확정)

- 브랜치 `v2-context-engineering`.
- **`git tag v2-baseline`을 Wave 1 시작 전에 찍는다** — A/B 검증의 baseline이다. 버그 수정이 baseline에
  들어가면 A/B가 버그 수정 효과와 압축 효과를 구분하지 못한다.
- 버그당 별도 커밋 + 회귀 테스트 동반. 이후 워크스트림마다 커밋.
- **머지 전에 L4 A/B를 돌리고 결과를 `02-verification.md`에 기록한다.**
- PR 본문: 이 계획 링크 + before/after 단어 수 표 + always-loaded 수치 + A/B 결과 요약.

## 9. 수용 기준

1. `python scripts/validate_harness.py --path . --strict` 가 이 repo에 대해 오류 0으로 통과한다.
2. 버그 8건 각각에 **수정 전 실패 / 수정 후 통과**하는 회귀 테스트가 `tests/fixtures/`에 있다.
3. 스킬 표면에서 `grep -rniE "doctor|checkup"` 가 0건이다 (D14).
4. 총 단어 수 < 26,937 (D15). 실측치를 §4 표에 기록.
5. `SKILL.md` < 3,750단어 (D21), 목표 ~1,970.
6. **always-loaded 표면 < 2,500단어** (D22). 이게 이번 개정의 대표 지표다.
7. `research/mechanics-2026-08.md`의 모든 ⚠ 행이 해소됐다.
8. `research/audit-synthesis.md` §4의 가드레일 중 **어느 것도 삭제되지 않았다.**
9. **L4 A/B가 머지 전에 실행됐고 회귀 판정이 0건이다.** 회귀가 나오면 그 항목은 되돌린다.
10. 계획과 충돌하는 사실을 발견했다면 계획 문서를 고치고 사유를 남겼다.

## 10. 가드레일

전체 목록과 구조 규칙 R1-R3은 [`research/audit-synthesis.md`](research/audit-synthesis.md) §4에 있다.
**구현 세션은 WS6 시작 전에 그 절을 반드시 읽는다.** 핵심 3개 규칙:

- **R1 — 린트 체크가 남아 있는 산문 gotcha는 절대 자르지 않는다.** 10쌍이 짝지어져 있다
  (예: `hooks.md:70` ↔ `validate_harness.py:95-102`). 한 쌍은 **단방향**이다: `workflows.md:33`의
  pure-literal `meta` 요구는 린트가 `meta` 리터럴의 *존재*만 확인하고 *순수성*은 확인하지 않으므로,
  체크를 잘라도 산문은 살아남아야 한다.
- **R2 — 세 곳에 있는 `once: true` 서술은 올바른 중복이다.** `hooks.md:52`, `skills.md:58`,
  `agents.md:41`. `SKILL.md:36-38`이 컴포넌트 타입별 개별 reference 로드를 요구하므로, 에이전트를
  생성하는 모델은 `skills.md`를 절대 열지 않는다. `agents.md:25`의 Explore/Plan gotcha가
  `hooks-events.md:221`, `skills.md:70`, `e2e-testing.md:133`에 의도적으로 재진술된 것도 같은 보호를 받는다.
- **R3 — `hooks.md:118-153`의 30행 라우터가 hooks.md/hooks-events.md 분할을 안전하게 만든다.**
  자르면 staged split이 라우팅 실패로 바뀐다 — 모델이 이벤트 하나 고르려고 3,766단어를 로드하게 된다.

## 11. 구현 세션 킥오프

```
docs/plan/v2/ 를 읽고 harness-creator v2 개정을 시작해줘.
사실 기준은 docs/plan/v2/research/mechanics-2026-08.md 야.
Wave 1부터 순서대로, 워크스트림마다 커밋해줘.
계획과 충돌하는 사실을 발견하면 멈추지 말고 계획 문서를 수정하고 보고해줘.
```

**시작 전 확인:**
- `git tag v2-baseline` (Wave 1 시작 **전**).
- `.tmp/docs_claude/`(2026-07-05 스냅샷)와 `.tmp/`의 아티클 사본이 로컬에 있는지.
- `~/.claude/skills/harness-creator` 심링크가 이 repo를 가리키는지 (플러그인 설치와 동시 사용 금지 —
  스킬이 두 이름으로 이중 등록된다).

**작업 중 지켜야 할 검증 규칙 (D24).** 이 repo의 `CLAUDE.md`는 "메커니즘 주장은 `.tmp/docs_claude/`에
대조하라"고 한다. 그 규칙은 유지하되, **버전 민감 메커니즘은 스냅샷으로 부족하다**:

> 타임아웃 값, matcher가 받는 값 목록, 버전 플로어, frontmatter 필드 집합 — 이 넷은
> `https://code.claude.com/docs/en/<page>` 라이브 문서로 확인한다.

B5(SessionEnd 타임아웃)가 정확히 이 함정이다. 7월 스냅샷의
`05-reference/07-hooks-reference.md:2623`이 문자 그대로 "SessionEnd hooks have a default timeout of
1.5 seconds"라고 적혀 있고, repo는 그걸 충실히 복사했으며, 라이브 문서는 이제 그것이 **공유 예산**이라고
말한다. 규칙을 지켰는데도 틀린 gotcha가 출하됐다.
