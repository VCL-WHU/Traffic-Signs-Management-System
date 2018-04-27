from modules import datapool
from modules import info_path

global_manager = datapool.DatapoolDelegate(info_path.datapool_info_dir)

if __name__ == '__main__':
    # global_manager.create_repo_with_signs(r"E:\sample_repo")
    print('get')
