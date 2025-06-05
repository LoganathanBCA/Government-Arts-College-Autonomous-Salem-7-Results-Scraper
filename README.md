# Student Results Automation

This project automates the process of fetching 2023-2025 M.Sc. CS students 4th semester results from the [GACSLM7 eCampus portal](https://ecampus.cc/gacslm7/index.php) using Selenium and saves all results in an HTML file.
Afterward, it extracts each student's marks and totals them from the HTML file and paste it into student_results.xlsx. 

## Features

- Reads student data (register number and date of birth) from an Excel file.
- Automates form filling and result extraction using Microsoft Edge WebDriver.
- Saves all student results in a single HTML file (`all_results.html`).
- Runs a post-processing script (`main_output_process.py`) after fetching results.

## Requirements

- Python 3.7+
- Microsoft Edge browser
- Edge WebDriver (`msedgedriver.exe`) in the project directory or in your PATH

### Python Packages

Install dependencies using:

```sh
pip install -r requirements.txt
```

Contents of `requirements.txt`:
```
pandas
openpyxl
selenium
beautifulsoup4
```

## Usage

1. **Prepare the Excel file**  
   Create a `students.xlsx` file with at least the following columns:
   - `register_no`
   - `dob` (in `DD/MM/YYYY` or `YYYY-MM-DD` format)

2. **Place `msedgedriver.exe`**  
   Download and place the correct version of `msedgedriver.exe` in your project folder.

3. **Run the script**  
   Execute the main script:
   ```sh
   python main.py
   ```

   After completion, `output_process.py` will run automatically.

4. **View Results**  
   Open `all_results.html or student_result.xlsx` to see all student results.

## Notes

- Make sure the Edge WebDriver version matches your installed Edge browser version.
- The script uses placeholder email and mobile number fields. Adjust as needed.
- If you encounter issues, check that all dependencies are installed and the Excel file is correctly formatted.

## Issues Faced When Creating This Project

- **DOB Field Formatting:**  
  Handling various date of birth formats in the Excel file required careful parsing and conversion to match the website's expected input.

- **Unable to Screenshot the Page:**  
  Direct screenshot automation was unreliable due to dynamic content and scrolling issues. As a workaround, web scraping was used to extract the required data.

- **Random Order of Student Papers:**  
  The order of subjects and the presence of arrears varied between students, making it challenging to extract marks consistently for each subject.

## Fork and Contribute

- Suggestions for improvement are welcome!  
- You can fork this repository and contribute by:
  - Creating a user interface (UI) for easier operation.
  - Exploring better ways to automate screenshots, such as scrolling and capturing the full page or handling minimized windows.
  - How to implement percentage, ranking and many more
  - Improving the extraction logic to handle more edge cases.

Feel free to submit pull requests or open issues for discussion.

## License

This project is for educational and automation purposes.