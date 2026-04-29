"""
parser.py — BeautifulSoup HTML parsing for student result tables.

Extracts student name, register number, and subject-wise marks dynamically.
No hardcoded subject names — discovers subjects from the HTML.
"""

from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)


def parse_result_html(html: str) -> dict | None:
    """
    Parse raw HTML of one student's result table.

    Args:
        html: Raw HTML string containing the exam_datail table.

    Returns:
        Dictionary with keys:
            - register_no: str
            - name: str
            - subjects: dict {subject_code: marks_str, ...}
        Returns None if parsing fails.
    """
    try:
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table", id="exam_datail")
        if not table:
            # If the html IS the table itself
            table = soup.find("table")
        if not table:
            logger.error("No table found in HTML")
            return None

        # Extract name and register number from thead rows
        name = "UNKNOWN"
        register_no = "UNKNOWN"

        thead_rows = table.find("thead")
        if thead_rows:
            all_rows = thead_rows.find_all("tr")
        else:
            all_rows = table.find_all("tr")

        for row in all_rows:
            strongs = row.find_all("strong")
            for strong in strongs:
                text_html = str(strong)
                text_plain = strong.get_text(separator=" ").strip()

                if "NAME OF THE CANDIDATE" in text_plain:
                    # Name is after <br> tag
                    if "<br" in text_html:
                        parts = text_html.split("<br")
                        if len(parts) > 1:
                            # Get text after the <br> and before </strong>
                            after_br = parts[1]
                            # Remove the closing > or /> 
                            if ">" in after_br:
                                after_br = after_br.split(">", 1)[1]
                            name = after_br.split("</strong>")[0].strip()
                            # Also handle <br/> variants
                            name = name.replace("</strong", "").strip()
                    if name == "UNKNOWN":
                        name = text_plain.replace("NAME OF THE CANDIDATE", "").strip()

                elif "REGISTER NUMBER" in text_plain:
                    if "<br" in text_html:
                        parts = text_html.split("<br")
                        if len(parts) > 1:
                            after_br = parts[1]
                            if ">" in after_br:
                                after_br = after_br.split(">", 1)[1]
                            register_no = after_br.split("</strong>")[0].strip()
                            register_no = register_no.replace("</strong", "").strip()
                    if register_no == "UNKNOWN":
                        # Fallback: last word
                        register_no = text_plain.split()[-1]

        # Extract subject rows from tbody
        subjects = {}
        tbody = table.find("tbody")
        if tbody:
            data_rows = tbody.find_all("tr")
        else:
            # Fallback: all rows that have <td> elements
            data_rows = [r for r in table.find_all("tr") if r.find("td")]

        for row in data_rows:
            cols = row.find_all("td")
            if len(cols) < 7:
                continue

            # Table structure (with colspan=2 on title):
            # col 0: SEMESTER
            # col 1: PART
            # col 2: SUB-CODE
            # col 3: TITLE OF PAPER (colspan=2, but BS4 sees it as 1 td)
            # col 4: CA  (index 4 because colspan doesn't add extra td)
            # col 5: SE
            # col 6: TOTAL
            # col 7: RESULT

            subject_code = cols[2].get_text(strip=True)
            if not subject_code:
                continue

            # Total marks is at index 6 (TOTAL column)
            # With colspan=2 on the title, we still have cols indexed as:
            # 0=SEM, 1=PART, 2=SUB-CODE, 3=TITLE, 4=CA, 5=SE, 6=TOTAL, 7=RESULT
            # But if the title has colspan=2, BS4 still treats it as a single <td>
            # So we need to count from the end: TOTAL is cols[-2], RESULT is cols[-1]
            # Safer approach: use index from end
            total_col = cols[-2]  # TOTAL column (second from last)
            marks = total_col.get_text(strip=True)

            # If marks is empty or dash, mark as "-"
            if not marks or marks == "-" or marks.lower() == "ab":
                marks = "-"

            subjects[subject_code] = marks

        result = {
            "register_no": register_no,
            "name": name,
            "subjects": subjects,
        }

        logger.info(
            f"Parsed: {register_no} ({name}) — {len(subjects)} subjects"
        )
        return result

    except Exception as e:
        logger.error(f"Failed to parse HTML: {e}")
        return None
