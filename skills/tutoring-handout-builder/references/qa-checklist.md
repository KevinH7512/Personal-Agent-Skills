# Handout QA checklist

Select the mode-specific checks before validation. K/Q/A mode uses the paired structural checks below. Single-PDF editable reconstruction mode uses the replica checks near the end in addition to the shared typography, scientific-notation, rendering, and delivery checks.

All checks below belong to the single review in round 1 and, only for substantive repairs, the targeted acceptance in round 2. Follow [SKILL.md](../SKILL.md#verification-budget-and-stopping-rules) for issue severity, renderer retries, and stopping. Checklist failures are findings to classify, not permission for unlimited correction. Cosmetic findings are reported to the user without editing. Do not run these sections as independent repeated audits.

## Structural validation

Before opening the generated files, compare the source inventory with the canonical content model:

- Every logical `Q` item appears once, in natural numeric order; multipart screenshots are joined correctly.
- Every question has one independently checked answer record, including material without a matching `A` image; every written-response item has one standard written solution.
- Every supplied image is accounted for; duplicates, orphans, and intentional omissions have an internal reason.
- No unrequested supplemental question, renumbering, or difficulty reclassification was introduced.
- The selected layout mode is recorded. In interleaved mode, every `Q` appears once under the nearest preceding supplied `K`, and intentional gaps in `K` numbering were not treated as omissions.

Run the included validator with the bundled workspace Python:

```powershell
python scripts/validate_handouts.py --student "<student.docx>" --answer "<answer.docx>"
```

Record the validator result and classify reported findings under the shared severity rules. If the document remains renderable, collect visual findings in this round before batch repair. Do not call a failing validator PASS even when its remaining findings are cosmetic. The script checks package integrity, A4 geometry, margins, fonts, sizes, line spacing, native math, stacked fractions, forbidden slash fractions, floating images, student/answer separation, question numbering, cross-version question-text parity, objective-answer run styling, written-answer label/body structure, question borders, real blank paragraphs, and question-section vertical alignment.

Additional Documents audits are optional diagnostics, used only for a concrete gap or failure not already resolved by the validator:

- `section_audit.py` for page geometry and section behavior;
- `images_audit.py` to confirm every figure is inline rather than floating;
- use the packaged DOCX renderer for the planned visual review, not another review pass.

## Visual review

In round 1, export each requested DOCX once and inspect every page at a readable scale. LibreOffice headless is preferred when available; otherwise use an available background Word exporter. Follow the shared retry and timeout limits. If exporting is unavailable or remains unsuccessful, deliver with the missing visual check disclosed. Round 2 reviews affected pages and downstream reflow as defined in SKILL.md.

Check all of the following:

- No clipping, overlap, missing glyphs, formula corruption, unexpected font substitution, or image distortion.
- Original and redrawn figures remain legible and fit side by side when requested.
- Student question page begins near the normal top margin, without a large blank band above the section heading.
- On an ordinary three-question student page, question 1 begins directly below the heading, question 2 begins near one-third of the usable height, and question 3 begins near two-thirds. Adjust the band sizes only when answer length justifies it; do not vertically center the group.
- Passing a “5–6 blank lines” count is not sufficient by itself; fail the page if the actual rendered question starts do not occupy the intended top/one-third/two-thirds bands.
- Blank writing lines have the same full height as pressing Enter in a normal 10 pt, 1.5-line paragraph. They must not appear visibly compressed.
- There are no gray lines or other separators between individual question blocks. In interleaved mode, exactly one thin solid light-gray rule appears only before each subsequent knowledge group that shares a continuous page flow; it is attached to that knowledge heading.
- In interleaved mode, every knowledge block has one full `Normal`-line of vertical space before its first owned question in both versions. The gap is neither missing nor inflated into student writing space, and it is not made from typed whitespace.
- Concentrated mode keeps all knowledge before all questions. Interleaved mode keeps each knowledge item once, followed by all questions assigned under the sparse-`K` rule.
- On an interleaved mixed page, one question receives most remaining height; two questions divide remaining space according to answer length. Question-only continuation pages return to the top/one-third/two-thirds rule.
- The first two short interleaved knowledge groups were actively tested for a shared first page before final writing space was allocated. Fail an avoidable page break when both groups, their first owned questions, the one-line gaps, and adequate writing space fit legibly; also fail an overpacked merge that shrinks text, formulas, figures, or writing space.
- A later knowledge group is merged onto the preceding page only when the prior page is more than half empty or contains only one knowledge group plus one question, and the next heading, core content, first question, required gap, and minimum writing or answer block fit completely.
- A marked challenge problem receives a full page.
- Answer pages flow continuously: if a page has substantial space, the next question begins there.
- Knowledge pages do not contain awkward orphan headings or tables pressed against surrounding text.
- Student and answer question numbers, wording, options, and diagrams match.
- Use structural evidence for native equation editability; no separate interactive Word selection audit is required. During the page review, spot-check fractions, roots, scripts, matrices, cases, accents, and Greek letters for visible correctness. Every quotient such as six分之π must use a real fraction bar (`\frac{\pi}{6}` → OMML `m:f`), never `π/6`.
- Every simple scientific script uses native Word subscript/superscript properties and every complex expression uses native Word math. No Unicode script lookalike or baseline formula digit remains. Compare chemistry coefficients, atom counts, ionic charges, oxidation states, arrows and conditions; mathematics powers and indices; and physics variables, vectors, units, and unit powers against the source.
- Student version contains no solution, variation, source, or doubt text.
- In the answer version, every newly inserted choice, true/false, or filled-blank token alone is dark red (`C00000`) on pale-yellow run shading (`FFF2CC`). Its parentheses, underscores, punctuation, surrounding stem, and options retain their ordinary styling; no full sentence or table cell is recolored just to mark one answer.
- Every written-response, short-answer, or worked-solution answer begins with the exact word `答案` alone on a dark-red line. Its body begins on the next nonempty line, remains black, and uses pale-yellow paragraph shading to distinguish it from the question. No legacy inline `标准解答：`, `答案：`, or `解析：` label replaces this structure.
- A purely inline objective-answer item needs no standalone `答案` line. A written-response item has exactly one, and a mixed item retains both the granular inline styling and the standalone written-answer block. No answer item has a meaningless variation.
- Any `【疑点：……】` sits next to the affected text, diagram, step, or conclusion and does not replace a usable best-effort solution.

## Single-PDF editable reconstruction checks

Run the validator with the bundled workspace Python:

```powershell
python scripts/validate_handouts.py --replica "<editable.docx>"
```

Before rendering, compare the source-page inventory with the reconstruction content model:

- Every retained heading, paragraph, prompt, option set, table, formula, blank, and figure appears once and in source order.
- Headers, footers, page numbers, watermarks, branding, copyright, advertising, QR codes, and decorative empty frames excluded by the user do not appear in text, images, headers, or footers.
- Recoverable prose, tables, and formulae are editable; screenshots are limited to tight crops of genuinely graphical material.
- Page breaks are semantic or natural rather than copies of the source pagination.
- Source blanks remain editable and unsolved unless the user asked otherwise.
- When this is an answer version, objective/fill-in insertions and written-response answer blocks follow the shared red-text, pale-yellow-background, and standalone-`答案` rules above.
- Every ambiguous reading has a best-effort transcription plus a local `【疑点：……】`.

During the same round-1 page review, confirm empty headers/footers, natural pagination, readable inline crops, and no clipped tables or equations. Reuse source-notation checks recorded during transcription; return to source images only for an uncertain or conflicting expression. Apply the shared cosmetic/substantive distinction to spacing and orphan headings.

## Final delivery

- Resolve one student/answer destination pair at run start. If a non-run file occupies a default name, choose one shared suffix once. Never overwrite that file or create successive revision copies during repair.
- Apply the shared maximum of two QA rounds: one initial review, and one acceptance only after batched substantive repairs. Do not regenerate for cosmetic findings.
- Keep temporary PDFs and page images outside the output folder.
- Confirm that this run added or updated only the mode's run-owned final `.docx` deliverable(s): two for K/Q/A mode or one for single-PDF mode. Preserve every pre-existing output file, and keep all other newly generated artifacts elsewhere.
- Deliver only final `.docx` files and summarize material layout, exclusions, or uncertainty decisions.
- Report actual coverage: structural result, full visual review or affected-page review, and any unreviewed content or renderer failure. Claim a full latest-version visual review only when every page of that version was actually inspected; targeted acceptance is not a new full review.
