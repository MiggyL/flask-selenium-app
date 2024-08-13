from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time

app = Flask(__name__)

@app.route('/automate', methods=['POST'])
def automate():
    data = request.json
    row_data = data.get('row_data')  # The data from Google Sheets

    # Setup Selenium WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)

    # Open the backend application
    driver.get('https://fifi-greetings-admin.firebaseapp.com/card/add')

    # Fill out the form using Selenium
    name_field = driver.find_element_by_name("name")
    details_field = driver.find_element_by_name("details")

    name_field.send_keys(row_data['name'])  # Fill the name field
    details_field.send_keys(f"Front Message: {row_data['name']}\nInside Message: {row_data['details']}\n\nCard Package...")

    # Submit the form if needed
    # submit_button = driver.find_element_by_name("submit")
    # submit_button.click()

    driver.quit()

    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
