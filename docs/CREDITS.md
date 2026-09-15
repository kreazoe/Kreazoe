# Frozen credits integration

`data/credits-registry.v1.json` is the authoritative structured V1.0 dataset. It retains all supplied fields and the excluded record. It is never rewritten by the renderer. Line-wrapped notes are stored as single JSON strings without changing their wording.

The site is static. `tools/build_credits.py` reads the registry and emits the credit section into `index.html`; the rest of the portfolio is untouched. `assets/credits.js` progressively enhances those records with search and filters. It does not create roles, fetch credits, or research evidence. All credit content is available without JavaScript.

Public badges belong only to `public_roles`: A = Public metadata; B = Publicly documented. First-hand role blocks read only `first_hand_roles` and never receive badges or public evidence links. Role filters use the selected evidence scope. Existing frozen exceptions retain co-production, attribution and project-level context. These contextual sentences do not supply roles or badges.

## Validate the current preview

Run from the repository root:

```sh
python tools/build_credits.py
python tools/check_credits.py
python tools/test_rendered_audit.py
python tools/audit_rendered_credits.py --report tools/credits-audit.v1.json
```

The independent rendered audit parses actual role-list text and badge placement, not just data attributes. It checks every credit against its corresponding registry record. It fails on an extra/missing/converted role, wrong tier label, badge outside public scope, evidence mismatch, unscoped role list, or first-hand verification. The report records dataset and HTML SHA-256 hashes. Negative tests deliberately introduce role and badge errors and require rejection.

## Future authorized registry versions

Keep V1.0 intact. Add the supplied frozen version as a new JSON file with the same schema, then regenerate only the credit section:

```sh
python tools/build_credits.py --registry data/credits-registry.v2.json
python tools/audit_rendered_credits.py --registry data/credits-registry.v2.json --report tools/credits-audit.v2.json
```

These commands illustrate the update path; V2 is not supplied or active. Version labels, record counts, artist/role choices and rendered role lists are derived from the selected data. No manual discography markup rewrite or new framework is needed. V1-specific regression fixtures stay pinned to V1. Review any new explicit presentation constraints supplied with a future version rather than inferring them. Preview validation and production authorization remain separate.
