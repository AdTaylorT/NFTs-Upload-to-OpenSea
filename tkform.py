import os
import subprocess
import sys
import tkinter
from tkinter import *
from tkinter import filedialog

from item import Item


# these could very well be statics, but whatever for now ...
# expectation is only one of these programs will run at once...


class TkForm:
    def __init__(self, start_upload):
        """ The gui form that will be used as input for Item values \r\n
        Note: Item creation effects tab order \r\n
        :param _gui: the tkinter object itself
        """
        print("create gui")
        _gui = Tk()
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
                                                    command=self.update_ifield_text)
        upload_folder_input_button.grid(row=21, column=0, sticky='w')
        self.select_source_folder_button = upload_folder_input_button
        self.select_source_folder_button.lift()
        # move the tab_order of folder_field to be directly after the upload_folder button
        self.get_ifield("folder_field").tkraise(aboveThis=upload_folder_input_button)

        open_browser = tkinter.Button(_gui, width=20, text="Open Chrome Browser", command=self.open_chrome_profile)
        open_browser.grid(row=22, column=1, sticky='w')
        self.open_browser_button = open_browser

        button_start = tkinter.Button(_gui, width=20, bg="green", fg="white", text="Start",
                                      command=start_upload)
        button_start.grid(row=25, column=1, sticky='w')
        self.start_button = button_start

    def update_ifield_text(self):
        """ Ask User for directory on clicking button, changes button name. \r\n
        :return: None
        """
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
        subprocess.Popen(["nohup google-chrome", "--remote-debugging-port=8989",
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
                self.input_field.grid(ipadx=grid_padx)

        def insert_text(self, text):
            self.input_field.delete(0, "end")
            self.input_field.insert(0, text)
