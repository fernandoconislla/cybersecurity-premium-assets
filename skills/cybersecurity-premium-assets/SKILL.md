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
5. Use the **approved** `assets/escudo-candado.svg` as the visual-family reference: confident smooth curves, deep navy outlines, clean white dividers when appropriate, flat cyan/navy surfaces, clear focal object, restrained detail. Do not attach shields/locks to unrelated assets.
6. Geometry must consist of independently editable paths/shapes, logically grouped and identified. Never modify the approved master as a side effect.
7. Verify at 1024, 128 and 64 pixels on white and visually compare next to the master.

## Workflow
1. Read master SVG and these rules, accept `nombre` plus optional `descripcion`.
2. Select the most recognizable visual metaphor without unnecessary decoration. Build real vector geometry with only the three token classes.
3. Normalize the visible bounding box to 922 dominant units, center the object in both axes with proportional scaling.
4. Run `python scripts/validate_asset.py assets/<slug>.svg`. Any failure blocks output. Inspect at native and reduced sizes; compare with the master.
5. Display SVG on screen, link its actual SVG file, and label it **candidate** until approved. Only save approved assets to the repository if that is the agreed workflow.

## Example
`{"nombre":"Base de datos","descripcion":"Cilindro apilado de tres niveles"}` -> `assets/base-de-datos.svg`. Build layered rounded ellipses, navy main silhouette, cyan planes and restrained white interior separations. Normalize and validate.

## Never rationalize violations
- More detail never permits a fourth shade or gradients.
- Changing geometry must not alter color tokens; rebranding must not alter geometry.
- PNG embedded in SVG is not a vector asset.
- Square canvas is not proof of correct 90% scale: test the visible bounding box.
- An attractive standalone icon is not necessarily part of this family: compare side-by-side.
- If a renderer cannot resolve CSS tokens, use a temporary **validation-only** copy with colors resolved; keep the SVG original parametrized.
