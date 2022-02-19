import os


class Item:
    """ Static object holder for fields """
    # TODO data dump this object as json, then load that item
    #   this will allow the application to resume after crash
    #   would this require an additional button? "Load from crash"
    #   or just auto-magically handle it by presence of json:
    #       the existence of json would mean application was halted in some fashion
    #       either throw manual close of crash ...
    #       -- after each item submission update json data dump with _current_num
    #       -- upon finish delete json state
    #       -- would have to handle loading form from json
    _current_num = 0  # counter
    _title_format = ""
    _file_path = ""
    _folder_path = ""
    _image_format = "png"

    collection_link = ""
    external_web_link = ""
    price = 0.00
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
    def get_price_str():
        return str(Item.price)

    @staticmethod
    def _build_abs_item_path():
        Item._file_path = os.path.join(
            Item._folder_path,
            '.'.join([Item.get_current_item_str(), Item._image_format]))

        return Item._file_path

    @staticmethod
    def _is_current_item_path_valid():
        return os.path.isfile(Item._build_abs_item_path())

    @staticmethod
    def get_current_item_absolute_path():
        if Item._is_current_item_path_valid():
            return Item._file_path
        raise FileNotFoundError

    @staticmethod
    def get_current_item_title():
        return ''.join([Item._title_format, Item.get_current_item_str()])

    @staticmethod
    def validate_int(value):
        if not value:
            return True
        try:
            int(value)
            return True
        except ValueError:
            pass
        return False

    @staticmethod
    def validate_float(value):
        if not value:
            return True
        try:
            float(value)
            return True
        except ValueError:
            pass
        return False

    @staticmethod
    def validate_url(value):
        if not value:
            return True
        if "https" in value:
            return True
        return False

    @staticmethod
    def validate_img(value):
        if not value:
            return True
        # ["JPG", "PNG", "GIF", "SVG", "MP4", "WEBM", "MP3", "WAV", "OGG", "GLB", "GLTF"]
        if str.upper(value) in ["JPG", "PNG", "GIF", "SVG", "MP4", "WEBM", "MP3", "WAV", "OGG", "GLB", "GLTF"]:
            return True
        return False

    @staticmethod
    def validate_folder(value):
        if not value:
            return True
        if os.path.isdir(value):
            return True
        return False



"""
except ValueError as err:
warning_popup(str(err))
pass
return Item"""