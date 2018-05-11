import os
import atexit
import uuid
from modules import user_exceptions
from modules import info_path
from modules import tools
from modules.repo import RepoDelegate


class DatapoolDelegate:
    def __init__(self, datapool_path):
        self._datapool_path = datapool_path
        self._datapool_info_path = DatapoolDelegate.get_datapool_info_path(self._datapool_path)

        self._repos_paths = None

        self._repos = None

        self._modified = False

        self._prepare()

        atexit.register(self._exit)


    @staticmethod
    def get_datapool_info_path(datapool_path):
        return os.path.join(datapool_path, info_path.datapool_info_file_name)    
        

    def _exit(self):
        if not self._modified:
            return
        
        tools.set_json_content(self._datapool_info_path, {"repos_paths": self._repos_paths})


    def has_repo(self, repo_name):
        return repo_name in self._repos

    
    def get_repo_names(self):
        return list(self._repos.keys())
    

    def get_catalog_names(self, repo_name):
        return self._repos[repo_name].get_catalog_names()
    

    def has_catalog(self, repo_name, catalog_name):
        return self._repos[repo_name].has_catalog(catalog_name)
    

    def get_repo(self, repo_name):
        return self._repos[repo_name]
    

    def get_catalog(self, repo_name, catalog_name):
        return self.get_repo(repo_name).get_catalog(catalog_name)
    

    def create_empty_repo(self, repo_path, repo_name, repo_description):
        if self.has_repo(repo_name):
            raise user_exceptions.RepoError('create repo already existed.')
        
        if not os.path.exists(repo_path):
            os.mkdir(repo_path)
        else:
            if os.listdir(repo_path):
                raise user_exceptions.RepoError('can not create empty repo in directory with files.')
        
        self._repos_paths.append(repo_path)
        self._repos[repo_name] = RepoDelegate.create_empty_repo(repo_path, repo_name, repo_description)

        self._modified = True


    def create_empty_catalog(self, repo_name, catalog_name, description):
        self._repos[repo_name].create_empty_catalog(catalog_name, description)
    

    def add_signs_to_catalog(self, repo_name, catalog_name, signs_path, volume, provider, description):
        self._repos[repo_name].add_signs_to_catalog(catalog_name, signs_path, volume, provider, description)


    def get_pictures_path(self, repo_name, catalog_name):
        repo = self._repos[repo_name]
        catalog = repo._catalogs[catalog_name]

        return catalog.get_signs_list()


    def create_repo_with_signs(self, src_dir, *, repo_name=None):
        path, dir_name = os.path.split(src_dir)
        temp_dir_name = uuid.uuid5(uuid.NAMESPACE_DNS, dir_name).hex
        temp_dir = os.path.join(path, temp_dir_name)

        os.renames(src_dir, temp_dir)

        final_repo_name = repo_name
        if not repo_name:
            final_repo_name = dir_name
        
        self.create_empty_repo(src_dir, final_repo_name, 'create automatically.')

        catalog_dirs = tools.get_dirs(temp_dir)
        for catalog_dir in catalog_dirs:
            self.create_empty_catalog(final_repo_name, catalog_dir, 'create automatically.')

            src_catalog_path = os.path.join(temp_dir, catalog_dir)

            files = tools.get_files(src_catalog_path)
            signs = [a_file for a_file in files if a_file.endswith('.jpg')]
            self.add_signs_to_catalog(final_repo_name, catalog_dir, src_catalog_path, len(signs), 'unknown', 'create automatically.')
        
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
