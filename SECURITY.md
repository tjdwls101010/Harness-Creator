# Security Policy

## Supported versions

Security support is best effort and applies only to the latest tagged release.

| Version | Supported |
|---|---|
| Latest tagged release | Yes |
| Older releases and untagged commits | No |

Support status does not create a response or fix SLA.

## Report a vulnerability

Do not open a public issue for a suspected vulnerability.

Use [GitHub private vulnerability reporting](https://github.com/tjdwls101010/Harness-Creator/security/advisories/new). Include:

- the affected release or commit;
- the component and execution path involved;
- reproduction steps or a minimal proof of concept;
- the impact you believe is possible;
- any conditions required to trigger it;
- whether you know of public disclosure or exploitation.

Reports are reviewed on a best-effort basis. The project does not promise an acknowledgment, remediation, disclosure, or release timeline.

## Scope

Security-sensitive areas include plugin packaging, generated hooks and permissions, subprocess execution in the Python tools, path handling, and behavior that could cause unintended file or command access.

Reports about a generated harness should distinguish a Harness Creator defect from project-specific code the user approved and generated.

## Disclosure

Please keep details private until the maintainer has assessed the report. If a fix is feasible, disclosure timing will be coordinated case by case without a guaranteed schedule.
