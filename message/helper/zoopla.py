# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import traceback
from webdriver_manager.chrome import ChromeDriverManager
import requests
from selenium.common.exceptions import NoSuchElementException


class mailer_zoopla:

    def __init__(self):
        self.driver = self.__get_driver()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        if exc_type is not None:
            traceback.print_exception(exc_type, exc_value, tb)

        self.driver.close()
        self.driver.quit()

        return True

    def get_account(self, url, query):
        self.driver.get(url)
        self.__send_email(self.driver, url, query)

    def __send_email(self, driver, url, query):
        print(url)

        input = driver.find_element_by_name("name")
        input.send_keys(query["name"])

        input = driver.find_element_by_name("email")
        input.send_keys(query["email"])

        input = driver.find_element_by_name("phone")
        input.send_keys(query["phone"])

        try:
            input = driver.find_element_by_name("postcode")
            input.send_keys(query["postcode"])
        except NoSuchElementException:
            pass

        driver.find_element_by_xpath("//select[@name='status']/option[text()='{}']".format(query["status"])).click()

        input = driver.find_element_by_name("message")
        input.send_keys(query["message"])

        if query["send_news"] == "TRUE":
            driver.find_elements_by_class_name("ui-form__row")[7].click()

        if query["send_offers"] == "TRUE":
            driver.find_elements_by_class_name("ui-form__row")[8].click()

        self.__pass_recaptcha(driver, url)

        driver.find_element_by_xpath("//input[@type='submit']").click()

    def __pass_recaptcha(self, driver, url):

        API_KEY = '75537cc6be065cac2a1bd316d687a5c3'  # Your 2captcha API KEY
        site_key = driver.find_element_by_class_name('g-recaptcha').get_attribute('data-sitekey')  # site-key, read the 2captcha docs on how to get this

        s = requests.Session()

        captcha_id = s.post(
            "http://2captcha.com/in.php?key={}&method=userrecaptcha&googlekey={}&pageurl={}".format(API_KEY, site_key,
                                                                                                    url)).text.split('|')[1]

        recaptcha_answer = s.get("http://2captcha.com/res.php?key={}&action=get&id={}".format(API_KEY, captcha_id)).text

        while 'CAPCHA_NOT_READY' in recaptcha_answer:
            time.sleep(5)
            recaptcha_answer = s.get("http://2captcha.com/res.php?key={}&action=get&id={}".format(API_KEY, captcha_id)).text

        recaptcha_answer = recaptcha_answer.split('|')[1]

        driver.execute_script("document.getElementById('g-recaptcha-response').innerHTML='" + recaptcha_answer + "';");
        driver.execute_script("recaptchaSuccess();")
        time.sleep(2)


    def __get_driver(self, debug=False):
        options = Options()
        #if not debug:
            #options.add_argument("--headless")
        options.add_argument("--window-size=1366,768")
        options.add_argument("--disable-notifications")
        options.add_argument("--lang=en")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        input_driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)
        #time.sleep(5)
        return input_driver


url = "https://www.zoopla.co.uk/for-sale/contact/54293747?search_identifier=6acaf87b0785fe79a85ecb180152347a"
query = {
    "name": "Jamie Smith",
    "email": "bluesky_butterfly@outlook.com",
    "phone": "01234 56790",
    "postcode": "AB1 2CD",
    "status": "I have a property to let",
    "message": "Hi, Agency! Could you please...?",
    "request_viewing": True,
    "send_news": True,
    "send_offers": True
}
#with mailer_zoopla() as scraper:
#    scraper.get_account(url, query)


