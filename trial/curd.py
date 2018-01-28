from curd.service import sites
from django.utils.safestring import mark_safe
from django.urls import re_path, reverse
from django.forms import ModelForm, widgets
from django.shortcuts import HttpResponse
from curd.service.views import SearchOption

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
        widgets = {
                'author_name': widgets.TextInput(attrs={'class': 'form-control', "placeholder": '作者名称'}),
                'age': widgets.TextInput(attrs={'class': 'form-control', "placeholder": '作者年龄'}),
                'gender': widgets.Select(attrs={'class': 'form-control', "placeholder": '作者年龄'},
                                         choices=models.Author.choices_list),
        }

class PublishModelForm(ModelForm):
    class Meta:
        model = models.Publish
        fields = '__all__'
        widgets = {
            'publish_name': widgets.TextInput(attrs={"class": 'form-control', "placeholder": '出版社名'}),
            'city': widgets.TextInput(attrs={"class": 'form-control', "placeholder": '城市'}),
            'email': widgets.TextInput(attrs={"class": 'form-control', "placeholder": '邮箱'}),

        }

class BookModelForm(ModelForm):
    class Meta:
        model = models.Book
        fields = '__all__'
        widgets = {
            'book_name': widgets.TextInput(attrs={"class": 'form-control', "placeholder": '图书名'}),
            'price': widgets.TextInput(attrs={"class": 'form-control', "placeholder": '价格'}),
            'authors': widgets.SelectMultiple(attrs={"class": 'form-control'},choices=models.Author.objects.all()),
            'publish': widgets.Select(attrs={"class": 'form-control'},choices=models.Publish.objects.all()),
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
        """ 覆盖基类CURDConfig中的get_list_display方法，并添加
            一个，如果只是想添加一个功能，可以不覆盖姊方法，仅仅将创建的函数通过"list_display"传递即可

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
    action_list = [multi_delete,]
    list_display = ['author_name', 'age', 'gender']
    search_list = ['author_name__contains', 'gender__contains']


class BookConfig(sites.CURDConfig):
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

    def author_display(self, obj=None, is_header=False):
        """ 定制作者字段在表格中显示的数据，如果默认会显示"trial.Author.None"
        Args:
            obj: 当前记录对象
            is_header: 是否为表头
        Return:
            当is_header=True时，返回表头字符串；
            当is_header=False时，返回tbody单元格内的数据
        """

        if is_header:
            return '作者'
        author_list = [str(author) for author in obj.authors.all()]
        authors = ','.join(author_list)
        return authors

    list_display = ['book_name', 'price', author_display, 'publish', like_this]
    combain_search_field_list = [
        SearchOption('authors', is_multi=True),
        SearchOption('publish')
    ]
    model_form_class =BookModelForm


class PublishConfig(sites.CURDConfig):
    list_display = ['publish_name', 'city', 'email']
    model_form_class = PublishModelForm

sites.site.register(models.Publish, PublishConfig)
sites.site.register(models.Author, AuthorConfig)
sites.site.register(models.Book, BookConfig)
