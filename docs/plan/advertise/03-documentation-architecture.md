# Documentation architecture

## 1. Front door

The root README carries the discovery and first-install path. It explains the product in roughly one screen, shows the main workflow, gives the recommended installation first, distinguishes structural and behavioral validation, and hands depth to `docs/wiki/`.

## 2. Canonical documentation

Canonical documentation remains tracked in `docs/wiki/` and follows Diátaxis:

- Tutorials build confidence through a guided first result.
- How-to guides solve a concrete user task.
- Reference describes commands, files, states, compatibility, and limitations.
- Explanation develops the mental model and design rationale.

`docs/wiki/README.md` indexes every canonical page. `Overview.md` introduces the set. `_Sidebar.md` provides compact local navigation.

## 3. Compatibility policy

The pre-overhaul flat wiki filenames remain as short redirect-style compatibility pages through v1.0. Each names one canonical replacement and contains no competing source of truth.

The GitHub Wiki feature should be disabled after merge so the tracked repository documentation is the only maintained wiki surface.

## 4. Content ownership

- README: discovery, evaluation, installation, and map.
- Tutorials: safe learning paths.
- How-to: task completion.
- Reference: exact product surface.
- Explanation: rationale and mental models.
- `docs/plan/`: design and launch records for maintainers.

## 5. Link rules

Internal links are relative, image paths are repository-relative, and every canonical page is reachable from the wiki index. External sources are linked at the point of the claim. The internal-link workflow blocks pull requests; the scheduled external-link workflow reports outages without blocking unrelated pull requests.

## 6. Language

New and rewritten public materials are English. The frozen skill directory is an explicit exception: its existing Korean trigger metadata remains unchanged and may be surfaced by third-party indexes.
