import time

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as expect_cond
from selenium.webdriver.support.wait import WebDriverWait

from tkform import TkForm

tk_form: TkForm
wait: WebDriverWait
web_driver: WebDriver


def main():
    global tk_form
    tk_form = TkForm(_start_web_driver_submissions)  # Create Form
    tk_form.gui.mainloop()  # Start Tk


def _start_web_driver_submissions():
    """Start The Application """
    # TODO check if the webdriver/chrome has been started ...
    print("Start Application ... ")
    global wait, web_driver

    _Item = tk_form.init_item_for_form()
    web_driver = _init_chrome_options(tk_form.main_directory)
    wait = WebDriverWait(web_driver, 240)
    end_num = int(tk_form.i_fields.get("End Number:").input_field.get())
    print(f"Start creating NFTs in Collection: [{_Item.collection_link:s}]")
    while _Item.get_current_item_nu() <= end_num:
        print(f"Starting Item: [{_Item.get_current_item_title():s}]")
        web_driver.get(_Item.collection_link)
        _enter_all_data_for_item(_Item)
        _submit_cost_for_item_in_currency(_Item)
        _Item.increment_current_item()
        print('NFT creation completed!')
        _reset_webdriver_to_submit_next()

    print("Done with all Items")


def _enter_all_data_for_item(item):
    print("Wait for add item element button to load")
    _wait_xpath('//*[@id="__next"]/div[1]/main/div/div/div[1]/span/a')
    add_item_link = web_driver.find_element_by_xpath('//*[@id="__next"]/div[1]/main/div/div/div[1]/span/a')
    print("Click add new Item")
    add_item_link.click()
    time.sleep(1)

    print("Wait for item data fields")
    _wait_xpath('//*[@id="media"]')
    _enter_data_slice_for_element(item, '//*[@id="media"]', 5)
    _enter_data_slice_for_element(item, '//*[@id="name"]', 5)
    _enter_data_slice_for_element(item, '//*[@id="external_link"]', 5)
    _enter_data_slice_for_element(item, '//*[@id="description"]', 5)


def _enter_data_slice_for_element(item, xpath, wait_time=5):
    print(f"Enter data for xpath: [{xpath:s}]")
    link = web_driver.find_element_by_xpath(xpath)
    link.send_keys(item.get_current_item_absolute_path())
    time.sleep(wait_time)


def _submit_cost_for_item_in_currency(item):
    # Select Polygon blockchain if applicable
    if tk_form.gui.is_polygon.get():
        blockchain_button = \
            web_driver.find_element(By.XPATH,
                                    '//*[@id="__next"]/div[1]/main/div/div/section/div/form/div[7]/div/div[2]')
        blockchain_button.click()
        polygon_button_location = '//span[normalize-space() = "Mumbai"]'
        _wait_xpath(polygon_button_location)
        polygon_button = web_driver.find_element(By.XPATH, polygon_button_location)
        polygon_button.click()
    print("currency selected")

    create = web_driver.find_element_by_xpath(
        '//*[@id="__next"]/div[1]/main/div/div/section/div[2]/form/div/div[1]/span/button')
    web_driver.execute_script("arguments[0].click();", create)
    print("unsure ... execute some script ... picking a button")
    time.sleep(1)

    _wait_css_selector("i[aria-label='Close']")
    close = web_driver.find_element_by_css_selector("i[aria-label='Close']")
    print("click close")
    close.click()
    time.sleep(1)

    _wait_xpath('//*[@id="__next"]/div[1]/main/div/div/div[1]/div/span[2]/a')
    sell = web_driver.find_element_by_xpath('//*[@id="__next"]/div[1]/main/div/div/div[1]/div/span[2]/a')
    print("click sell")
    sell.click()

    _wait_css_selector("input[placeholder='Amount']")
    amount = web_driver.find_element_by_css_selector("input[placeholder='Amount']")
    print("enter value")
    amount.send_keys(item.price)

    _wait_css_selector("button[type='submit']")
    listing = web_driver.find_element_by_css_selector("button[type='submit']")
    print("click submit")
    listing.click()


def _reset_webdriver_to_submit_next():
    # wait until the window is available.
    print("Wait until window is free ... ")
    while len(web_driver.window_handles) != 2:
        print('.', end='')
        time.sleep(5)

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
    time.sleep(5)

    print("change control to main page")
    web_driver.switch_to.window(main_page)
    time.sleep(5)


def _init_chrome_options(in_project_path):
    """Helper Function to initialize chrome options """
    opt = Options()
    opt.add_experimental_option("debuggerAddress", "localhost:8989")
    w_driver = webdriver.Chrome(
        executable_path=in_project_path + "/chromedriver.exe",
        options=opt,
    )
    return w_driver


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
