#!/usr/bin/env python3
"""
chapter_splitter.py — Phase 2, step 1.

Reads all 7 HP book .txt files from /books/, strips page markers, detects
ALL-CAPS chapter headings, and writes backend/data/chapters.json.

Run from any directory with the venv active:
    python backend/preprocessing/chapter_splitter.py
"""

import json
import logging
import re
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]
BOOKS_DIR = ROOT / "books"
OUTPUT_PATH = ROOT / "backend" / "data" / "chapters.json"

BOOK_TITLES: dict[int, str] = {
    1: "Harry Potter and the Philosopher's Stone",
    2: "Harry Potter and the Chamber of Secrets",
    3: "Harry Potter and the Prisoner of Azkaban",
    4: "Harry Potter and the Goblet of Fire",
    5: "Harry Potter and the Order of the Phoenix",
    6: "Harry Potter and the Half-Blood Prince",
    7: "Harry Potter and the Deathly Hallows",
}

# Matches page markers: "Page | 12 Harry Potter and the ... - J.K. Rowling"
PAGE_MARKER_RE = re.compile(r"^Page \| \d+ Harry Potter.*J\.K\. Rowling\s*$")

# Punctuation stripped before the uppercase check — covers all apostrophe variants
# (ASCII U+0027, left/right smart quotes U+2018/U+2019, modifier U+02BC),
# hyphens, commas, ampersands, and forward slashes.
_PUNCT_FOR_CAPS_CHECK = re.compile(r"[‘’’ʼ—\-,&/]")

# Scan artifact lines that can interrupt blank runs without being real content.
# Examples: "-4", "254", "7 " — stray page numbers or split page-marker fragments
# left behind after stripping the full "Page | N Harry Potter..." lines.
_ARTIFACT_LINE_RE = re.compile(r"^\s*[-–]?\d+\s*$")

# A chapter heading must have this many consecutive blank/artifact lines before it.
# Verified on Book 1: all 17 chapter headings have ≥4 preceding blanks.
# In-text ALL CAPS (newspaper headlines, supply lists, letter headers) have ≤3.
MIN_BLANKS_BEFORE_HEADING = 4

# Caps lines that pass the blank-count threshold but are NOT chapter headings.
# Keyed as (book_number, stripped_line_text).
#
# Book 5, "IMPROPER USE OF MAGIC OFFICE": the Ministry of Magic letter that
# Harry receives appears twice in the OCR. The first copy (L~1469, 1 blank
# before) is ignored by the threshold. The second copy (L~1805, 5 blanks
# before — extra blanks inserted by the OCR's page-break formatting) passes
# the threshold but is a letter department header, not a chapter heading.
_FALSE_POSITIVE_HEADINGS: frozenset[tuple[int, str]] = frozenset({
    (5, "IMPROPER USE OF MAGIC OFFICE"),
})


def _is_caps_line(line: str) -> bool:
    """Return True if this line contains only uppercase words plus common punctuation.

    Strips apostrophes and punctuation first to handle OCR apostrophe variants
    (ASCII, smart quotes, etc.) that would otherwise break a simple regex.
    Minimum 3 chars to exclude stray single-char artifacts like "/" or "I".
    """
    stripped = line.strip()
    if len(stripped) < 3:
        return False
    cleaned = _PUNCT_FOR_CAPS_CHECK.sub("", stripped)
    # Must be uppercase letters and spaces, at least 2 chars after cleaning
    return len(cleaned) >= 2 and bool(re.match(r"^[A-Z][A-Z ]+$|^[A-Z]{2,}$", cleaned))


def _count_preceding_blanks(lines: list[str], index: int) -> int:
    """Count blank lines before lines[index], treating scan artifact lines as blank.

    Artifact lines (bare numbers like "-4", "254") are stray fragments left after
    page-marker stripping that would otherwise break an otherwise-long blank run.
    Treating them as blank lets the threshold logic work correctly.
    """
    count = 0
    j = index - 1
    while j >= 0 and (lines[j].strip() == "" or bool(_ARTIFACT_LINE_RE.match(lines[j]))):
        count += 1
        j -= 1
    return count


def _strip_page_markers(lines: list[str]) -> list[str]:
    """Remove page-marker lines.

    Page markers inflate blank-line counts if left in — removing them first
    keeps the blank-line threshold logic clean.
    """
    return [line for line in lines if not PAGE_MARKER_RE.match(line)]


def _parse_chapters(lines: list[str], book_num: int) -> list[dict]:
    """Detect chapter headings and extract per-chapter text.

    Heading detection rules:
    1. Line must pass _is_caps_line().
    2. Must have >= MIN_BLANKS_BEFORE_HEADING consecutive blank lines before it.
    3. Consecutive caps lines with 0 blank lines between them are merged into a
       single title — handles multi-line headings e.g.:
         "THE JOURNEY FROM PLATFORM"  (line N)
         "NINE AND THREE-QUARTERS"    (line N+1, 0 blanks between)
       → merged as "THE JOURNEY FROM PLATFORM NINE AND THREE-QUARTERS".

    # AMBIGUOUS PARSING DECISIONS:
    # - Bare chapter-number digits (e.g. "3", "7") sometimes appear as the last
    #   non-blank line before the blank block preceding a heading. They are
    #   treated as blank by _count_preceding_blanks (via _ARTIFACT_LINE_RE) so
    #   they don't reduce the blank count below the detection threshold.
    # - OCR artifacts produce misspelled titles in some files
    #   (e.g. "DIAGON ALLY" for "DIAGON ALLEY", "NICHOLAS FLAMBL" for
    #   "NICOLAS FLAMEL"). Titles are preserved as-is; a correction lookup
    #   table is out of scope for this script.
    # - Book 3, chapter 18 title may appear truncated as "MOONY, WORMTAIL,
    #   PADFOOT, AND" (without "PRONGS") if the OCR dropped the last line of
    #   a two-line heading at a page break. Content split is still correct.
    # - Book 4: one chapter heading between THE PARTING OF THE WAYS and THE
    #   BEGINNING is absent from the OCR file — no caps line exists there at
    #   any blank count. Book 4 yields 36 detectable chapters; the 37th was
    #   lost entirely to OCR and cannot be recovered from text alone.
    # - Book 5: "IMPROPER USE OF MAGIC OFFICE" appears twice in the OCR. The
    #   first occurrence (1 blank before) is below threshold and ignored. The
    #   second (5 blanks, from OCR page-break formatting) passes the threshold
    #   but is a letter department header. Listed explicitly in
    #   _FALSE_POSITIVE_HEADINGS and skipped.
    """
    headings: list[tuple[int, str, int]] = []  # (title_start, merged_title, title_end)

    i = 0
    while i < len(lines):
        if _is_caps_line(lines[i]):
            stripped = lines[i].strip()
            if (
                (book_num, stripped) not in _FALSE_POSITIVE_HEADINGS
                and _count_preceding_blanks(lines, i) >= MIN_BLANKS_BEFORE_HEADING
            ):
                title_start = i
                parts = [stripped]
                i += 1
                # Absorb immediately-following caps lines (zero blank lines between)
                while (
                    i < len(lines)
                    and _is_caps_line(lines[i])
                    and _count_preceding_blanks(lines, i) == 0
                ):
                    parts.append(lines[i].strip())
                    i += 1
                headings.append((title_start, " ".join(parts), i))
                continue
        i += 1

    chapters: list[dict] = []
    for idx, (title_start, title, title_end) in enumerate(headings):
        next_heading_start = headings[idx + 1][0] if idx + 1 < len(headings) else len(lines)
        raw_lines = lines[title_end:next_heading_start]
        text = "\n".join(line.rstrip() for line in raw_lines).strip()

        chapters.append({
            "book_number": book_num,
            "book_title": BOOK_TITLES[book_num],
            "chapter_number": idx + 1,
            "chapter_title": title,
            "text": text,
        })

    return chapters


def main() -> None:
    """Parse all 7 books and write chapters.json. Prints a validation summary."""
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    all_chapters: list[dict] = []

    for book_num in range(1, 8):
        book_path = BOOKS_DIR / f"Book{book_num}.txt"
        if not book_path.exists():
            log.warning(f"  [WARN] Book{book_num}.txt not found at {book_path} — skipping")
            continue

        raw_lines = book_path.read_text(encoding="utf-8").splitlines()
        cleaned_lines = _strip_page_markers(raw_lines)
        chapters = _parse_chapters(cleaned_lines, book_num)
        all_chapters.extend(chapters)

        log.info(f"\nBook {book_num} — {BOOK_TITLES[book_num]}: {len(chapters)} chapters detected")
        if chapters:
            log.info(f"  First : {chapters[0]['chapter_title']}")
            log.info(f"  Last  : {chapters[-1]['chapter_title']}")
        else:
            log.warning("  [WARN] No chapters detected — check MIN_BLANKS_BEFORE_HEADING or file format")

    OUTPUT_PATH.write_text(
        json.dumps(all_chapters, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    log.info(f"\nTotal: {len(all_chapters)} chapters written to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
