---
name: cybersecurity-premium-assets
description: Use when generating, editing, validating, or saving premium cybersecurity teaching assets as parametrized SVG icons from a required asset name and an optional composition description, preserving an approved visual family.
---

# Cybersecurity Premium Assets

## Contract
**Two inputs:** `nombre` (required, non-empty) and `descripcion` (optional). Without a description, infer a clear, recognizable metaphor from the name. A description may change composition, but must never override hard rules. Report any ignored conflicting instruction.

**Output:** an original, genuine editable SVG `assets/<slug>.svg`, shown inline and linked. Never use a PNG as the main deliverable. Only mark as approved after explicit user approval.

## Hard rules
1. Canvas `width="1024" height="1024" viewBox="0 0 1024 1024"`. Background fully transparent.
2. Exactly three global CSS tokens in `<style>`: `--PRIMARY: #092B60;`, `--SECONDARY: #38BDF8;`, `--CONTRAST: #FFFFFF;`. All painted shapes use `.primary`, `.secondary`, or `.contrast` classes reading `var(--TOKEN)`. Values may later change for rebranding; the roles must not change.
3. No fourth colors, gradients, shadows, filters, patterns, opacity effects, raster images, external artwork, or background rectangle. Whites must be internal and enclosed by stronger colored surfaces for visibility on white backgrounds.
4. Main subject's dominant visible dimension ≈ 90% (922 units, tolerance ±2%). Preserve aspect ratio, center *both* axes; keep equal geometric margins on the minor dimension and avoid clipping. Optical offsets of up to 12 units require justification.
5. Use **both approved, immutable references**: `assets/escudo-candado.svg` (shield/lock) and `assets/base-de-datos.svg` (database V2). They define the family together: smooth Bézier curves, deep navy outer contours, restrained enclosed white divider, cyan/navy flat field split, clear focal subject, consistent detail density. Do not attach shields/locks to unrelated concepts or clone the database silhouette.
6. Geometry must consist of independently editable paths/shapes, logically grouped and identified. Never modify **either approved reference** as a side effect. Design new assets as fresh files.
7. Verify at 1024, 128 and 64 pixels on white and visually compare side by side with **both** approved references. The icon must read as the named concept without labels.

## Workflow
1. Read **both** approved SVG references and these rules, accept `nombre` plus optional `descripcion`.
2. Select the most recognizable visual metaphor without unnecessary decoration. Build real vector geometry with only the three token classes.
3. Normalize the visible bounding box to 922 dominant units, center the object in both axes with proportional scaling.
4. Run `python scripts/validate_asset.py assets/<slug>.svg`. Any failure blocks output. Inspect at native and reduced sizes; compare in a single contact sheet with the shield **and** database masters.
5. Perform TWO mandatory audits before delivering: technical (hard invariants) AND visual-design (criteria below). Fix defects and re-audit; passing technical validation alone never means design approval.
6. Display the candidate SVG on screen next to **both approved assets**, link the actual SVG file, and report both audits transparently. Label it **candidate** until explicit user approval. Once approved, save it in `assets/<slug>.svg` and update the approved-family catalog in this skill without changing earlier assets. Never store rejected proposals as approved library entries.

## Mandatory visual-design audit
Evaluate each category separately with an evidence-based 0–10 score and a concrete finding:
1. **Concept recognition:** Does the silhouette immediately communicate the named object, even at 64px? Identify confusing alternative readings.
2. **Premium refinement:** Bézier continuity, smooth tangencies, optical alignment, accurate corners and clean silhouette.
3. **Composition and hierarchy:** coherent focal point, intentional negative space, no competing decorations.
4. **Geometry and volume:** physically/plausibly connected layers, correct overlaps, no floating separators, elliptical bands disconnected from the silhouette, or arbitrary features. For stacked forms, separations must visibly join lateral edges.
5. **Optical balance:** perceived mass and left/right distribution, beyond mathematical centering.
6. **Visual-family consistency:** compare side-by-side with **both** approved masters—outline hierarchy, contained white inner contour, split navy/cyan treatment where appropriate, density of detail, and similar optical scale. Match the graphic language, not either icon's silhouette.
7. **Color-role composition:** only approved tokens, contrast on white, no excessively heavy single-color region without design rationale.
8. **Small-size readability:** inspect at 128px and 64px, check whether detailing becomes noise.

**Mandatory verdict:** APPROVE FOR USER REVIEW / REQUIRES REVISION / TECHNICALLY INVALID. A design failing recognizability, layer continuity, or family consistency is REQUIRES REVISION, even when technically valid. Scores are qualitative and must not be invented as test results. Include actionable changes prioritized by impact; never assert user approval before explicit user decision.

## Approved-family catalog (immutable references)
- `assets/escudo-candado.svg` — Shield and centered padlock; baseline for bold outer contour, white enclosed divider, half navy/cyan field and compact focal subject.
- `assets/base-de-datos.svg` — Approved database V2; baseline for three connected cylindrical levels, restrained curved separators that reach lateral edges, simplified upper ellipse, no floating oval bands, no decorative three-dot indicator.

Both are equally authoritative examples of the same family, not interchangeable templates. The approved database geometry must not be changed by requests for unrelated concepts.

## Usage examples
- `{"nombre":"Base de datos"}` → use the approved `assets/base-de-datos.svg` as the existing asset; do **not** regenerate a different candidate without a requested revision.
- `{"nombre":"Servidor","descripcion":"Tres bandejas apiladas vistas de frente"}` → construct an original server SVG, matching both references' visual grammar without adding a shield or a cylinder.

**Design lesson from database V1 → V2:** an identifiable silhouette alone does not pass review. If separators float or decoration competes with the primary concept, simplify and reconnect the geometry before presenting a candidate.

## Never rationalize violations
- More detail never permits a fourth shade or gradients.
- Changing geometry must not alter color tokens; rebranding must not alter geometry.
- PNG embedded in SVG is not a vector asset.
- Square canvas is not proof of correct 90% scale: test the visible bounding box.
- An attractive standalone icon is not necessarily part of this family: compare side-by-side.
- If a renderer cannot resolve CSS tokens, use a temporary **validation-only** copy with colors resolved; keep the SVG original parametrized.
