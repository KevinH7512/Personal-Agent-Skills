from __future__ import annotations

import argparse
import hashlib
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from zipfile import BadZipFile, ZipFile

from docx import Document
from lxml import etree


NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "m": "http://schemas.openxmlformats.org/officeDocument/2006/math",
    "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "pr": "http://schemas.openxmlformats.org/package/2006/relationships",
}

QUESTION_RE = re.compile(r"^\s*(\d{1,3})\s*[.．、]\s*")
QUESTION_SECTION_WORDS = ("题目", "习题", "练习", "训练")
ANSWER_LABEL = "答案"
LEGACY_ANSWER_LABELS = ("标准解答：", "答案：", "解析：")
ANSWER_RED = "C00000"
ANSWER_FILL = "FFF2CC"
VARIATION_MARKER = "条件微调与举一反三："
FRACTION_SLASHES = "/⁄∕"
LINEAR_FRACTION_RE = re.compile(
    rf"(?:\d+(?:\.\d+)?|[A-Za-z]|[α-ωΑ-Ωπ]|[)\]\}}])\s*"
    rf"[{re.escape(FRACTION_SLASHES)}]\s*"
    rf"(?:\d+(?:\.\d+)?|[A-Za-z]|[α-ωΑ-Ωπ]|[(\[\{{])"
)
RAW_LATEX_RE = re.compile(r"\\(?:d?frac|tfrac|sqrt|begin|end|overline|vec|hat|sum|int)\b")
UNICODE_SCRIPT_RE = re.compile(r"[⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎]")
BASELINE_CHEMICAL_DIGIT_RE = re.compile(
    r"(?:^|[^A-Za-z])(?:[A-Z][a-z]?)+(?:\([^)]*\))?\d"
)


@dataclass
class Report:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def require(self, condition: bool, message: str) -> None:
        if not condition:
            self.errors.append(message)


@dataclass
class PackageParts:
    root: etree._Element
    styles: etree._Element
    settings: etree._Element
    image_hashes_by_rel: dict[str, str]
    header_footer_text: str
    header_footer_graphics: int


@dataclass
class BodyBlock:
    text: str
    element: etree._Element


@dataclass
class QuestionBlock:
    number: int
    blocks: list[BodyBlock]


@dataclass
class DocFacts:
    role: str
    path: Path
    root: etree._Element
    text: str
    math_count: int
    fraction_count: int
    image_uses: int
    image_hashes_by_rel: dict[str, str]
    questions: list[QuestionBlock]
    normal_after: str | None


def attr(element: etree._Element, namespace: str, name: str) -> str | None:
    return element.get(f"{{{NS[namespace]}}}{name}")


def load_parts(path: Path, role: str, report: Report) -> PackageParts | None:
    report.require(path.is_file(), f"{role}: file not found: {path}")
    if not path.is_file():
        return None

    try:
        with ZipFile(path) as package:
            corrupt = package.testzip()
            report.require(corrupt is None, f"{role}: corrupt ZIP member: {corrupt}")
            names = set(package.namelist())
            required = ("word/document.xml", "word/styles.xml", "word/settings.xml")
            missing = [name for name in required if name not in names]
            report.require(not missing, f"{role}: missing package parts: {', '.join(missing)}")
            if missing:
                return None

            root = etree.fromstring(package.read("word/document.xml"))
            styles = etree.fromstring(package.read("word/styles.xml"))
            settings = etree.fromstring(package.read("word/settings.xml"))

            image_hashes_by_rel: dict[str, str] = {}
            rel_name = "word/_rels/document.xml.rels"
            if rel_name in names:
                rels = etree.fromstring(package.read(rel_name))
                for rel in rels.xpath("//pr:Relationship", namespaces=NS):
                    rel_id = rel.get("Id")
                    target = rel.get("Target")
                    rel_type = rel.get("Type", "")
                    if not rel_id or not target or not rel_type.endswith("/image"):
                        continue
                    part = str(PurePosixPath("word") / PurePosixPath(target))
                    report.require(part in names, f"{role}: image relationship {rel_id} targets missing {part}")
                    if part in names:
                        image_hashes_by_rel[rel_id] = hashlib.sha256(package.read(part)).hexdigest()

            header_footer_text_parts: list[str] = []
            header_footer_graphics = 0
            for name in sorted(names):
                if not re.fullmatch(r"word/(?:header|footer)\d+\.xml", name):
                    continue
                part_root = etree.fromstring(package.read(name))
                header_footer_text_parts.extend(
                    part_root.xpath("(//w:t | //m:t)/text()", namespaces=NS)
                )
                header_footer_graphics += int(
                    part_root.xpath("count(//w:drawing | //w:pict)", namespaces=NS)
                )
    except (BadZipFile, OSError, etree.XMLSyntaxError) as exc:
        report.errors.append(f"{role}: cannot read DOCX package: {exc}")
        return None

    return PackageParts(
        root,
        styles,
        settings,
        image_hashes_by_rel,
        "".join(header_footer_text_parts),
        header_footer_graphics,
    )


def text_of(root: etree._Element) -> str:
    return "".join(root.xpath("(//w:t | //m:t)/text()", namespaces=NS))


def normalize(text: str) -> str:
    return re.sub(r"\s+", "", text.replace("\u00a0", " "))


def normalize_for_parity(text: str) -> str:
    compact = normalize(text)
    return re.sub(r"[_＿—–\-.·]{2,}", "", compact)


def run_text(run: etree._Element) -> str:
    return "".join(run.xpath("(.//w:t | .//m:t)/text()", namespaces=NS))


def run_color(run: etree._Element) -> str | None:
    values = run.xpath("./w:rPr/w:color/@w:val", namespaces=NS)
    return values[0].upper() if values else None


def run_fill(run: etree._Element) -> str | None:
    values = run.xpath("./w:rPr/w:shd/@w:fill", namespaces=NS)
    return values[0].upper() if values else None


def is_inline_answer_run(run: etree._Element) -> bool:
    return bool(normalize(run_text(run))) and run_color(run) == ANSWER_RED and run_fill(run) == ANSWER_FILL


def is_answer_label_element(element: etree._Element) -> bool:
    if element.tag != f"{{{NS['w']}}}p":
        return False
    visible = "".join(element.xpath("(.//w:t | .//m:t)/text()", namespaces=NS))
    return normalize(visible) == ANSWER_LABEL


def paragraph_fill(element: etree._Element) -> str | None:
    if element.tag != f"{{{NS['w']}}}p":
        return None
    values = element.xpath("./w:pPr/w:shd/@w:fill", namespaces=NS)
    return values[0].upper() if values else None


def text_without_inline_answers(element: etree._Element) -> str:
    pieces: list[str] = []
    run_tags = {f"{{{NS['w']}}}r", f"{{{NS['m']}}}r"}
    for node in element.xpath(".//w:t | .//m:t", namespaces=NS):
        run = next((ancestor for ancestor in node.iterancestors() if ancestor.tag in run_tags), None)
        if run is None or not is_inline_answer_run(run):
            pieces.append(node.text or "")
    return "".join(pieces)


def body_blocks(root: etree._Element) -> list[BodyBlock]:
    body = root.find("w:body", namespaces=NS)
    if body is None:
        return []
    blocks: list[BodyBlock] = []
    for child in body:
        if child.tag not in {f"{{{NS['w']}}}p", f"{{{NS['w']}}}tbl"}:
            continue
        pieces = child.xpath("(.//w:t | .//m:t)/text()", namespaces=NS)
        blocks.append(BodyBlock("".join(pieces).strip(), child))
    return blocks


def is_heading_block(block: BodyBlock) -> bool:
    if block.element.tag != f"{{{NS['w']}}}p":
        return False
    styles = block.element.xpath("./w:pPr/w:pStyle/@w:val", namespaces=NS)
    return bool(styles and styles[0].startswith("Heading"))


def find_question_blocks(root: etree._Element, role: str, report: Report) -> list[QuestionBlock]:
    blocks = body_blocks(root)
    start = None
    for index, block in enumerate(blocks):
        compact = normalize(block.text)
        if len(compact) <= 24 and any(word in compact for word in QUESTION_SECTION_WORDS):
            start = index + 1
            break
    report.require(start is not None, f"{role}: no recognizable question-section heading found")
    if start is None:
        start = 0

    questions: list[QuestionBlock] = []
    active: QuestionBlock | None = None
    for block in blocks[start:]:
        # In interleaved mode a knowledge heading terminates the preceding
        # question block. Knowledge prose is ignored until the next numbered Q.
        if is_heading_block(block):
            active = None
            continue
        match = QUESTION_RE.match(block.text)
        if match:
            active = QuestionBlock(int(match.group(1)), [block])
            questions.append(active)
        elif active is not None:
            active.blocks.append(block)

    report.require(bool(questions), f"{role}: no numbered questions found")
    numbers = [question.number for question in questions]
    report.require(len(numbers) == len(set(numbers)), f"{role}: duplicate question numbers: {numbers}")
    report.require(numbers == sorted(numbers), f"{role}: question numbers are not increasing: {numbers}")
    return questions


def check_section_geometry(root: etree._Element, role: str, report: Report) -> None:
    sections = root.xpath("//w:sectPr", namespaces=NS)
    report.require(bool(sections), f"{role}: no section properties")
    expected_margins = {"left": 1417, "right": 1814, "top": 964, "bottom": 964}
    for index, section in enumerate(sections, start=1):
        page_size = section.find("w:pgSz", namespaces=NS)
        report.require(page_size is not None, f"{role}: section {index} has no page size")
        if page_size is not None:
            report.require(
                attr(page_size, "w", "w") == "11906" and attr(page_size, "w", "h") == "16838",
                f"{role}: section {index} is not A4 portrait",
            )

        margins = section.find("w:pgMar", namespaces=NS)
        report.require(margins is not None, f"{role}: section {index} has no margins")
        if margins is not None:
            for key, expected in expected_margins.items():
                raw = attr(margins, "w", key)
                report.require(raw is not None, f"{role}: section {index} has no {key} margin")
                if raw is not None:
                    try:
                        actual = int(raw)
                    except ValueError:
                        report.errors.append(f"{role}: section {index} {key} margin is not numeric: {raw}")
                    else:
                        report.require(
                            abs(actual - expected) <= 3,
                            f"{role}: section {index} {key} margin is {actual}, expected about {expected} dxa",
                        )

        vertical = section.find("w:vAlign", namespaces=NS)
        if vertical is not None:
            report.require(
                attr(vertical, "w", "val") == "top",
                f"{role}: section {index} vertical alignment must be top",
            )


def check_styles(styles: etree._Element, role: str, report: Report) -> None:
    report.require(
        styles.xpath(
            "boolean(//w:style[@w:styleId='Normal']//w:rFonts"
            "[@w:ascii='Times New Roman'][@w:hAnsi='Times New Roman'][@w:eastAsia='SimSun'])",
            namespaces=NS,
        ),
        f"{role}: Normal style fonts must be Times New Roman + SimSun",
    )
    report.require(
        styles.xpath("boolean(//w:style[@w:styleId='Normal']//w:sz[@w:val='20'])", namespaces=NS),
        f"{role}: body style must be 10 pt",
    )
    report.require(
        styles.xpath("boolean(//w:style[@w:styleId='Normal']//w:spacing[@w:line='360'])", namespaces=NS),
        f"{role}: body style must use 1.5 line spacing",
    )
    for style_id in ("Heading1", "Heading2", "Heading3"):
        report.require(
            styles.xpath(
                f"boolean(//w:style[@w:styleId='{style_id}']//w:sz[@w:val='24'])",
                namespaces=NS,
            ),
            f"{role}: {style_id} must be 12 pt",
        )
        report.require(
            styles.xpath(
                f"boolean(//w:style[@w:styleId='{style_id}']//w:rFonts[@w:eastAsia='SimHei'])",
                namespaces=NS,
            ),
            f"{role}: {style_id} Chinese font must be SimHei",
        )


def normal_after_value(styles: etree._Element) -> str | None:
    values = styles.xpath(
        "//w:style[@w:styleId='Normal']/w:pPr/w:spacing/@w:after",
        namespaces=NS,
    )
    return values[0] if values else None


def is_real_empty_paragraph(element: etree._Element) -> bool:
    if element.tag != f"{{{NS['w']}}}p":
        return False
    occupied = element.xpath(
        "boolean(.//w:t | .//m:t | .//m:oMath | .//a:blip | .//w:br | .//w:sectPr)",
        namespaces=NS,
    )
    return not occupied


def check_fraction_encoding(root: etree._Element, role: str, report: Report) -> int:
    math_text = "".join(root.xpath("//m:oMath//m:t/text() | //m:oMath//w:t/text()", namespaces=NS))
    report.require(
        not any(char in math_text for char in FRACTION_SLASHES),
        f"{role}: native equation contains a linear slash fraction; use an OMML m:f stacked fraction",
    )

    visible_text = text_of(root)
    match = LINEAR_FRACTION_RE.search(visible_text)
    report.require(
        match is None,
        f"{role}: visible linear fraction '{match.group(0) if match else ''}' found; use a stacked fraction bar",
    )
    raw_latex = RAW_LATEX_RE.search(visible_text)
    report.require(
        raw_latex is None,
        f"{role}: raw LaTeX command '{raw_latex.group(0) if raw_latex else ''}' is visible instead of native Word math",
    )
    return int(root.xpath("count(//m:f)", namespaces=NS))


def check_scientific_scripts(root: etree._Element, role: str, report: Report) -> None:
    visible_text = text_of(root)
    unicode_script = UNICODE_SCRIPT_RE.search(visible_text)
    unicode_script_text = unicode_script.group(0) if unicode_script else ""
    report.require(
        unicode_script is None,
        f"{role}: Unicode script lookalike {unicode_script_text!r} found; use native Word subscript/superscript or OMML",
    )

    suspicious: list[str] = []
    for run in root.xpath("//w:r[not(ancestor::m:oMath)]", namespaces=NS):
        text = "".join(run.xpath(".//w:t/text()", namespaces=NS))
        if not text or not BASELINE_CHEMICAL_DIGIT_RE.search(text):
            continue
        vertical = run.xpath("./w:rPr/w:vertAlign/@w:val", namespaces=NS)
        if not vertical:
            suspicious.append(text.strip())
    report.require(
        not suspicious,
        f"{role}: possible baseline chemical formula digits found in ordinary runs: {suspicious[:8]}; split formula counts into native subscript runs",
    )


def check_question_borders(facts: DocFacts, report: Report) -> None:
    for question in facts.questions:
        for block in question.blocks:
            horizontal = block.element.xpath(
                ".//w:pPr/w:pBdr/w:top | .//w:pPr/w:pBdr/w:bottom",
                namespaces=NS,
            )
            report.require(
                not horizontal,
                f"{facts.role}: question {question.number} contains a horizontal paragraph border; use blank space only",
            )


def check_student_writing_space(student: DocFacts, report: Report) -> None:
    report.require(
        "\u00a0" not in student.text,
        "student: nonbreaking spaces are being used as fake blank lines; use genuinely empty Normal paragraphs",
    )

    for question in student.questions:
        blanks = [block.element for block in question.blocks if is_real_empty_paragraph(block.element)]
        report.require(
            len(blanks) >= 5,
            f"student: question {question.number} has only {len(blanks)} real blank lines; ordinary questions need at least 5 full lines before render-based band positioning",
        )
        for index, paragraph in enumerate(blanks, start=1):
            style_values = paragraph.xpath("./w:pPr/w:pStyle/@w:val", namespaces=NS)
            report.require(
                not style_values or style_values[0] == "Normal",
                f"student: question {question.number} blank line {index} is not a Normal paragraph",
            )

            spacing_nodes = paragraph.xpath("./w:pPr/w:spacing", namespaces=NS)
            if not spacing_nodes:
                continue
            spacing = spacing_nodes[0]
            line = attr(spacing, "w", "line")
            rule = attr(spacing, "w", "lineRule")
            before = attr(spacing, "w", "before")
            after = attr(spacing, "w", "after")
            report.require(
                line in (None, "360") and rule in (None, "auto"),
                f"student: question {question.number} blank line {index} is not full 1.5-line spacing",
            )
            report.require(
                before in (None, "0"),
                f"student: question {question.number} blank line {index} has artificial before-spacing",
            )
            allowed_after = {None, student.normal_after}
            report.require(
                after in allowed_after,
                f"student: question {question.number} blank line {index} overrides Normal after-spacing ({after!r})",
            )


def image_hashes(elements: list[BodyBlock], rel_map: dict[str, str]) -> list[str]:
    hashes: list[str] = []
    for block in elements:
        for rel_id in block.element.xpath(".//a:blip/@r:embed", namespaces=NS):
            hashes.append(rel_map.get(rel_id, f"missing:{rel_id}"))
    return hashes


def common_checks(
    path: Path,
    role: str,
    report: Report,
    *,
    require_questions: bool = True,
) -> DocFacts | None:
    parts = load_parts(path, role, report)
    if parts is None:
        return None
    root, styles, settings = parts.root, parts.styles, parts.settings
    text = text_of(root)

    check_section_geometry(root, role, report)
    check_styles(styles, role, report)

    direct_sizes = set(root.xpath("//w:rPr/w:sz/@w:val", namespaces=NS))
    unexpected_sizes = sorted(direct_sizes - {"20", "24"})
    report.require(not unexpected_sizes, f"{role}: unexpected direct font sizes: {unexpected_sizes}")

    anchors = int(root.xpath("count(//wp:anchor)", namespaces=NS))
    blips = root.xpath("//a:blip/@r:embed", namespaces=NS)
    report.require(anchors == 0, f"{role}: floating images are not allowed")
    for rel_id in blips:
        report.require(rel_id in parts.image_hashes_by_rel, f"{role}: unresolved image relationship {rel_id}")

    report.require(
        settings.xpath("boolean(//m:mathFont[@m:val='Cambria Math'])", namespaces=NS),
        f"{role}: native math default must be Cambria Math",
    )
    math_count = int(root.xpath("count(//m:oMath)", namespaces=NS))
    fraction_count = check_fraction_encoding(root, role, report)
    check_scientific_scripts(root, role, report)
    math_hint = re.search(r"[=≠≤≥√∑∫]|(?:sin|cos|tan|log|ln)\s*\(?|[α-ωΑ-Ω]", text, re.IGNORECASE)
    report.require(not math_hint or math_count > 0, f"{role}: math-like text found but no native Word equations")

    report.require(
        not root.xpath("boolean(//w:instrText[contains(., 'PAGE')])", namespaces=NS),
        f"{role}: page-number fields are not allowed",
    )
    for marker in ("TODO", "待补", "待确认", "Lorem ipsum"):
        report.require(marker not in text, f"{role}: unfinished placeholder found: {marker}")

    try:
        Document(path)
    except Exception as exc:  # python-docx exposes several package-level exception types
        report.errors.append(f"{role}: python-docx cannot reopen file: {exc}")

    questions = find_question_blocks(root, role, report) if require_questions else []
    return DocFacts(
        role,
        path,
        root,
        text,
        math_count,
        fraction_count,
        len(blips),
        parts.image_hashes_by_rel,
        questions,
        normal_after_value(styles),
    )


def question_statement(question: QuestionBlock) -> list[BodyBlock]:
    statement: list[BodyBlock] = []
    for block in question.blocks:
        if is_answer_label_element(block.element):
            break
        if any(marker in block.text for marker in LEGACY_ANSWER_LABELS) or VARIATION_MARKER in block.text:
            break
        compact = normalize(block.text)
        if compact and not re.fullmatch(r"[_＿—–\-.·]{3,}", compact):
            statement.append(block)
    return statement


def statement_text(question: QuestionBlock) -> str:
    text = "".join(text_without_inline_answers(block.element) for block in question_statement(question))
    return normalize_for_parity(text)


def visible_runs(element: etree._Element) -> list[etree._Element]:
    return [
        run
        for run in element.xpath(".//w:r | .//m:r", namespaces=NS)
        if normalize(run_text(run))
    ]


def validate_answer_label_and_body(
    blocks: list[BodyBlock],
    label_index: int,
    role: str,
    item_name: str,
    report: Report,
) -> None:
    label = blocks[label_index].element
    label_runs = visible_runs(label)
    report.require(bool(label_runs), f"{role}: {item_name} answer label has no visible run")
    report.require(
        bool(label_runs) and all(run_color(run) == ANSWER_RED for run in label_runs),
        f"{role}: {item_name} standalone 答案 label must be dark red {ANSWER_RED}",
    )

    body_block = next(
        (block for block in blocks[label_index + 1 :] if normalize(block.text)),
        None,
    )
    report.require(body_block is not None, f"{role}: {item_name} standalone 答案 label has no body beneath it")
    if body_block is None:
        return
    report.require(
        body_block.element.tag == f"{{{NS['w']}}}p" and paragraph_fill(body_block.element) == ANSWER_FILL,
        f"{role}: {item_name} written-answer body must begin on the next nonempty paragraph with pale-yellow {ANSWER_FILL} paragraph shading",
    )
    red_body_runs = [run for run in visible_runs(body_block.element) if run_color(run) == ANSWER_RED]
    report.require(
        not red_body_runs,
        f"{role}: {item_name} written-answer body must remain normal black rather than red",
    )


def validate_answer_markup(
    facts: DocFacts,
    report: Report,
    *,
    require_signal: bool,
) -> None:
    root = facts.root
    role = facts.role
    for marker in LEGACY_ANSWER_LABELS:
        report.require(marker not in facts.text, f"{role}: legacy answer label remains: {marker}")

    label_elements = [
        paragraph
        for paragraph in root.xpath("//w:p", namespaces=NS)
        if is_answer_label_element(paragraph)
    ]
    inline_answer_runs: list[etree._Element] = []
    for run in root.xpath("//w:r | //m:r", namespaces=NS):
        if not normalize(run_text(run)):
            continue
        label_ancestor = next(
            (ancestor for ancestor in run.iterancestors() if is_answer_label_element(ancestor)),
            None,
        )
        if label_ancestor is not None:
            continue
        color = run_color(run)
        fill = run_fill(run)
        if color == ANSWER_RED:
            report.require(
                fill == ANSWER_FILL,
                f"{role}: red answer text outside the standalone 答案 label must have pale-yellow {ANSWER_FILL} run shading",
            )
        if fill == ANSWER_FILL:
            report.require(
                color == ANSWER_RED,
                f"{role}: pale-yellow {ANSWER_FILL} run shading is reserved for dark-red inline answer text",
            )
        if is_inline_answer_run(run):
            inline_answer_runs.append(run)

    all_blocks = body_blocks(root)
    for label_number, label in enumerate(label_elements, start=1):
        index = next(
            (index for index, block in enumerate(all_blocks) if block.element == label),
            None,
        )
        if index is None:
            report.errors.append(f"{role}: standalone 答案 label {label_number} is outside the document body flow")
            continue
        validate_answer_label_and_body(all_blocks, index, role, f"answer block {label_number}", report)

    if require_signal:
        report.require(
            bool(label_elements or inline_answer_runs),
            f"{role}: answer version contains neither styled inline answers nor a standalone 答案 block",
        )


def validate_question_answer_markup(question: QuestionBlock, role: str, report: Report) -> None:
    label_indices = [
        index for index, block in enumerate(question.blocks) if is_answer_label_element(block.element)
    ]
    report.require(
        len(label_indices) <= 1,
        f"{role}: question {question.number} has {len(label_indices)} standalone 答案 labels; expected at most 1",
    )
    inline_runs = [
        run
        for block in question_statement(question)
        for run in block.element.xpath(".//w:r | .//m:r", namespaces=NS)
        if is_inline_answer_run(run)
    ]
    report.require(
        bool(label_indices or inline_runs),
        f"{role}: question {question.number} has neither a styled inline answer nor a standalone 答案 block",
    )


def validate_pair(student: DocFacts, answer: DocFacts, report: Report) -> None:
    forbidden = (
        *LEGACY_ANSWER_LABELS,
        VARIATION_MARKER,
        "【疑点：",
        "来源：",
        "出处：",
        "参考答案：",
    )
    for marker in forbidden:
        report.require(marker not in student.text, f"student: contains answer-only marker {marker}")
    student_answer_labels = [
        paragraph
        for paragraph in student.root.xpath("//w:p", namespaces=NS)
        if is_answer_label_element(paragraph)
    ]
    report.require(not student_answer_labels, "student: contains a standalone answer-only 答案 label")
    student_inline_answers = [
        run
        for run in student.root.xpath("//w:r | //m:r", namespaces=NS)
        if is_inline_answer_run(run)
    ]
    report.require(not student_inline_answers, "student: contains styled inline answer text")

    validate_answer_markup(answer, report, require_signal=True)

    student_numbers = [question.number for question in student.questions]
    answer_numbers = [question.number for question in answer.questions]
    report.require(
        student_numbers == answer_numbers,
        f"pair: question numbers differ (student={student_numbers}, answer={answer_numbers})",
    )

    answer_by_number = {question.number: question for question in answer.questions}
    for student_question in student.questions:
        number = student_question.number
        answer_question = answer_by_number.get(number)
        if answer_question is None:
            continue

        validate_question_answer_markup(answer_question, "answer", report)

        report.require(
            statement_text(student_question) == statement_text(answer_question),
            f"pair: question {number} wording/options differ between versions",
        )

        student_images = image_hashes(question_statement(student_question), student.image_hashes_by_rel)
        answer_images = image_hashes(question_statement(answer_question), answer.image_hashes_by_rel)
        report.require(
            student_images == answer_images,
            f"pair: question {number} diagrams differ between versions",
        )

    report.require(answer.math_count >= student.math_count, "answer: native equation count is lower than student version")
    report.require(
        answer.fraction_count >= student.fraction_count,
        "answer: stacked fraction count is lower than student version",
    )
    report.require(answer.image_uses >= student.image_uses, "answer: image use count is lower than student version")


def validate(student_path: Path, answer_path: Path) -> Report:
    report = Report()
    student = common_checks(student_path, "student", report)
    answer = common_checks(answer_path, "answer", report)
    if student is not None:
        check_question_borders(student, report)
        check_student_writing_space(student, report)
    if answer is not None:
        check_question_borders(answer, report)
    if student is not None and answer is not None:
        validate_pair(student, answer, report)
    return report


def validate_chemistry_conventions(facts: DocFacts, role: str, report: Report) -> None:
    text = facts.text
    for forbidden in ("经典例题", "【巩固练习", "易错点整理", "本节易错点自行整理"):
        report.require(
            forbidden not in text,
            f"chemistry-{role}: forbidden chemistry-handout label remains: {forbidden}",
        )
    report.require(
        not re.search(r"【\s*例\s*\d+\s*】", text),
        f"chemistry-{role}: classic examples must use 例1, 例2, ... without brackets",
    )

    example_numbers = [int(value) for value in re.findall(r"(?<![\w】])例\s*(\d+)", text)]
    if example_numbers:
        unique_numbers = list(dict.fromkeys(example_numbers))
        report.require(
            unique_numbers == list(range(1, max(unique_numbers) + 1)),
            f"chemistry-{role}: classic-example numbering is not the contiguous sequence 例1..例N",
        )

    if role == "student":
        short_blanks = []
        for match in re.finditer(r"（([ \u3000\u00a0]*)）", text):
            inner = match.group(1).replace("\u00a0", " ")
            width = sum(2 if char == "\u3000" else 1 for char in inner)
            if width < 6:  # three full-width character cells
                short_blanks.append(match.group(0))
        report.require(
            not short_blanks,
            f"chemistry-student: {len(short_blanks)} choice/true-false blank parenthesis field(s) provide less than three full-width characters",
        )
        labels = [
            paragraph
            for paragraph in facts.root.xpath("//w:p", namespaces=NS)
            if is_answer_label_element(paragraph)
        ]
        styled_answers = [
            run
            for run in facts.root.xpath("//w:r | //m:r", namespaces=NS)
            if is_inline_answer_run(run)
        ]
        report.require(not labels, "chemistry-student: contains a standalone answer-only 答案 label")
        report.require(not styled_answers, "chemistry-student: contains styled inline answer text")
    else:
        validate_answer_markup(facts, report, require_signal=True)


def validate_replica(replica_path: Path, chemistry_role: str | None = None) -> Report:
    report = Report()
    facts = common_checks(
        replica_path,
        "replica",
        report,
        require_questions=False,
    )
    if facts is None:
        return report

    parts = load_parts(replica_path, "replica", report)
    if parts is not None:
        report.require(
            not normalize(parts.header_footer_text),
            "replica: headers and footers must contain no visible text",
        )
        report.require(
            parts.header_footer_graphics == 0,
            "replica: headers and footers must contain no graphics, watermarks, or page furniture",
        )
    report.require(bool(normalize(facts.text)), "replica: document body contains no editable text")
    if chemistry_role is not None:
        validate_chemistry_conventions(facts, chemistry_role, report)
    return report


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Validate tutoring handout pair invariants or one editable PDF reconstruction"
    )
    parser.add_argument("--student", type=Path)
    parser.add_argument("--answer", type=Path)
    parser.add_argument("--replica", type=Path)
    parser.add_argument("--chemistry-role", choices=("student", "answer"))
    args = parser.parse_args(argv)
    pair_selected = args.student is not None or args.answer is not None
    if args.replica is not None and pair_selected:
        parser.error("choose either --replica or the --student/--answer pair")
    if args.replica is None and not (args.student is not None and args.answer is not None):
        parser.error("provide --replica or both --student and --answer")
    if args.chemistry_role is not None and args.replica is None:
        parser.error("--chemistry-role is valid only with --replica")
    return args


def main(argv=None) -> int:
    args = parse_args(argv)
    if args.replica is not None:
        report = validate_replica(args.replica.resolve(), args.chemistry_role)
        success_message = (
            "replica package, layout, empty headers/footers, native math, scientific scripts, answer markup, and selected chemistry conventions passed"
        )
    else:
        report = validate(args.student.resolve(), args.answer.resolve())
        success_message = (
            "student/answer package, layout, role separation, numbering, answer markup, and question parity passed"
        )
    for warning in report.warnings:
        print(f"WARN: {warning}")
    if report.errors:
        print(f"FAIL ({len(report.errors)} error(s))", file=sys.stderr)
        for error in report.errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("PASS")
    print(success_message)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
