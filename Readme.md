# 图片库管理程序

## 1. 功能总结

### 1.1 已实现功能

1. 创建图片库以及图片分类（**增**）
1. 返回图片路径（**查**）

### 1.2 未实现功能

1. 重命名功能（**改**）
1. 删除文件功能（**删**）
1. 异常机制
1. 日志功能
1. GUI

## 2. 概览

**思路**：使用 `json` 文件管理信息

### 2.1 文件结构

#### 2.1.1 项目结构

```
information:
    datapool_info.json -- 记录图片库信息

modules:
    exceptions.py -- 异常类定义，未完成
    helper.py -- 管理类，已完成
    info_path.py -- 包含 datapool_info.json 路径，仓库信息文件的文件名，类别信息文件的文件名
    tools.py -- 包含几个工具函数

manager.py -- 包含一个全局的系统管理变量
```

#### 2.1.2 系统文件结构

```
repo_dir_1:
    repo_info.json

    catalog_dir_1:
        catalog_info.json

        1
        2
        ...
    catalog_dir_2:
        catalog_info.json

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
    "maxid": 2, -- 分配 id 时使用
    "repo_props": [
        {
            "name": "sample_repo", -- repo 名
            "id": 2, -- repo id
            "volume": 440, -- repo 中的图片数量
            "description": "create on existing repo", -- repo 的描述信息
            "datetime": "2018-04-21 17:35:34", -- repo 的创建时间
            "path": "E:\\sample_repo" -- repo 路径
        }
    ]
}
```

`repo_info.json`
```
{
    "maxid": 2,
    "catalog_props": [
        {
            "name": "19 禁止超车",
            "id": 1,
            "volume": 221,
            "subdir": "19 禁止超车", -- catalog 的文件夹名
            "description": "create on existing repo",
            "datetime": "2018-04-21 17:35:34"
        },
        {
            "name": "31 限制高度",
            "id": 2,
            "volume": 219,
            "subdir": "31 限制高度",
            "description": "create on existing repo",
            "datetime": "2018-04-21 17:35:34"
        }
    ]
}
```

`catalog_info.json`
```
{
    "maxid": 1,
    "signlist_props": [
        {
            "id": 1,
            "volume": 221,
            "datetime": "2018-04-21 17:35:34",
            "provider": "create on existing repo, unknown provider" -- 已标注图片的标注者信息
        }
    ]
}
```
