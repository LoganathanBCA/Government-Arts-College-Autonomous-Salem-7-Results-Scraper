"""
exporter.py — pandas Excel/CSV export for student results.

Builds a unified DataFrame with dynamic subject columns discovered
from all students. No hardcoded subjects.
"""

import pandas as pd
from io import BytesIO
import logging

logger = logging.getLogger(__name__)


def build_dataframe(student_results: list[dict]) -> pd.DataFrame:
    """
    Build a unified DataFrame from all student result dicts.

    Args:
        student_results: List of dicts, each with keys:
            - register_no: str
            - name: str
            - subjects: dict {subject_code: marks, ...}

    Returns:
        DataFrame with columns: Name, Register No, <subject_codes...>, Total
    """
    if not student_results:
        return pd.DataFrame()

    # Discover all unique subject codes across all students
    all_subject_codes: list[str] = []
    seen = set()
    for student in student_results:
        for code in student.get("subjects", {}):
            if code not in seen:
                all_subject_codes.append(code)
                seen.add(code)

    # Build rows
    rows = []
    for student in student_results:
        row = {
            "Name": student.get("name", "UNKNOWN"),
            "Register No": student.get("register_no", "UNKNOWN"),
        }

        total = 0
        subjects = student.get("subjects", {})

        for code in all_subject_codes:
            marks = subjects.get(code, "-")
            row[code] = marks

            # Sum numeric marks only
            if marks != "-":
                try:
                    total += int(marks)
                except (ValueError, TypeError):
                    pass

        row["Total"] = total
        rows.append(row)

    # Build DataFrame with ordered columns
    columns = ["Name", "Register No"] + all_subject_codes + ["Total"]
    df = pd.DataFrame(rows, columns=columns)

    logger.info(
        f"Built DataFrame: {len(df)} students × {len(all_subject_codes)} subjects"
    )
    return df


def export_to_excel_bytes(df: pd.DataFrame) -> bytes:
    """
    Export DataFrame to Excel (.xlsx) and return as bytes.

    Args:
        df: pandas DataFrame to export.

    Returns:
        Excel file content as bytes.
    """
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Results")

        # Auto-adjust column widths
        worksheet = writer.sheets["Results"]
        for column_cells in worksheet.columns:
            max_length = 0
            column_letter = column_cells[0].column_letter
            for cell in column_cells:
                try:
                    cell_len = len(str(cell.value)) if cell.value else 0
                    max_length = max(max_length, cell_len)
                except Exception:
                    pass
            adjusted_width = min(max_length + 3, 40)
            worksheet.column_dimensions[column_letter].width = adjusted_width

    buffer.seek(0)
    return buffer.getvalue()
