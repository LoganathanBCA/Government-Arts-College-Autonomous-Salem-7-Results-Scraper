# 🎓 GACSLM7 Results Scraper

A web application that automates scraping student exam results from the **Government Arts College (Autonomous), Salem-7** [eCampus portal](https://ecampus.cc/gacslm7/index.php). Upload a spreadsheet of student register numbers and dates of birth, hit scrape, and download a consolidated Excel report of all results — no manual copy-pasting needed.

## ✨ Features

- **Bulk Scraping** — Scrape results for dozens of students in one go, automatically
- **Smart Retry** — Each student is retried up to 3 times if the portal is slow or unresponsive
- **File Upload** — Accepts both `.xlsx` (Excel) and `.csv` file formats
- **Live Progress** — Real-time progress bar, student-by-student status (✓ success / ✗ failed)
- **Consolidated Export** — All results merged into a single Excel file with dynamically discovered subject columns
- **Headless Browser** — Runs Chrome in the background (no visible browser window)

## 📋 Requirements

- **Python 3.10+**
- **Google Chrome** (installed on your system)

### Python Dependencies

| Package | Purpose |
|---------|---------|
| `fastapi` | Web framework for the backend API |
| `uvicorn[standard]` | ASGI server to run FastAPI |
| `selenium` | Browser automation for scraping |
| `webdriver-manager` | Auto-downloads the correct ChromeDriver |
| `beautifulsoup4` | HTML parsing of result tables |
| `pandas` | Data manipulation and DataFrame building |
| `openpyxl` | Excel file reading and writing |
| `python-multipart` | File upload handling in FastAPI |

## 🚀 How to Run

### 1. Clone the repository

```bash
git clone https://github.com/LoganathanBCA/Government-Arts-College-Autonomous-Salem-7-Results-Scraper.git
cd Government-Arts-College-Autonomous-Salem-7-Results-Scraper
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

This installs: `fastapi`, `uvicorn[standard]`, `selenium`, `webdriver-manager`, `beautifulsoup4`, `pandas`, `openpyxl`, and `python-multipart`.

### 3. Start the server

```bash
uvicorn backend.main:app --reload
```

### 4. Open in browser

Go to [http://127.0.0.1:8000](http://127.0.0.1:8000)

## 📄 Input File Format

The input file must be either `.xlsx` (Excel) or `.csv` with **exactly two columns**:

| Column | Header Name | Format | Example |
|--------|-------------|--------|---------|
| 1 | `register_no` | 2-digit year + 3-letter dept code + 6-digit number | `24UCS250904` |
| 2 | `dob` | Date of birth in **mm/dd/yyyy** | `10/20/2006` |

### Example `.xlsx` / `.csv`

| register_no | dob |
|-------------|------|
| 24UCS250904 | 10/20/2006 |
| 24UCS250905 | 11/28/2006 |
| 24UCS250906 | 03/15/2006 |
| ... | ... |

### Important Notes

- Column headers **must** be exactly `register_no` and `dob` (case-insensitive)
- DOB supports multiple formats: `mm/dd/yyyy`, `dd/mm/yyyy`, `yyyy-mm-dd`, `dd-mm-yyyy`
- The recommended format is `mm/dd/yyyy` to avoid ambiguity
- If using `.csv`, ensure the file is UTF-8 encoded
- No extra columns, empty rows, or merged cells — keep it simple

## 🔄 How It Works

### 1. 📤 Upload
- User uploads a `.xlsx` or `.csv` file via the web interface  
- Backend:
  - Validates required columns  
  - Parses and standardizes date formats  

---

### 2. 🌐 Scrape
- User clicks **"Start Scraping"**  
- Backend actions:
  - Launches headless Chrome browser  
  - Navigates to the results portal  

- For each student:
  - Fills:
    - Register Number  
    - Date of Birth  
    - Email format  
    - Mobile number  
  - Submits the form  
  - Clicks on the **"Result"** link  
  - Extracts the result table HTML  
  - Retries up to **3 times** if a failure occurs  

---

### 3. 🧠 Parse
- Uses `BeautifulSoup` to extract structured data:
  - Student Name  
  - Register Number  
  - Subject Codes & Marks *(dynamically detected)*  

---

### 4. 📊 Export
- All parsed data is merged into a single DataFrame  
- Output structure:
  - Name  
  - Register Number  
  - Subjects  
  - Total Marks  

- Final output:
  - Downloadable as **`student_results.xlsx`**  

---


## 📁 Project Structure

```
├── backend/
│   ├── __init__.py
│   ├── main.py          # FastAPI server & API endpoints
│   ├── scraper.py       # Selenium browser automation
│   ├── parser.py        # BeautifulSoup HTML parsing
│   └── exporter.py      # Pandas Excel export
├── frontend/
│   ├── index.html       # UI structure
│   ├── style.css        # Glassmorphic dark theme
│   └── app.js           # Upload, progress & results logic
├── requirements.txt
├── .gitignore
└── README.md
```

## 👨‍💻 Credits

**OG Developer:** [Loganathan](https://github.com/LoganathanBCA)

**Reworked by:** [Balaji](https://github.com/balafromtn)
