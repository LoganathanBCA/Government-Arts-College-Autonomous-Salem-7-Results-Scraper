from bs4 import BeautifulSoup
import openpyxl

with open("all_results.html", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "html.parser")

wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Results"

headers = [
    "NAME OF THE CANDIDATE",
    "REGISTER NUMBER",
    "Research Writing and Publication Ethics",
    "Project - Viva Voce",
    "Cloud Computing Lab",
    "Web Application Development & hosting",
    "Total"
]
ws.append(headers)

def extract_name_and_reg(name_row):
    strongs = name_row.find_all("strong")
    name = "UNKNOWN"
    reg = "UNKNOWN"
    if len(strongs) >= 2:
        # Name
        html = str(strongs[0])
        if "<br>" in html:
            name = html.split("<br>")[1].split("</strong>")[0].strip()
        else:
            text = strongs[0].get_text(separator=" ").strip()
            # Remove the label if present
            if "NAME OF THE CANDIDATE" in text:
                name = text.replace("NAME OF THE CANDIDATE", "").strip()
            else:
                name = text
        # Register number
        reg_html = str(strongs[1])
        if "<br>" in reg_html:
            reg = reg_html.split("<br>")[1].split("</strong>")[0].strip()
        else:
            reg = strongs[1].get_text(separator=" ").strip().split()[-1]
    return name, reg
def get_mark(rows, subject):
    for row in rows:
        cols = row.find_all("td")
        if len(cols) >= 5 and subject.lower() in cols[3].get_text().lower():
            if len(cols) > 7:
                mark = cols[6].get_text(strip=True)
                try:
                    return int(mark)
                except ValueError:
                    return 0
    return 0

for table in soup.find_all("table", id="exam_datail"):
    name_row = table.find_all("tr")[2]
    name, reg = extract_name_and_reg(name_row)
    rows = table.find("tbody").find_all("tr")
    rwp_ethics = get_mark(rows, "Research Writing and Publication Ethics")
    project = get_mark(rows, "Project - Viva Voce")
    cloud_lab = get_mark(rows, "Cloud Computing Lab")
    web_lab = get_mark(rows, "Web Application Development")
    total = rwp_ethics + project + cloud_lab + web_lab
    ws.append([name, reg, rwp_ethics, project, cloud_lab, web_lab, total])

wb.save("student_results.xlsx")
print("Excel file 'student_results.xlsx' created.")