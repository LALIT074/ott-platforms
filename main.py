from flask import Flask, request, jsonify
from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Initialize Flask app
app = Flask(__name__)

# URL to open
url = 'https://www.netflix.com/in/LoginHelp'

# Flask route to check phone number availability
@app.route('/check_phone_number', methods=['POST'])
def check_phone_number():
    # Get the phone number from the API request
    data = request.get_json()
    phone_number = data.get('phone_number')

    if not phone_number:
        return jsonify({"error": "Phone number is required"}), 400

    # Set up the Firefox driver using webdriver_manager
    service = Service(executable_path=GeckoDriverManager().install())
    browser = webdriver.Firefox(service=service)

    try:
        # Open the given URL
        browser.get(url)

        # Wait for the page to load
        time.sleep(2)

        # Find the element by XPath and click it
        button_xpath = '//*[@id="appMountPoint"]/div/div/div/div[3]/div[1]/div/div[1]/div[2]/label'
        button = browser.find_element(By.XPATH, button_xpath)
        button.click()
        time.sleep(2)

        # Find the input field by XPath and input the phone number
        input_xpath = '//*[@id="forgot_password_input"]'
        phone_number_input = browser.find_element(By.XPATH, input_xpath)
        phone_number_input.send_keys(phone_number)

        # Click the button to proceed
        button_xpath = '//*[@id="appMountPoint"]/div/div/div/div[3]/div[1]/div/button'
        button = WebDriverWait(browser, 5).until(EC.element_to_be_clickable((By.XPATH, button_xpath)))
        button.click()

        # Wait for the result to appear after clicking the button
        time.sleep(2)  # Replace this with WebDriverWait if necessary

        # Extract the result text
        result_xpath = '//*[@id="appMountPoint"]/div/div/div/div[3]/div[1]/div/div[1]/div[2]'
        result_element = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.XPATH, result_xpath)))
        result_text = result_element.text

        # Determine if the phone number is available
        if result_text == "This phone number is not linked to any account. Please try using your email instead.":
            response = {"phone_number": phone_number, "status": "not available"}
        else:
            response = {"phone_number": phone_number, "status": "available"}

    except Exception as e:
        response = {"error": str(e)}

    finally:
        # Close the browser
        browser.quit()

    # Return the response
    return jsonify(response)

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True ,port=9090)
