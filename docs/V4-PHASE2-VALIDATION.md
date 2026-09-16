# V4 Phase 2 preview validation

Resumed from preview commit 9a793fef32027e98ec54c186c2023cfbc7eae16d. Phase 2 source survived locally but had not been committed. The implementation was retained rather than rebuilt.

## Scope

- Ten cinematic selections generated only from FEATURED_VERIFIED records, linked to full record details.
- Registry-generated explorer with Artist, Year, Project, exact Role, evidence scope, featured filter and search.
- Existing co-production context and separate first-hand roles preserved.
- Separate unpopulated releases and recognition components; no inferred releases or recognition.
- V3 career, education and capabilities preserved; two legitimate email contact journeys.

## Integrity and regression results

Run `python tools/check_credits.py`, `python tools/test_rendered_audit.py`, `python tools/check_phase2.py`, and `python tools/audit_rendered_credits.py --report tools/credits-audit.v1.json`.

All passed after resuming. Frozen JSON SHA-256: 3f139dd6d7734f7b3631033db839b95bfea5017330b3e0fe5be136392eb6657a.

34 unique records; 10 additional featured navigation previews without duplicated role badges. 29 public role values; 35 first-hand role values. 17 Tier A Public metadata labels; one Tier B Publicly documented label; zero Tier C verification badges. 21 first-hand blocks, including five mixed-evidence records. Zero inferred roles or misapplied badges. The excluded Emtee DIY 2 title track never renders. Evidence destinations match the frozen source URLs.

Browser checks: all 33 non-default filter options matched dataset expectations; search by artist, track and project and empty results passed. Before/after role-block comparisons confirmed search and filtering cannot alter evidence classifications. Featured links open the correct detail; Enter/Space and mobile menu navigation work; focused form controls show a 2px outline. Both CV download actions succeeded. Contact links use the existing email with distinct subjects and no submission backend.

Visual review completed before the interruption at desktop 1280px, tablet 768px, mobile 390px and small mobile 320px. The same HTML/CSS was preserved and overflow rechecked after resuming: document widths equalled scroll widths at all four sizes. Logo/favicon images loaded. No application console errors were observed; browser-extension messages were excluded. Both CV files and original assets are byte-identical to V3. Canonical, SEO/Open Graph/Twitter and Person JSON-LD metadata remain intact. All internal anchor and asset targets passed static checks.

## Performance and limits

Native static HTML/CSS/JavaScript, no new runtime dependency or artwork. Runtime source plus original images totals 215,398 bytes, excluding CV downloads. No benchmark or Lighthouse score is claimed. Reduced-motion CSS reviewed; OS-level preference emulation and physical-device/screen-reader testing were not available. External evidence URLs were checked against the frozen registry, not independently researched or exhaustively uptime-tested. Email actions were inspected, not sent. Production deployment verification is deferred until separately authorized.

Preview ready for review and separate production authorization. Main and GitHub Pages configuration were not changed.
