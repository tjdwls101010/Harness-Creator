# harness-creator v4 — 번들 스크립트 CLI 자기서술성

> 구현 완료(2026-08-19). v1(`docs/plan/00-*` ~ `06-*`)·v2(`docs/plan/v2/`)·v3(`docs/plan/v3/`) 계획은 역사적 기록으로 온전히 남는다. 이 세대는 **어떤 기존 결정도 개정하지 않는다** — D16·D31·D33·WS2-6을 인용해 그 위에 검사 하나를 더한다.

## 1. 한 문장

**`SKILL.md:106`은 스크립트 CLI를 인터페이스 표면 첫 번째로 꼽지만, 그 주장은 `--help`가 완비돼 있어야만 성립한다 — 그리고 스킬은 그걸 가르치지도, 검사하지도 않았다.**

## 2. 진단 — 구멍이 세 군데였다

교리의 논거는 "an interface is re-read from the tool's own signature on every use"다. 즉 **시그니처가 스스로를 설명한다**는 전제 위에 서 있다. `help=` 없이 선언된 인자는 `--help`에 이름만 찍히므로 모델이 소스를 열게 되고, 인터페이스가 조용히 문서로 되돌아간다. 스타일 문제가 아니라 교리가 약속한 이득이 발생하지 않는 상태다.

| # | 구멍 | 위치 |
|---|---|---|
| 1 | 교리가 생성기에 전달되지 않음 | `references/skills.md:40`의 유일한 스크립트 문단이 *파라미터화*만 다룬다. 자기서술성은 어디에도 없다 |
| 2 | 정본 예시가 틀린 것을 가르침 | `tests/fixtures/good-harness/.../scripts/run.py`가 맨 `ArgumentParser()`와 `help=` 없는 `--target`을 담고 있었다 |
| 3 | 검증기가 스크립트 내부를 안 봄 | `validate_harness.py`에서 `scripts/`는 `_SKILL_POINTER_RE` 하나뿐 — 산문이 가리킨 경로의 실재만 확인 |

`--help` 완비 요구 자체는 `docs/plan/04-scripts-and-validation.md:7`에 이미 있었다. 다만 그건 harness-creator **자신의** 스크립트에 건 규칙이고, 출하되지 않는 개발 문서에만 살아 있었다. 도구는 규칙을 지키는데 그 규칙이 산출물로 전달된 적이 없다 — 실제로 자기 다섯 스크립트는 전부 `description=__doc__` + 전 인자 `help=`이고, `hook_event.py:126`은 `choices=`까지 쓴다.

구멍 #2가 파급이 가장 크다. 생성물은 정본 픽스처를 모방하기 때문이다.

## 3. D43 — 번들 스크립트 CLI 자기서술성 검사

`validate_harness.py`가 `.claude/skills/*/scripts/**/*.py`를 `ast`로 파싱한다(**실행하지 않는다**).

| 검사 | 심각도 |
|---|---|
| `add_argument`에 `help=` 누락 | E |
| `add_parser`에 `help=` 누락 | E |
| 파싱 불가(SyntaxError) | E |
| `ArgumentParser`에 `description=` 누락 | W |
| `description=__doc__`인데 모듈 docstring 없음 | W |

**심각도를 나눈 근거:** 인자를 선언해 놓고 설명을 안 붙일 정당한 이유는 없다(E). 반면 플래그 두 개짜리 스크립트가 파서 설명을 생략하는 건 방어 가능하다(W). E여야 "오류 0까지 수정 후 완료" 하드라인이 루프를 닫는다 — 원래 불만이 "간혹 빼먹는다"였고, W는 무시되므로 해결이 안 된다.

**범위를 Python argparse로 한정한 근거:** WS2-6의 원칙 — *"정상 하네스에서 울리는 체크는 체크가 없는 것보다 나쁘다."* `.sh`·`.js`는 usage 관례가 제각각이라 오탐이 나고, 오탐 한 번이면 경고 전체가 무시된다. `.claude/hooks/`는 stdin JSON을 읽지 CLI가 아니므로 대상이 아니다. click·typer 스크립트는 `.add_argument`를 키로 삼는 구조 덕분에 별도 게이트 없이 침묵한다.

**문구 품질은 채점하지 않는다.** WS2-6이 기각한 검사들과 같은 함정이다 — 어휘 신호로 좋은 설명과 나쁜 설명을 가를 수 없고, 만들면 생성기가 프로젝트가 아니라 린터를 만족시키려 글을 쓰게 된다.

### WS2-6의 기각 목록을 뒤집는 것이 아니다

기각된 검사들(디렉터리 트리 감지기, 의존성 목록 감지기)은 **좋은 경우와 나쁜 경우를 가르는 어휘 신호가 없어서** 기각됐다. 이 검사는 `help=` 키워드의 유무라는 이진 사실을 본다. 판정에 해석이 개입하지 않는다.

## 4. 산문/검사 분담 (D33 적용)

*"산문은 결정을, 체크는 결과를."*

- **산문** — `references/skills.md`의 파라미터화 문단 뒤 3문장. 결정만 담는다: 파라미터화는 필요조건이지 충분조건이 아니고, 전 인자에 `help=`, 파서에 `description=`, 닫힌 공간엔 `choices=`.
- **검사** — consequence를 나른다. "모델이 소스를 열게 된다"는 문구는 `ConsequenceClauseTests`가 앵커로 고정한다. 그 클래스의 규약상 근거가 `references/*.md`에 있어야 하므로, 산문 없이 검사만 넣는 경로는 애초에 막혀 있었다.

새 `references/scripts.md`는 만들지 않았다. 번들 스크립트는 독립 컴포넌트 타입이 아니고(D31), 스킬 생성과 같은 호출 경로에 있어 분리해도 읽는 양이 줄지 않는다.

## 5. TDD가 걷어낸 죽은 코드 2건

계획 초안에 있었으나 **red를 만들 수 없어서 구현 전에 뺐다.** 두 건 모두 "먼저 실패하는 테스트를 쓴다"를 지키려는 순간 드러났다.

- **`help=argparse.SUPPRESS` 면제** — SUPPRESS는 `help=`에 *담겨서* 전달되므로 "`help=` 키워드가 있는가" 검사를 이미 통과한다. 면제 분기가 통과시킬 red가 없었다.
- **`import argparse` 게이트** — `.add_argument` 호출을 키로 삼으므로 argparse를 안 쓰는 스크립트는 구조적으로 이미 침묵한다.

후자는 슬라이스가 아니라 **회귀 핀**으로 남겼다(`cli-edge-cases`의 `stdin_helper.py`). 작성 즉시 green이므로 red→green 슬라이스인 척하지 않고 경계를 문서화한다고 테스트에 적었다.

## 6. Seam

단 하나: **`vh.run(root, strict)` → `(findings, exit_code)`**. 검사 내부 함수는 어떤 테스트도 직접 부르지 않는다 — 슬라이스가 여섯 개고 매번 내부 모양이 바뀌므로, 시그니처에 테스트를 못 박으면 이후 슬라이스가 거기 갇힌다. `HeuristicFalsePositiveTests`가 `_check_*`를 직접 부르는 선례가 있으나 이번엔 따르지 않았다.

false-positive 가드는 `good-harness`가 아니라 **새 `tests/fixtures/cli-edge-cases/`**에 둔다. `good-harness`가 생성물이 모방하는 교육용 정본이라는 게 구멍 #2의 핵심이라, 거기에 `action="version"` 같은 고문 케이스를 섞으면 가르치는 바가 흐려진다.

탐색 헬퍼는 `harness_common.py`가 아니라 `validate_harness.py`에 인라인했다. 공유 규약은 두 구현이 어긋나는 걸 막으려는 것인데 호출자가 하나면 어긋날 대상이 없다.

## 7. 범위 밖

- **`SKILL.md` 무수정.** 검사는 `validate_harness.py` 내부 동작이고, 생성기가 알아야 할 내용은 스킬 생성 시 이미 로드되는 `references/skills.md`로 간다. v3의 순감소 압박(D34) 아래 늘릴 이유가 없다.
- **워크플로우 `args`.** 같은 렌즈를 대면 `SKILL.md:106`의 다섯 인터페이스 표면 중 검증기가 보는 건 스킬 `description`과 에이전트 `tools:` 둘뿐이다. 워크플로우 `args`는 스크립트 CLI와 **같은 종류의 구멍이고 아직 열려 있다.** 다음 세대 후보.
- `--help` 문구 품질 채점, 비-Python 스크립트.

## 8. 완료 판정

1. `python3 -m unittest discover -s tests -q` 전부 통과 (176 tests).
2. `validate_harness.py --path . --strict` exit 0 — 자기 다섯 스크립트가 새 검사를 통과한다.
3. `good-harness`가 `--strict`에서도 findings 0 — `run.py`가 모범 사례로 교체됐다.
4. `cli-edge-cases`가 findings 0 — 가드가 산다.
5. `ConsequenceClauseTests`에 `help=` 앵커 1건 추가, 근거가 `references/skills.md`에 있다.
