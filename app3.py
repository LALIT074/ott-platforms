from flask import Flask, request, jsonify
from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

app = Flask(__name__)

# Zomato URL
zomato_url = 'https://www.zomato.com/'

# Flask route to check phone number availability on Zomato
@app.route('/check_phone_number_zomato', methods=['POST'])
def check_phone_number_zomato():
    # Get the phone number from the API request
    data = request.get_json()
    phone_number = data.get('phone_number')

    if not phone_number:
        return jsonify({"error": "Phone number is required"}), 400

    # Set up the Firefox driver using webdriver_manager
    service = Service(GeckoDriverManager().install())
    browser = webdriver.Firefox(service=service)

    try:
        # Open the given URL
        browser.get(zomato_url)
        
        # Wait for the page to load completely
        WebDriverWait(browser, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        # Click the login/sign-up button to trigger the pop-up
        login_button_xpath = '/html/body/div[1]/div/div[2]/header/nav/ul[2]/li[4]'
        login_button = WebDriverWait(browser, 15).until(
            EC.element_to_be_clickable((By.XPATH, login_button_xpath))
        )
        login_button.click()

        # Wait to ensure iframes or modal pop-ups load
        time.sleep(5)

        # Switch to the correct iframe if present
        all_iframes = browser.find_elements(By.TAG_NAME, "iframe")
        phone_input = None

        # Iterate over iframes and try switching
        for iframe in all_iframes:
            try:
                browser.switch_to.frame(iframe)

                # Check if the phone input field is inside this iframe
                phone_input_xpath = '/html/body/div[2]/div/div[2]/section[2]/section/div[1]/div/input'
                phone_input = WebDriverWait(browser, 5).until(
                    EC.visibility_of_element_located((By.XPATH, phone_input_xpath))
                )
                break  # Exit the loop if the input is found

            except Exception:
                browser.switch_to.default_content()  # Switch back to the main content

        # Ensure you're in the correct frame or main content for the input
        if not phone_input:
            browser.switch_to.default_content()
            phone_input = WebDriverWait(browser, 15).until(
                EC.visibility_of_element_located((By.XPATH, phone_input_xpath))
            )

        # Enter the phone number into the input field
        phone_input.send_keys(phone_number)

        # Click the submit button (if needed)
        submit_button_xpath = '/html/body/div[2]/div/div[2]/section[2]/section/button'
        submit_button = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, submit_button_xpath))
        )
        submit_button.click()

        # Wait for any error message to display
        time.sleep(10)

        # Check if an error message appears
        try:
            error_message_xpath = '//*[@id="id-82"]/section[2]/section/p[1]'
            error_message = browser.find_element(By.XPATH, error_message_xpath)
            zomato_status = "not available" if error_message.is_displayed() else "available"
        except:
            zomato_status = "available"

        # Return the result for Zomato
        result = {
            "zomato_status": zomato_status
        }

    except Exception as e:
        result = {"error": str(e)}

    finally:
        # Close the browser
        browser.quit()

    # Return the result
    return jsonify(result)


# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True, port=9090)
