# CURDSite 类

## 代码

```python
class CURDSite:
    """ 可以看作一个容器，其静态属性`_registry`放置着`model_class`模
        型类和模型对应的`config_obj`配置对象。
    功能:
        1. 注册模型类
        2. 生成一级路由

    """
    def __init__(self, name):
        self.name = name
        self._registry = {}         # 存放model及其对应的CURBConfig()实例键值对

    def register(self, model_class, curd_config_class=None):
        """ 注册传入的model模型类，如果没有提供配置类curd_config_class，默认使用CURDConfig类
        Args:
            model_class: models.py中要注册的模型类
            curd_config_class: 模型类对应的配置类
        Return:
            None
        """

        if not curd_config_class:
            curd_config_class = CURDConfig
        self._registry[model_class] = curd_config_class(model_class, self)

    def get_urls(self):
        """ 编辑包含已注册模型类的字典，生成路径与下一级路由分发的映射关系
        Return:
            包含映射关系的列表
        """

        urlpatterns = []
        for model_class, curd_config_obj in self._registry.items():
            app_name = model_class._meta.app_label
            model_name = model_class._meta.model_name
            temp_path = path(
                '{app_name}/{model_name}/'.format(app_name=app_name, model_name=model_name),
                (curd_config_obj.urls, None, None)
            )
            urlpatterns.append(temp_path)
        return urlpatterns

    @property
    def urls(self):
        """ 实现路由分发
        Return:
            返回一个元组:
                第一个元素为生成的一级路由映射关系组成的列表
                第二个元素为方向解析时会用到的路由空间
                第三个元素为site对象的name属性，实例化时提供，当namespace没有提供的时候，它将作为namespace被使用
        """
        
        return self.get_urls(), 'curd', self.name



site = CURDSite("curd")       # 实现单例模式
```

## 单例模式
- 在程序运行过程中，只有一个site对象

## 功能介绍
#### 注册模型类
- `_registry`字典内存放的是所有已经通过`site`对象注册了的`模型类`和该模型类对应的`配置对象`之间的键值对。`配置对象`中封装了对该`模型类`增删改查功能以及其他功能
	- 大概逻辑如下

```python

config_obj = self.config_class() if self.config_class else CURDConfig()

_register = {
	"author": config_obj,
}
```

#### 生成一级路由
- 当我们将一个`模型类`通过`site`对象的`register`方法注册了之后，`get_urls`方法中会遍历`self._register`字典，并生成为每一个字典中的模型类生成`增、删、改、查`一级路由，将这些路由封装到列表中返回
- url格式如下
	- `/curd/应用名/模型类名/ + 二级路由分发`

## 细节解释
#### 1. 关于路由分发
- Django中，路由分发的本质其实就是一个三元元组，包括include函数返回的也是一个三元元组，不明白的可以看我在Django admin源码分析中的介绍

#### 2. 关于namespace 
- namespace在url的反向解析中会用到，他的作用就是用来区分具有相同别名的url。
- 在2.0版本与低版本中的使用
	- 在Django2.0版本中，路由分发时我们需要在元组的第二个元素位置上指定namespace的名称
	- 在Django2.0以下的版本中，路由需要在元组的第三个位置上指定namespace的名称
#### 3. 关于path和re_path
- 这是Django2.0中新出现的，`re_path`就对应之前版本中的`url`，path是新增的一个路由函数 