# -*- coding: utf-8 -*-
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import traceback
from webdriver_manager.chrome import ChromeDriverManager
import csv
import requests


class mailer_rightmove:

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

        if query["view_property"] == "TRUE":
            driver.find_element_by_xpath("//label[@for='viewProperty']").click()

        driver.find_element_by_xpath("//select[@name='title']/option[text()='{}']".format(query["title"])).click()

        input = driver.find_element_by_name("firstName")
        input.send_keys(query["firstName"])

        input = driver.find_element_by_name("lastName")
        input.send_keys(query["lastName"])

        input = driver.find_element_by_name("comments")
        input.send_keys(query["comments"])

        input = driver.find_element_by_name("telephone")
        input.send_keys(query["telephone"])

        input = driver.find_element_by_name("email")
        input.send_keys(query["email"])

        driver.find_element_by_xpath(
            "//select[@id='countryCode']/option[@value='{}']".format(query["country_code"])).click()

        input = driver.find_element_by_name("postcode")
        input.send_keys(query["postcode"])
        time.sleep(2)

        driver.find_element_by_class_name("addresspicker-suggestions").click()

        input = driver.find_element_by_name("address")
        input.send_keys(query["address"])
        #time.sleep(2)

        try:
            driver.find_element_by_xpath("//select[@name='emailAnswerEnquirerType']/option[text()='{}']".format(query["emailAnswerEnquirerType"])).click()
            #time.sleep(2)
        except NoSuchElementException:
            pass

        try:
            driver.find_element_by_xpath("//select[@name='emailAnswerSellSituationType']/option[text()='{}']".format(query["to_sell"])).click()
            #time.sleep(2)
        except NoSuchElementException:
            pass

        try:
            driver.find_element_by_xpath("//select[@name='emailAnswerRentSituationType']/option[text()='{}']".format(query["to_let"])).click()
            #time.sleep(2)
        except NoSuchElementException:
            pass

        if query["request_valuation"] == "TRUE":
            driver.find_element_by_xpath("//label[@for='requestValuation']").click()

        driver.find_element_by_xpath("//input[@type='submit']").click()

        self.__pass_recaptcha(driver, url)
        time.sleep(10)

    def __pass_recaptcha(self, driver, url):

        API_KEY = '75537cc6be065cac2a1bd316d687a5c3'  # Your 2captcha API KEY
        captcha2 = driver.find_element_by_xpath("//div/div/iframe").get_attribute("src")
        captcha3 = captcha2.split('=')
        site_key = captcha3[2]
        #print(site_key)
        s = requests.Session()

        captcha_id = s.post(
            "http://2captcha.com/in.php?key={}&method=userrecaptcha&googlekey={}&pageurl={}".format(API_KEY, site_key,
                                                                                                    url)).text.split('|')[1]
        #print(captcha_id)
        recaptcha_answer = s.get("http://2captcha.com/res.php?key={}&action=get&id={}".format(API_KEY, captcha_id)).text
        #print(recaptcha_answer)
        while 'CAPCHA_NOT_READY' in recaptcha_answer:
            time.sleep(5)
            recaptcha_answer = s.get("http://2captcha.com/res.php?key={}&action=get&id={}".format(API_KEY, captcha_id)).text
            #print(recaptcha_answer)

        recaptcha_answer = recaptcha_answer.split('|')[1]
        #print(recaptcha_answer)
        time.sleep(2)

        driver.execute_script("document.getElementById('g-recaptcha-response').innerHTML='" + recaptcha_answer + "';");
        driver.execute_script("onCaptchaSubmit();")


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



with open("sample/rightmove.csv") as f:
    lis = [line.split(',') for line in f]
    flag_header = 1
    icnt = 0
    for x in lis:
        icnt = icnt + 1
        if flag_header == 1:
            flag_header = 0
            continue
        # if icnt != 5:
        #     continue
        url = x[0]
        query = {
            "more_details": x[1],
            "view_property": x[2],
            "title": x[3],#['Mr', 'Mrs', 'Miss', 'Ms']
            "firstName": x[4],
            "lastName": x[5],
            "comments": x[6],
            "telephone": x[7],
            "email": x[8],
            "country_code": x[9],#['AF', 'AL', 'DZ', 'AS', 'AD', 'AO', ...]
            "postcode": x[10],
            "address": x[11],
            "to_sell": x[12],
            "to_let": x[13],
            "request_valuation": x[14],
            "emailAnswerEnquirerType": x[15]#['surveyor_agent', 'investor_developer' ,'tenant_buyer', 'other']
        }
        with mailer_rightmove() as scraper:
            scraper.get_account(url, query)

