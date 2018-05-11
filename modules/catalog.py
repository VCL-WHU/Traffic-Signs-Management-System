import os
import atexit
from modules import info_path
from modules import tools


class CatalogDelegate:
    def __init__(self, catalog_path):
        self._catalog_path = catalog_path
        self._catalog_info_path = CatalogDelegate.get_catalog_info_path(self._catalog_path)

        self._name = None
        self._volume = None
        self._maxid = None
        self._description = None
        self._datetime = None

        self._modified = False

        self._prepare()

        atexit.register(self._exit)


    def _exit(self):
        if not self._modified:
            return
        
        content = {}
        content['name'] = self._name
        content['volume'] = self._volume
        content['maxid'] = self._maxid
        content['description'] = self._description
        content['datetime'] = self._datetime

        tools.set_json_content(self._catalog_info_path, content)


    # 传入路径应存在
    @staticmethod
    def create_empty_catalog(path, name, description):
        catalog_info_file = CatalogDelegate.get_catalog_info_path(path)
        catalog_content = {"name": name, "volume": 0, "maxid": 0, "description": description, "datetime": tools.get_time()}
        tools.set_json_content(catalog_info_file, catalog_content)

        signs_list_info_file = CatalogDelegate.get_signs_list_info_path(path)
        signs_list_content = {}
        tools.set_json_content(signs_list_info_file, signs_list_content)

        return CatalogDelegate(path)
    

    @staticmethod
    def get_catalog_info_path(catalog_path):
        return os.path.join(catalog_path, info_path.catalog_info_file_name)

    
    @staticmethod
    def get_signs_list_info_path(catalog_path):
        return os.path.join(catalog_path, info_path.signs_list_info_file_name)

    
    def name(self):
        return self._name


    def add_signs(self, signs_path, volume, provider, description):
        self._maxid += 1
        id = self._maxid

        os.renames(signs_path, os.path.join(self._catalog_path, str(id)))

        self._volume += volume

        signs_list_info_file = CatalogDelegate.get_signs_list_info_path(self._catalog_path)
        signs_list_info = tools.get_json_content(signs_list_info_file)
        signs_list_info[id] = {'volume': volume, 'provider': provider, 'description': description, 'datetime': tools.get_time()}
        tools.set_json_content(signs_list_info_file, signs_list_info)

        self._modified = True


    def get_path(self):
        return self._catalog_path
    

    def get_signs_list(self):
        signs_list_info_file = CatalogDelegate.get_signs_list_info_path(self._catalog_path)
        signs_list_info = tools.get_json_content(signs_list_info_file)

        signs_list_info = tools.get_json_content(signs_list_info_file)
        return self.get_path(), list(signs_list_info.keys())

    
    def _prepare(self):
        catalog_info = tools.get_json_content(self._catalog_info_path)

        self._name = catalog_info['name']
        self._volume = catalog_info['volume']
        self._maxid = catalog_info['maxid']
        self._description = catalog_info['description']
        self._datetime = catalog_info['datetime']
