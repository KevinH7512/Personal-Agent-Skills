# Knowledge and question layout modes

Resolve the mode before authoring whenever `K` material exists. Use the user's explicit choice. If no choice was supplied, ask once whether the handout should use concentrated or interleaved knowledge; do not silently choose.

## Mode A: concentrated knowledge

Place all supplied knowledge material first under `一、知识梳理`, then begin the ordered questions on a new page under `二、题目` (student) or `二、题目与解答` (answer). Use the ordinary question-only page rules in the handout specification. Do not add group separators.

## Mode B: interleaved knowledge

Use one global heading containing the word `题目`, such as `一、知识点与题目`, so the document remains structurally recognizable. Then repeat this sequence in source order:

1. one knowledge group;
2. every question owned by that knowledge group;
3. in the answer version, each question's styled answer content and any meaningful variation immediately after that question.

Do not repeat a knowledge item when its questions continue onto another page. `Aq` always verifies and supplies answer evidence for `Qq`, regardless of the knowledge grouping.

Leave one full `Normal`-line of vertical space between the final knowledge paragraph, figure, or table and the first owned question. Apply the same gap in the student and answer versions. Prefer paragraph spacing equal to one normal line; if an empty paragraph is used, it must be a genuinely empty `Normal` paragraph rather than typed whitespace.

### Sparse `K` numbering defines ownership

Treat gaps in `K` numbering as intentional. For ordered knowledge IDs `K_n`, each `K_n` owns `Q_n` through `Q_(m-1)`, where `K_m` is the next supplied knowledge item. The last supplied `K` owns every remaining question whose number is at least its own number. Operationally, each `Q_q` belongs to the nearest preceding supplied `K_k` for which `k <= q`.

Example:

- `K01` owns `Q01`;
- `K02` owns `Q02` and `Q03` because the next supplied knowledge item is `K04`;
- `K04` owns `Q04`;
- `K05` owns `Q05` and any later questions until another supplied `K` appears.

Multipart suffixes such as `K02a`, `K02b`, `Q03a`, and `Q03b` remain parts of their numbered logical items. A question numbered before the first supplied `K` has no supported owner: continue with the best placement and mark the issue locally in the answer version.

### Student-page placement

- If a page contains one knowledge group and one question, keep the group at the top and give most of the remaining usable height to that question.
- If it contains one knowledge group and two questions, divide the remaining writing space between them according to the already-written answer lengths. Equal halves are only the starting point.
- Before fixing the number of writing-space paragraphs, test whether the next adjacent knowledge group can share the page. Preserve the one-line knowledge-to-question gap and at least the ordinary 5–6 full `Normal` lines for each short question involved in the packing test; add more space when the checked answers justify it.
- Do not force the top/one-third/two-thirds rule onto a mixed knowledge-and-question page.
- If a knowledge group owns three or more questions, show the knowledge content once. Let the questions flow naturally to later pages. Any continuation page containing questions only uses the ordinary three-question top/one-third/two-thirds layout.
- Give all questions real empty `Normal` paragraphs for writing space; never use compressed spacers or visual separators.

### Page transitions and group separator

Do not force every knowledge group onto a fresh page before testing the actual content. In particular, actively test whether the first two short knowledge groups can share the first page in sequence; prefer the shared page when both groups, their first owned questions, the required knowledge-to-question gaps, and the minimum answer-informed writing space fit legibly without shrinking text, formulas, or figures.

For later transitions, first try to place the next group on the preceding page when either:

- more than half of that page's usable area is empty; or
- the page currently contains only one knowledge group and one question.

In the student version, merge only when the next group's heading, core knowledge content, first question, one-line knowledge-to-question gap, and minimum writing space can all fit completely. In the answer version, the first question, its standalone red `答案` label when the item is written-response, and the beginning of the shaded answer body must also stay together. Otherwise start the group on the next page; do not strand only a heading, partial core explanation, question stem, or answer label at the bottom.

When two knowledge groups share a page or follow one another in the same flow, place exactly one subtle thin solid light-gray horizontal rule between the previous group's final question area and the next knowledge heading. Implement it as the top paragraph border of the following knowledge heading. Do not add a label, colored band, second rule, or any border to a question paragraph. No separator is used merely because one question follows another.

### Answer-version flow

Keep the same group and question order as the student version. Within each group use `K → Q → 客观题内嵌答案或“答案”独立行＋正文 → 可选变式`, then proceed to the next owned question. Continue onto the next page whenever needed; do not force one question per page. Apply the same group-transition rule and the same single gray separator when groups meet in one continuous page flow.
