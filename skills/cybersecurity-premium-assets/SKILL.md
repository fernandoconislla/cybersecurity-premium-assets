---
name: cybersecurity-premium-assets
description: Use when generating, editing, validating, or saving premium cybersecurity teaching assets as parametrized SVG icons from a required asset name and an optional composition description, preserving an approved visual family.
---

# Cybersecurity Premium Assets

## Contract
**Two inputs:** `nombre` (required, non-empty) and `descripcion` (optional). Both values originate **only from the user**. When `nombre` is absent and the user wants to generate an asset, ask for the name; optionally offer a small input screen with required name and optional description. When the user only asks for ideas, propose concepts without treating the proposal as a submitted input. **Never invent or auto-populate `nombre` or `descripcion` and present them as user-supplied.** If `descripcion` is omitted, autonomously choose a sensible visual composition as an internal design decision; keep the input truly absent. A description may change composition, but never override hard rules. Report conflicts.

**Output:** an original, genuine editable SVG `assets/<slug>.svg`, visibly previewed and linked. PNG may be a QA preview only, never the substitute deliverable. Verify actual file existence/path before offering downloads. Only mark as approved after explicit user approval.

## Hard rules
1. Canvas `width="1024" height="1024" viewBox="0 0 1024 1024"`. Background fully transparent.
2. Exactly three global CSS tokens in `<style>`: `--PRIMARY: #092B60;`, `--SECONDARY: #38BDF8;`, `--CONTRAST: #FFFFFF;`. All painted shapes use `.primary`, `.secondary`, or `.contrast` classes reading `var(--TOKEN)`. Values may later change for rebranding; the roles must not change.
3. No fourth colors, gradients, shadows, filters, patterns, opacity effects, raster images, external artwork, or background rectangle. Whites must be internal and enclosed by stronger colored surfaces for visibility on white backgrounds.
4. Main subject's dominant visible dimension ≈ 90% (922 units, tolerance ±2%). Preserve aspect ratio, center *both* axes; keep equal geometric margins on the minor dimension and avoid clipping. Optical offsets of up to 12 units require justification.
5. Use **all six approved, immutable references**: `assets/escudo-candado.svg` (shield/lock), `assets/base-de-datos.svg` (database V2), `assets/servidor.svg` (server), `assets/firewall.svg` (firewall V3), `assets/api-key.svg` (API KEY V3), and `assets/cloud.svg` (Cloud V2). They define the family together: smooth Bézier curves, deep navy outer contours, restrained enclosed white divider, cyan/navy flat field split, clear focal subject, consistent detail density. Do not attach shields/locks to unrelated concepts or clone the database silhouette.
6. Geometry must consist of independently editable paths/shapes, logically grouped and identified. Never modify **any approved reference** as a side effect. Design new assets as fresh files.
7. Verify at 1024, 128 and 64 pixels on white and visually compare side by side with **all** approved references. The icon must read as the named concept without labels.
8. **Color-layout decisions must be justified, never mechanically copied:** All three palette tokens remain globally defined and no fourth color may be used, but splitting an object into cyan/navy halves is **not mandatory**. Decide whether to split based on the concept's geometry, legibility and perceptual benefit. Whenever choosing either **split** or **uniform fill**, state that choice and its specific rationale to the user in the visual audit. If the split is merely decorative, do not use it. A uniform cyan field can retain primary navy outlines and contained white detailing, thereby using the full palette without an arbitrary division.

## Workflow
1. Read **all** approved SVG references and these rules, accept `nombre` plus optional `descripcion`.
2. Select the most recognizable visual metaphor without unnecessary decoration. Build real vector geometry with only the three token classes.
3. Normalize the visible bounding box to 922 dominant units, center the object in both axes with proportional scaling.
4. Run `python scripts/validate_asset.py assets/<slug>.svg`. Any failure blocks output. Inspect at native and reduced sizes; compare in a single contact sheet with **all** approved masters.
5. Perform TWO mandatory audits before delivering: technical (hard invariants) AND visual-design (criteria below). Fix defects and re-audit; passing technical validation alone never means design approval.
6. Display the candidate SVG on screen next to **all approved assets**, link the verified actual SVG file, and report both audits transparently. Label it **candidate** until explicit user approval.
7. **Mandatory user decision gate:** after showing previews and audits, ask explicitly **«¿Apruebas este asset?»**, with two working choices: **«Aprobar e incorporar a GitHub»** or **«Solicitar una nueva optimización de diseño»**. Prefer a compact interactive radio-group + confirmation button when available; otherwise ask in natural language. The control must act only on the specific candidate shown, not on an unspecified future version. Never silently approve or automatically publish. If user approves unambiguously in text, that is sufficient—do not ask again.
8. On **approval**, publish the **exact candidate file the user reviewed** at `assets/<slug>.svg`, update the approved-family catalog in this skill, confirm repository file URLs and preserve hashes of previously approved assets. Never redraw or subtly change geometry between approval and publishing. On **optimization**, produce a revised candidate and repeat both audits and the decision gate. Never store rejected proposals as approved entries.
9. **Automatically return to the beginning after successful publication:** after confirming BOTH that the approved SVG exists on GitHub and that the skill/catalog update succeeded (while previous approved masters remain unchanged), display a compact new-asset input screen with **`nombre` required** and **`descripcion` optional**, both initially **blank**. Ask the user which asset to make next. Do not reuse the previous asset name/description and do not start new generation until the user submits the new input. If any publication step fails, do not show a misleading completed cycle—report the failure and resume verification/repair first. Do not confuse the new-asset screen with the preceding approval decision screen.

## Mandatory visual-design audit
Evaluate each category separately with an evidence-based 0–10 score and a concrete finding:
1. **Concept recognition:** Does the silhouette immediately communicate the named object, even at 64px? Identify confusing alternative readings.
2. **Premium refinement:** Bézier continuity, smooth tangencies, optical alignment, accurate corners and clean silhouette.
3. **Composition and hierarchy:** coherent focal point, intentional negative space, no competing decorations.
4. **Geometry and volume:** physically/plausibly connected layers, correct overlaps, no floating separators, elliptical bands disconnected from the silhouette, or arbitrary features. For stacked forms, separations must visibly join lateral edges.
5. **Optical balance:** perceived mass and left/right distribution, beyond mathematical centering.
6. **Visual-family consistency:** compare side-by-side with **all** approved masters—outline hierarchy, contained white inner contour, split navy/cyan treatment where appropriate, density of detail, and similar optical scale. Match the graphic language, not either icon's silhouette.
7. **Color-role composition and explicit decision:** only approved tokens, contrast on white, no excessively heavy single-color region without design rationale. **Mandatory disclosure:** write a short section **«Decisión cromática y justificación»** stating **«División cromática: Sí/No»**, why it materially improves (or fails to improve) geometry, meaning, hierarchy or volume, and the trade-off. Explain this *before* asking for the user's approval. Absence of the explanation fails the design-audit process.
8. **Small-size readability:** inspect at 128px and 64px, check whether detailing becomes noise.

**Mandatory verdict:** READY FOR USER APPROVAL / REQUIRES REVISION / TECHNICALLY INVALID. A design failing recognizability, layer continuity, or family consistency is REQUIRES REVISION, even when technically valid. Scores are qualitative and must not be invented as test results. Document concrete deficiencies even if average score is high; failing one critical criterion cannot be masked by an average. Include actionable changes prioritized by impact; never assert user approval before explicit user decision.

## Approved-family catalog (immutable references)
- `assets/escudo-candado.svg` — Shield and centered padlock; baseline for bold outer contour, white enclosed divider, half navy/cyan field and compact focal subject.
- `assets/base-de-datos.svg` — Approved database V2; baseline for three connected cylindrical levels, restrained curved separators that reach lateral edges, simplified upper ellipse, no floating oval bands, no decorative three-dot indicator.
- `assets/servidor.svg` — Approved server asset 03; baseline for clean rectangular geometry, three equally structured frontal modules, aligned ventilation slots and status circles, navy/white chassis contour, and consistent cyan/navy split.
- `assets/firewall.svg` — Approved firewall asset 04, version V3; a wide horizontal brick wall scaled to use available height, staggered mortar joints, centered flame directly over the wall with no medallion, enclosing navy/white double contour and a split cyan/navy field. Preserve this design, not the earlier tall panel (V1) or circular-medallion concept (V2).
- `assets/api-key.svg` — Approved API KEY asset 05, version V3; diagonally oriented key filling the square canvas, circular split-color head with horizontal legible **API** letters converted into vector paths, a simplified shaft with clean two-tooth geometry, navy/white outline system. Preserve the diagonal with horizontal lettering; do not restore code angle-bracket glyphs or unnecessarily detailed teeth.
- `assets/cloud.svg` — Approved Cloud asset 06, version V2; recognizable continuous horizontal cloud silhouette with uniform cyan inner fill, navy external contour and enclosed white border. Deliberately **no** artificial vertical color split; rationale: a continuous cloud form gains no semantic or volumetric clarity from dividing it. Preserve approved V2 geometry and color treatment unless user explicitly requests revision.

All approved references are equally authoritative examples of the same family, not interchangeable templates. The approved database geometry must not be changed by requests for unrelated concepts.

## Usage examples
- `{"nombre":"Base de datos"}` → use the approved `assets/base-de-datos.svg` as the existing asset; do **not** regenerate a different candidate without a requested revision.
- `{"nombre":"Servidor"}` → reuse approved `assets/servidor.svg`; do not regenerate without a requested revision.
- `{"nombre":"Firewall"}` → reuse approved `assets/firewall.svg`; do not regenerate or substitute a vertical panel without a requested revision.
- `{"nombre":"API KEY"}` → reuse approved `assets/api-key.svg`; do not regenerate without an explicit revision request.
- `{"nombre":"Cloud"}` → reuse approved `assets/cloud.svg`; do not reintroduce a split without explicit request and visual justification.
- `{"nombre":"Firewall","descripcion":"Equipo de red con puertos visibles"}` → generate a NEW SVG using only the user-supplied parameters and comparing against all approved assets.

**Design lesson from database V1 → V2:** an identifiable silhouette alone does not pass review. If separators float or decoration competes with the primary concept, simplify and reconnect the geometry before presenting a candidate.

**Design lesson from firewall V1 → V3:** correct conventional orientation is essential: a firewall is typically represented by a horizontal brick wall, not a narrow vertical panel. The wall should fill the available canvas proportionally rather than leave excessive vertical negative space, while preserving the dominant-dimension normalization rule. The flame should sit directly at the center of the wall, not inside an unrequested circular badge. Assess silhouette, negative space, placement and concept-specific composition before approving.

**Design lesson from Cloud V1 → V2 (approved):** copying the cyan/navy vertical split onto every object is not family consistency. For a continuous cloud silhouette the vertical seam does not improve recognition or volume and detracts from minimalism. Uniform cyan surface with navy outer contour and enclosed white border is the approved solution. Every new candidate still requires an explicit split-versus-uniform decision and justification, without assuming Cloud's treatment works universally.

**Design lesson from API KEY V1 → V3:** keep established semantic imagery but prioritize clear textual meaning when the user specifies it (API rather than a generic code symbol). Diagonal orientation can significantly improve square-canvas utilization; maintain horizontal letter baselines for legibility even when the object is diagonal. Simplify internal teeth and microdetails before approving. Verify that letters remain real editable vector paths, never embedded raster or font-dependent text.

## Learned operational safeguards
- **Source of truth and freshness:** Fetch the latest `SKILL.md`, the approved SVGs and validator from GitHub **at the start of each new request**; do not rely on cached instructions, a prior conversation or a made-up installed skill version.
- **Distinct user inputs vs design decisions:** `descripcion` absent means absent, not an assistant-composed description. A proposed concept is not a confirmed `nombre`.
- **Approval is scoped and binding:** associate user approval with the exact candidate bytes/filename shown; only publish those bytes, not a reconstruction. On interrupted publication, check GitHub first and resume the original confirmed action without changing the design.
- **Evidence, not decorative previews:** verify renders at 1024/128/64, against both approved originals; use actual candidate preview and never substitute a generic image-search result or an inert download control. If previews fail, disclose the failure and fix it before seeking approval.
- **Two independent gates:** technical validation must genuinely be run, not inferred from visually plausible markup; visual design audit must be critical rather than automatically assigning 9+/10.
- **Traceable publication:** after explicit approval, check GitHub fetch result and report the published path. Confirm master-file SHAs unchanged; update skill/catalog only after successful asset publication.
- **Closed-loop UX:** after successful publication AND skill/catalog verification, show fresh empty fields for `nombre` and optional `descripcion`. Each successful publication ends at the beginning of a new cycle, awaiting the user's next submission.
- **Minimalism:** remove features that do not help identification (floating decorative bands, gratuitous status indicators, competing top-edge details). Avoid treating reused colors as sufficient evidence of family coherence.

## Never rationalize violations
- More detail never permits a fourth shade or gradients.
- Changing geometry must not alter color tokens; rebranding must not alter geometry.
- PNG embedded in SVG is not a vector asset.
- Square canvas is not proof of correct 90% scale: test the visible bounding box.
- An attractive standalone icon is not necessarily part of this family: compare side-by-side.
- If a renderer cannot resolve CSS tokens, use a temporary **validation-only** copy with colors resolved; keep the SVG original parametrized.
