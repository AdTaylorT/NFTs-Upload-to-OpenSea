import os
import platform
import sys
import time

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as expect_cond
from selenium.webdriver.support.wait import WebDriverWait

from item import Item as _Item
from tkform import TkForm

tk_form: TkForm
web_driver: WebDriver
wait: WebDriverWait


def main():
    # TODO later story will elaborate on this for each system
    if platform.system() != 'Windows':
        return 1

    global tk_form
    tk_form = TkForm(_start_web_driver_submissions)  # Create Form
    tk_form.gui.mainloop()  # Start Tk
    # RHEl get version of chrome
    # google-chrome --version | sed 's/Google Chrome //' | perl -nle 's/([^.]*).*// && print $1'


def _start_web_driver_submissions():
    """Start The Application """
    # TODO check if the webdriver/chrome has been started ...
    print("Start Application ... ")
    global wait

    _init_web_driver()
    wait = WebDriverWait(web_driver, 2)
    end_num = int(tk_form.i_fields.get("End Number:").input_field.get())
    print(f"Start creating NFTs in Collection: [{_Item.collection_link:s}]")
    while _Item.get_current_item_nu() <= end_num:
        print(f"Starting Item: [{_Item.get_current_item_title():s}]")
        web_driver.get(_Item.collection_link)
        _enter_all_data_for_item()
        _submit_cost_for_item_in_currency()
        _Item.increment_current_item()
        print('NFT creation completed!')
        _reset_webdriver_to_submit_next()

    print("Done with all Items")


def _enter_all_data_for_item():
    print("Wait for add item element button to load")
    _wait_xpath('//*[@id="__next"]/div[1]/main/div/div/div[1]/span/a')
    add_item_link = web_driver.find_element_by_xpath('//*[@id="__next"]/div[1]/main/div/div/div[1]/span/a')
    print("Click add new Item")
    add_item_link.click()
    time.sleep(1)

    print("Wait for item data fields")
    _wait_xpath('//*[@id="media"]')
    _enter_data_slice_for_element(_Item.get_current_item_absolute_path(), '//*[@id="media"]', 2)
    _enter_data_slice_for_element(_Item.get_current_item_title(), '//*[@id="name"]', 2)
    _enter_data_slice_for_element(_Item.external_web_link, '//*[@id="external_link"]', 2)
    _enter_data_slice_for_element(_Item.description, '//*[@id="description"]', 2)


def _enter_data_slice_for_element(field_value, xpath, wait_time=5):
    print(f"Enter data for xpath: [{xpath:s}]")
    link = web_driver.find_element_by_xpath(xpath)
    link.send_keys(field_value)
    time.sleep(wait_time)


def _submit_cost_for_item_in_currency():
    # Select Polygon blockchain if applicable
    if tk_form.is_polygon.get():
        blockchain_button = \
            web_driver.find_element(By.XPATH,
                                    '//*[@id="__next"]/div[1]/main/div/div/section/div/form/div[7]/div/div[2]')
        blockchain_button.click()
        polygon_button_location = '//span[normalize-space() = "Mumbai"]'
        _wait_xpath(polygon_button_location)
        polygon_button = web_driver.find_element(By.XPATH, polygon_button_location)
        polygon_button.click()
    print("currency selected")
    time.sleep(1)

    create = web_driver.find_element_by_xpath(
        '//*[@id="__next"]/div[1]/main/div/div/section/div[2]/form/div/div[1]/span/button')
    web_driver.execute_script("arguments[0].click();", create)
    print("unsure ... execute some script ... picking a button")
    time.sleep(5)
    # TODO check is a human is needed??

    _wait_css_selector("i[aria-label='Close']")
    close = web_driver.find_element_by_css_selector("i[aria-label='Close']")
    print("click close -- on popup")
    close.click()
    time.sleep(1)

    _wait_xpath('//*[@id="__next"]/div[1]/main/div/div/div[1]/div/span[2]/a')
    sell = web_driver.find_element_by_xpath('//*[@id="__next"]/div[1]/main/div/div/div[1]/div/span[2]/a')
    print("click sell")
    sell.click()

    _wait_css_selector("input[placeholder='Amount']")
    amount = web_driver.find_element_by_css_selector("input[placeholder='Amount']")
    print("enter value")
    amount.send_keys(_Item.get_price_str())

    _wait_css_selector("button[type='submit']")
    listing = web_driver.find_element_by_css_selector("button[type='submit']")
    print("click submit")
    listing.click()


def _reset_webdriver_to_submit_next():
    # wait until the window is available.
    print("Wait until window is free ... ")
    while len(web_driver.window_handles) != 2:
        print('.', end='')
        time.sleep(2)

    main_page = web_driver.current_window_handle
    login_page = web_driver.window_handles[1]
    for handle in web_driver.window_handles:
        if handle != main_page:
            login_page = handle

    print("change the control to sign-in page")
    web_driver.switch_to.window(login_page)
    _wait_css_selector("button[data-testid='request-signature__sign']")
    sign = web_driver.find_element_by_css_selector("button[data-testid='request-signature__sign']")
    sign.click()
    time.sleep(2)

    print("change control to main page")
    web_driver.switch_to.window(main_page)
    time.sleep(2)


def _init_web_driver():
    """Helper Function to initialize chrome options """
    global web_driver

    chrome_driver_exec = os.path.join(sys.path[0], "chromedriver.exe")
    if not os.path.isfile(chrome_driver_exec):
        exit(1)

    opt = Options()
    opt.add_experimental_option("debuggerAddress", "localhost:9223")
    print(chrome_driver_exec)
    web_driver = webdriver.Chrome(executable_path=chrome_driver_exec,
                                  options=opt)


def _wait_css_selector(css):
    """Helper Function wait for css """
    try:
        wait.until(expect_cond.presence_of_element_located((By.CSS_SELECTOR, css)))
    except TimeoutException:
        print(f"Timed out waiting for element: [{css:s}]")
        print(TimeoutException)
        pass  # until this is working, don't care about this exception


def _wait_xpath(xpath):
    """Helper Function wait for xpath"""
    try:
        wait.until(expect_cond.presence_of_element_located((By.XPATH, xpath)))
    except TimeoutException:
        print(f"Timed out waiting for element: [{xpath:s}]")
        print(TimeoutException)
        pass  # until this is working, don't care about this exception


if __name__ == '__main__':
    main()
