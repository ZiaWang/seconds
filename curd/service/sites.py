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
