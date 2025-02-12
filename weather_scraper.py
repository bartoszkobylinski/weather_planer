import datetime
import logging
import os.path
import sqlite3
import time

import requests_cache
import schedule
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from credentials import credentials
from data_extracting import extract_data
from db_functions import insert_data_to_database, make_database
from points import points

requests_cache.install_cache("bouyweather_archive_cache", expire_after=360)

user = credentials.get("user")
password = credentials.get("password")
logging.basicConfig(
    filename=f"logger_scraper {datetime.datetime.now()}.txt", level=logging.INFO
)

seconds = 10


# setting a browser
options = webdriver.ChromeOptions()
options.add_argument("--incognito")
options.add_argument("--allow-running-insecure-content")
options.add_argument("--ignore-certificate-errors")

path = "/home/bart/PythonProjects/weather/weather_planer/chromedriver"

browser = webdriver.Chrome(path, options=options)
browser.get("https://www.buoyweather.com")
browser.fullscreen_window()


def login_user(user, password):
    # Function to go through login page on a website
    time.sleep(seconds)
    # Finding and clicking on a Sign in button on html
    try:
        browser.find_element_by_xpath('//*[@id="top"]/div/nav/ul/li[3]/a').click()
    except Exception as error:
        logging.warning(error)
    time.sleep(seconds)
    # Finding and filling up an email to log in
    try:
        browser.find_element_by_id("email").send_keys(user)
    except Exception as error:
        logging.warning(error)
    # Findirng and fillig up a password to log in
    try:
        browser.find_element_by_id("password").send_keys(password)
    except Exception as error:
        logging.warning(error)
    # Finding and clicking on a Sign in button
    try:
        browser.find_element_by_xpath(
            '//*[@id="content"]/div/div[2]/div/div/div[2]/form/button'
        ).click()
    except Exception as error:
        logging.warning(error)


def navigate_to_point(latitude, longitude):
    # Function to go to given coordinates
    time.sleep(seconds)
    try:
        browser.find_element_by_xpath('//*[@id="main"]/div/section/div/a[1]').click()
    except Exception as error:
        logging.warning(error)
    time.sleep(seconds)
    try:
        browser.find_element_by_id("custom-loc-toggle").click()
    except Exception as error:
        logging.warning(error)
    time.sleep(seconds)
    try:
        browser.find_element_by_id("custom-lat").send_keys(latitude)
        browser.find_element_by_id("custom-lon").send_keys(longitude)
        browser.find_element_by_id("custom-latlon").click()
    except Exception as error:
        logging.warning(error)
    time.sleep(seconds)
    try:
        browser.find_element_by_xpath(
            '//*[@id="map-container"]/div/div[2]/div[3]/div/a'
        ).click()
    except Exception as error:
        logging.warning(error)


def get_data_point():
    data_list = []
    all_days = browser.find_elements_by_class_name("day")
    for day in all_days:
        day = day.text.replace("\n", " ")
        data_list.append(day)
    return data_list


def gather_information_from_all_points():
    point = 1
    for coordinates in range(len(points)):
        navigate_to_point(
            points[coordinates][str(coordinates + 1)]["latitude"],
            points[coordinates][str(coordinates + 1)]["longitude"],
        )
        dictionary_with_data = extract_data(get_data_point())
        for dictionary in dictionary_with_data:
            insert_data_to_database(dictionary, point)
        browser.find_element_by_xpath('//*[@id="forecast-mini-map"]/div').click()
        point += 1


def job():
    login_user(user,password)
    gather_information_from_all_points()


def main():
    if not os.path.exists("weather.db"):
        make_database()
    schedule.every(5).minutes.do(job)

    while True:
        schedule.run_pending()
        time.sleep(1)


main()
