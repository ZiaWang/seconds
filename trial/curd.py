from curd.service import sites
from django.utils.safestring import mark_safe
from django.urls import re_path, reverse
from django.forms import ModelForm
from django.shortcuts import HttpResponse

from trial import models


class AuthorModelForm(ModelForm):
    """ Author表对应模型类 """

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
    """ CURDConfig派生类，用来根据用户权限来自定义功能
    """



    show_action_form = True
    show_search_form = True

    def multi_delete(self, request):
        """ 批量操作action对应的函数
        Args:
            request: 当请求对象，用来获取要操作的记录对象id
        """

        delete_id_list = request.POST.getlist('id')
        self.model_class.objects.filter(id__in = delete_id_list).delete()
        return HttpResponse('这里用来存放用户删除完成后的业务逻辑')

    multi_delete.func_description = '批量删除'              # 定义函数对象属性，用来在模板上显示

    def get_show_add_btn(self):
        """ 验证用户是否具备添加记录功能权限
        Return:
            如果用户有权限，返回True，否则返回False
        """

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


    def get_list_display(self):
        """ 覆盖基类CURDConfig中的get_list_display方法，并添加一个"""

        data = []
        if self.list_display:
            data.extend(self.list_display)
            data.append(AuthorConfig.delete)
            data.append(AuthorConfig.change)
            data.insert(0, AuthorConfig.checkbox)
            data.append(AuthorConfig.like_this)
        return data

    model_form_class = AuthorModelForm
    action_list = [multi_delete,]
    list_display = ['author_name', 'age', 'gender']
    search_list = ['author_name__contains', 'gender__contains']


sites.site.register(models.Publish)
sites.site.register(models.Author, AuthorConfig)
sites.site.register(models.Book)
