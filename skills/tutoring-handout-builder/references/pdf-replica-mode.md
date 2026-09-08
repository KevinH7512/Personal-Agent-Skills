# Chemistry handout production (single-PDF editable reconstruction)

Use this mode when the user supplies one chemistry study PDF and requests an editable Word reconstruction. Content fidelity and editability take priority over matching the PDF's page count or decorative layout. This mode is isolated from the concentrated and interleaved K/Q/A rules; changes made here must not alter either K/Q/A workflow.

## 0. Chemistry-only numbering and answer conventions

Apply these conventions only in chemistry handout production:

- Number the document's classic worked examples as `例1`, `例2`, `例3`, … in one natural sequence beginning at 1. Do not keep `经典例题`, square brackets, corner brackets, or forms such as `【例1】` around these labels.
- Number consolidation exercises with plain Arabic numerals only: `1.`, `2.`, `3.`, `4.`, … in natural order. Remove `巩固练习`, `【巩固练习】`, and any brackets around an exercise number. Preserve the supplied exercise wording and order.
- In the student handout, every answer parenthesis for a multiple-choice or true/false item must contain space equivalent to at least three full-width characters, for example `（　　　）`. This minimum is about writable room, not a literal requirement to use that exact number of spaces. In an answer version, replace the blank with the actual answer instead of retaining the empty space.
- Do not create or retain a final `易错点整理` section, including variants such as `本节易错点自行整理`. Finish at the actual teaching content or the user's retained review outline.

When the user requests an answer version, preserve the supplied or user-edited student handout byte-for-byte and create a separate `<title>-答案版.docx`. Keep headings, example/exercise numbering, question wording, options, formulas, figures, and order aligned with the student baseline. Fill choice/true-false fields and blank knowledge fields with only the newly inserted answer token in dark-red `C00000` text on pale-yellow `FFF2CC` run shading. For a written-response, short-answer, or worked-solution item, place the exact word `答案` alone in a dark-red paragraph, then begin the black answer body on the next paragraph with pale-yellow paragraph shading. Do not substitute inline `答案：`, `解析：`, or `标准解答：` labels for this structure. Independently solve every question; do not copy an uncertain answer without checking it.

## 1. Establish the reconstruction boundary

Before extraction, record the requested document title and classify visible source material into:

- **retain as editable:** teaching headings, explanatory prose, questions, answer content already present in the source, options, blanks, tables, captions, labels, and ordinary scientific notation;
- **retain as a tight figure crop:** molecular or apparatus drawings, mind maps, relationship diagrams, charts, photographs, and other genuinely graphical content whose faithful editable redraw would require guessing or disproportionate work;
- **exclude:** user-designated watermarks, recurring headers and footers, page numbers, publisher or brand furniture, copyright text, advertising, QR codes, social-media prompts, and decorative empty frames;
- **uncertain:** content whose reading or role cannot be established reliably. Continue with the best-supported transcription and attach `【疑点：……】` at that exact location.

Do not treat a full page as an image merely because it contains a diagram. Recover surrounding prose, formulae, and tables as editable content, then crop only the graphical region. Do not reproduce excluded material in a new header, footer, cover, note, image crop, or document property.

## 2. Extract by semantics, not by page imitation

Inspect every page visually and also extract embedded text with coordinates. The visual page is authoritative for order, grouping, blanks, scripts, arrows, and diagrams; embedded text is transcription evidence, not a complete layout model.

Create a page-linked canonical sequence with roles such as:

- document title and section/subsection headings;
- prose, list item, prompt, option set, answer line, or callout;
- editable table with row/column spans and cell roles;
- inline scientific expression or display equation;
- figure crop with source page and crop bounds;
- localized doubt note;
- excluded page-furniture record with a reason.

Merge paragraphs split only by a PDF line or page break. Preserve meaningful boundaries, numbering, option order, fill-in blanks, labels, and explicit emphasis. Let Word paginate naturally; do not insert page breaks merely to mirror the PDF.

## 3. Reconstruct scientific notation semantically

Never trust baseline PDF extraction to preserve scripts. Re-read every formula and symbol visually.

- Use Word run `subscript`/`superscript` properties for simple inline scripts that remain structurally clear and editable.
- Use native Word math (OMML/Cambria Math) for fractions, roots, matrices, cases, stacked isotope notation, reaction arrows with conditions, vectors/accents, or any expression whose structure would be ambiguous in ordinary runs.
- Do not use Unicode subscript/superscript digits or signs as a substitute for Word structure.
- Chemistry: keep stoichiometric coefficients baseline; atom counts subscript; ionic charge magnitude and sign superscript; oxidation state superscript; hydrate coefficients baseline; element capitalization exact; state labels and reaction arrows intact. Examples: `CuSO₄·5H₂O`, `SO₄²⁻`, `NH₄⁺`, `Fe³⁺`, `2NaOH`, `CO₂↑`.
- Mathematics: powers are superscript, indices are subscript, variables are italic, named functions and ordinary prose are upright, and every quotient is a native stacked fraction.
- Physics: variables and vector symbols follow the source and subject convention; units are upright; unit powers are semantic superscripts; compound symbol indices remain subscripts.

After authoring, perform a dedicated script pass over every page containing formulae. Compare capitalization, element order, atom counts, coefficients, charge, arrows, state symbols, and punctuation against the source image. A visually small script error is a content error, not a cosmetic defect.

## 4. Rebuild content cleanly

Apply the exact page geometry, typography, tables, equation, and black/gray textbook rules in `handout-spec.md`. Do not carry over decorative source colors or page furniture unless the user explicitly asks. Headers and footers remain empty, and no page-number field is added.

Rebuild ordinary tables as native Word tables with explicit widths, repeating header rows when they span pages, comfortable padding, and no fixed row heights. Preserve meaningful merged cells and blank answer cells. If a table is too structurally graphical to rebuild reliably, crop it only when the user has permitted screenshots and a crop remains readable.

Keep figure crops inline, tightly bounded, and free of neighboring excluded material. Preserve aspect ratio. Do not upscale a crop until labels blur. Add alt text or a concise caption only when the source supplies one or the relationship would otherwise be unclear.

Preserve source blanks as editable underscore runs or blank table cells when they are part of the teaching content. Do not invent extra classroom writing space or solve source blanks unless requested.

## 5. Naming, output, and doubts

Default to `<title>-可编辑版.docx` unless the user specifies another name. If the user also requests answers, preserve the student file and create `<title>-答案版.docx` as the new deliverable. Keep source renders, crops, extraction data, and QA images in `work` or a temporary folder.

Place every `【疑点：……】` beside the affected content, including the competing reading when it changes meaning. A doubt note must not replace a usable best-effort transcription. Do not create a separate ambiguity appendix unless requested.

## 6. Acceptance gate

Validate the DOCX with the replica mode of `scripts/validate_handouts.py`; for chemistry files also pass `--chemistry-role student` or `--chemistry-role answer`. Then render it and inspect every page at 100% zoom. In addition to ordinary layout QA, confirm:

- all requested teaching content appears once and in source order;
- all excluded headers, footers, page numbers, watermarks, branding, copyright, advertising, QR codes, and decorative empty frames are absent;
- all ordinary text, tables, blanks, and scientific notation that can reasonably be editable are editable;
- every retained crop contains only relevant graphical content;
- no scientific subscript or superscript has been flattened to baseline or Unicode lookalikes;
- every `【疑点】` is local and understandable;
- headers and footers are empty and the document has no page-number field.
- classic worked-example labels are the contiguous sequence `例1`, `例2`, … with no enclosing brackets;
- consolidation exercises use plain Arabic numerals with no `巩固练习` label or enclosing brackets;
- student choice/true-false answer parentheses provide at least three full-width characters of writing room, while answer-version parentheses contain the actual answer;
- every newly inserted choice, true/false, or blank answer token in the answer version is dark red on pale-yellow run shading, without recoloring its surrounding stem or option;
- every written-response answer uses a standalone dark-red `答案` paragraph followed by a black body paragraph with pale-yellow paragraph shading;
- no final `易错点整理` section remains.
