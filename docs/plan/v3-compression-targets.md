# v3 후보 — v1 산문의 principle 중심 압축

> 2026-08-03, v0.2.0 릴리즈 직후 작성. **아직 계획이 아니라 측정된 후보 목록이다.**
> 착수 전에 범위를 합의해야 한다.

## 왜 이게 남았나

v2의 전제는 "지능이 올라갈수록 rail을 걷어내고 principle을 압축해 넣는다"였고, 총 분량이 줄 거라 예상했다. 실제로는 26,937 → 30,712 (+14%)로 **늘었다.** 두 가지가 겹쳤다.

1. **검증된 메커니즘 ~2,000단어가 추가됐다** — workspace trust, 보호 경로, auto memory, `Write(path)` 미매칭, compaction 생존 매트릭스 등. 이건 아티클 기준으로도 남겨야 하는 것들이고, 빼서 숫자를 맞추는 건 "틀린 gotcha보다 없는 gotcha가 낫다"의 역적용이다. **되돌리지 않는다.**
2. **v2 압축 패스에서 −1,025를 회수했지만, 그 77%가 내가 v2에서 쓴 글이었다.** v1 원본은 계획이 이름으로 지목한 3블록(레시피 2·3 JSON, `skills.md` 재논증, Bad CLAUDE.md 블록)만 건드렸다.

즉 **v1 본문은 사실상 손대지 않은 상태**이고, 원래 관심사가 겨냥하던 대상이 바로 거기다.

## 측정치 (v0.2.0 기준)

110단어를 넘는 문단이 **43개, 6,436단어**. 그중 **96%(6,167단어)가 v1 원본 그대로**다.

파일별 상위 후보 (단어 수 / 파일 / 첫 구절):

```
253  agents.md       1. **Restate the rule directly in the delegation prompt text.**
232  skills.md       But splitting has a cost that points the opposite direction...
213  skills.md       The interview should actively look for consolidation...
212  agents.md       Leave `model` unset (or set it to `inherit`) unless...
196  agents.md       Hooks declared inside an agent's own frontmatter...
190  e2e-testing.md  The likely-correct approach, and the one run_e2e.py implements...
180  agents.md       Agent count is itself a cost, independent of any single agent's quality...
176  e2e-testing.md  The second habit worth carrying over just as deliberately...
169  e2e-testing.md  validate_harness.py is free and structural...
162  agents.md       An agent's identifier — the thing Claude actually matches on...
161  workflows.md    If the answer is no — the task's shape genuinely varies...
159  workflows.md    This matters because a thick workflow...
159  skills.md       What survives that filter is domain knowledge...
157  agents.md       Concretely, when the interview surfaces something that sounds agent-shaped...
155  agents.md       The two most commonly auto-invoked built-in subagents...
```

재측정 명령:

```bash
cd .claude/skills/harness-creator && python3 - <<'PY'
import pathlib, re
rows=[]
for f in sorted(pathlib.Path("references").glob("*.md")):
    t=re.sub(r"```.*?```","",f.read_text(),flags=re.S)
    for p in t.split("\n\n"):
        s=p.strip()
        if s.startswith(("#","|","-","*",">")): continue
        if len(s.split())>=110: rows.append((len(s.split()),f.name,s[:90]))
rows.sort(reverse=True)
for w,f,s in rows: print(f"{w:4d}  {f:24} {s}")
print(f"\n{len(rows)} paragraphs, {sum(r[0] for r in rows)} words")
PY
```

## 하지 말아야 할 것

- **전면 재작성 금지 (D13).** "수천 시간의 교훈이 현재 문장에 암묵적으로 박혀 있어 재작성에서 소실될 위험이 실재한다." v2 감사가 v1 doctrine을 5개 렌즈로 훑고 "틀린 doctrine 주장은 하나도 없었다"고 판정했다. 고칠 건 밀도이지 내용이 아니다.
- **길이가 곧 밀도인 문단은 건드리지 않는다.** 위 목록에도 섞여 있다 — `agents.md`의 Explore/Plan 대응책 3가지는 각각 "언제 쓰는가"가 붙은 라우팅 정보이고, `skills.md`의 목록 예산 설명은 숫자와 귀결이 얽혀 있다. 판별식은 v2 계획 §5 그대로.
- **분량 목표를 먼저 정하지 않는다.** v2의 WS6가 그 함정이었다. 목표 숫자가 있으면 가드레일을 자를 압력이 생긴다.

## 반드시 해야 할 것

- **파일당 적대적 검증.** v2 압축에서 이 방식으로 손실 4건을 잡았고, 그중 하나가 *"이 줄을 지우면 클로드가 틀리나?"* 라는 **검사 문장**이었다 — 원칙만 남기고 검사를 자른, rail/principle 역전 그 자체. 검증 없이는 반드시 재발한다.
- **`tests/test_skill_surface.py`의 `GuardrailTests`를 믿되 과신하지 않는다.** 앵커는 *삭제*를 잡지 *희석*을 잡지 못한다.
- **별도 브랜치·별도 PR.** v0.2.0은 "결함 12건 + 검증된 메커니즘 + always-loaded −50%"로 검증이 끝났다. 성격이 다른 작업을 섞으면 리뷰가 불가능해진다.

## 현실적 기대치

6,436단어 전부가 군더더기는 아니다. **회수 가능량은 1,500~2,500단어** 정도로 보고, 그보다 많이 나오면 과잉 트림을 의심할 것.

always-loaded(2,411단어)는 이 작업으로 거의 움직이지 않는다 — 대상이 전부 조건부 로드되는 reference이기 때문이다. **이건 세션당 비용 절감이 아니라 밀도 개선이다.** 그 구분을 착수 전에 분명히 해두는 편이 낫다.

## v0.2.0이 남긴 별건 항목

- **README 낡음**: 배지 `version-0.1.0`(7행), "v0.1.0 is complete…"(164행). 릴리즈가 만든 staleness라 문서 트랙 작업.
- **A4 갭 (L4에서 확인)**: 생성된 하네스가 "워크플로우 에이전트는 `acceptEdits`로 돌고 세션 allowlist를 상속한다"를 반영하지 못한다. `workflows.md`에 산문은 있으나 도달하지 않는다. 회귀가 아니라 기존 미달.
- **L5 미실행**: 대화형 인터뷰 도그푸딩. `AskUserQuestion`이 headless/서브에이전트에 없어 자동화 불가. v2가 인터뷰를 네 곳 건드렸으므로(I1 스코프 축, I3 인터페이스 프로브 + 권한 확대 별도 질문, I4 배포 축, I2 감산 게이트) 사람이 한 번 돌려봐야 한다.
