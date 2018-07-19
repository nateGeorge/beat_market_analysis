# would need to use selenium to get this to work...meh, just use a multidownloader for chrome
# core
import os
import time
import pytz
import glob
import calendar
import datetime
import shutil


# installed
import requests as req
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys

from fake_useragent import UserAgent
import numpy as np
import pandas as pd
import pandas_market_calendars as mcal

import constituents_utils as cu

# for headless browser mode with FF
# http://scraping.pro/use-headless-firefox-scraping-linux/
# from pyvirtualdisplay import Display
# display = Display(visible=0, size=(800, 600))
# display.start()


def setup_driver():
    """
    need to first download and setup geckodriver; instructions here:
    https://stackoverflow.com/a/40208762/4549682
    use geckodriver 0.20.1 until brokenpipeerror bug is fixed: https://github.com/mozilla/geckodriver/issues/1321
    """
    # couldn't get download working without manual settings...
    # https://stackoverflow.com/questions/38307446/selenium-browser-helperapps-neverask-openfile-and-savetodisk-is-not-working
    # create the profile (on ubuntu, firefox -P from command line),
    # download once, check 'don't ask again' and 'save'
    # also change downloads folder to ticker_data within git repo
    # then file path to profile, and use here:
    prof_path = '/home/nate/.mozilla/firefox/exzvq4ez.investing.com' # investing.com was the name of the profile
    # saves to /home/nate/github/beat_market_analysis folder by default
    profile = webdriver.FirefoxProfile(prof_path)
    # auto-download unknown mime types:
    # http://forums.mozillazine.org/viewtopic.php?f=38&t=2430485
    # set to text/csv and comma-separated any other file types
    # https://stackoverflow.com/a/9329022/4549682
    profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'text/csv')
    # https://www.lifewire.com/firefox-about-config-entry-browser-445707
    # profile.set_preference('browser.download.folderList', 1) # downloads folder
    # profile.set_preference('browser.download.manager.showWhenStarting', False)
    # profile.set_preference('browser.helperApps.alwaysAsk.force', False)
    # # profile.set_preference('browser.download.dir', '/tmp')
    # profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'text/csv')
    # profile.set_preference('browser.helperApps.neverAsk.saveToDisk', '*')
    driver = webdriver.Firefox(profile, executable_path='/home/nate/geckodriver')

    # prevent broken pipe errors
    # https://stackoverflow.com/a/13974451/4549682
    driver.implicitly_wait(5)
    # driver.set_page_load_timeout(10)
    return driver

def download_daily_data(driver=None, date=None):
    """
    checks which files already exist, then downloads remaining files to bring up to current

    or if 'date' supplied (i.e. 2018-04-12, yyyy-mm-dd, as a string), then downloads for that specific date
    """
    if driver is None:
        driver = setup_driver()
        driver = log_in(driver)
        time.sleep(3)  # wait for login to complete...could also use some element detection


def sign_in(driver):
    driver.get('https://www.investing.com')
    # if popup appears, close it -- seems to only happen when not signed in
    # seems to only appear after moving mouse around on page and waiting a sec
    # driver.execute_script("document.getElementsByClassName('popupCloseIcon')[0].click()")
    # from selenium.webdriver.common.action_chains import ActionChains
    # hoverover = ActionChains(driver).move_to_element(element1).perform()
    # time.sleep(5)
    # popup = driver.find_elements_by_id('PromoteSignUpPopUp')
    # if popup is not None:
    #     close_icon = popup.find_element_by_class_name('popupCloseIcon')
    #     close_icon.click()

    driver.find_element_by_xpath("//*[text()='Sign In']").click()
    username = os.environ.get('investing_username')
    password = os.environ.get('investing_password')
    driver.find_element_by_id('loginFormUser_email').send_keys(username)
    driver.find_element_by_id('loginForm_password').send_keys(password)
    # click the "Sign In" button
    popup = driver.find_element_by_id('loginPopup')
    time.sleep(1.27 + np.random.random())
    popup.find_element_by_link_text('Sign In').click()


def wait_for_data_download(filename=cu.get_home_dir() + 'S&P 600 Components.csv'):
    """
    waits for a file (filename) to exist; when it does, ends waiting
    """
    while not os.path.exists(filename):
        time.sleep(0.3)

    return


def check_if_files_exist():
    """
    """
    home_dir = cu.get_home_dir()
    data_list = ['price', 'performance', 'technical', 'fundamental']

    todays_date = datetime.datetime.today().strftime('%Y-%m-%d')
    # check if todays data has already been downloaded
    latest_date = cu.get_latest_daily_date().strftime('%Y-%m-%d')
    if latest_date == todays_date:
        # check that all 4 files are there
        for d in data_list:
            if not os.path.exists(home_dir + 'data/investing.com/sp600_{}_'.format(d) + todays_date + '.csv'):
                return False

        print("today's data is already downloaded")
        return True

    return False


def download_sp600_data(driver):
    """
    downloads sp600 data from investing.com
    """
    if check_if_files_exist():
        return

    print('data not up to date; downloading')

    home_dir = cu.get_home_dir()
    data_list = ['price', 'performance', 'technical', 'fundamental']
    todays_date = datetime.datetime.today().strftime('%Y-%m-%d')

    driver.get('https://www.investing.com/indices/s-p-600-components')

    for d, next_d in zip(data_list, data_list[1:] + [None]):
        print('downloading {} data...'.format(d))
        dl_link = driver.find_element_by_class_name('js-download-index-component-data')
        # need to use alt+click to download without prompt
        # set the option browser.altClickSave to true in config:
        # https://stackoverflow.com/questions/36338653/python-selenium-actionchains-altclick
        # https://superuser.com/a/1009706/435890
        ActionChains(driver).key_down(Keys.ALT).click(dl_link).perform()
        ActionChains(driver).key_up(Keys.ALT).perform()
        if next_d is not None:
            driver.find_element_by_id('filter_{}'.format(next_d)).click()

        time.sleep(1.57 + np.random.random())
        wait_for_data_download()
        shutil.move(home_dir + 'S&P 600 Components.csv', home_dir + 'data/investing.com/sp600_{}_'.format(d) + todays_date + '.csv')


if __name__ == '__main__':
    if not check_if_files_exist():
        driver = setup_driver()
        sign_in(driver)
        download_sp600_data(driver)
