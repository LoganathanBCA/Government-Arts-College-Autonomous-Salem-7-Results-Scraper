"""
parser.py — BeautifulSoup HTML parsing for student result tables.

Extracts student name, register number, and subject-wise marks dynamically.
Supports two table layouts:
  - Old (ecampus.cc): 8 cols, <br> in <strong>, table id="exam_datail"
  - New (SLMGACCOE): 7 cols, colon-separated text in <strong>, no table id
"""

from bs4 import BeautifulSoup, Tag
import logging

logger = logging.getLogger(__name__)

TABLE_IDS = ["exam_datail", "exam_detail", "result_table"]

# Header labels (case-insensitive matching)
NAME_LABELS = ["name of the candidate", "name of the student"]
REGNO_LABELS = ["register number", "register no", "reg no"]
SUBJECT_HEADERS = ["course code", "subject code", "sub-code", "sub code"]


def _find_table(soup: BeautifulSoup) -> Tag | None:
    """Locate the result table by known IDs, then fallback to first <table>."""
    for tid in TABLE_IDS:
        t = soup.find("table", id=tid)
        if t:
            return t
    return soup.find("table")


def _extract_after_colon(text: str, label: str) -> str | None:
    """Extract value after 'label:' in text. Case-insensitive."""
    lower = text.lower()
    idx = lower.find(label.lower() + ":")
    if idx == -1:
        idx = lower.find(label.lower() + " :")
        if idx == -1:
            return None
    val = text[idx + len(label) + 1:] if " :" not in text[idx:idx+len(label)+3] else text[idx + len(label) + 3:]
    val = val.strip().strip(":")
    return val if val else None


def _extract_after_br(html: str) -> str | None:
    """Extract text after <br> tag inside a <strong> element."""
    if "<br" not in html:
        return None
    parts = html.split("<br", 1)
    if len(parts) < 2:
        return None
    after_br = parts[1]
    if ">" in after_br:
        after_br = after_br.split(">", 1)[1]
    val = after_br.split("</strong>")[0].strip()
    val = val.replace("</strong", "").strip()
    return val if val else None


def parse_result_html(html: str) -> dict | None:
    """
    Parse raw HTML of one student's result table.

    Args:
        html: Raw HTML string containing the result table.

    Returns:
        Dictionary with keys:
            - register_no: str
            - name: str
            - subjects: dict {subject_code: marks_str, ...}
        Returns None if parsing fails.
    """
    try:
        soup = BeautifulSoup(html, "html.parser")
        table = _find_table(soup)
        if not table:
            logger.error("No table found in HTML")
            return None

        name = "UNKNOWN"
        register_no = "UNKNOWN"
        sub_code_idx = 1  # default for new portal (Course Code at col 1)

        # Scan all header rows (thead > tr, or all tr)
        thead = table.find("thead")
        rows = thead.find_all("tr") if thead else table.find_all("tr")

        for row in rows:
            # Check <strong> elements for student info
            for strong in row.find_all("strong"):
                text = strong.get_text(separator=" ").strip()
                text_lower = text.lower()

                for label in NAME_LABELS:
                    if label in text_lower:
                        val = _extract_after_colon(text, label)
                        if val:
                            name = val
                        if not val or name == "UNKNOWN":
                            val = _extract_after_br(str(strong))
                            if val:
                                name = val
                        break

                for label in REGNO_LABELS:
                    if label in text_lower:
                        val = _extract_after_colon(text, label)
                        if val:
                            register_no = val
                        if not val or register_no == "UNKNOWN":
                            val = _extract_after_br(str(strong))
                            if val:
                                register_no = val
                        break

            # Check <th> elements for column headers to detect layout
            for th in row.find_all("th"):
                th_text = th.get_text(strip=True).lower()
                for header in SUBJECT_HEADERS:
                    if header in th_text:
                        # Found the "Course Code" header - count its position
                        all_ths = row.find_all("th")
                        for i, t in enumerate(all_ths):
                            if header in t.get_text(strip=True).lower():
                                sub_code_idx = i
                                break
                        break

        # Extract subject rows
        subjects = {}
        tbody = table.find("tbody")
        data_rows = (
            tbody.find_all("tr")
            if tbody
            else [r for r in table.find_all("tr") if r.find("td")]
        )

        for row in data_rows:
            cols = row.find_all("td")
            if len(cols) < 6:
                continue

            # Subject code at detected column index
            if sub_code_idx < len(cols):
                subject_code = cols[sub_code_idx].get_text(strip=True)
            else:
                continue
            if not subject_code:
                continue

            # TOTAL is second from last column, RESULT is last
            total_col = cols[-2]
            marks = total_col.get_text(strip=True)

            if not marks or marks == "-" or marks.lower() in ("ab", "absent"):
                marks = "-"

            subjects[subject_code] = marks

        result = {
            "register_no": register_no,
            "name": name,
            "subjects": subjects,
        }

        logger.info(f"Parsed: {register_no} ({name}) — {len(subjects)} subjects")
        return result

    except Exception as e:
        logger.error(f"Failed to parse HTML: {e}")
        return None
