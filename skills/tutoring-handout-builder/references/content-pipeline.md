# Source extraction and content pipeline

Use this pipeline to separate source interpretation from page layout. The internal inventory and content model are working data, not extra user deliverables.

## 1. Inventory and grouping

Natural-sort supported images and explicitly supplied PDFs. Ignore temporary files such as `~$*.docx` and generated `output`, `work`, or render folders.

Interpret the leading letter as the role and the number as the logical item:

- `K01`, `K02`: ordered knowledge material;
- `Q01`, `Q02`: ordered questions;
- `A01`, `A02`: reference answers corresponding to the same-numbered question;
- `Q03a`, `Q03b`, `Q03-01`, `Q03-02`: ordered parts of one logical question unless the visible content proves otherwise.

Record, before transcription:

- logical item ID and ordered source files;
- missing numbers, duplicate parts, corrupt files, and unsupported files;
- `Q` items without `A` evidence and `A` items without a matching `Q`;
- likely diagram continuations or answer pages that cover more than one question.

Do not infer that every image is a separate item. Do not silently discard an orphan or duplicate.

When `K` material exists, record the selected layout mode in the canonical model. In concentrated mode, `K` order controls only the knowledge section. In interleaved mode, sparse `K` numbers are grouping instructions, not missing-file defects: assign each question to the nearest preceding supplied `K` whose numeric ID is less than or equal to the question number. Read `layout-modes.md` for the complete ownership and page-flow rules.

## 2. Canonical content model

Maintain one canonical representation from which both DOCX files are rendered. A Python structure, JSON file, or equivalent in-memory model is acceptable. It should distinguish at least:

- document title and topic metadata;
- selected layout mode and, for interleaved mode, ordered knowledge groups with their owned question IDs;
- knowledge prose, equations, tables, and figures;
- question number, wording, options, subparts, and question figures;
- answer-form metadata (`inline_objective`, `written_response`, or `mixed`), granular inline-answer spans, standard written solution, optional variations with solutions, source metadata, and localized doubt notes;
- source-file trace for each uncertain or reconstructed element.

Question content is immutable shared content. Keep answer-only fields separate in the canonical model rather than mixing them into the shared question text. For an objective or fill-in field, retain the student blank plus an answer-span value and render that value only in the answer version with the required red font and pale-yellow run shading. For a written response, retain a separate answer-body node so the answer renderer can emit the standalone red `答案` paragraph and the distinguished body beneath it. Generate both versions from this model so parity does not depend on deleting paragraphs from a DOCX.

## 3. Transcription and reconstruction

Read all parts of a logical item before transcribing it. Preserve wording, symbols, option order, subpart order, units, diagram labels, and explicit source metadata. Correct only unmistakable OCR artifacts; do not silently rewrite the mathematical problem.

Use Word text for prose and OMML for mathematical expressions. Preserve the semantic structure of fractions during transcription: canonical equation data must represent `π/6`, `a/b`, and similar quotients as `\frac{\pi}{6}`, `\frac{a}{b}`, or an equivalent structured fraction node, never as a slash-delimited text string. The DOCX conversion must produce an OMML `m:f` fraction. If conversion fails, repair the equation pipeline; do not substitute a slash or leave raw LaTeX visible.

Reconstruct scientific scripts from meaning rather than trusting OCR or baseline extracted text. Use native Word subscript/superscript runs for simple inline forms and OMML for complex structure. Do not use Unicode script characters. Recheck mathematical exponents and indices, physics variables/vectors/units, and chemistry coefficients, atom counts, ionic charges, oxidation states, capitalization, reaction arrows, state symbols, and conditions against the source image. Forms such as `CuSO₄`, `SO₄²⁻`, `Fe³⁺`, and `x²` must remain semantically editable.

Crop images to graphical content rather than embedding full screenshots containing recoverable text or formulas. Keep the original graphic when labels or geometry cannot be redrawn confidently.

For every unresolved ambiguity, choose the best-supported reading, continue, and attach a concise `【疑点：……】` to the affected answer content. Include the competing reading when it would change the solution.

## 4. Mathematical verification

Solve each question without relying on the supplied `A` image, then compare:

- assumptions, domain, units, sign conventions, cases, and final result;
- whether the reference answer belongs to the same question or continuation;
- whether the source itself appears inconsistent or incomplete.

Prefer the independently justified solution. If a discrepancy cannot be resolved from the supplied material, preserve the question and mark the exact conflict in the answer version; never propagate a doubtful answer into the student version.

## 5. Pre-layout gate

Before generating Word files, confirm:

- every logical `Q` has one canonical question node and one checked answer record; every written-response item has one standard written solution;
- numbering and options are complete and ordered;
- every source fraction is represented as a structured fraction rather than slash text;
- each image is classified as question content, answer evidence, knowledge content, or intentionally unused with a reason;
- variations, if any, meet the instructional-value rule;
- no unrequested question or course-design decision has been added.
- the layout mode is resolved, and every interleaved `Q` is assigned exactly once under the sparse-`K` rule.
