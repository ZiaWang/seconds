# 构建路由系统

## 1. 利用python模块实现单例对象site
1. 首先创建文件。在`curd`应用下创建文件夹`service`，在其下创建`sites.py`。
2. 我们接下来要在这个类中定义两个类
	- `CURDSite`
		- 这个类实例化的到的就是site对象，我们要通过这个对象来实现模型的注册和路由分发的功能
	- `CURDConfig`
		- 这个类用来进行路由的进一步分发，并实现每一个路径对应的视图函数

3. 要实现CURDConfig类的单例模式，只需要在`site.py`文件中实例化一个对象即可，当程序中其他要实例化CURBConfig的时候，我们只需要赋予其`site.py`中实例化的对象即可



```python
from django.urls import path, re_path
from django.shortcuts import render


class CURDConfig:
    list_display = []

    def __init__(self, model_class, curb_site_obj):
        self.model_class = model_class
        self.site = curb_site_obj

    def get_urls(self):
        """ 生成路径与视图函数映射关系的列表
        Return:
            返回生成的列表
        """

        app_model = self.model_class._meta.app_label, self.model_class._meta.model_name
        urlpatterns = [
            re_path(r'^$', self.show, name='%s_%s_show' % app_model),
            # re_path(r'^add/$', self.add, name='%s_%s_add'%app_model),
            # re_path(r'^/(\d+)/delete/$', self.delete, name='%s_%s_delete'%app_model),
            # re_path(r'^/(\d+)/change/$', self.change, name='%s_%s_change'%app_model),
        ]
        return urlpatterns

    @property
    def urls(self):
        return self.get_urls()

    def show(self, request):
        """ 列表页面对应的视图函数
        Return:
            HttpResponse: 返回包含渲染好了的页面的响应对象
        """

        objects = self.model_class.objects.all()
        return render(request, 'curd/show.html', {"objects": objects, "config_obj": self})


class CURDSite:
    def __init__(self):
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
        return self.get_urls(), None, None

# 实现单例模式
site = CURDSite()

```


#### 简单解释
1. 关于`list_display`
	- 这个静态属性时提供了自定义表格将要显示的字段的一个借口，如果在启动文件`curd.py`文件中自定义了一个`CURDConfig`类的派生类，在这个派生类中我们可以在`list_display`指定要在表格中显示的字段
	- 当这个静态字段在`CURDConfig`类的派生类中没有指定时，默认将只显示对象(`__str__`方法的返回值)

2. 关于路由分发
	- Django中，路由分发的本质其实就是一个三元元组，包括include函数返回的也是一个三元元组，不明白的可以看我在Django admin源码分析中的介绍

3. 关于path与re_path
	- 这是Django2.0中新出现的，`re_path`就对应之前版本中的`url`，path是新增的一个路由函数 



## 2. 注册模型
- 当我们将一个模型通过`site`对象的`register`方法注册了之后，在上述路由系统中，就会生成与该模型操作相关的多个url，url格式如下
	- `/curd/应用名/模型名/`对应列表界面
	- `/curd/应用名/模型名/add/`对应添加界面
	- `/curd/应用名/模型名/(\d+)/delete/`对应删除界面
	- `/curd/应用名/模型名/(\d+)/change/`对应修改界面

- 注册模型的代码应该放在curd程序的启动文件中，因此我们在应用`trial`目录下的`curd.py`启动文件中注册`/trial/models.py`中模型

```python
from curd.service import sites

from trial import models


sites.site.register(models.Publish)
sites.site.register(models.Author, AuthorConfig)
sites.site.register(models.Book)
```

## 3. 配置路由

```python
from curd.service import sites
from django.urls import path

urlpatterns = [
    path('curd/', sites.site.urls),
]
```


## 流程分析
1. 项目启动，根据`/trail/apps.py`中的`ready`函数，去当前所有已经注册了的应用中寻找`curd.py`模块，并将该模块加载到内存中。
2. 执行`curd.py`中的site对象的register方法，该方法内部流程如下
	1. 首先完成注册，注册其实就是将每一个传入的`model_class`模型类作为key，该模型类作和site对象作为参数实例化得到的CURDConfig实力对象作为value保存在`_registry`字典中
3. 注册路由时，`path`内调用的`sites.site.urls`在`site`对象内部返回的是一个三元元组，元组的第一个元素对应一个存放了路径与下一级路由映射关系的列表
	1. 初始化一个urlpatterns空列表
	2. 循环遍历site对象的`_registry`属性对应的字典，同时获取每一个`modle_class`对应的模型类名与模型类所在的应用的名称
		1. 使用这些名称生成一个一级路由`/app_name/model_name/`
		2. 使用路由分发，调用字典中`model_class`对应的配置类`curd_config_class`的实例对象的`urls`属性方法（有`@property`装饰）
			1. `urls`返回之中调用了`curd_config_object`对象的`get_urls`方法，该方法内生成了一个存放路径与视图函数映射关系的列表。

	