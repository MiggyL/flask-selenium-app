from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return "Flask Selenium App is running!"

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

    driver.quit()

    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
