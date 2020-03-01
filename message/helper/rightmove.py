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
        driver.find_element_by_xpath("//select[@id='buyingPropertyEnquiry-title']/option[text()='{}']".format(query["title"])).click()

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
        time.sleep(2)
        driver.find_element_by_xpath("//select[@name='emailAnswerEnquirerType']/option[text()='{}']".format(query["emailAnswerEnquirerType"])).click()
        time.sleep(2)
        driver.find_element_by_xpath("//input[@type='submit']").click()

        self.__pass_recaptcha(driver, url)
        time.sleep(2)

    def __pass_recaptcha(self, driver, url):

        API_KEY = '75537cc6be065cac2a1bd316d687a5c3'  # Your 2captcha API KEY
        captcha2 = driver.find_element_by_xpath("//div/div/iframe").get_attribute("src")
        captcha3 = captcha2.split('=')
        site_key = captcha3[2]
        print(site_key)
        s = requests.Session()

        captcha_id = s.post(
            "http://2captcha.com/in.php?key={}&method=userrecaptcha&googlekey={}&pageurl={}".format(API_KEY, site_key,
                                                                                                    url)).text.split('|')[1]
        print(captcha_id)
        recaptcha_answer = s.get("http://2captcha.com/res.php?key={}&action=get&id={}".format(API_KEY, captcha_id)).text
        print(recaptcha_answer)
        while 'CAPCHA_NOT_READY' in recaptcha_answer:
            time.sleep(5)
            recaptcha_answer = s.get("http://2captcha.com/res.php?key={}&action=get&id={}".format(API_KEY, captcha_id)).text
            print(recaptcha_answer)

        recaptcha_answer = recaptcha_answer.split('|')[1]
        print(recaptcha_answer)
        time.sleep(10)

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


url = "https://www.rightmove.co.uk/commercial-property-for-sale/contactBranch.html?propertyId=" \
      "86731319&backListLink=%2Fcommercial-property-for-sale%2Ffind.html%3FsearchType%3DSALE%26" \
      "locationIdentifier%3DREGION%255E91993%26insId%3D1%26radius%3D0.0%26displayPropertyType" \
      "%3Dcommercial%26businessForSale%3D%26minBedrooms%3D%26maxBedrooms%3D%26minPrice%3D" \
      "%26maxPrice%3D%26areaSizeUnit%3Dsqft%26minSize%3D%26maxSize%3D%26partBuyPartRent%3D%2" \
      "6maxDaysSinceAdded%3D%26_includeSSTC%3Don%26sortByPriceDescending%3D%26primaryDisplay" \
      "PropertyType%3D%26secondaryDisplayPropertyType%3D%26oldDisplayPropertyType%3D%26oldPr" \
      "imaryDisplayPropertyType%3D%26newHome%3D%26auction%3Dfalse&backToPropertyURL=/commercia" \
      "l-property-for-sale/property-86731319.html&fromButtonId=property-detail-button-rhs"
query = {
            "view_property": True,
            "title": "Mrs",#['Mr', 'Mrs', 'Miss', 'Ms']
            "firstName": "testA",
            "lastName": "testB",
            "comments": "Hi, Agency! Could you please...?",
            "telephone": "01234 56790",
            "email": "bluesky_butterfly@outlook.com",
            "country_code": "GB",#['AF', 'AL', 'DZ', 'AS', 'AD', 'AO', ...]
            "postcode": "AB1 2CD",
            "address": "TEST Address",
            "emailAnswerEnquirerType": "investor_developer"#['surveyor_agent', 'investor_developer' ,'tenant_buyer', 'other']
        }
#with mailer_rightmove() as scraper:
#    scraper.get_account(url, query)


