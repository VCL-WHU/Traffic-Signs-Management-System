import os
import uuid
from modules import tools
from modules import datapool
from modules import info_path
from modules import datapool


class SystemManager:
    def __init__(self):
        self._datapool = datapool.DatapoolDelegate(info_path.datapool_info_dir)

    def get_repo_names(self):
        return self._datapool.get_repo_names()
    

    def get_repo(self, repo_name):
        return self._datapool.get_repo(repo_name)
    

    def get_catalog(self, repo_name, catalog_name):
        return self._datapool.get_catalog(repo_name, catalog_name)

    
    def has_repo(self, repo_name):
        return self._datapool.has_repo(repo_name)
    

    def get_catalog_names(self, repo_name):
        return self._datapool.get_catalog_names(repo_name)
    

    def has_catalog(self, repo_name, catalog_name):
        return self._datapool.has_catalog(repo_name, catalog_name)
    

    def get_pictures_path(self, repo_name, catalog_name):
        return self._datapool.get_pictures_path(repo_name, catalog_name)


    def add_signs_to_catalog(self, repo_name, catalog_name, signs_path, volume, provider, description, *, auto_count=False):
        if auto_count:
            volume = self._count_pictures(signs_path)

        self._datapool.add_signs_to_catalog(repo_name, catalog_name, signs_path, volume, provider, description)
    

    def create_empty_repo(self, repo_path, repo_name, repo_description):
        self._datapool.create_empty_repo(repo_path, repo_name, repo_description)


    def create_empty_catalog(self, repo_name, catalog_name, description):
        self._datapool.create_empty_catalog(repo_name, catalog_name, description)
    
    
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

            self.add_signs_to_catalog(final_repo_name, catalog_dir, src_catalog_path, self._count_pictures(src_catalog_path), 'unknown', 'create automatically.')
        
        return temp_dir


    def batch_add_signs(self, repo_name, src_dir, *, args=None):
        src_catalog_dirs = tools.get_dirs(src_dir)

        unadded_dirs = []
        for src_catalog_dir in src_catalog_dirs:
            dest_catalog_name = src_catalog_dir

            if not args is None:
                dest_catalog_name = args[src_catalog_dir]
            
            if self.has_catalog(repo_name, src_catalog_dir):
                src_catalog_path = os.path.join(src_dir, src_catalog_dir)
                self.add_signs_to_catalog(repo_name, dest_catalog_name, src_catalog_path, 0, 'unknown', 'add automatically.', auto_count=True)
            else:
                unadded_dirs.append(src_catalog_dir)
        
        return unadded_dirs
    

    def _count_pictures(self, src_dir):
        files = tools.get_files(src_dir)

        return len([a_file for a_file in files if os.path.splitext(a_file)[1] in ('.jpg', )])


global_manager = SystemManager()


if __name__ == '__main__':
    global_manager.create_repo_with_signs(r"E:\sample_repo")
    # print(global_manager.get_repo_names())
    # print(global_manager.get_catalog_names('sample_repo'))
    # print(global_manager.get_pictures_path('sample_repo', '19 禁止超车'))
    # global_manager.add_signs_to_catalog('sample_repo', '31 限制高度', r"E:\1", 0, 'csj', 'test', auto_count=True)
    global_manager.batch_add_signs('sample_repo', r"E:\abc")