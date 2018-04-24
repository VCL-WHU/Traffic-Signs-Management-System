import json
import os
from modules import info_path
from modules import tools
import uuid


class SystemHelper:
    def __init__(self):
        self._datapool_info = dict()
        self._repos_info = dict()

        self._prepare()
        pass


    '''
    检验是否存在某个库
    '''
    def has_repo(self, repo_name):
        return repo_name in self._get_repo_props()


    '''
    返回所有的库名称
    '''
    def get_repo_names(self):
        return list(self._get_repo_props().keys())


    '''
    创建一个新的库
    '''
    def create_empty_repo(self, repo_name, repo_path, repo_description):
        if self.has_repo(repo_name):
            pass

        if not os.path.exists(repo_path):
            os.mkdir(repo_path)
        else:
            if os.listdir(repo_path):
                pass
        
        # 添加信息到 datapool
        get_id = self._inc_datapool_info_maxid()
        content = {'name': repo_name, 'id': get_id, 'volume': 0, 'description': repo_description, 'datetime': tools.get_time(), 'path': repo_path}

        self._get_repo_props()[repo_name] = content

        # 添加 repo_info 的初始 repo_info.json 信息
        repo_info_path = os.path.join(repo_path, info_path.repo_info_file_name)
        tools.set_json_content(repo_info_path, {'maxid': 0, 'catalog_props': []})

        # 将 repo_info.json 的信息读入到 self._repos_info
        self._init_repo_info(repo_name)


    '''
    在当前以整理的一个库的基础上创建库，默认以文件夹名作为各个分类名
    返回创建的临时文件夹的路径，包括源目录中没有用到的文件，可能不存在该文件夹
    '''
    def create_repo_with_signs(self, source_dir, *, repo_name=None):
        path, dir_name = os.path.split(source_dir)
        temp_dir_name = uuid.uuid5(uuid.NAMESPACE_DNS, dir_name).hex
        temp_dir = os.path.join(path, temp_dir_name)

        os.renames(source_dir, temp_dir)
        
        final_repo_name = repo_name
        if not repo_name:
            final_repo_name = dir_name
        
        self.create_empty_repo(final_repo_name, source_dir, 'create on existing repo')
        
        catalog_dirs = tools.get_dirs(temp_dir)
        for catalog_dir in catalog_dirs:
            self.create_catalog(final_repo_name, catalog_dir, 'create on existing repo')
            
            source_catalog_path = os.path.join(temp_dir, catalog_dir)

            files = tools.get_files(source_catalog_path)
            signs = [a_file for a_file in files if a_file.endswith('.jpg')]
            self.move_signs_to(source_catalog_path, final_repo_name, catalog_dir, len(signs), 'create on existing repo, unknown provider')

        return temp_dir


    '''
    检查是否有某个类别
    '''
    def has_catalog(self, repo_name, catalog_name):
        return catalog_name in self._get_catalog_props(repo_name)


    '''
    获取库中所有类别名的列表
    '''
    def get_catalog_names(self, repo_name):
        return list(self._get_catalog_props(repo_name).keys())


    '''
    创建一个新的类别
    '''
    def create_catalog(self, repo_name, catalog_name, catalog_description):
        if self.has_catalog(repo_name, catalog_name):
            pass
        
        repo_path = self._get_repo_path(repo_name)
        uncreated_catalog_path = os.path.join(repo_path, catalog_name)

        if not os.path.exists(uncreated_catalog_path):
            os.mkdir(uncreated_catalog_path)
        else:
            if os.listdir(uncreated_catalog_path):
                pass

        # 添加信息到 repo_info
        get_id = self._inc_repo_info_maxid(repo_name)
        content = {'name': catalog_name, 'id': get_id, 'volume': 0, 'subdir': catalog_name, 'description': catalog_description, 'datetime': tools.get_time()}

        self._get_catalog_props(repo_name)[catalog_name] = content
        
        # 添加 catalog_info 的初始 catalog_info.json 信息
        catalog_info_path = os.path.join(uncreated_catalog_path, info_path.catalog_info_file_name)
        tools.set_json_content(catalog_info_path, {'maxid': 0, 'signlist_props': []})


    '''
    将源目录中的图片录入库中
    '''
    def move_signs_to(self, origin_dir, repo_name, catalog_name, volume, provider):
        catalog_path = self._get_catalog_path(repo_name, catalog_name)

        catalog_info = self._get_catalog_info(repo_name, catalog_name)

        catalog_info['maxid'] += 1
        sign_item_id = catalog_info['maxid']

        sign_item_path = os.path.join(catalog_path, str(sign_item_id))

        os.renames(origin_dir, sign_item_path)

        catalog_info['signlist_props'].append({'id': sign_item_id, 'volume': volume, 'datetime': tools.get_time(), 'provider': provider})

        tools.set_json_content(self._get_catalog_info_path(repo_name, catalog_name), catalog_info)

        self._get_catalog_prop(repo_name, catalog_name)['volume'] += volume
        self._get_repo_prop(repo_name)['volume'] += volume


    '''
    获取某类别图片的路径，返回图片分类路径以及由 文件夹名，图片数 构成的列表
    '''
    def get_content_of_catalog(self, repo_name, catalog_name):
        path = self._get_catalog_path(repo_name, catalog_name)
        catalog_info = self._get_catalog_info(repo_name, catalog_name)
        signlist_path = [(str(props['id']), props['volume']) for props in catalog_info['signlist_props']]
        return path, signlist_path


    '''
    若修改了库的内容，需要调用该函数把修改写入
    '''
    def write_back(self):
        temp_repo_props = list(self._get_repo_props().values())
        tools.set_json_content(info_path.datapool_info_path, {'maxid': self._get_datapool_info_maxid(), 'repo_props': temp_repo_props})

        for repo_name in self.get_repo_names():
            repo_dir = self._get_repo_path(repo_name)
            repo_info_path = os.path.join(repo_dir, info_path.repo_info_file_name)

            temp_catalog_props = list(self._get_catalog_props(repo_name).values())
            tools.set_json_content(repo_info_path, {'maxid': self._get_repo_info_maxid(repo_name), 'catalog_props': temp_catalog_props})


    def _prepare(self):
        self._init_datapool_info()
        for repo_name in self._datapool_info['repo_props']:
            self._init_repo_info(repo_name)


    def _init_datapool_info(self):
        raw_datapool_info = tools.get_json_content(info_path.datapool_info_path)

        datapool_info = dict()
        datapool_info['maxid'] = raw_datapool_info['maxid']
        datapool_info['repo_props'] = {repo_prop['name']: repo_prop for repo_prop in raw_datapool_info['repo_props']}
        
        self._datapool_info = datapool_info


    def _get_datapool_info(self):
        return self._datapool_info


    def _get_datapool_info_maxid(self):
        return self._get_datapool_info()['maxid']


    def _inc_datapool_info_maxid(self):
        datapool_info = self._get_datapool_info()
        datapool_info['maxid'] += 1
        return datapool_info['maxid']


    def _get_repo_props(self):
        return self._datapool_info['repo_props']


    def _get_repo_prop(self, repo_name):
        if not self.has_repo(repo_name):
            pass
        
        return self._get_repo_props()[repo_name]


    def _get_repo_path(self, repo_name):
        return self._get_repo_prop(repo_name)['path']


    def _get_repo_id(self, repo_name):
        return self._get_repo_prop(repo_name)['id']


    def _init_repo_info(self, repo_name):
        repo_info_dir = self._get_repo_path(repo_name)
        repo_info_path = os.path.join(repo_info_dir, info_path.repo_info_file_name)

        raw_repo_info = tools.get_json_content(repo_info_path)

        repo_info = dict()
        repo_info['maxid'] = raw_repo_info['maxid']
        repo_info['catalog_props'] = {catalog_prop['name']: catalog_prop for catalog_prop in raw_repo_info['catalog_props']}

        repo_id = self._get_repo_id(repo_name)
        self._repos_info[repo_id] = repo_info


    def _get_repo_info(self, repo_name):
        repo_id = self._get_repo_id(repo_name)

        return self._repos_info[repo_id]
    

    def _get_repo_info_maxid(self, repo_name):
        repo_info = self._get_repo_info(repo_name)
        return repo_info['maxid']


    def _inc_repo_info_maxid(self, repo_name):
        repo_info = self._get_repo_info(repo_name)
        repo_info['maxid'] += 1
        return repo_info['maxid']


    def _get_catalog_props(self, repo_name):
        repo_info = self._get_repo_info(repo_name)
        return repo_info['catalog_props']


    def _get_catalog_prop(self, repo_name, catalog_name):
        catalog_props = self._get_catalog_props(repo_name)
        if not catalog_name in catalog_props:
            pass
        
        return catalog_props[catalog_name]


    def _get_catalog_path(self, repo_name, catalog_name):
        repo_path = self._get_repo_path(repo_name)
        catalog_subdir = self._get_catalog_prop(repo_name, catalog_name)['subdir']
        return os.path.join(repo_path, catalog_subdir)


    def _get_catalog_info(self, repo_name, catalog_name):
        catalog_info_path = self._get_catalog_info_path(repo_name, catalog_name)

        return tools.get_json_content(catalog_info_path)


    def _get_catalog_info_path(self, repo_name, catalog_name):
        catalog_path = self._get_catalog_path(repo_name, catalog_name)
        catalog_info_path = os.path.join(catalog_path, info_path.catalog_info_file_name)

        return catalog_info_path

if __name__ == '__main__':
    helper = SystemHelper()

    helper.create_repo_with_signs(r"E:\tempfiles\sample_repo")
    helper.write_back()
