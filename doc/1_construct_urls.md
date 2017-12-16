# 构建路由系统

## 1. 利用python模块实现单例对象site
1. 首先创建文件。在`curd`应用下创建文件夹`service`，在其下创建`sites.py`。
2. 我们接下来要在这个类中定义两个类
	- `CURDSite`
		- 可以看作一个容器，其静态属性`_registry`放置着`model_class`模型类和模型对应的`config_obj`配置对象。
		- 功能
			- 模型注册
			- 路由分发
		- 实例
			- `site`（单例模式）
	- `CURDConfig`
		- 这个配置类为每一个模型类`model_class`生成url对应关系，并处理用户请求
		- 功能
			- 路由
				- 为每一个`model_class`模型类生成url路径与视图函数之间的映射关系
			- 视图函数

3. 要实现CURDConfig类的单例模式，只需要在`site.py`文件中实例化一个对象即可，当程序中其他要实例化CURBConfig的时候，我们只需要赋予其`site.py`中实例化的对象即可


- 下面放源码，其中的一些细节会在后面慢慢解释


```python
from django.urls import path, re_path
from django.shortcuts import render, HttpResponse, redirect
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.forms import ModelForm


class CURDConfig:
    """  为每一个`model_class`模型类生成url路径与视图函数之间的映射关系

    """

    list_display = []           # 存放列表页面表格要显示的字段

    def __init__(self, model_class, curb_site_obj):
        self.model_class = model_class
        self.site = curb_site_obj

    # 路由部分
    def get_urls(self):
        """ 生成路径与视图函数映射关系的列表，并扩展该列表
        Return:
            返回存放路由关系的列表
        """

        # 生成增、删、改、查基本映射关系
        app_model = (
            self.model_class._meta.app_label,
            self.model_class._meta.model_name
        )
        urlpatterns = [
            re_path(r'^$', self.show_view, name='%s_%s_show' % app_model),
            re_path(r'^add/$', self.add_view, name='%s_%s_add' % app_model),
            re_path(r'^(\d+)/delete/$', self.delete_view, name='%s_%s_delete' % app_model),
            re_path(r'^(\d+)/change/$', self.change_view, name='%s_%s_change' % app_model),
        ]

        # 扩展路由映射关系
        extra_patterns = self.extra_url()
        urlpatterns.extend(extra_patterns)
        return urlpatterns

    @property
    def urls(self):
        return self.get_urls()

    def extra_url(self):
        """ 为用户扩展urls提供的接口，只需要在CURDConfig派生类中派生覆盖此方法即可
        Return:
            存放了路径与视图函数映射关系的列表(re_path, path, url)
        """

        return []

    # 页面显示(权限相关)部分
    def get_list_display(self):
        """ 处理用户权限之内的相关操作，派生CURDConfig类中可以根据用户权限来分配响应的功能按钮/链接，
            实现每个类中可以在增删改查之外，再扩展自己类的URL
        Return:
            包含了权限操作按钮/链接在内的列表
        """

        data = []
        if self.list_display:
            # data.extend(self.list_display)    # 不能是self调用，与后面链接起来，got multiple values for argument 'is_header'
            # data.append(self.delete)
            # data.append(self.change)
            # data.insert(0, self.checkbox)
            data.extend(self.list_display)
            data.append(CURDConfig.delete)
            data.append(CURDConfig.change)
            data.insert(0, CURDConfig.checkbox)
        return data

    show_add_btn = False        # 先否显示添加按钮权限接口

    def get_show_add_btn(self):
        """ CURDConfig中，根据用户权限来判断用户是否有添加记录按钮对应的权限，如果有则返回True
        Return:
            布尔值，代表用户是否有权限，该值将传递给上下文中用于渲染页面添加按钮
        """

        # 中间存放业务逻辑
        return self.show_add_btn

    # 定制列表页面要显示的列（功能按钮/链接）
    def delete(self, obj=None, is_header=False):
        """ 列表页面单条记录删除按钮/链接
        Args:
            obj: 该记录对象
            is_header: 当用于生成列表标题"<th>"的时候为True
        Return:
            一个SafeText对象，可以将字符串中的html内容转化为标签，
            此处为删除功能的超链接
        """

        if is_header:
            return '删除'
        return mark_safe('<a href="%s">删除</a>' % (self.get_delete_url(obj.id), ))

    def change(self, obj=None, is_header=False):
        """ 列表页面单条记录编辑按钮/链接
        Args:
            obj: 该记录对象
            is_header: 当用于生成列表标题"<th>"的时候为True
        Return:
            编辑功能超链接
        """

        if is_header:
            return '编辑'
        return mark_safe('<a href="%s">编辑</a>' % (self.get_change_url(obj.id), ))

    def checkbox(self, obj=None, is_header=False):
        """ 列表页面单条记录的选择checkbox，用于批量记录操作
        Args:
            obj: 该checkbox所在记录对象
            is_header: 当用于生成列表标题"<th>"的时候为True
        Return:
            关于选择该条记录的checkbox框
        """

        if is_header:
            return '选择'
        return mark_safe('<input type="checkbox" name="id" value="%s" />' % (obj.id, ))

    # 反向解析获取url部分
    def get_delete_url(self, nid):
        """ 获取删除记录对应的路径
        Args:
            nid: 该记录的id
        Return:
            字符串形式的路径
        """
        
        alias = 'curb:%s_%s_delete' % (
            self.model_class._meta.app_label, 
            self.model_class._meta.model_name
        )
        return reverse(alias, args=(nid, ))

    def get_change_url(self, nid):
        """ 获取编辑记录对应的url
        Args:
            nid: 该记录的id
        Return:
            字符串形式的路径
        """
        
        alias = 'curb:%s_%s_change' % (
            self.model_class._meta.app_label, 
            self.model_class._meta.model_name
        )
        return reverse(alias, args=(nid, ))

    def get_show_url(self):
        """ 获取列表页面的url
        Return:
            字符串形式的路径
        """
        
        alias = 'curb:%s_%s_show' % (
            self.model_class._meta.app_label, 
            self.model_class._meta.model_name
        )
        return reverse(alias)

    def get_add_url(self):
        """ 获取增加记录对应的url
        Return:
            字符串形式的路径
        """
        
        alias = 'curb:%s_%s_add' % (
            self.model_class._meta.app_label, 
            self.model_class._meta.model_name
        )
        return reverse(alias)

    # 视图函数部分
    def show_view(self, request):
        """ 列表页面对应的视图函数
        Return:
            HttpResponse: 返回包含渲染好了的页面的响应对象
        """

        objects = self.model_class.objects.all()
        return render(request, 'curd/show.html', {"objects": objects, 
                                                  "config_obj": self, 
                                                  "add_url": self.get_add_url(), 
                                                  "show_add_btn": self.get_show_add_btn()})

    # form表单部分
    model_form_class = None

    def get_model_form_class(self):
        """ 获取modelform表单，如果在派生的CURDConfig中创建了ModelForm派生类，就是用该类，否则使用默认的ViewModelForm
        Return:
            ModelForm类的派生类
        """
        
        if self.model_form_class:
            return self.model_form_class
        else:
            meta_class = type(
                'Meta', 
                (object, ), 
                {"model": self.model_class, 
                 "fields": "__all__"}
            )
            ViewModelForm = type(
                'ViewModelForm', 
                (ModelForm, ), 
                {"Meta": meta_class}
            )
            return ViewModelForm

    # 路径处理部分
    def add_view(self, request):
        """ 添加记录路径对应的视图函数
        Args:
            request: 当前请求对象
        Return:
            HttpResponse: 包含响应结果的响应对象。如果是GET请求，返回页面，如果是POST请求，将重定向至列表页面
        """

        model_form_class = self.get_model_form_class()
        
        if request.method == 'GET':
            return render(request, 'curd/add.html', {"form": model_form_class()})
        else:
            form = model_form_class(data=request.POST)
            if form.is_valid():
                form.save()
                return redirect(to=self.get_show_url())
            else:
                return render(request, 'curd/add.html', {"form": form})

    def delete_view(self, request, nid):
        """ 删除一条记录
        Args:
            request: 当前请求对象
            nid: 当前要被删除的记录的id
        Return:
            HttpResponse: 重定向到列表页面
        """
        
        obj = self.model_class.objects.filter(id=nid)
        obj.delete()
        return redirect(self.get_show_url())

    def change_view(self, request, nid):
        """ 编辑一条记录
        Args:
            request: 当前请求对象
            nid: 当前要被编辑的记录的id
        Return:
            GET请求: 返回编辑页面
            POST请求: 验证编辑后的数据
                1. 验证通过，重定向到列表页面
                2. 验证失败，返回包含错误信息的编辑页面
        """
        
        obj = self.model_class.objects.filter(id=nid).first()
        if not obj:
            return redirect(self.get_show_url())
        
        model_form_class = self.get_model_form_class()
        
        if request.method == 'GET':
            form = model_form_class(instance=obj)
            return render(request, 'curd/change.html', {"form":form})
        else:
            form =model_form_class(data=request.POST, instance=obj)
            if form.is_valid():
                form.save()
                return redirect(to=self.get_show_url())
            else:
                return render(request, 'curd/change.html', {"form": form})


```


#### 细节解释
###### 1. 钩子函数`extra_url`、`get_urls`与视图函数
- `get_urls`是CURDConfig为模型类提供了基本的增、删、改、查路由映射，内部还调用了一个扩展路由映射的对象方法`extra_url`，用来扩展路由
- `extra_url`用来扩展路由映射关系，在`get_urls`仅仅只为每一个模型类提供了简单的增、删、改、查路由映射，如果你想额外给指定的模型类增加其他的路由映射关系，那么你就可以在`extra_url`中创建号映射关系之后，将其封装在列表或者元组中返回。
- 在使用`extra_url`扩展了路由映射关系之后，我们可以在派生类中定义这个映射对应的视图函数

- **注意：最好给定义的url路径指定一个别名**


###### 2. `list_display`与`get_list_display`
- `list_display`提供了自定义表格将要显示的字段的一个接口，如果在启动文件`curd.py`文件中自定义了一个`CURDConfig`类的派生类，在这个派生类中我们可以在`list_display`指定要在表格中显示的字段
	- 当这个静态字段在`CURDConfig`类的派生类中没有指定时，默认将只显示对象(`__str__`方法的返回值)
-  `get_list_display`方法用来扩展指定模型类对应的url。只需要在`curd.py`启动文件中，覆盖基类(CURDConfig)的`get_list_display`方法即可，因此`list_display`起到的仅仅是一个存放要显示的指定字段的作用。
- **注意**
	- **如果在派生类中覆盖了基类的`get_list_display`方法，需要在派生类中定义传入的函数名对应的函数**
	- **`get_list_display`中传入的是函数不是方法，你只需要以类名调用该方法名传入即可，比如"MyConfig.func"，如果你传入的是类似"self.func"，那么就会片抛出参数相关错误"got multiple values for argument 'xxxx'"**

###### 3. 权限管理、`show_add_btn`与`get_show_add_btn`
- `show_add_btn`是一个布尔值，表示是否要将添加按钮显示在页面上，在`curd.py`我们定义的`CURDConfig`派生类中，可以设置该静态字段的值。
- `get_show_add_btn`的返回值就是对象的`show_add_btn`属性，你也可以重写该方法，
	- 如果该方法返回的布尔值为True，则页面上将出现添加按钮，否则将不出现
	- **"get_show_add_btn"方法内部应该要有用户权限验证对应的业务逻辑**

###### 7. 反向解析、命名空间namespace与get_xxx_url
- 派生类中你可以使用反向解析通过我们自定义路由的别名来生成该路径
- namespace
	- namespace在url的反向解析中会用到，他的作用就是用来区分具有相同别名的url。
	- 在2.0版本与低版本中的使用
		- 在Django2.0版本中，路由分发时我们需要在元组的第二个元素位置上指定namespace的名称
		- 在Django2.0以下的版本中，路由需要在元组的第三个位置上指定namespace的名称

###### 8. 元类、`model_form_class` 与 `get_model_form_class`
- 在添加记录页面和编辑记录页面我们都需要在页面中生成表单，但是每一个模型类的字段根本是无法预知的，因此我们就不能使用`Form`组件来完成这个任务，只能使用`ModelForm`来生成表单页面和进行表单验证以及保存表单数据到数据库。
- `model_form_class`默认为`None`，你可以在`curd.py`中创建一个继承自`ModelForm`模型类，并将该类传递给派生类中的`model_form_class`静态字段，在`get_model_form_class`方法中会有这个流程
	- 如果你在在派生类中通过`model_form_class`传递了一个`ModleForm`派生类，那么该**"模型类"**对应的表单将会按照你定义的ModelForm派生类来生成。
		- 你可以在`ModleForm`派生类中指定form表单的样式、对应的模型类、要显示的字段、错误信息等等
	- 如果你没有指定`ModleForm`派生类，在`get_model_form_class`方法中将会使用type元类来动态的为你组装一个`ModleForm`派生类。

###### 9. 字段函数 
- 这个名字我觉得挺合适，顾名思义，这个函数的返回值将用于在列表页面的表格中显示一列数据
- 规则
	- 这个函数名任意，但是要有实际意义
	- 参数`(self, tr_obj=None, is_header=False)`
		- 第一个参数就是派生类的的实例对象config_obj
		- 第二个参数是一个记录对象，默认为None，一定要记得给这个参数设置默认值None，因为在生成表格的时候，此函数生成表头字段和普通字段时会传入不同个数的参数
		- 第三个参数就像他的名字一样，是否要显示为表头。你不需要设置，默认为False就好

###### 10. 关于路由分发
	- Django中，路由分发的本质其实就是一个三元元组，包括include函数返回的也是一个三元元组，不明白的可以看我在Django admin源码分析中的介绍

###### 11. 关于path与re_path
	- 这是Django2.0中新出现的，`re_path`就对应之前版本中的`url`，path是新增的一个路由函数 

###### 举例

```python
from curd.service import sites
from django.utils.safestring import mark_safe
from django.urls import re_path, reverse
from django.forms import ModelForm

from trial import models


class AuthorModelForm(ModelForm):
    class Meta:
        model = models.Author
        fields = "__all__"
        error_messages = {
            "author_name": {
                "reqired": "作者名不能为空"
            }, 
            "age": {
                "required": "年龄不能为空",
                "invalid": "年龄必须为数字"
            } 
        }
        

class AuthorConfig(sites.CURDConfig):
    
    
    def get_show_add_btn(self):
        # 验证添加按钮权限
        user_has_permission = True     # 模拟权限验证过程
        if user_has_permission:
            return True
        else:
            return False

    def extra_url(self):
        """ 扩展功能url
        Return:
            包含路由映射关系的列表
        """

        app_model = self.get_app_model()

        extra_patterns = [
            re_path(r'^(\d+)/like/$', self.like_this, name="%s_%s_like" % app_model)
        ]
        return extra_patterns

    def get_like_url(self, nid):
        """ 反向生成"喜欢"功能对应url
        Return:
            返回字符串形式的url
        """

        alias = "curd:%s_%s_like" % self.get_app_model()
        return reverse(alias, args=(nid, ))
    
    def like_this(self, obj=None, is_header=False):
        """ 列表页面"喜欢"功能链接
        Args:
            obj: 当前记录对象
            is_header: 是否为标题
        Return:
            返回该功能对应的url超链接
        """

        if is_header:
            return '喜欢吗'
        return mark_safe('<a href="%s">喜欢这个记录</a>' % self.get_like_url(obj.id))

    list_display = ['author_name', 'age', 'gender']
    
    def get_list_display(self):
        """ 覆盖基类CURDConfig中的get_list_display方法，并添加一个

        """
        data = []
        if self.list_display:
            data.extend(self.list_display)
            data.append(AuthorConfig.delete)
            data.append(AuthorConfig.change)
            data.insert(0, AuthorConfig.checkbox)
            data.append(AuthorConfig.like_this)
        return data
    
    model_form_class = AuthorModelForm


sites.site.register(models.Publish)
sites.site.register(models.Author, AuthorConfig)
sites.site.register(models.Book)
```


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

	