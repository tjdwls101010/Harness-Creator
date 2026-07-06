# 01 — 아키텍처: repo 구조, 패키징, 파일 트리

## 1. 이 repo의 최종 구조

```
Harness-Creator/                        # github.com/tjdwls101010/Harness-Creator
├── .claude-plugin/
│   ├── plugin.json                     # 플러그인 매니페스트
│   └── marketplace.json                # 이 repo 자체가 마켓플레이스
├── .claude/
│   └── skills/
│       └── harness-creator/            # ★ 본체 (아래 §3)
├── CLAUDE.md                           # 이 repo 자체의 개발용 CLAUDE.md (M0에서 작성)
├── README.md                           # 설치법(플러그인/심링크), 사용법, 철학 요약
├── docs/
│   └── plan/                           # 이 계획 문서 (구현 후에도 설계 기록으로 유지)
├── tests/
│   └── fixtures/                       # 스크립트 자기 테스트용 정상/오류 하네스 픽스처 (M2)
│                                       #   — repo 루트에 둔다: 스킬 디렉토리에 넣으면 개발 전용
│                                       #   파일이 플러그인 사용자에게 배포됨 (철학 #4 위반)
└── .tmp/                               # gitignored — docs_claude 스냅샷 등 로컬 참조 자료
```

### 패키징 (D11)

- `marketplace.json`: `name`(kebab-case), `owner{name}`, `plugins[{name, source: "./"}]` 필수.
- `plugin.json`: `name: "harness-creator"` 필수. 컴포넌트는 기본적으로 플러그인 루트의
  `skills/`에서 스캔되지만, **`skills` 경로 필드는 기본 스캔에 추가(ADD)하는 방식**이므로
  `"skills": "./.claude/skills"`로 지정해 같은 디렉토리가 (a) 이 repo에서의 프로젝트 스킬
  (도그푸딩)과 (b) 플러그인 컴포넌트를 겸하게 한다.
  - **[V1 — 실측 완료, M0]** 동작 확인됨. `claude plugin validate .`로 매니페스트 통과,
    로컬 마켓플레이스 추가(`claude plugin marketplace add .`) 후 설치(`claude plugin install
    harness-creator@harness-creator`)하면 `claude plugin details harness-creator`가
    `Skills (1) harness-creator`를 정확히 보고한다. `"skills": "./.claude/skills"` 경로
    지정이 실제로 동작함 — 폴백(루트 `skills/`로 이동) 불필요.
- 버전: `version`을 명시(semver). 생략 시 git SHA 버전닝(커밋마다 업데이트로 간주)이라
  의도치 않은 잦은 업데이트 유발.
- **플러그인 제약이 harness-creator에는 안 걸린다**: 제약(플러그인 agents의
  hooks/mcpServers/permissionMode 무시, workflows 배포 불가)은 플러그인이 컴포넌트로 싣는
  것들에 대한 제약이다. harness-creator는 스킬 하나 + 내부 스크립트뿐이고, agents/workflows는
  플러그인 컴포넌트가 아니라 **대상 프로젝트에 생성해주는 산출물**이므로 무관.
- **주의(심링크와 플러그인 설치 동시 활성 금지)**: 개발자 자신의 머신에서 심링크
  (`~/.claude/skills/harness-creator`, bare 이름으로 즉시 트리거)와 플러그인 설치
  (`harness-creator@harness-creator`, `/harness-creator:harness-creator`로 네임스페이스)를
  동시에 활성화하면 같은 스킬이 서로 다른 두 이름으로 중복 등록된다(심링크는 동일 타깃 도달 시
  dedupe되지만, 플러그인 스킬은 별도 네임스페이스라 dedupe 대상이 아님 — `.tmp/docs_claude/
  02-build-with-claude-code/03-skills/01-extend-claude-with-skills.md` §symlink 문단).
  일상 개발은 심링크만 유지하고, 플러그인 배포 흐름을 스모크 테스트할 때만 일시적으로
  마켓플레이스 추가+설치 후 검증이 끝나면 `claude plugin uninstall`+`marketplace remove`로
  되돌린다(M0에서 실제로 이 절차로 검증 후 정리함).

### 네이밍 **[V2 — 문서로 해소, M0. 실측 불필요했음]**

플러그인 스킬은 `/플러그인명:스킬명`으로 네임스페이스된다(공식 문서로 확인 —
`.tmp/docs_claude/02-build-with-claude-code/04-plugins/02-create-plugins.md`,
`05-reference/08-plugins-reference.md`). 안 B(디렉토리 `harness-creator` 유지, 플러그인
경로는 `/harness-creator:harness-creator` 감수)로 확정한다:

- 안 A(디렉토리명을 `create`로) 기각: 심링크 사용자에게 `/create`라는 지나치게 범용적인
  이름을 남긴다.
- 안 C(플러그인 루트에 단일 SKILL.md, `skills` 매니페스트 필드 없이) 기각: 공식 문서상 가능한
  패턴이지만, 이 경우 스킬이 플러그인 루트에 있어야 하므로 `.claude/skills/harness-creator/`
  구조(심링크 개발 루프·프로젝트 스킬 도그푸딩이 의존하는 경로, D11)와 양립하지 않는다.
  D11이 요구하는 "플러그인+심링크 병행"을 깨뜨리므로 실측 없이 기각.
- 안 B 확정 근거: description 기반 자동 트리거가 주 진입 경로이므로 네임스페이스된 슬래시
  명령의 실사용 영향은 작고, 심링크 경로에서는 애초에 bare `harness-creator`로 트리거된다
  (플러그인 경로 사용자만 `:harness-creator` 접미를 본다). README에 두 경로의 호출 형태
  차이를 명시한다.

### 로컬 경로 마켓플레이스 설치의 캐시 누출 (M5에서 발견)

`claude plugin marketplace add ./`(또는 절대 경로)처럼 **로컬 디렉토리를 소스로** 설치하면
git이 아니라 파일시스템을 그대로 복사하는 것으로 보인다 — `.gitignore`된 `.tmp/`(로컬 전용
문서 스냅샷, 수십 MB)까지 `~/.claude/plugins/cache/`에 통째로 복사됨을 실측 확인했다
(`git ls-files`로 `.tmp/`가 추적되지 않음을 재확인 — 실제 GitHub 소스
`tjdwls101010/Harness-Creator` 설치는 git 추적 콘텐츠만 가져오므로 이 문제와 무관할 것으로
추정되나, 이 세션에서 GitHub 경로 자체는 실측하지 못함). 개발/테스트 중 로컬 경로로
`marketplace add`를 쓸 때는: (1) `claude plugin uninstall` + `marketplace remove`만으로는
`~/.claude/plugins/cache/<name>/`가 남는다 — 수동으로 지워야 함. (2) 이 캐시에 `.tmp/`처럼
큰 로컬 전용 디렉토리가 딸려올 수 있으니 정리 시 크기를 확인할 것.

### 심링크 개발 루프 (D11)

```bash
ln -s /Users/seongjin/Documents/Coding/harness-creator/.claude/skills/harness-creator \
      ~/.claude/skills/harness-creator
```

- 심링크된 스킬 디렉토리는 공식 지원(중복 도달 시 dedupe됨).
- SKILL.md 수정은 세션 내 즉시 반영. 마켓플레이스 설치본은 `~/.claude/plugins/cache`에
  복사되므로 `claude plugin update` 필요 → 개발은 심링크, 배포는 플러그인.
- README에 두 설치 경로를 모두 문서화한다.

## 2. 스킬 본체 파일 트리

```
.claude/skills/harness-creator/
├── SKILL.md                     # 오케스트레이터: 철학·라우팅·운영 플로우 (< 500줄, 목표 ~350줄)
├── references/
│   ├── claude-md-and-rules.md   # CLAUDE.md + rules 작성 가이드 (생성 시점 로드)
│   ├── skills.md                # 스킬 작성 가이드 (생성 시점 로드)
│   ├── hooks.md                 # hooks 설계 가이드 + gotchas (생성 시점 로드)
│   ├── hooks-events.md          # 30개 이벤트 × I/O 계약 밀도 테이블 (hook 세부 설계 시 로드)
│   ├── agents.md                # 서브에이전트 작성 가이드 (생성 시점 로드)
│   ├── workflows.md             # dynamic workflow 작성·활용 가이드 (생성 시점 로드)
│   ├── interview.md             # 인터뷰 프로토콜 상세 + 스펙 문서 템플릿 (인터뷰 시작 시 로드)
│   └── e2e-testing.md           # e2e 검증 설계 + headless claude -p 기법 (검증 단계 로드)
└── scripts/
    ├── validate_harness.py      # 결정론적 린트 (04 문서)
    ├── audit_harness.py         # 기존 하네스 인벤토리 (04 문서)
    ├── test_hook.py             # 훅 단위 테스트 (04 문서)
    └── run_e2e.py               # headless 세션 런처 (04 문서)
```

### 분할 근거 (progressive disclosure — 로드 시점 기준)

- SKILL.md: 모든 경로에서 필요한 것만 — 철학, 레이어 라우팅 프레임워크, 운영 플로우(감사→인터뷰→생성→검증→반복), 스크립트 사용법 요약. 컴포넌트별 세부는 담지 않는다.
- references/는 **"어떤 컴포넌트를 생성하는가"라는 분기**에 대응한다. CLAUDE.md만 만드는 세션이
  hooks 이벤트 테이블을 로드할 이유가 없다 — 로드 시점이 명확히 다르므로 분할이 정당하다.
- `hooks.md` vs `hooks-events.md` 분할: 설계 원칙·gotcha(항상 필요)와 30개 이벤트 전수
  테이블(특정 이벤트 세부 설계 때만 필요)은 로드 시점이 다르다. 단 hooks.md에 이벤트
  선택 요약표(이벤트명 + 한 줄 용도)는 포함해 라우팅 실패를 막는다.
- **분할하지 않는 것**: 인터뷰 단계별 파일 분할(전 단계가 한 흐름에서 쓰임 — interview.md 하나),
  컴포넌트별 템플릿 파일 분리(각 가이드 문서에 인라인 예시로 포함 — 별도 templates/ 디렉토리는
  라우팅 비용만 늘림).
- 각 references 파일의 상세 목차는 `05-references-inventory.md`.

## 3. 생성 산출물의 표준 형태 (대상 프로젝트에 만들어지는 것)

```
<target-project>/
├── CLAUDE.md                        # < 200줄, 포인터 정책 (03 문서)
└── .claude/
    ├── harness-spec.md              # 스펙 문서 (02 문서 §4) — 단일 진실 공급원
    ├── settings.json                # hooks + permissions
    ├── rules/*.md                   # 경로 스코프 규칙 (필요 시)
    ├── skills/<name>/SKILL.md       # 도메인 스킬 (필요 시)
    ├── agents/*.md                  # 커스텀 서브에이전트 (필요 시)
    ├── workflows/*.js               # 사전 정의 워크플로우 (필요 시, D12 원칙)
    └── hooks/*.sh|*.py              # 훅 스크립트 실체 (settings.json이 참조)
```

- 훅 스크립트는 `.claude/hooks/`에 두고 settings.json에서
  `${CLAUDE_PROJECT_DIR}/.claude/hooks/<name>` 절대 경로로 참조한다(exec form 권장).
- 모든 산출물은 커밋 가능한 표면만 사용한다. `settings.local.json`은 개인 설정이 필요한
  경우(예: 개인 API 키 요구 훅)에만, 사용자에게 고지 후 생성.

## 4. 대상 프로젝트에 쓰기 작업 시 주의 (protected paths)

`.claude/` 하위와 `.mcp.json` 등은 **protected path**라서 어떤 allow rule로도 쓰기 프롬프트를
사전 제거할 수 없다(안전 검사가 allow rule 평가보다 먼저 실행됨). 실사용 흐름:

- 첫 `.claude/` 쓰기에서 "Yes, and allow Claude to edit its own settings for this session"
  옵션을 선택하면 그 세션 동안 후속 `.claude/` 쓰기가 승인된다.
- SKILL.md의 생성 단계 지침에 "생성 시작 전 사용자에게 이 프롬프트가 뜰 것을 미리 알리라"를
  포함한다 (UX 매끄러움).
