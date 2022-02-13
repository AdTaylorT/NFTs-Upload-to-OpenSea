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
gui = Tk()
gui.geometry('450x350')
gui.title("NFTs Upload to OpenSea  ")
main_directory = os.path.join(sys.path[0])
is_polygon = BooleanVar(value=False)
path_to_nfts = ""


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


"""
Initialize InputFields in gui
the inputs from the form according to their input fields
"""
collection_link_input = IField("OpenSea Collection Link:", 2, 0, gui)
start_num_input = IField("Start Number:", 3, 0, gui)
end_num_input = IField("End Number:", 4, 0, gui)
price = IField("Price:", 5, 0, gui)
title = IField("Title:", 6, 0, gui)
description = IField("Description:", 7, 0, gui)
file_format = IField("NFT Image Format:", 8, 0, gui)
external_link = IField("External link:", 9, 0, gui)
folder_location = IField("", 21, 0, gui, 80)
wait = WebDriverWait()


def main():
    """Start The Application """
    print("Start Application ... ")
    project_path = main_directory
    file_path = folder_location.input_field.get()
    collection_link = collection_link_input.input_field.get()
    start_num = int(start_num_input.input_field.get())
    current_item_num = start_num
    end_num = int(end_num_input.input_field.get())

    item_price = float(price.input_field.get())
    item_title = title.input_field.get() + str(start_num)
    item_image_format = file_format.input_field.get()
    item_ext_link = str(external_link.input_field.get())
    item_description = description.input_field.get()

    web_driver = init_chrome_options(project_path)
    global wait
    wait = WebDriverWait(web_driver, 15)

    while current_item_num <= end_num:
        print("Start creating NFT " + item_title)

        web_driver.get(collection_link)
        wait_xpath('//*[@id="__next"]/div[1]/main/div/div/div[1]/span/a')
        add_item_link = web_driver.find_element_by_xpath('//*[@id="__next"]/div[1]/main/div/div/div[1]/span/a')
        add_item_link.click()
        time.sleep(1)

        wait_xpath('//*[@id="media"]')
        image_upload_link = web_driver.find_element_by_xpath('//*[@id="media"]')
        file_path = os.path.join(file_path, '.'.join([str(current_item_num), item_image_format]))
        image_path = os.path.abspath(file_path)
        image_upload_link.send_keys(image_path)

        name = web_driver.find_element_by_xpath('//*[@id="name"]')
        name.send_keys(item_title)  # +1000 for other folders #change name before "#"
        time.sleep(0.5)

        ext_link = web_driver.find_element_by_xpath('//*[@id="external_link"]')
        ext_link.send_keys(item_ext_link)
        time.sleep(0.5)

        desc = web_driver.find_element_by_xpath('//*[@id="description"]')
        desc.send_keys(item_description)
        time.sleep(0.5)

        # Select Polygon blockchain if applicable
        if is_polygon.get():
            blockchain_button = \
                web_driver.find_element(By.XPATH,
                                        '//*[@id="__next"]/div[1]/main/div/div/section/div/form/div[7]/div/div[2]')
            blockchain_button.click()
            polygon_button_location = '//span[normalize-space() = "Mumbai"]'
            wait.until(expect_cond.presence_of_element_located((By.XPATH, polygon_button_location)))
            polygon_button = web_driver.find_element(By.XPATH, polygon_button_location)
            polygon_button.click()

        create = web_driver.find_element_by_xpath(
            '//*[@id="__next"]/div[1]/main/div/div/section/div[2]/form/div/div[1]/span/button')
        web_driver.execute_script("arguments[0].click();", create)
        time.sleep(1)

        wait_css_selector("i[aria-label='Close']")
        cross = web_driver.find_element_by_css_selector("i[aria-label='Close']")
        cross.click()
        time.sleep(1)

        main_page = web_driver.current_window_handle
        wait_xpath('//*[@id="__next"]/div[1]/main/div/div/div[1]/div/span[2]/a')
        sell = web_driver.find_element_by_xpath('//*[@id="__next"]/div[1]/main/div/div/div[1]/div/span[2]/a')
        sell.click()

        wait_css_selector("input[placeholder='Amount']")
        amount = web_driver.find_element_by_css_selector("input[placeholder='Amount']")
        amount.send_keys(str(item_price))

        wait_css_selector("button[type='submit']")
        listing = web_driver.find_element_by_css_selector("button[type='submit']")
        listing.click()
        # wait until the window is available.
        while len(web_driver.window_handles) != 2:
            print('.', end='')
            time.sleep(.5)

        login_page = web_driver.window_handles[1]

        for handle in web_driver.window_handles:
            if handle != main_page:
                login_page = handle
        # change the control to signin page
        web_driver.switch_to.window(login_page)
        wait_css_selector("button[data-testid='request-signature__sign']")
        sign = web_driver.find_element_by_css_selector("button[data-testid='request-signature__sign']")
        sign.click()
        time.sleep(1)

        # change control to main page
        web_driver.switch_to.window(main_page)
        time.sleep(1)

        start_num = start_num + 1
        print('NFT creation completed!')


def init_chrome_options(in_project_path):
    """Helper Function to initialize chrome options """
    opt = Options()
    opt.add_experimental_option("debuggerAddress", "localhost:8989")
    w_driver = webdriver.Chrome(
        executable_path=in_project_path + "/chromedriver.exe",
        options=opt,
    )
    return w_driver


def wait_css_selector(css):
    """Helper Function wait for css """
    try:
        wait.until(expect_cond.presence_of_element_located((By.CSS_SELECTOR, css)))
    except TimeoutException:
        print(f"Timed out waiting for element: [{css:s}]")


def wait_xpath(xpath):
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
    global path_to_nfts
    path_to_nfts = filedialog.askdirectory()
    if path_to_nfts:
        folder_location.insert_text(path_to_nfts)


# gui buttons
button_start = tkinter.Button(gui, width=20, bg="green", fg="white", text="Start", command=main)
button_start.grid(row=25, column=1, sticky='w')
polygon_check_box = tkinter.Checkbutton(gui, text='Polygon Blockchain', variable=is_polygon)
polygon_check_box.grid(row=20, column=0, sticky='w')
open_browser = tkinter.Button(gui, width=20, text="Open Chrome Browser", command=open_chrome_profile)
open_browser.grid(row=22, column=1, sticky='w')
upload_folder_input_button = tkinter.Button(gui, width=20, text="NFTs Source Folder:", command=source_folder_location)
upload_folder_input_button.grid(row=21, column=0, sticky='w')

if __name__ == '__main__':
    # Start Tk
    gui.mainloop()
