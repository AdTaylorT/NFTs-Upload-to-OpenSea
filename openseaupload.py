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

from item import Item


# these could very well be statics, but whatever for now ...
# expectation is only one of these programs will run at once...


class MyForm:
    def __init__(self, _gui):
        """ The gui form that will be used as input for Item values \r\n
        Note: Item creation effects tab order \r\n
        :param _gui: the tkinter object itself
        """
        print("create gui")
        # init and store tk gui
        _gui.geometry('450x350')
        _gui.title("NFTs Upload to OpenSea  ")
        self.gui = _gui
        self.main_directory = os.path.join(sys.path[0])
        self.is_polygon = BooleanVar(value=False)

        # gui input fields
        self.i_fields = {"OpenSea Collection Link:": self.IField(self.gui, "OpenSea Collection Link:", 2, 0),
                         "Start Number:": self.IField(self.gui, "Start Number:", 3, 0),
                         "End Number:": self.IField(self.gui, "End Number:", 4, 0),
                         "Price:": self.IField(self.gui, "Price:", 5, 0),
                         "Title:": self.IField(self.gui, "Title:", 6, 0),
                         "Description:": self.IField(self.gui, "Description:", 7, 0),
                         "NFT Image Format:": self.IField(self.gui, "NFT Image Format:", 8, 0),
                         "External link:": self.IField(self.gui, "External link:", 9, 0),
                         "folder_field": self.IField(self.gui, "folder_field", 21, 0, 80)}

        # check box
        polygon_check_box = tkinter.Checkbutton(_gui, text='Polygon Blockchain', variable=self.is_polygon)
        polygon_check_box.grid(row=20, column=0, sticky='w')
        self.check_box = polygon_check_box

        # gui buttons
        upload_folder_input_button = tkinter.Button(_gui, width=20, text="NFTs Source Folder:",
                                                    command=self.source_folder_location)
        upload_folder_input_button.grid(row=21, column=0, sticky='w')
        self.select_source_folder_button = upload_folder_input_button
        self.select_source_folder_button.lift()
        # move the tab_order of folder_field to be directly after the upload_folder button
        self.get_ifield("folder_field").tkraise(aboveThis=upload_folder_input_button)

        open_browser = tkinter.Button(_gui, width=20, text="Open Chrome Browser", command=self.open_chrome_profile)
        open_browser.grid(row=22, column=1, sticky='w')
        self.open_browser_button = open_browser

        button_start = tkinter.Button(_gui, width=20, bg="green", fg="white", text="Start",
                                      command=start_web_driver_submissions)
        button_start.grid(row=25, column=1, sticky='w')
        self.start_button = button_start

        _gui.mainloop()  # Start Tk

    def source_folder_location(self):
        """ Ask User for directory on clicking button, changes button name. \r\n
        :return: None
        """
        # folder_field = IField("", 21, 0, TkForm.gui, 80)
        # image_folder = folder_field.input_field.get()
        folder_field = self.get_ifield_value("folder_field")
        image_folder = filedialog.askdirectory(initialdir=folder_field) \
            if os.path.isdir(folder_field) \
            else filedialog.askdirectory()
        if image_folder:
            self.i_fields.get("folder_field").insert_text(image_folder)

    def open_chrome_profile(self):
        """ Create a new Chrome subprocess\r\n
        :return: None
        """
        subprocess.Popen(["start", "chrome", "--remote-debugging-port=8989",
                          "--user-data-dir=" + self.main_directory + "/chrome_profile", ],
                         shell=True, )

    def get_ifield(self, key):
        return self.i_fields.get(key).input_field

    def get_ifield_value(self, key):
        return self.get_ifield(key).get()

    def init_item_for_form(self):
        Item._current_num = int(self.get_ifield_value("Start Number:"))
        Item._title_format = self.get_ifield_value("Title:")
        Item._folder_path = self.get_ifield_value("folder_field")
        Item._image_format = self.get_ifield_value("NFT Image Format:")

        Item.collection_link = self.get_ifield_value("OpenSea Collection Link:")
        Item.external_web_link = str(self.get_ifield_value("External link:"))
        Item.price = float(self.get_ifield_value("Price:"))
        Item.description = self.get_ifield_value("Description:")
        return Item

    class IField:
        def __init__(self, gui, label, row_ind, column_ind, grid_padx=0):
            """ IField Helper object the process of creating InputFields\r\n
            :param gui: tk parent object
            :param label: (string) value to display as name
            :param row_ind: (int) row position
            :param column_ind: (int) column position
            :param grid_padx: (int) optional to set grid width
            """
            self.input_field = Entry(gui, justify=LEFT)
            self.input_field.label = Label(gui, text=label)
            self.input_field.label.grid(row=row_ind, column=column_ind)
            self.input_field.grid(row=row_ind, column=column_ind + 1, sticky='w')
            if grid_padx:
                print(grid_padx)
                self.input_field.grid(ipadx=grid_padx)

        def insert_text(self, text):
            self.input_field.delete(0, "end")
            self.input_field.insert(0, text)


def start_web_driver_submissions():
    """Start The Application """
    # TODO check if the webdriver has been started ...
    print("Start Application ... ")
    _Item = TkForm.init_item_for_form()
    web_driver = init_chrome_options(TkForm.main_directory)
    wait = WebDriverWait(web_driver, 15)
    end_num = int(TkForm.i_fields.get("End Number:").input_field.get())
    print(f"Start creating NFTs in Collection: [{_Item.collection_link:s}]")
    while _Item.get_current_item_nu() <= end_num:
        print(f"Starting Item: [{_Item.get_current_item_title():s}]")
        web_driver.get(_Item.collection_link)
        _enter_all_data_for_item(_Item, web_driver, wait)
        _submit_cost_for_item_in_currency(_Item, web_driver, wait)
        _Item.increment_current_item()
        print('NFT creation completed!')
        _reset_webdriver_to_submit_next(web_driver, wait)

    print("Done with all Items")


def _enter_all_data_for_item(item, web_driver, wait):
    print("Wait for add item element button to load")
    wait_xpath(wait, '//*[@id="__next"]/div[1]/main/div/div/div[1]/span/a')
    add_item_link = web_driver.find_element_by_xpath('//*[@id="__next"]/div[1]/main/div/div/div[1]/span/a')
    print("Click add new Item")
    add_item_link.click()
    time.sleep(1)

    print("Wait for item data fields")
    wait_xpath(wait, '//*[@id="media"]')
    _enter_data_slice_for_element(item, web_driver, '//*[@id="media"]', 0.5)
    _enter_data_slice_for_element(item, web_driver, '//*[@id="name"]', 0.5)
    _enter_data_slice_for_element(item, web_driver, '//*[@id="external_link"]', 0.5)
    _enter_data_slice_for_element(item, web_driver, '//*[@id="description"]', 0.5)


def _enter_data_slice_for_element(item, web_driver, xpath, wait_time):
    print(f"Enter data for xpath: [{xpath:s}]")
    link = web_driver.find_element_by_xpath(xpath)
    link.send_keys(item.get_current_item_absolute_path())
    time.sleep(wait_time)

    return link


def _submit_cost_for_item_in_currency(item, web_driver, wait):
    # Select Polygon blockchain if applicable
    if TkForm.gui.is_polygon.get():
        blockchain_button = \
            web_driver.find_element(By.XPATH,
                                    '//*[@id="__next"]/div[1]/main/div/div/section/div/form/div[7]/div/div[2]')
        blockchain_button.click()
        polygon_button_location = '//span[normalize-space() = "Mumbai"]'
        wait_xpath(wait, polygon_button_location)
        polygon_button = web_driver.find_element(By.XPATH, polygon_button_location)
        polygon_button.click()
    print("currency selected")

    create = web_driver.find_element_by_xpath(
        '//*[@id="__next"]/div[1]/main/div/div/section/div[2]/form/div/div[1]/span/button')
    web_driver.execute_script("arguments[0].click();", create)
    print("unsure ... execute some script ... picking a button")
    time.sleep(1)

    wait_css_selector(wait, "i[aria-label='Close']")
    close = web_driver.find_element_by_css_selector("i[aria-label='Close']")
    print("click close")
    close.click()
    time.sleep(1)

    wait_xpath(wait, '//*[@id="__next"]/div[1]/main/div/div/div[1]/div/span[2]/a')
    sell = web_driver.find_element_by_xpath('//*[@id="__next"]/div[1]/main/div/div/div[1]/div/span[2]/a')
    print("click sell")
    sell.click()

    wait_css_selector(wait, "input[placeholder='Amount']")
    amount = web_driver.find_element_by_css_selector("input[placeholder='Amount']")
    print("enter value")
    amount.send_keys(item.price)

    wait_css_selector(wait, "button[type='submit']")
    listing = web_driver.find_element_by_css_selector("button[type='submit']")
    print("click submit")
    listing.click()


def _reset_webdriver_to_submit_next(web_driver, wait):
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

    print("change the control to sign-in page")
    web_driver.switch_to.window(login_page)
    wait_css_selector(wait, "button[data-testid='request-signature__sign']")
    sign = web_driver.find_element_by_css_selector("button[data-testid='request-signature__sign']")
    sign.click()
    time.sleep(1)

    print("change control to main page")
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


if __name__ == '__main__':
    TkForm = MyForm(Tk())  # Create Form
