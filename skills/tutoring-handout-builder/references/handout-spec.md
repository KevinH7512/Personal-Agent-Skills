# Tutoring handout specification

## Deliverables and naming

- Produce Word only unless the user asks for another format.
- Default names: `<title>-学生版.docx` and `<title>-答案版.docx`.
- In single-PDF editable reconstruction mode, produce one file named `<title>-可编辑版.docx` by default.
- Title format: `MM.DD-学段学科-主题`, for example `08.23-高中数学-三角函数图像` or `08.30-初中数学-最值问题（2）`.
- Use the same base title in both documents. A restrained `学生版` or `答案版` subtitle is allowed, but it must not alter the shared question content.
- Student version should normally be about 5 pages (commonly 4–6 and no more than 8). Answer version should normally stay within 10 pages. Treat these as page budgets, not reasons to omit content.
- The handout is designed for A4 single-sided printing. Do not add page numbers.

## Typography and page geometry

Use these exact defaults unless the user changes them:

- A4 portrait, top/bottom margins 17 mm, left margin 25 mm, right margin 32 mm.
- Body 10 pt; document title and all heading levels 12 pt.
- Chinese body: SimSun. Chinese headings and labels: SimHei.
- English letters and Arabic numerals: Times New Roman.
- Native Word equations: Cambria Math.
- Every mathematical fraction uses a stacked fraction bar. Author `\frac{numerator}{denominator}` and convert it to native OMML `m:f`; for example, `\frac{\pi}{6}` must display as π over 6, never as `π/6`. Do not leave raw LaTeX commands visible.
- Ordinary paragraphs: 1.5 line spacing. Keep spacing consistent rather than using manual empty paragraphs for decoration. The explicit interleaved knowledge-to-question gap is structural spacing: make it exactly one full `Normal` line, preferably through paragraph spacing rather than typed whitespace.
- Title: centered, 12 pt bold, with a restrained light-gray rule below it.
- Main section heading: 12 pt bold with a thin gray rule. Use black and gray only except for the answer-only annotations defined below: dark red `C00000` and pale yellow `FFF2CC` are reserved for those annotations in the answer version.
- Tables: thin light-gray grid, light-gray header, slightly lighter row-label cells, comfortable cell padding, vertically centered contents.

Maintain a restrained textbook style. Do not add colorful bands, difficulty badges, decorative icons, page furniture, or labels such as “原图/重绘图”, “例题/练习”. The red-and-yellow answer treatment below is a semantic annotation, not a decorative palette.

## Scientific notation and scripts

These rules apply to both K/Q/A handout mode and single-PDF editable reconstruction mode.

- Preserve scripts by meaning, not appearance. For simple inline forms, put the relevant characters in separate Word runs and set native `subscript` or `superscript` formatting. For structurally complex forms, use native OMML. Do not use Unicode subscript/superscript characters as a visual shortcut.
- Chemistry: stoichiometric coefficients are baseline; formula atom counts are subscripts; ionic charge magnitudes and signs and oxidation states are superscripts; hydrate coefficients remain baseline; element-symbol capitalization is exact. Recheck forms such as `CuSO₄·5H₂O`, `SO₄²⁻`, `NH₄⁺`, `Fe³⁺`, `Ca(OH)₂`, reaction arrows, gas/precipitate markers, and conditions above or below arrows.
- Mathematics: exponents are superscripts, indices are subscripts, variables are italic, and nested or stacked structure is native Word math. A quadratic expression such as `x²` must not become baseline `x2`.
- Physics: variables and vectors follow subject convention; units remain upright; powers in units are superscripts; symbol indices are subscripts. Preserve Greek letters, primes, dots, arrows, and sign conventions.
- Chemical symbols and units remain upright. Do not italicize an entire formula merely because it contains Latin letters.
- After generation, compare every scientific expression visually against the source. Treat any changed capitalization, coefficient, atom count, charge, exponent, index, arrow, state symbol, or unit as a content defect.

Keep figures inline. Preserve aspect ratio, avoid upscaling a low-resolution crop until labels blur, and keep figure captions or labels with the figure. Prevent headings from becoming the last line of a page and prevent a question stem from separating from its options or diagram.

## Knowledge content

- Follow the selected structure in `layout-modes.md`: either one concentrated knowledge section or interleaved knowledge groups.
- In interleaved mode, place one full `Normal`-line of vertical space after each knowledge block and before its first owned question in both document versions.
- Synthesize the supplied `K` screenshots into editable explanatory text plus figures. Preserve mathematical meaning and common caveats.
- Preserve the source's logical scope: definitions, preconditions, symbol meanings, domains, units, and exception cases must stay attached to the rule they qualify.
- Knowledge content may take one or two pages depending on the material.
- Do not invent fill-in blanks; the tutor will design any classroom blanks later.
- When the source includes a diagram, place the original crop and a clean redraw side by side when both remain legible. Size the pair so roughly two comparable images can fit across one page.

## Student question layout

- In concentrated mode, begin the question section on a new page after the knowledge section. In interleaved mode, use the mixed-page and continuation-page rules in `layout-modes.md`.
- In interleaved mode, test whether two short opening knowledge groups can share the first page before committing the first group's final writing-space paragraphs. Merge them when the full sequence remains legible and each short question retains at least its ordinary 5–6 full writing lines; do not create an avoidable page break merely to give each opening knowledge group its own page.
- The question section must use normal top vertical alignment. Do not center the entire section vertically; this creates an unusable blank band above `二、题目`.
- Normally place three questions on one page. Use the marked tutor judgment for exceptions; a marked final/challenge problem may occupy one full page.
- Divide the usable question area (inside the page margins and below the section heading) into three vertical bands. Put question 1 at the top of the first band, question 2 near the one-third position, and question 3 near the two-thirds position. Do not vertically center the combined block.
- Generate and check the answer version first, then use the relative answer lengths to adjust band boundaries when one question clearly needs more or less writing room. Equal thirds are the default; answer-informed adjustment is preferable to blindly assigning the same spacer after every question.
- Do not treat “5–6 blank lines” as a complete layout rule. Use however many full-height lines are needed to place the next question at its target band or to reflect the checked answer length; 5–6 lines is only a minimum baseline for an ordinary short question.
- Each blank line must be a genuinely empty `Normal` paragraph, equivalent to pressing Enter once: 10 pt paragraph mark, inherited 1.5 line spacing, and the same paragraph spacing as an ordinary Normal paragraph.
- Do not create writing space with nonbreaking-space characters, underscored lines, compressed blank paragraphs, zero-after overrides, exact-height objects, blank table rows, text boxes, or one large spacer paragraph.
- Do not add gray lines, paragraph borders, rules, or drawn separators between questions. Separation comes only from the allocated blank writing space. The sole exception is interleaved mode's one thin solid light-gray rule before a new knowledge group; it belongs to the following knowledge heading, never to a question.
- Leave ordinary answer space after the final question instead of manufacturing a large blank band above the question section.
- Remove every answer, solution, variation, doubt note, and source note.

## Answer version layout

- Keep question numbers and wording identical to the student version.
- Classify each answer insertion before rendering it. A choice selection, true/false selection, or filled blank is an **inline objective answer**. A worked solution, explanatory response, or ordinary short-answer response is a **written-response answer**. A mixed question may contain both forms.
- For every inline objective answer, style only the newly inserted answer run—such as `A`, `B`, `正确`, `离子`, or `原子`—with dark-red font color `C00000` and pale-yellow run shading `FFF2CC`. Keep the original stem, answer parentheses, blank boundary, underscores, punctuation, option text, and surrounding scientific runs unchanged. Do not recolor or shade a whole sentence, option, paragraph, or table cell merely because it contains the answer.
- Preserve answer-token granularity in scientific text. If a filled answer contains a formula, ion, charge, coefficient, subscript, superscript, or OMML expression, retain its semantic formatting and apply the red-and-yellow annotation only to the answer's textual/math container; never flatten the notation to obtain the color effect.
- For every written-response answer, insert one paragraph whose complete visible text is exactly `答案`: no colon, numbering, explanation, or trailing text. Make the label dark red `C00000` (bold is allowed) and keep it on the same page as the beginning of its body.
- Begin the written-response body in the next nonempty paragraph. Keep its prose, formulas, and diagrams in normal black and distinguish the answer area from the question with pale-yellow paragraph shading `FFF2CC`; a restrained gray left rule or modest left indent is allowed in addition to the shading. Do not make the whole body red.
- An inline objective-answer question does not need a standalone `答案` paragraph unless it also contains a written-response component. A written-response question must have exactly one standalone `答案` paragraph before the next numbered question. Do not use legacy inline labels such as `标准解答：`, `答案：`, or `解析：` in place of this structure.
- Put `条件微调与举一反三：` immediately after the standard solution only when a meaningful variation exists.
- Do not force one question per page. When more than roughly 30% of a page remains after a solution, continue with the next question and its answer.
- A challenge problem may take a full page when marked by the tutor.
- If reliable source metadata was supplied, put it only in the answer version. If region/year/original-number data is absent, do not invent or add a source line.
- Put `【疑点：……】` exactly where transcription, diagram matching, or mathematical correctness remains uncertain. Continue the rest of the document.
- Keep a question, its options/diagram, the standalone `答案` label, and the beginning of its body together when practical; never strand the label alone at a page bottom.

## Content boundaries

- The tutor selects and orders questions. Do not replace that intellectual work with automated question selection.
- Use supplied answers for verification. Re-solve the questions independently and flag conflicts at the affected step or conclusion.
- Standard solutions should explain the key reasoning and likely error points implicitly through the work. Do not add a separate teaching-advice appendix unless requested.
- A variation must change structure, method, boundary behavior, or conceptual insight. Do not include a variation that merely changes numbers without adding instructional value.
- Do not add supplemental questions, change the selected order, or reclassify difficulty unless the user explicitly requests that course-design work.
