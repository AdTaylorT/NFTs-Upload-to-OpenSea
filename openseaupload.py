import os
import subprocess
import sys
import time
import tkinter

from tkinter import *
from tkinter import filedialog

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as expect_cond
from selenium.webdriver.support.wait import WebDriverWait

# Initialize Globals
print("create gui")
gui = Tk()
gui.geometry('450x350')
gui.title("NFTs Upload to OpenSea  ")
main_directory = os.path.join(sys.path[0])
is_polygon = BooleanVar(value=False)


class IField:
    def __init__(self, label, row_io, column_io, master=gui, grid_padx=0):
        """ initialize the object

        :param label:
        :param row_io:
        :param column_io:
        :param master:
        :param grid_padx: optional to set grid
        """
        master = master
        self.input_field = Entry(master, justify=LEFT)
        self.input_field.label = Label(master, text=label)
        self.input_field.label.grid(row=row_io, column=column_io)
        self.input_field.grid(row=row_io, column=column_io + 1, sticky='w')
        if grid_padx:
            print(grid_padx)
            self.input_field.grid(ipadx=grid_padx)

    def insert_text(self, text):
        self.input_field.delete(0, "end")
        self.input_field.insert(0, text)


class Item:
    """ Static object placeholder for fields """
    _current_num = 0  # counter
    _title_format = ""
    _file_path = ""
    _folder_path = ""
    _image_format = "png"

    collection_link = ""
    external_web_link = ""
    price = 1
    description = ""

    @staticmethod
    def increment_current_item():
        Item._current_num += 1

    @staticmethod
    def get_current_item_nu():
        return Item._current_num

    @staticmethod
    def get_current_item_str():
        return str(Item._current_num)

    @staticmethod
    def _build_abs_item_path():
        Item._file_path = os.path.join(
            Item._folder_path,
            '.'.join([Item.get_current_item_str(), Item._image_format]))

        return Item._file_path

    @staticmethod
    def is_current_item_path_valid():
        return os.path.isfile(Item._build_abs_item_path())

    @staticmethod
    def get_current_item_absolute_path():
        if Item.is_current_item_path_valid():
            return Item._file_path
        raise FileNotFoundError

    @staticmethod
    def get_current_item_title():
        return ''.join([Item._title_format, Item.get_current_item_str()])


def init():
    print("enter init")
    IField("Start Number:", 3, 0, gui)
    IField("Title:", 6, 0, gui)
    IField("", 21, 0, gui, 80)
    IField("NFT Image Format:", 8, 0, gui)
    IField("OpenSea Collection Link:", 2, 0, gui)
    IField("External link:", 9, 0, gui)
    IField("Price:", 5, 0, gui)
    IField("Description:", 7, 0, gui)
    IField("End Number:", 4, 0, gui)

    # gui buttons
    button_start = tkinter.Button(gui, width=20, bg="green", fg="white", text="Start", command=main)
    button_start.grid(row=25, column=1, sticky='w')
    polygon_check_box = tkinter.Checkbutton(gui, text='Polygon Blockchain', variable=is_polygon)
    polygon_check_box.grid(row=20, column=0, sticky='w')
    open_browser = tkinter.Button(gui, width=20, text="Open Chrome Browser", command=open_chrome_profile)
    open_browser.grid(row=22, column=1, sticky='w')
    upload_folder_input_button = tkinter.Button(gui, width=20, text="NFTs Source Folder:",
                                                command=source_folder_location)
    upload_folder_input_button.grid(row=21, column=0, sticky='w')


def main():
    web_driver = init_chrome_options(main_directory)
    wait = WebDriverWait(web_driver, 15)

    """Start The Application """
    print("Start Application ... ")
    Item._current_num = int(IField("Start Number:", 3, 0, gui).input_field.get())
    Item._title_format = IField("Title:", 6, 0, gui).input_field.get()
    Item._folder_path = IField("", 21, 0, gui, 80).input_field.get()
    Item._image_format = IField("NFT Image Format:", 8, 0, gui).input_field.get()
    Item.collection_link = IField("OpenSea Collection Link:", 2, 0, gui).input_field.get()
    Item.external_web_link = str(IField("External link:", 9, 0, gui).input_field.get())
    Item.price = float(IField("Price:", 5, 0, gui).input_field.get())
    Item.description = IField("Description:", 7, 0, gui).input_field.get()
    end_num = int(IField("End Number:", 4, 0, gui).input_field.get())
    print(f"Start creating NFTs in Collection: [{Item.collection_link:s}]")
    while Item.get_current_item_nu() <= end_num:
        upload_file(Item, web_driver, wait)
        Item.increment_current_item()
        reset_webpage_to_submit_next(web_driver, wait)

    print("Done with all Items")


def upload_file(item, web_driver, wait):
    print(f"Starting Item: [{Item.get_current_item_title():s}]")
    web_driver.get(Item.collection_link)
    enter_image_details_on_webform(item, web_driver, wait)
    submit_cost_for_item(item, web_driver, wait)
    print('NFT creation completed!')


def enter_image_details_on_webform(item, web_driver, wait):
    wait_xpath(wait, '//*[@id="__next"]/div[1]/main/div/div/div[1]/span/a')
    add_item_link = web_driver.find_element_by_xpath('//*[@id="__next"]/div[1]/main/div/div/div[1]/span/a')
    add_item_link.click()
    time.sleep(1)

    wait_xpath(wait, '//*[@id="media"]')
    image_upload_link = web_driver.find_element_by_xpath('//*[@id="media"]')
    image_upload_link.send_keys(item.get_current_item_absolute_path())

    name = web_driver.find_element_by_xpath('//*[@id="name"]')
    name.send_keys(item.get_current_item_title())  # +1000 for other folders #change name before "#"
    time.sleep(0.5)

    ext_link = web_driver.find_element_by_xpath('//*[@id="external_link"]')
    ext_link.send_keys(item.external_web_link)
    time.sleep(0.5)

    desc = web_driver.find_element_by_xpath('//*[@id="description"]')
    desc.send_keys(item.description)
    time.sleep(0.5)


def submit_cost_for_item(item, web_driver, wait):
    # Select Polygon blockchain if applicable
    if is_polygon.get():
        blockchain_button = \
            web_driver.find_element(By.XPATH,
                                    '//*[@id="__next"]/div[1]/main/div/div/section/div/form/div[7]/div/div[2]')
        blockchain_button.click()
        polygon_button_location = '//span[normalize-space() = "Mumbai"]'
        wait_xpath(wait, polygon_button_location)
        polygon_button = web_driver.find_element(By.XPATH, polygon_button_location)
        polygon_button.click()

    create = web_driver.find_element_by_xpath(
        '//*[@id="__next"]/div[1]/main/div/div/section/div[2]/form/div/div[1]/span/button')
    web_driver.execute_script("arguments[0].click();", create)
    time.sleep(1)

    wait_css_selector(wait, "i[aria-label='Close']")
    close = web_driver.find_element_by_css_selector("i[aria-label='Close']")
    close.click()
    time.sleep(1)

    wait_xpath(wait, '//*[@id="__next"]/div[1]/main/div/div/div[1]/div/span[2]/a')
    sell = web_driver.find_element_by_xpath('//*[@id="__next"]/div[1]/main/div/div/div[1]/div/span[2]/a')
    sell.click()

    wait_css_selector(wait, "input[placeholder='Amount']")
    amount = web_driver.find_element_by_css_selector("input[placeholder='Amount']")
    amount.send_keys(item.price)

    wait_css_selector(wait, "button[type='submit']")
    listing = web_driver.find_element_by_css_selector("button[type='submit']")
    listing.click()


def reset_webpage_to_submit_next(web_driver, wait):
    # wait until the window is available.
    print("Wait until window is free ... ")
    while len(web_driver.window_handles) != 2:
        print('.', end='')
        time.sleep(.5)

    main_page = web_driver.current_window_handle
    login_page = web_driver.window_handles[1]
    for handle in web_driver.window_handles:
        if handle != main_page:
            login_page = handle

    # change the control to sign-in page
    web_driver.switch_to.window(login_page)
    wait_css_selector(wait, "button[data-testid='request-signature__sign']")
    sign = web_driver.find_element_by_css_selector("button[data-testid='request-signature__sign']")
    sign.click()
    time.sleep(1)

    # change control to main page
    web_driver.switch_to.window(main_page)
    time.sleep(1)


def init_chrome_options(in_project_path):
    """Helper Function to initialize chrome options """
    opt = Options()
    opt.add_experimental_option("debuggerAddress", "localhost:8989")
    w_driver = webdriver.Chrome(
        executable_path=in_project_path + "/chromedriver.exe",
        options=opt,
    )
    return w_driver


def wait_css_selector(wait, css):
    """Helper Function wait for css """
    try:
        wait.until(expect_cond.presence_of_element_located((By.CSS_SELECTOR, css)))
    except TimeoutException:
        print(f"Timed out waiting for element: [{css:s}]")


def wait_xpath(wait, xpath):
    """Helper Function wait for xpath"""
    try:
        wait.until(expect_cond.presence_of_element_located((By.XPATH, xpath)))
    except TimeoutException:
        print(f"Timed out waiting for element: [{xpath:s}]")


def open_chrome_profile():
    """ Create a new Chrome subprocess

    :return: None
    """
    subprocess.Popen(
        [
            "start",
            "chrome",
            "--remote-debugging-port=8989",
            "--user-data-dir=" + main_directory + "/chrome_profile",
        ],
        shell=True,
    )


def source_folder_location():
    """ Ask User for directory on clicking button, changes button name.

    side effect: modifies path_to_nfts
    :return: None
    """
    folder_field = IField("", 21, 0, gui, 80)
    image_folder = folder_field.input_field.get()
    image_folder = filedialog.askdirectory(initialdir=image_folder) if os.path.isdir(image_folder) \
        else filedialog.askdirectory()
    if image_folder:
        folder_field.insert_text(image_folder)


init()

# if __name__ == '__main__':

""" Start Tk """
gui.mainloop()
