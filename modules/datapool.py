import os
import atexit
import uuid
from modules import info_path
from modules import tools 


class DatapoolDelegate:
    def __init__(self, datapool_path):
        self._datapool_path = datapool_path
        self._datapool_info_path = DatapoolDelegate.get_datapool_info_path(self._datapool_path)

        self._repos_paths = None

        self._repos = None

        self._prepare()

        atexit.register(self._exit)


    @staticmethod
    def get_datapool_info_path(datapool_path):
        return os.path.join(datapool_path, info_path.datapool_info_file_name)    
        

    def _exit(self):
        tools.set_json_content(self._datapool_info_path, {"repos_paths": self._repos_paths})


    def has_repo(self, repo_name):
        return repo_name in self._repos

    
    def get_repo_names(self):
        return list(self._repos.keys())
    

    def get_catalog_names(self, repo_name):
        return self._repos[repo_name].get_catalog_names()
    
    
    def create_empty_repo(self, repo_path, repo_name, repo_description):
        if self.has_repo(repo_name):
            pass
        
        if not os.path.exists(repo_path):
            os.mkdir(repo_path)
        else:
            if os.listdir(repo_path):
                pass
        
        self._repos_paths.append(repo_path)
        self._repos[repo_name] = RepoDelegate.create_empty_repo(repo_path, repo_name, repo_description)


    def create_empty_catalog(self, repo_name, catalog_name, description):
        self._repos[repo_name].create_empty_catalog(catalog_name, description)
    

    def add_signs_to_catalog(self, repo_name, catalog_name, signs_path, volume, provider, description):
        self._repos[repo_name].add_signs_to_catalog(catalog_name, signs_path, volume, provider, description)
    

    def create_repo_with_signs(self, src_dir, *, repo_name=None):
        path, dir_name = os.path.split(src_dir)
        temp_dir_name = uuid.uuid5(uuid.NAMESPACE_DNS, dir_name).hex
        temp_dir = os.path.join(path, temp_dir_name)

        os.renames(src_dir, temp_dir)

        final_repo_name = repo_name
        if not repo_name:
            final_repo_name = dir_name
        
        self.create_empty_repo(src_dir, final_repo_name, 'create on existing repo')

        catalog_dirs = tools.get_dirs(temp_dir)
        for catalog_dir in catalog_dirs:
            self.create_empty_catalog(final_repo_name, catalog_dir, 'create on existing repo')

            src_catalog_path = os.path.join(temp_dir, catalog_dir)

            files = tools.get_files(src_catalog_path)
            signs = [a_file for a_file in files if a_file.endswith('.jpg')]
            self.add_signs_to_catalog(final_repo_name, catalog_dir, src_catalog_path, len(signs), 'unknown', 'create on existing repo')
        
        return temp_dir


    def _prepare(self):
        datapool_info = tools.get_json_content(self._datapool_info_path)

        self._repos_paths = datapool_info['repos_paths']

        self._repos = self._init_repos(self._repos_paths)


    def _init_repos(self, repo_paths):
        repos = {}
        for repo_path in repo_paths:
            repo = RepoDelegate(repo_path)
            repos[repo.name()] = repo
        
        return repos


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

        self._prepare()

        atexit.register(self._exit)
    

    def _exit(self):
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
    

    def add_signs_to_catalog(self, catalog_name, signs_path, volume, provider, description):
        self._volume += volume
        self._catalogs[catalog_name].add_signs(signs_path, volume, provider, description)


    def name(self):
        return self._name
    

    def get_catalog_names(self):
        return list(self._catalogs.keys())
    

    def has_catalog(self, catalog_name):
        return catalog_name in self._catalogs

    
    def create_empty_catalog(self, name, description):
        if self.has_catalog(name):
            pass
        
        catalog_dir = os.path.join(self._repo_path, name)
        os.mkdir(catalog_dir)
        self._subdirs.append(name)

        self._catalogs[name] = CatalogDelegate.create_empty_catalog(catalog_dir, name, description)
    

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


class CatalogDelegate:
    def __init__(self, catalog_path):
        self._catalog_path = catalog_path
        self._catalog_info_path = CatalogDelegate.get_catalog_info_path(self._catalog_path)

        self._name = None
        self._volume = None
        self._maxid = None
        self._description = None
        self._datetime = None

        self._prepare()

        atexit.register(self._exit)


    def _exit(self):
        content = {}
        content['name'] = self._name
        content['volume'] = self._volume
        content['maxid'] = self._maxid
        content['description'] = self._description
        content['datetime'] = self._datetime

        tools.set_json_content(self._catalog_info_path, content)


    @staticmethod
    def create_empty_catalog(path, name, description):
        catalog_info_file = CatalogDelegate.get_catalog_info_path(path)
        catalog_content = {"name": name, "volume": 0, "maxid": 0, "description": description, "datetime": tools.get_time(), "subdirs": []}
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


    def _prepare(self):
        catalog_info = tools.get_json_content(self._catalog_info_path)

        self._name = catalog_info['name']
        self._volume = catalog_info['volume']
        self._maxid = catalog_info['maxid']
        self._description = catalog_info['description']
        self._datetime = catalog_info['datetime']
