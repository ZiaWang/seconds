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

    def get_app_model(self):
        """ 获取当前模型类的名称和该模型类所在应用的名称
        Return:
              返回一个存放二元元组: (模型类名, 应用名)
        """

        app_model = (
            self.model_class._meta.app_label,
            self.model_class._meta.model_name
        )
        return app_model

    # 路由部分
    def get_urls(self):
        """ 生成路径与视图函数映射关系的列表，并扩展该列表
        Return:
            返回存放路由关系的列表
        """

        # 生成增、删、改、查基本映射关系
        app_model = self.get_app_model()
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

        alias = 'curd:%s_%s_delete' % self.get_app_model()
        return reverse(alias, args=(nid, ))

    def get_change_url(self, nid):
        """ 获取编辑记录对应的url
        Args:
            nid: 该记录的id
        Return:
            字符串形式的路径
        """

        alias = 'curd:%s_%s_change' % self.get_app_model()
        return reverse(alias, args=(nid, ))

    def get_show_url(self):
        """ 获取列表页面的url
        Return:
            字符串形式的路径
        """

        alias = 'curd:%s_%s_show' % self.get_app_model()
        return reverse(alias)

    def get_add_url(self):
        """ 获取增加记录对应的url
        Return:
            字符串形式的路径
        """

        alias = 'curd:%s_%s_add' % self.get_app_model()
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
        return self.get_urls(), 'curd', None

# 实现单例模式
site = CURDSite()
