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
        driver.find_element_by_xpath("//div[@class='ui-cookie-consent-choose__buttons']/button[@data-responsibility='acceptAll']").click()
        time.sleep(3)
        input = driver.find_element_by_name("name")
        input.send_keys(query["name"])

        input = driver.find_element_by_name("email")
        input.send_keys(query["email"])

        input = driver.find_element_by_name("phone")
        input.send_keys(query["phone"])

        if query["company"] != "null":
            driver.find_element_by_xpath("//input[@name='company_name']").send_keys(query["company"])

        if query["sector"] != "null":
            driver.find_element_by_xpath("//input[@name='business_sector']").send_keys(query["sector"])

        if query["no."] != "null":
            driver.find_element_by_xpath("//input[@name='number_of_employees']").send_keys(query["no."])

        if query["date"] != "null":
            driver.find_element_by_xpath("//input[@name='ideal_date_of_occupation']").send_keys(query["date"])


        try:
            input = driver.find_element_by_name("postcode")
            input.send_keys(query["postcode"])
        except NoSuchElementException:
            pass

        try:
            driver.find_element_by_xpath("//select[@name='status']/option[@value='{}']".format(query["status"])).click()
            time.sleep(2)
        except NoSuchElementException:
            pass

        input = driver.find_element_by_name("message")
        input.send_keys(query["message"])

        elems = driver.find_elements_by_class_name("ui-form__row")

        if query["request_viewing"] == "TRUE":
            elems[len(elems) - 3].click()

        if query["send_news"] == "TRUE":
            elems[len(elems) - 2].click()

        if query["send_offers"] == "TRUE":
            elems[len(elems) - 1].click()

        self.__pass_recaptcha(driver, url)

        driver.find_element_by_xpath("//input[@type='submit']").click()
        time.sleep(5)

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


with open("sample/zoopla.csv") as f:
    lis = [line.split(',') for line in f]
    flag_header = 1
    icnt = 0
    for x in lis:
        icnt = icnt + 1
        if flag_header == 1:
            flag_header = 0
            continue
        # if icnt != 6:
        #     continue
        url = x[0]
        query = {
            "name": x[1],
            "email": x[2],
            "phone": x[3],
            "postcode": x[4],
            "status": x[5],
            "company": x[6],
            "sector": x[7],
            "no.": x[8],
            "date": x[9],
            "message": x[10],
            "request_viewing": x[11],
            "send_news": x[12],
            "send_offers": x[13].replace('\n', '')
        }
        with mailer_zoopla() as scraper:
            scraper.get_account(url, query)