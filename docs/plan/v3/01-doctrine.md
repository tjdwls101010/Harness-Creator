# PR1 — 교리 교정과 인터페이스

> v3의 첫 번째 PR. 작은 diff, 높은 사고 밀도. **여기서 확정되는 교리가 PR2(압축)의 판별식이 된다** — 순서를 뒤집으면 판별식 없이 4천 단어를 자르게 된다.

## 1. 이 PR이 고치는 것

v2는 생성물에게 두 가지를 각각 독립된 절과 리트머스 테스트로 가르쳤다.

| 교리 | 거처 | 테스트 |
|---|---|---|
| (A) why를 붙여라 → conviction | `skills.md` §Conviction over compliance | "내가 준 why만으로 모델이 이 지시를 재도출할 수 있나?" |
| (B) 모델이 아는 건 쓰지 마라 | `skills.md` §Don't write what the model already knows | "이 줄이 없으면 모델이 실제로 틀리나?" |

그리고 세 번째를 **종속절 하나로만** 가지고 있다.

| (C) 한 번 말하고 멈춰라 | `skills.md:14` 문장 중간 | 없음 |

**결함은 (C)의 부재가 아니라 (B)의 적용 범위다.** (B)는 *어떤 주장을 넣을지*(내용 선택)에만 걸리고, *그 주장을 정당화하는 문장*에는 걸리지 않는다. 그래서 교리를 충실히 따르는 생성기는 한 절짜리 규칙 + 세 문장짜리 논증을 쓴다. 이건 문체 사고가 아니라 **교리의 비대칭이 만든 필연적 산물**이고, 그래서 `agents.md`·`skills.md`·`e2e-testing.md`·`workflows.md`가 지금 그 모양이며, **이 스킬이 생성할 모든 하네스도 그 모양이 된다.**

그래서 고칠 곳은 두 군데가 아니라 한 군데다 — 새 원칙 추가가 아니라 **기존 원칙 (B)를 why에까지 일관 적용**하는 것. 이 프레이밍을 유지해야 한다. "압축 원칙을 새로 추가한다"로 쓰면 교리가 하나 더 늘어나고, 그건 이 PR이 반대하는 바로 그 행동이다.

## 2. 무엇을 어디에 쓰나 (D30: SKILL.md 단일 정본)

(B)가 `skills.md`에만 있는 게 이미 결함이다 — `SKILL.md:42`가 "이번 패스의 모든 컴포넌트 타입에 대해 reference를 로드하라"고 하므로, **CLAUDE.md만 생성하는 패스나 hooks만 생성하는 패스는 `skills.md`를 열지 않는다.** 그리고 D18이 근거를 이미 확정해 뒀다: auto-compaction은 스킬 본문 앞 5,000토큰을 재부착하지만 reference를 Read한 결과는 요약되어 사라진다. **SKILL.md의 교리가 compaction 이후에도 살아남는 유일한 사본이다.**

그러므로 이번에 추가·수정되는 교리 4건은 전부 `SKILL.md`의 Authoring philosophy 절에 들어간다. `skills.md` §Conviction과 §Don't write는 그대로 둔다(스킬 생성 패스가 보는 심화판이고, R2의 "의도된 중복" 논리가 그대로 적용된다).

## 3. 문안 (초안 — 구현 세션이 다듬어도 되지만 주장은 보존한다)

### 3.1 (B)를 why까지 확장

`SKILL.md`의 Authoring philosophy 안, "Don't write what a capable model already knows" 문장 **직후**에 삽입한다. 그 문장 바로 옆이어야 한다 — 같은 필터의 두 번째 적용이라는 게 배치로 드러나야 하고, 별도 절로 떼면 "새 원칙"으로 읽힌다.

> The same filter runs on the why: keep the clause that makes the rule re-derivable, cut the sentences that argue for it. Conviction is whether a reason is present, not how far it runs — a model that reads a reason does not need to be talked into it, and the sentences doing the talking bury the gotcha beside them. The shapes that go: restating the claim you just made, arguing for it, spelling out a consequence the reader computes anyway, giving the negative case equal weight when the positive implies it, and narrating what the next paragraph is about to do.

약 95단어. 마지막 문장(다섯 가지 형태)이 이걸 **운영 가능하게** 만드는 부분이다 — 이름 없이 "설득을 자르라"고만 하면 모델은 자기 글에서 그걸 못 알아본다. 이 스킬 자신의 교리("테스트 문장이 원칙을 운영 가능하게 만든다")를 여기 적용한 것.

**이 문단 자체가 자기 예시여야 한다.** 다섯 가지 형태에 각각 설명을 붙이면 250단어가 되고, 그 순간 이 문단은 자기 주장의 반례가 된다. 설명 없는 나열로 유지한다.

### 3.2 인터페이스 = 압축 수단

`SKILL.md:93`의 인터페이스 문단은 **정의가 이미 맞다.** 아티클(56–66행)이 말하는 건 *tools, scripts, files*의 파라미터 표현력이고, 현재 문단의 "an interface is re-read from the tool's own signature on every use" + 열거된 다섯 표면(스크립트 CLI, 훅 설정 입력, workflow `args`, 스킬 `description`, 에이전트 `tools:`)이 정확히 그것이다. `interview.md:48`의 `--env` 프로브도 마찬가지로 정확하다.

**빠진 건 두 가지다.**

첫째, 아티클의 설계 레버 — 파라미터 공간이 *가르친다*는 것. 지금 문단은 "an interface expresses what is *valid*"라는 **제약** 프레임만 갖고 있다. 아티클의 Todo 예시는 `pending/in_progress/completed` enum이 세 경우의 존재 자체로 사용법을 암시한다는 **교시** 프레임이다. 추가할 문장:

> The design lever is the parameter space: an argument that can only take three named values teaches the three cases by existing.

둘째, 압축과의 연결. 이게 이번 PR의 핵심 연결점이고 지금 어디에도 없다.

> This is also the strongest compression available: prose moved into a signature is not shortened, it is relocated to a surface that is re-read for free.

합계 약 47단어. 기존 문단 안에 삽입하며, "The boundary: an interface expresses what is *valid*, never when to reach for it or why" 경계 문장은 **그대로 남긴다** — 그게 인터페이스 남용을 막는 유일한 제동이다.

### 3.3 rich references (아티클의 빠진 7번째 전환)

아티클 94–104행 *"Then: Simple specs → Now: Rich references"* 가 스킬 표면에 사실상 없다. 확인 결과 `rubric:`이 `e2e-testing.md:110`에 채점용으로 한 번 나오는 게 전부이고, "레퍼런스는 코드일 수 있다"(아티클 102·134행)는 0건이다.

`SKILL.md` Authoring philosophy 안, progressive disclosure 논의 **뒤**에 삽입한다(레퍼런스가 무엇일 수 있는지는 어디에 둘지를 정한 다음 문제다).

> A reference does not have to be prose. A failing test, a schema, a rubric, or a function in another codebase pins a target more precisely than a paragraph describing it, in a language the model reads natively — and unlike a paragraph it can be run. When the interview surfaces "here's what good looks like," ask whether the answer is a file that already exists.

약 65단어. 마지막 문장이 인터뷰용 운영 지침이다.

**경계를 분명히 할 것:** `.claude/harness-spec.md`는 여전히 마크다운이다. spec은 *기록*이지 *목표*가 아니므로 모순이 아니다. 구현 세션이 이걸 "spec을 테스트로 바꾸자"로 오독하면 안 된다.

### 3.4 체크 메시지도 인터페이스다 (R1 개정의 근거)

`SKILL.md`의 인터페이스 문단 끝에 붙인다.

> A check's failure message is an interface too — read at exactly the moment it matters, free otherwise. Where a rule is mechanically detectable, state the decision in prose and let the check's own output carry the consequence, instead of paying for both on every load.

약 50단어. 아티클 86행("지시는 시스템 프롬프트가 아니라 툴 설명에")의 하네스 판이다.

**정직한 한계를 구현 세션이 알아야 한다:** 린트는 생성 *후*에 돌므로 작성 시점이 아니라 교정 시점에 가르친다. 즉 산문을 완전히 없애면 클로드가 한 번 틀리고 교정받는 턴이 생긴다. 그래서 §3.4는 "산문을 지워라"가 아니라 **"산문은 결정을, 체크는 결과를"** 이라는 분업이다. 이 구분이 무너지면 R1 개정이 그냥 가드레일 해제가 된다.

## 4. 분량 제약 (D34)

| | 현재 | PR1 이후 |
|---|---:|---:|
| `SKILL.md` | 2,411단어 | **2,411단어 이하** |

추가되는 교리는 약 **257단어**(95 + 47 + 65 + 50)다. D34가 순감소를 강제하므로 **PR1은 SKILL.md 안에서 최소 257단어를 회수해야 한다.** 따라서 **SKILL.md는 PR1에서 한 번만 손대고 PR2 목록에서 제외한다** — 두 PR이 같은 파일을 건드리면 리뷰가 불가능해진다.

이 순서가 중요한 이유: 압축을 가르치는 문단이 상시 로드 표면을 늘리면 그 자체로 자기 주장의 반례다. 원차적으로 차단한다.

### 4.1 이 제약은 검증되지 않았다 — 못 지키면 D34를 고친다

SKILL.md의 장문단은 **788단어**, 4개다.

| 행 | 단어 | 요지 | 표 변환 적합성 |
|---:|---:|---|---|
| `:91` | 273 | Authoring philosophy | **낮음** — 교리 본문. 여기가 §3의 삽입 지점이다 |
| `:87` | 198 | "How to apply it, in four questions" | **높음** — 4개 질문 각각에 답과 귀결. 표의 정의 그대로 |
| `:116` | 192 | Hard lines 1 | **중간** — 3개 항목 열거지만 각각이 서사를 갖는다 |
| `:93` | 125 | 인터페이스 원칙 | **낮음** — §3.2가 여기에 47단어를 더한다 |

**파일럿 회수율(~6%)을 788단어에 그대로 적용하면 ~47단어다. 257단어에 한참 못 미친다.** 순감소가 가능하려면 `:87`과 `:116`이 표 변환으로 평균보다 훨씬 크게 줄어야 한다. 그건 **추정이지 실측이 아니다.**

**PR1의 첫 단계는 `:87`과 `:116`을 실제로 표로 만들어 회수량을 재는 것이다.** 그 결과에 따라:

| 회수량 | 조치 |
|---|---|
| ≥ 257단어 | D34 그대로. 계획대로 진행 |
| 150~257단어 | §3의 문안을 **한 번** 조인다. 단 §3.1의 다섯 형태 나열과 §3.3의 마지막 운영 문장은 자르지 않는다 — 그게 각 교리를 운영 가능하게 만드는 부분이다 |
| < 150단어 | **D34를 폐기한다.** 대체 게이트는 §4.2. 사유를 기록한다 |

### 4.2 실측 결과와 대체 게이트 (C1/C2 — 구현 세션 2026-08-04)

**구현 세션이 착수 전에 손으로 T1b/T2 초안을 짜서 실측했다.**

| 문단 | 현재 | 초안 | 회수 |
|---|---:|---:|---:|
| `:87` 네 질문 → 표(T1b) | 198 | 173 | **25** |
| `:91` Authoring philosophy (T2) | 273 | 262 | 11 |
| `:116` Hard lines (T2) | 192 | 161 | 31 |
| `:93` 인터페이스 (T2) | 125 | ~112 | ~13 |
| **합계** | | | **~80** |

**`< 150` 분기다.** 계획 자신의 추정(~47)보다는 높지만 257에는 한참 못 미친다.

**`:87`이 거의 안 줄어드는 이유가 계획이 예상하지 못한 것이고, PR2에도 영향이 있다(→ `02-compression.md` §2.1의 C13).** 마크다운 표 문법이 `wc -w`에서 단어로 세어진다 — 행마다 파이프 3개, 구분행 하나, 헤더 행 하나. 4행짜리 표에서는 이 고정 비용이 삭제되는 연결 산문만큼을 되먹는다. T1만 적용한 첫 초안은 198 → **203**으로 오히려 늘었다.

**대체 게이트: `SKILL.md < 2,500단어`. "< 2,700"이 아니다.** 계획이 못 본 사실이 있다 — 이 repo 자신의 `.claude/harness-spec.md:14`가 *"Hold the always-loaded surface … under 2,500 words"*를 목표로 걸어두었고 `:43`이 *"`SKILL.md` is the sole always-loaded surface"*라고 그 surface를 명시한다. 2,700은 이 repo 자신의 spec을 조용히 깬다.

**PR1 1단계의 실제 절차:** 교리 4건을 온전한 문안으로 넣고 `:87`·`:116`을 변환한 뒤 `wc -w`로 잰다(에이전트 자기 보고를 믿지 않는다 — `03-verification.md` §3.6). 2,500 미만이면 그대로 간다. 넘으면 **멈추고 사용자에게 숫자를 들고 묻는다** — §3의 문안을 조일지, `harness-spec.md`의 목표를 올리고 Design rationale에 사유를 남길지. 어느 쪽이든 기계적 상한(D18/D21의 5,000토큰 ≈ 3,700단어)에는 여유가 크므로 이건 자기 일관성 판단이지 용량 판단이 아니다.

### 4.3 실행 결과 (2026-08-04)

| | 단어 |
|---|---:|
| 이전 | 2,411 |
| 교리 4건 | +257 |
| T2 회수 (절 삭제만, 패러프레이즈 없음) | −51 |
| 교리 문단에 교리를 자기 적용 | −15 |
| **최종** | **2,602** |
| 장문단(≥110w) 갇힌 단어 | **788 → 580** |

**C15 — 2,500은 목표가 아니라 통과해야 하는 테스트였다.** `tests/test_skill_surface.py::AlwaysLoadedBudgetTests.test_skill_md_within_budget`이 `WORD_BUDGET = 2500`으로 이를 강제한다. 계획의 대체 게이트 "< 2,700"을 그대로 썼다면 **테스트가 깨진 채로 머지됐을 것이고 PR1 수용 기준 5(테스트 전부 통과)와 정면으로 모순됐다.** 계획은 이 테스트의 존재를 몰랐다.

**결정 (사용자, 2026-08-04): `WORD_BUDGET`을 2,650으로 올리고 교리를 온전히 둔다.** 사유 셋 —

1. **2,500은 메커니즘이 아니다.** 같은 클래스가 `HARD_CEILING = 3750  # ~5,000 tokens; past here content is dropped`을 따로 갖고 있고 제품 사실은 그쪽 하나뿐이다. 2,500은 v2가 *덜어내는* 작업 중에 정한 자기 목표이고, v3는 *더하는* 작업이다.
2. **숫자가 안 굽으면 그게 rail이다.** `SKILL.md`가 "Numbers need their justification and their exception in the same breath"라고 쓰고 `skills.md:14`가 "a number stripped of its reason is a rail wearing a digit"이라고 쓴다. 근거가 바뀐 숫자를 붙들면 스킬이 자기 검사에 걸린다.
3. **D39와 일관된다.** PR2는 "과잉 트림은 분량이 아니라 claim 손실로 판정한다"인데 PR1에만 경성 분량 게이트를 걸면 두 PR의 기준이 어긋난다.

`HARD_CEILING`은 손대지 않았고 2,602는 그로부터 **1,148단어** 아래다. 테스트 docstring과 `harness-spec.md`의 Design rationale에 이 유도 과정을 적어 뒀다 — 다음 세대가 근거 없는 숫자를 물려받지 않도록.

**C14 — 코드펜스 안의 산문을 아무도 측정하지 않았다.** 정본 측정 스크립트가 ```` ``` ```` 펜스를 제거하고 시작하므로 펜스 내용은 장문단 통계에 한 번도 잡힌 적이 없다. `SKILL.md`의 Operating loop 펜스는 512단어(파일의 20%)이고 그 안 트리 주석에 파일에서 가장 밀도 높은 논증이 들어 있었다 — Wrap-up의 `validate_harness.py` 주석 하나에서만 29단어가 나왔다.

전 파일 실측(펜스 안에서 실단어 6개 이상인 줄 = 코드가 아니라 산문 주석으로 간주):

| 파일 | 총 단어 | 펜스 안 | 그중 산문 주석 |
|---|---:|---:|---:|
| `SKILL.md` | 2,611 | 512 (20%) | **368** |
| `e2e-testing.md` | 3,642 | 466 (13%) | **252** |
| `agents.md` | 3,377 | 200 (6%) | **187** |
| `workflows.md` | 2,295 | 353 (15%) | **137** |
| `claude-md-and-rules.md` | 2,905 | 142 (5%) | 103 |
| `interview.md` | 2,961 | 133 (4%) | 71 |
| `skills.md` | 3,005 | 65 (2%) | 11 |
| `hooks.md` | 5,537 | 64 (1%) | 0 |
| `hooks-events.md` | 3,777 | 285 (8%) | 0 |
| **합계** | | **2,220** | |

**`hooks.md`는 이 사각지대가 없다** (펜스 1%) — 최대 대상 파일이므로 직관적으로는 반대일 것 같지만 아니다. 실제 대상은 `e2e-testing.md`·`agents.md`·`workflows.md`이고, 이 셋에서 **약 580단어의 미측정 산문**이 나온다. 각 파일 압축 시 펜스 안 주석을 별도로 훑는다. 단 펜스 안의 *코드*는 판별식 원문대로 그대로 보존한다 — 대상은 트리 주석과 코드 옆 설명문뿐이다.

**교리를 짧게 쓰려다 의미를 잃는 것이 상시 로드 250단어보다 훨씬 나쁘다.** D34는 자기모순을 막으려는 장치이지 그 자체가 목적이 아니고, 목적을 위해 수단이 내용을 훼손하면 수단을 버린다. 이건 이 스킬이 "숫자에는 예외를 함께 준다"고 가르치는 것의 자기 적용이다.

## 5. `validate_harness.py` 체크 메시지 강화

현재 findings 대부분이 *무엇이 틀렸나*만 말한다. `add(findings, level, location, message)` (`validate_harness.py:48`)가 유일한 emit 헬퍼이고 호출 지점은 34곳이다.

**모범 형태는 이미 파일 안에 둘 있다 (C7 — 계획 초안은 한 개만 알고 있었다).**

```
:228        "no 'description' -- this skill can never auto-trigger"
:218-222    "frontmatter did not parse (...) -- the skill body still loads,
             but auto-triggering is silently dead"
현재 다수    "must be an object" / "does not exist" / "missing required 'name' field"
```

**규칙: 결과절을 붙일 수 있는 finding에만 붙인다.** `"top level of settings.json must be an object"`는 결과절이 없다 — 틀리면 그냥 안 된다. 반면 조용히 실패하는 것들은 전부 결과절을 가질 수 있다.

우선순위 대상:

| 위치 | 현재 | 붙일 결과절의 요지 |
|---|---|---|
| `:295` **agents** frontmatter 파싱 실패 | "frontmatter did not parse" | `:218`의 skills 판과 대칭으로. **C7:** 결과절이 없는 건 `check_agents`의 이쪽이고, `check_skills`(`:218`)에는 이미 붙어 있다 |
| `:240` SKILL.md 본문 길이 (`MAX_SKILL_BODY_LINES=500`) | "over the N-line guideline" | 왜 500행인가 — 긴 본문은 자기 핵심 지시를 묻는다 |
| `:317` 알 수 없는 model 값 | "verify this is a real model id/alias" | 미해결 시 무슨 일이 나는지 |
| `:460`/`:463` paths glob 괄호 | "unmatched brace" | glob이 안 맞으면 규칙이 아예 안 걸린다 |
| `:525` @import 대상 없음 | "import target does not exist" | launch 시점 확장이므로 세션 시작이 깨진다 |
| `:638` spec 부재 | "should carry a spec" | drift 검사가 기준을 잃는다 |
| ~~rules 파일 `paths:` 부재~~ | — | **C6 — 이미 목표 형태다.** `:416-420`이 *"no 'paths:' frontmatter -- this rule loads at launch just like CLAUDE.md, same as if it weren't split out at all"*라고 쓰고 `test_rule_without_paths_is_warning`이 이미 앵커하고 있다. 대상에서 제외 |

각 메시지 강화는 `tests/test_validate_harness.py`에 대응 assertion을 갖는다. **기존 idiom을 그대로 쓴다** — `BadHarnessTests`의 `_assert_warning_contains(location_substr, message_substr)` / `_assert_error_contains(...)` (`:44-58`, 부분 문자열 매칭). 메시지 문구를 테스트가 앵커하면 이후 희석이 회귀로 잡힌다.

**주의:** 메시지를 늘리는 건 상시 로드 비용이 아니지만(스크립트 stdout이다) 무한정 늘릴 것도 아니다. 한 finding당 결과절 한 절.

## 6. 가드레일 R1의 정확한 개정 문안

> **[C3/C4 — 구현 세션 2026-08-04] 이 절의 지시 두 개가 틀렸다.**
>
> **(a) 경로.** R1은 `research/audit-synthesis.md`가 아니라 **`docs/plan/v2/research/audit-synthesis.md`**에 있다.
>
> **(b) 그 파일을 고쳐 쓰면 안 된다.** 문서 3–8행이 직접 이렇게 쓴다 — *"이 문서는 원본 그대로 보존한다 — 계획 문서가 여기서 결정을 추출했고, 인용된 라인 번호와 측정치의 출처가 여기다."* 인용 원장이지 살아 있는 스펙이 아니고, `00-overview.md` §0의 "v2 계획은 역사적 기록으로 온전히 남는다"와도 그래야 맞다. **개정본의 정본은 신규 `docs/plan/v3/04-guardrails.md`이고, v2의 R1 자리에는 개정 포인터 한 줄만 남긴다.**
>
> **(c) 10쌍의 행 번호는 전부 낡았다.** 예: `workflows.md`의 pure-literal `meta` 린트는 R1이 적은 `validate_harness.py:309-314`가 아니라 현재 **`:336-337`**, `Date.now()` 금지는 `:316-326`이 아니라 **`:344-346`**이다. 산문 쪽 인용도 어긋난다 — R1의 `hooks.md:70`(unanchored matcher)은 현재 `:72`다. v2 문서가 동결됐으므로 당연한 표류다. **10쌍 각각을 현재 파일에서 다시 찾아 분해한다.** 짝을 못 찾는 쌍은 "쌍이 소멸함"으로 기록한다.

`docs/plan/v2/research/audit-synthesis.md` §4의 R1은 현재 이렇게 읽힌다: **"린트 체크가 남아 있는 산문 gotcha는 절대 자르지 않는다."** 10쌍이 짝지어져 있다.

개정:

> **R1 (v3) — 린트 체크가 있는 gotcha는 산문에서 *결정*을 남기고 *결과*를 체크 메시지로 옮긴다. 산문 전체를 지우지는 않는다.**
> 근거: 린트는 생성 후에 돌므로 작성 시점의 결정을 대신할 수 없다. 옮길 수 있는 건 "틀리면 무슨 일이 나는가"이고, 남겨야 하는 건 "그래서 무엇을 고르는가"다.
> 단방향 예외는 유지: `workflows.md:33`의 pure-literal `meta` 요구는 린트가 `meta`의 *존재*만 확인하고 *순수성*은 확인하지 않으므로, 산문이 전부 남는다.

10쌍 각각에 대해 구현 세션이 "결정 / 결과" 분해를 `04-guardrails.md` §2에 기록한다. 분해가 안 되는 쌍(결과가 곧 결정인 경우)은 손대지 않는다.

## 7. PR1 수용 기준

1. `SKILL.md` 단어 수가 **2,500 미만**이다 (§4.2 — D34의 2,411 순감소는 실측으로 폐기됐고, 대체 게이트는 이 repo 자신의 `harness-spec.md:14`가 이미 걸어둔 숫자다). 넘었다면 사용자와 합의한 조치와 사유가 기록됐다.
2. 추가된 교리 4건이 전부 `SKILL.md`에 있고, `skills.md` §Conviction·§Don't write는 삭제되지 않았다.
3. `grep -cE "rubric|failing test|schema" SKILL.md` ≥ 1 — rich references가 실제로 도달한다.
4. 강화된 체크 메시지마다 `tests/test_validate_harness.py`에 문구를 앵커하는 assertion이 있다.
5. `for f in tests/test_*.py; do python3 "$f"; done` 전부 통과, `validate_harness.py --path . --strict` exit 0. (C9 — `python3 tests/*.py`는 동작하지 않는다.)
6. `docs/plan/v3/04-guardrails.md`에 R1(v3) 문안과 10쌍의 "결정/결과" 분해가 있고, v2 원본에는 포인터 한 줄만 추가됐다 (C3).
7. **§3.1 문단이 자기 예시다** — 다섯 가지 형태에 설명이 붙지 않았다. 이건 리뷰어가 눈으로 확인한다.

> **범위 (사용자 확인, 2026-08-04):** 배포되는 것은 `.claude/skills/harness-creator/` 안의 `SKILL.md`·`references/`·`scripts/` 뿐이다. 루트 `CLAUDE.md`는 스킬의 구성 요소가 아니라 이 레포를 만들 때 쓰는 비계이므로 **PR1에서 손대지 않는다.** `00-overview.md` §5b가 지적한 끊어진 포인터는 릴리즈 위생 커밋으로 옮긴다.
