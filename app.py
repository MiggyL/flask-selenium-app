from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Set up Google Sheets API credentials
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("prefab-drake-431702-g4-b7deec5e0aed.json", scope)
client = gspread.authorize(creds)

@app.route('/')
def home():
    return "Flask Selenium App is running!"

@app.route('/automate', methods=['POST'])
def automate():
    data = request.json
    sheet_name = data.get('sheet_name')
    row_number = int(data.get('row_number'))
    spreadsheet_id = data.get('spreadsheet_id')

    try:
        print(f"Attempting to access sheet: {sheet_name}, row: {row_number}, spreadsheet ID: {spreadsheet_id}")

        # Access the spreadsheet using the dynamic spreadsheet ID
        spreadsheet = client.open_by_key(spreadsheet_id)
        sheet = spreadsheet.worksheet(sheet_name)

        print(f"Successfully accessed sheet: {sheet_name}")

        # Get the data from columns B and C in the specified row
        row_data = sheet.row_values(row_number)
        if len(row_data) < 3:
            raise ValueError(f"Not enough data in row {row_number}, expected at least 3 columns.")
        
        name_data = row_data[1]  # Column B
        details_data = row_data[2]  # Column C

        print(f"Data in row {row_number}, Column B: {name_data}, Column C: {details_data}")

        # Selenium WebDriver Setup
        chrome_options = Options()
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        # Attempt to attach to an existing Chrome session
        chrome_options.debugger_address = "127.0.0.1:9222"  # Ensure Chrome is running with this debugger port

        chromedriver_path = r'D:/School/College/Notebooks/Year 3/Term 4/OJT/Ollopa/Project/chrome/chromedriver.exe'
        service = Service(executable_path=chromedriver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)

        try:
            # Switch to the tab with the URL for the "Add Card" form
            for handle in driver.window_handles:
                driver.switch_to.window(handle)
                print(f"Switched to tab with URL: {driver.current_url}")
                if "fifi-greetings-admin.firebaseapp.com/card/add" in driver.current_url:
                    print("Switched to the correct tab.")
                    break

            # Fill the form fields
            name_field = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, "//input[@formcontrolname='name']"))
            )
            print("Name field found. Sending keys...")
            name_field.send_keys(name_data)
            print("Name data sent.")

            details_field = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, "//textarea[@formcontrolname='details']"))
            )
            print("Details field found. Sending keys...")
            details_message = (
                f"Front Message: {name_data}\n"
                f"Inside Message: {details_data}\n\n"
                "Card Package:\n"
                "Includes 1 card, 1 envelope, and a FiBei Greeting Seal.\n"
                "Envelope color may vary.\n\n"
                "Dimension: 7.2\" H x 5\" W\n"
                "Layout: Portrait / 2 Fold\n"
                "Card Type: Standard\n"
                "Made from well-managed forest paper.\n\n"
                "Personalized Message:\n"
                "Add your own message and we'll do it for you.\n\n"
                "As a GIFT from us!\n"
                "You will get a FREE 5 Stickers from FiBei Greetings!!!"
            )
            details_field.send_keys(details_message)
            print("Details data sent.")
            return jsonify({"status": "success"})

        except Exception as e:
            print(f"An error occurred during Selenium operation: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500

        finally:
            driver.quit()

    except gspread.exceptions.WorksheetNotFound:
        error_message = f"Sheet '{sheet_name}' not found in the spreadsheet."
        print(error_message)
        return jsonify({"status": "error", "message": error_message}), 404
    except Exception as e:
        print(f"An error occurred when accessing Google Sheets: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
