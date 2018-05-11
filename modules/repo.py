import os
import atexit
from modules import user_exceptions
from modules import info_path
from modules import tools
from modules.catalog import CatalogDelegate


class RepoDelegate:
    def __init__(self, repo_path):
        self._repo_path = repo_path
        self._repo_info_path = RepoDelegate.get_repo_info_path(self._repo_path)

        self._name = None
        self._volume = None
        self._description = None
        self._datetime = None
        self._subdirs = None

        self._catalogs = None

        self._modified = False

        self._prepare()

        atexit.register(self._exit)
    

    def _exit(self):
        if not self._modified:
            return
        
        content = {}
        content['name'] = self._name
        content['volume'] = self._volume
        content['description'] = self._description
        content['datetime'] = self._datetime
        content['subdirs'] = self._subdirs

        tools.set_json_content(self._repo_info_path, content)


    # 传入的路径应存在
    @staticmethod
    def create_empty_repo(path, name, description):
        repo_info_file = RepoDelegate.get_repo_info_path(path)
        content = {"name": name, "volume": 0, "description": description, "datetime": tools.get_time(), "subdirs": []}
        tools.set_json_content(repo_info_file, content)

        return RepoDelegate(path)


    @staticmethod
    def get_repo_info_path(repo_path):
        return os.path.join(repo_path, info_path.repo_info_file_name)


    def name(self):
        return self._name
    

    def add_signs_to_catalog(self, catalog_name, signs_path, volume, provider, description):
        self._volume += volume
        self._catalogs[catalog_name].add_signs(signs_path, volume, provider, description)

        self._modified = True


    def get_path(self):
        return self._repo_path


    def get_signs_list(self, catalog_name):
        return self._catalogs[catalog_name].get_signs_list()
    

    def get_catalog_path(self, catalog_name):
        return self._catalogs[catalog_name].get_path()
    

    def get_catalog_names(self):
        return list(self._catalogs.keys())
    

    def has_catalog(self, catalog_name):
        return catalog_name in self._catalogs
    

    def get_catalog(self, catalog_name):
        return self._catalogs[catalog_name]

    
    def create_empty_catalog(self, name, description):
        if self.has_catalog(name):
            raise user_exceptions.CatalogError('create catalog already existed.')
        
        catalog_dir = os.path.join(self._repo_path, name)
        os.mkdir(catalog_dir)
        self._subdirs.append(name)

        self._catalogs[name] = CatalogDelegate.create_empty_catalog(catalog_dir, name, description)
        
        self._modified = True
    

    def _prepare(self):
        repo_info = tools.get_json_content(self._repo_info_path)

        self._name = repo_info['name']
        self._volume = repo_info['volume']
        self._description = repo_info['description']
        self._datetime = repo_info['datetime']
        self._subdirs = repo_info['subdirs']

        catalogs_paths = [os.path.join(self._repo_path, subdir) for subdir in self._subdirs]
        self._catalogs = self._init_catalogs(catalogs_paths)
    

    def _init_catalogs(self, catalogs_paths):
        catalogs = {}
        for catalog_path in catalogs_paths:
            catalog = CatalogDelegate(catalog_path)

            catalogs[catalog.name()] = catalog
        
        return catalogs
