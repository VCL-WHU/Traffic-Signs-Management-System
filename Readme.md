# 图片库管理程序

## 1. 功能总结

- [x] 创建图片库以及图片分类（**增**）
- [x] 返回图片路径（**查**）
- [x] 异常机制
- [x] 添加图片以及批量添加图片
- [ ] 重命名功能（**改**）
- [ ] 删除文件功能（**删**）
- [ ] 日志功能
- [ ] GUI

## 2. 概览

**思路**：使用 `json` 文件管理信息

### 2.1 文件结构

#### 2.1.1 项目结构

```
information:
    datapool_info.json -- 记录图片库信息

modules:
    user_exceptions.py -- 异常类定义，已完成
    catalog.py -- 类别层级控制以及描述，已完成
    repo.py -- 仓库层级控制以及描述，已完成
    datapool.py -- 数据池层级控制及描述，已完成
    info_path.py -- 包含 datapool_info.json 路径，仓库信息文件的文件名，类别信息文件的文件名
    tools.py -- 包含几个工具函数

manager.py -- 提供全局控制
```

#### 2.1.2 系统文件结构

```
repo_dir_1:
    repo_info.json

    catalog_dir_1:
        catalog_info.json
        signs_list_info.json

        1
        2
        ...
    catalog_dir_2:
        catalog_info.json
        signs_list_info.json

        1
        2
        ...
    
    ...

...
```

### 2.2 文件示例

`datapool_info.json`

```
{
    "repos_paths": [
        path1,  // 仓库路径 1
        path2,  // 仓库路径 2
        ...
    ]
}
```

`repo_info.json`

```
{
    "name": "sample_repo",   // 仓库名
    "volume": 880,           // 图片总量
    "description": "create automatically.",  // 仓库描述信息
    "datetime": "2018-05-11 21:45:23",       // 仓库创建时间
    "subdirs": [             // 其下分类子文件夹名
        "19 禁止超车",
        "31 限制高度"
    ]
}
```

`catalog_info.json`

```
{
    "name": "31 限制高度",  // 分类名
    "volume": 438,         // 分类下图片数量
    "maxid": 2,            // 当前最大 id，id为创建唯一标识用
    "description": "create automatically.",  // 分类描述信息
    "datetime": "2018-05-11 21:45:26"        // 分类添加时间
}
```

`signs_list_info.json`

```
{
    "1": {  // 分类下系列 1，为其 id，也是其子文件夹名
        "volume": 219,          // 该系列图片数量
        "provider": "unknown",  // 标注者信息
        "description": "create automatically.",  // 系列描述信息
        "datetime": "2018-05-11 21:45:27"        // 系列创建时间
    },
    "2": {
        "volume": 219,
        "provider": "unknown",
        "description": "add automatically.",
        "datetime": "2018-05-11 21:45:34"
    }
}
```

## 3. 代码结构

### 3.1 文件映射到变量

`datapool_info.json` 文件由 `modules.datapool.DatapoolDelegate` 类管理，
`repo_info.json` 文件由 `modules.repo.RepoDelegate` 类管理，
`catalog.json` 和 `signs_list_info.json` 由 `modules.catalog.CatalogDelegate` 类管理

这三个类的初始化都由其路径开始，各层之间不透明，降低了耦合性。

### 3.2 类关系

`SystemManager` 包含 `DatapoolDelegate`，`DatapoolDelegate` 包含若干 `RepoDelegate` 实例，`RepoDelegate` 包含若干 `CatalogDelegate` 实例。

上层类提供底层类的公共 API，并添加本层的 API。

### 3.3 部分 `SystemManager` API 介绍

* `get_repo_names(self)`
    * 功能：
        返回当前仓库名构成的列表，用于查询。

* `get_repo(self, repo_name)`
    * 参数：
        `repo_name`：仓库名
    * 功能：
        根据提供的仓库名返回该仓库的实例，用于自定义查询相关信息，但应谨慎处理，不更改其信息。

* `get_catalog(self, repo_name, catalog_name)`
    * 参数：
        `repo_name`：仓库名
        `catalog_name`：分类名
    * 功能：
        根据提供的仓库名和分类名返回该分类的实例，用于自定义查询相关信息，但应谨慎处理，不更改其信息。

* `get_pictures_path(self, repo_name, catalog_name)`
    * 功能：
        返回该分类下所有系列的路径，返回格式为 `(分类文件夹, [各系列文件夹名])`

* `add_signs_to_catalog(...)`
    * 参数：
        `signs_path`：需要添加图片的文件夹路径。
        `volume`：添加的图片数，可直接添加，也可通过指定 `auto_count` 自动计数，自动计数只计数扩展名为 `.jpg` 的文件。
        `auto_count`：若为 `True`，则使用自动计数，默认值为 `False`。
    * 功能：
        添加已有的图片到指定的分类中，将产生一个新的系列。

* `create_repo_with_signs(self, src_dir, *, repo_name=None)`
    * 参数：
        `src_dir`：指定的仓库文件夹，其中含有分类文件
        `repo_name`：默认为 `None`，直接以文件夹名作为仓库名，若设置为其它名称，则以该值为准。
    * 功能：
        在已有的仓库中创建各种信息，并将仓库添加到系统中。默认添加描述信息为 `create automatically.`，默认 `provider` 为 `unknown`。

* `batch_add_signs(self, repo_name, src_dir, *, args=None)`
    * 参数：
        `src_dir`：其下含有所有需要添加的分类，可看作是一个需要合并的仓库。
        `args`：若提供一个源仓库下所有分类到目标仓库下分类的映射，则使用映射值作为合并的分类名，否则使用源仓库的子文件夹名作为分类名。
    * 功能：
        将现有仓库合并入已有仓库，若要合并入的分类不存在，则返回源仓库中的该分类，且不对其做任何操作。

### 3.4 注意事项

* `manager.global_manager` 为唯一全局 `SystemManager` 实例，一般情况下应不再创建其它实例，避免信息出现差错。

* 可通过包含 `manager.py` 包将管理系统引入自己的代码中使用。
