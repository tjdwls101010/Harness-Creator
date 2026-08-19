---
name: edge-skill
description: >
  Exercises argparse shapes the CLI self-description check must stay silent on.
  Use only as a false-positive fixture for validate_harness.py.
---

# Edge-case skill

Every script under `scripts/` here is a correct CLI. Any finding this fixture
produces is a false positive in the check, not a defect in the fixture.
