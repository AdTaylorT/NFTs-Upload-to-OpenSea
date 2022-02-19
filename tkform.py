import os
import platform
import subprocess
import tkinter
from tkinter import *
from tkinter import filedialog

from item import Item


class TkForm:
    _collection_link = "OpenSea Collection Link:"
    _start_num = "Start Number:"
    _end_num = "End Number:"
    _price = "Price:"
    _title = "Title:"
    _description = "Description:"
    _nft_image_format = "NFT Image Format:"
    _ext_link = "External link:"
    _folder_field = "folder_field"

    popup: Toplevel

    def __init__(self, start_upload):
        """ The gui form that will be used as input for Item values \r\n
        Note: Item creation effects tab order \r\n
        :param start_upload: the start_upload method
        """
        print("create gui")
        _gui = Tk()
        # init and store tk gui
        _gui.geometry('450x350')
        _gui.title("NFTs Upload to OpenSea  ")
        self.gui = _gui
        self.is_polygon = BooleanVar(value=False)

        # gui input fields
        self.i_fields = {
            TkForm._collection_link: self.IField(self, TkForm._collection_link, Item.validate_url, "fo", 2, 0),
            TkForm._start_num: self.IField(self, TkForm._start_num, Item.validate_int, "k", 3, 0),
            TkForm._end_num: self.IField(self, TkForm._end_num, Item.validate_int, "k", 4, 0),
            TkForm._price: self.IField(self, TkForm._price, Item.validate_float, "k", 5, 0),
            TkForm._title: self.IField(self, TkForm._title, None, "", 6, 0),
            TkForm._description: self.IField(self, TkForm._description, None, "", 7, 0),
            TkForm._nft_image_format: self.IField(self, TkForm._nft_image_format, Item.validate_img, "fo", 8, 0),
            TkForm._ext_link: self.IField(self, TkForm._ext_link, None, "", 9, 0),
            TkForm._folder_field: self.IField(self, TkForm._folder_field, "fo", Item.validate_folder, 21, 0, 80)}

        # check box
        polygon_check_box = tkinter.Checkbutton(_gui, text='Polygon Blockchain', variable=self.is_polygon)
        polygon_check_box.grid(row=20, column=0, sticky='w')
        self.check_box = polygon_check_box

        # gui buttons
        upload_folder_input_button = tkinter.Button(_gui, width=20, text='NFTs Source Folder:',
                                                    command=self.update_folder_field_text)
        upload_folder_input_button.grid(row=21, column=0, sticky='w')
        self.select_source_folder_button = upload_folder_input_button
        self.select_source_folder_button.lift()
        # move the tab_order of folder_field to be directly after the upload_folder button
        self.get_ifield(TkForm._folder_field).tkraise(aboveThis=upload_folder_input_button)

        open_browser = tkinter.Button(_gui, width=20, text='Configure Chrome', command=self.open_chrome_profile)
        open_browser.grid(row=22, column=1, sticky='w')
        self.open_browser_button = open_browser

        button_start = tkinter.Button(_gui, width=20, bg="green", fg="white", text='Start', command=start_upload)
        button_start.grid(row=25, column=1, sticky='w')
        self.start_button = button_start

    def update_folder_field_text(self):
        """ Ask User for directory on clicking button, changes button name. \r\n
        :return: None
        """
        folder_field = self.get_ifield_value(TkForm._folder_field)
        image_folder = filedialog.askdirectory(initialdir=folder_field) \
            if os.path.isdir(folder_field) \
            else filedialog.askdirectory()
        if image_folder:
            self.i_fields.get(TkForm._folder_field).insert_text(image_folder)

    @staticmethod
    def open_chrome_profile():
        """ Create a new Chrome subprocess\r\n
        :return: None
        """
        if platform.system() != "Windows":
            exit(1)

        usr_chrome_data = os.path.join(os.getenv('LOCALAPPDATA'), "Google", "Chrome", "User Data")
        print(usr_chrome_data)
        if not os.path.isdir(usr_chrome_data):
            os.mkdir(usr_chrome_data)
        directory_arg = ''.join(["--user-data-dir=", usr_chrome_data])
        print(directory_arg)

        debug_port = "--remote-debugging-port=9223"
        subprocess.Popen(["start", "chrome", debug_port, directory_arg, "https://opensea.io/collections"], shell=True)

    def get_ifield(self, key):
        return self.i_fields.get(key).input_field

    def get_ifield_value(self, key):
        return self.get_ifield(key).get()

    def warning_popup(self, message):
        if hasattr(self, 'popup') and self.popup:
            return
        self.popup = Toplevel()
        self.popup.wm_title("Warning!")

        label = tkinter.Label(self.popup, text=message, padx=50, pady=50, justify=CENTER, font=('Arial', 20))
        label.pack()
        self.popup.focus_set()
        self.popup.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        self.popup.destroy()
        delattr(self, 'popup')

    class IField:
        def __init__(self, parent, label, callback, vdt, row_ind, column_ind, grid_padx=0):
            """ IField Helper object the process of creating InputFields\r\n
            :param parent: tk parent object
            :param label: (string) value to display as name
            :param row_ind: (int) row position
            :param column_ind: (int) column position
            :param grid_padx: (int) optional to set grid width
            """
            if vdt == 'k':
                self.input_field = Entry(parent.gui, validate='key', justify=LEFT)
            elif vdt == 'fo':
                self.input_field = Entry(parent.gui, validate='focusout', justify=LEFT)
            else:
                self.input_field = Entry(parent.gui, justify=LEFT)

            if callback:
                reg = parent.gui.register(callback)
                self.input_field.config(validatecommand=(reg, '%P'))
                reg = parent.gui.register(parent.warning_popup)
                self.input_field.config(invalidcommand=(reg, f"Failed Field: {label}"))

            self.input_field.label = Label(parent.gui, text=label)
            self.input_field.label.grid(row=row_ind, column=column_ind)

            self.input_field.grid(row=row_ind, column=column_ind + 1, sticky='w')
            if grid_padx:
                self.input_field.grid(ipadx=grid_padx)

        def insert_text(self, text):
            self.input_field.delete(0, END)
            self.input_field.insert(0, text)
