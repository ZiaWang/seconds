# CURDConfig 类

## 内部函数

```
路由部分:
        add_request_decorator
        get_urls
        extra_url

功能权限部分:
        get_list_display
        get_show_add_btn
        get_show_search_form
        get_search_list
        get_show_action_form
        get_action_list

记录操作权限部分:
        delete
        change
        checkbox

反向解析url部分:
        get_delete_url
        get_change_url
        get_add_url
        get_show_url

视图函数部分:
        show_view
        add_view
        delete_view
        change_view

表单部分:
        get_model_form_class

搜索功能部分:
        create_search_condition
        get_combain_search_field_list
```

## 功能介绍
- **实现修改配置有几个步骤**
	1. 创建配置类`CURDConfig`的派生类
	2. 在派生类中修改配置项或创建新功能
	3. 将派生的配置类和模型类在通过site对象注册

- 对于不同的用户，其具备的权限是不同的，比如`添加记录的权限`，`删除记录的权限`，`编辑记录的权限`等等。`CURDConfig`类中提供的增删改查功能都可以通过`CURDConfig`派生类中修改配置项来完成

#### 预留钩子函数
- 对于`CURDConfig`类中定义的类似`get_list_display`方法，比如`get_show_add_btn`, `get_show_add_btn`, `get_show_search_form`等都会配合`用户权限`在`CURDConfig`的派生类中进行覆盖

- 举一个我在其他项目(`crm`)中的例子，`crm`项目中我使用到了自己开发的`基于角色的权限管理系统`以及`seconds`这个组件

```python
class UserConfig(CURDConfig):
	def get_edit_link(self):
		result = []
		user_permission_list = self.request.session.get(settings.USER_PERMISSION_DICT)		# session的key存放在了配置文件中，这样修改起来只需要修改配置文件即可
		if "add" in user_permission_list:				# 有编辑权限
			result.extend(self.edit_link)
			return result
		else:					# 无编辑权限
			return []			
```

#### 配置列表页面，table表格能够显示的字段和功能
- list_display列表用来存放表格的一列列的字段，其内有两种类型的数据
	1. 当前model类中的字段名的字符串形式
	2. 自定义一个功能函数

###### 定义功能函数
- 功能函数根据每一个用户的权限来进行配置，比如查看“详细信息”功能，你就可以定义一个函数，让其返回一个超链接，这意味着你需要在配置类中同时配置该链接的路由映射(url和视图函数)
- 功能函数的参数是有限制的，定义的功能函数中，至少有`obj`和`is_header`两个默认参数
	- 即`func(self, obj=None, is_header=False)`。
	- 函数参数的默认值是固定的，你不需要做任何修改，只需要专注函数体内的业务逻辑：
		- `obj`指向的是一个记录对象，你可以在这个函数中调用他的字段，比如`pk`。在这个函数中你不需要为其传值
		- `is_header`是个布尔值，函数体内，`is_header`为True的时候表示该函数的返回值用来作为表头，否则作为tbody中单元格内的数据，通常是一个超链接，当然也可以是要显示的其他信息

- 注意
	- 定义好的功能函数要以**函数名变量的形式**存放在`list_display`中，不要传入一个方法
		- 比如，应该是`[ "name"， delete]`或者`["name", AuthorConfig.delete]`，而非`["name", self.delete]`

```python
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
```

###### 处理choices关联关系字段
- 对于使用了choices的字段，要想在列表中显示，需要在派生类自定义一个功能函数，然后将函数名传递给`list_display`中	
	- 调用记录对象的`get_fieldName.display()`方法即可获取choices列表中对应的value

```python
class CustomerConfig(CURDConfig):

    edit_link = ['qq']

    def gender_display(self, obj=None, is_header=False):
        """ 获取客户性别数据的函数 """
        
        if is_header:
            return '性别'
        return obj.get_gender_display()
    
    list_display = ['name', 'qq', gender_display]
```

###### 处理多对多字段
- 多对多字段在列表中的默认显示的是类似`appxx.model.None`。我们可以定义一个功能函数来处理它
- 注意
	- **我们可以对多对多的每一个对象添加样式甚至是超链接**。当添加超链接的时候，通常会是一个删除该多对多关系的超链接

```python
    def teachers(self, obj=None, is_header=False):
        """ 构造列表页面表格中"任课老师"字段
        Args:
            obj: 当前行记录对象
            is_header: 是否是表头
        Return:
            当is_header为True的时候，返回表头数据，否则返回有教师名拼接成的字符串
        """

        if is_header:
            return '授课老师'
        teacher_list = [
            '<span>%s &nbsp;</span>' % str(teacher)
            for teacher in obj.teachers.all()
        ]
        teacher_html = ''.join(teacher_list)
        return mark_safe(teacher_html)

```

###### 为单元格配置其他功能
 

```python
    def course_display(self, obj=None, is_header=False):
        if is_header:
            return '感兴趣的课程'
        course_list = [
            '<a href="/curd/crm/customer/del_pre_course/%s/%s/?%s" style="display:inline-block; border: 1px solid blue; padding: 5px;margin: 3px">%s &nbsp;x</a>' % (obj.id, course.id, self.request.GET.urlencode(),str(course))
            for course in obj.course.all()
        ]
        return mark_safe(''.join(course_list))

    def del_pre_course(self, request, customer_id, course_id):
        customer = self.model_class.objects.filter(pk=customer_id).first()
        customer.course.remove(course_id)
        return redirect("%s?%s" % (self.get_show_url(), self.request.GET.urlencode()))

    def extra_url(self):
        urlpatterns = [
            re_path(r'del_pre_course/(\d+)/(\d+)/', self.add_request_decorator(self.del_pre_course), name="%s_%s_dc" % self.get_app_model())
        ]
        return urlpatterns
```


#### 配置列表页面基本增删改功能
###### 关于权限
- 默认的，每一条记录都对应着选择、删除和修改的功能，如果用户不具备改权限，可以在派生类中重写`get_list_display`方法来取消这些默认权限

- `CURDConfig`中默认功能分配代码

```python
    def get_list_display(self):
        """ 处理用户权限之内的相关操作，派生CURDConfig类中可以根据用户权限来分配响应的功能按钮/链接，
            实现每个类中可以在增删改查之外，再扩展自己类的URL
        Return:
            包含了权限操作按钮/链接在内的列表
        """

        data = []
        if self.list_display:
            data.extend(self.list_display)
            data.append(CURDConfig.delete)      # 注意：是函数而不是方法！
            data.append(CURDConfig.change)
            data.insert(0, CURDConfig.checkbox)
        return data
```

- 如果你不想给这个用户这些功能权限，你可以在派生类中重写这个方法。比如

```python
    def get_list_display(self):
        """ 修改curd默认的功能权限，不对该用户提供删除和修改等功能，
            只有查看表格信息的权限
        
        """
        
        result = []
        if self.list_display:
            result.extend(self.list_display)
        return result
```


###### 增加功能
- 在派生类中配置静态属性`show_add_btn=True`就会开启用户添加记录的权限。

###### 编辑功能
- 组件中提供了两种可以用来编辑记录的途径
	1. 编辑按钮单占一个单元格，使用`list_display`，默认就是这种
	2. 编辑按钮以超链接的形式与其他字段结合，这个字段你可以在`edit_link`列表中任意指定，甚至指定多个，`edit_link`中不必须是字段，也可以是自己定义的字段

```python
# 使用edit_link实现编辑
class CourseConfig(CURDConfig):
    list_display = ['course_name']
    edit_link = ['course_name']

class ClassListConfig(CURDConfig):
    def course_semester(self, obj=None, is_header=False):
        """ 将课程和班级拼接后显示在单元格 """
        if is_header:
            return '班级'
        return '%s(%s)' % (obj.course, obj.semester)

    edit_link = [course_semester]
```

#### 配置批量操作action步骤
1. 使用`show_action_form=True`可以在页面上显示批量操作表单下拉框
2. 配置`action_list`
	- `action_list`中存放的是一个个用来批量处理记录对象的函数
	- 函数配置
		- 需要为函数对象设置一个`func_description`属性，他将在下拉框中显示，下拉框的value属性值将会是该函数名
3. 在派生类中自定义批量操作方法
	- 该方法要传递一个`request`参数


```python
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
        return HttpResponse('这里用来存放用户删除完成后的业务逻辑，比如跳转等')

    multi_delete.func_description = '批量删除' 
	
	action_list = [multi_delete,]   
```

###### 内部运行原理/流程解释
1. 当用户点击批量操作执行按钮之后，表单会将多个记录对象id传递给`site`对象的`show_view`方法
2. 在该方法内部会进行一个`and`的判断
	- `if request.method == 'POST' and self.get_show_action_form():` 
		- 第一个判断不需要解释
		- 第二个判断是为了保证即使一个没有action批量操作权限的用户在前端伪造的数据，该数据也进入不了数据库操作
3. 进入判断之后，会通过**反射**执行表单提交过来的方法 

```python
    def show_view(self, request, *args, **kwargs):
        """ 列表页面对应的视图函数
        功能:
            1. 对于GET请求，返回列表页面
            2. 对于批量操作action的POST请求，执行该action，执行完该action之后，可以自定义返回值，也可以没有，按需求而定
        Return:
            HttpResponse: 返回包含渲染好了的页面的响应对象
        """

        if request.method == 'POST' and self.get_show_action_form():
            func_name = request.POST.get('action')
            func = getattr(self, func_name)
            if func:
                ret = func(request, *args, **kwargs)

        combain_condition = {}
        option_list = self.get_combain_search_field_list()
        for key in request.GET.keys():
            value_list = request.GET.getlist(key)
            flag = False
            for option in option_list:
                if option.field_name == key:
                    flag = True
                    break
            if flag:
                combain_condition['%s__in' % key] = value_list

        objects = self.model_class.objects.filter(self.create_search_condition()).filter(**combain_condition)
        show_obj = ShowView(self, objects)
        return render(request, 'curd/show.html', {"show_obj": show_obj})
```




#### 配置ModelForm
###### 步骤
1. 在`curd.py`文件中创建一个`ModelForm`的派生类
2. 在派生类内部定义一个`Meta`类，在该类中
	- `model`指定要绑定的模型类
	- `fields`指定要使用的字段，一般用`"__all__"`
	- `widgets`指定样式和属性
		- 是一个字典，字典的key是字符串形式的字段
	- 等其他字段
3. 在配置类中让`model_form_class`指向你创建的ModelForm派生类

```python
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

class AuthorConfig(sites.CURDConfig):
    """ CURDConfig派生类，用来根据用户权限来自定义功能
    """
	
	# 省略中间
    model_form_class = AuthorModelForm
```
 
###### 流程介绍
1. 当添加/编辑按钮时，根据路由关系，会进入到`add_view`视图函数中
2. 视图函数内部会执行`site`对象的`get_model_form_class`方法，返回一个ModelForm的派生类
	- 如果在配置类中指定了ModelForm派生类，返回的将是该派生类
	- 如果没有指定。在`get_model_form_class`内部会动态的使用`type`元类创建一个modelForm派生类并返回
3. 接着通过该ModelForm派生类实例化一个form对象完成表单的渲染、数据的校验、数据的保存等功能

```python

class CURDConfig:
    model_form_class = None

    def get_model_form_class(self):
        """ 获取modelform表单，如果在派生的CURDConfig中创建了ModelForm派
            生类，就使用该类，否则使用默认的ViewModelForm

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
                 "fields": "__all__"})

            view_model_form_class = type(
                'ViewModelForm',
                (ModelForm, ),
                {"Meta": meta_class})
            return view_model_form_class


	def add_view(self, request):
        """ 添加记录路径对应的视图函数
        Args:
            request: 当前请求对象
        Return:
            HttpResponse: 包含响应结果的响应对象。如果是GET请求，返回页面，如果是POST请求，将重定向至列表页面
        """

        model_form_class = self.get_model_form_class()

        if request.method == 'GET':
            return render(request, 'curd/add.html', {"form":model_form_class()})
        else:
            form = model_form_class(data=request.POST)
            if form.is_valid():
                obj = form.save()
                _popbackid = request.GET.get('_popbackid')		# popup功能
                if _popbackid:
                    response_data = {
                        "id": obj.pk,
                        "text": str(obj),
                        "_popbackid": _popbackid
                    }
                    return render(request, "curd/popback.html", {"response_data": response_data})
                else:
                    return redirect(to=self.get_show_url())
            else:
                return render(request, 'curd/add.html', {"form": form})
```

#### popup功能
- popup功能其实就是基于当前页面打开一个新的窗口，在新的窗口中进行相关操作
- 在本项目中，popup会在`add`视图对应的页面中出现，它用来实现动态的添加一个关联对象到单选框或多选框中

- 由于popup功能只需要添加在关联对象即"add"页面上的单选框/复选框上，所以在渲染表单的时候，我们需要对要渲染的字段进行判断
	- 如果是关联对象ForeignKey/ManyToManyKey，就为其添加触发popup功能的按钮
	- 否则就当做普通字段对待

```python
@register.inclusion_tag(filename='curd/form.html')
def form_popup(form_obj):
    """ 渲染表单，并为单选框/复选框后面添加popup链接按钮
    Args:
        form_obj: 视图函数响应上下文中的form对象
    Return:
        上下文对象(字典)，用于渲染表单
    """

    new_form = []
    for bound_field in form_obj:
        temp = {"is_popup": False, "bound_field": bound_field}

        if isinstance(bound_field.field, ModelChoiceField):
            field_related_model_class = bound_field.field.queryset.model
            app_model = (
                field_related_model_class._meta.app_label,
                field_related_model_class._meta.model_name
            )
            base_url = reverse("curd:%s_%s_add" % app_model)
            popup_url = "%s?_popbackid=%s" % (base_url, bound_field.auto_id)
            temp["is_popup"] = True
            temp["popup_url"] = popup_url
        new_form.append(temp)

    return {"form": new_form}
```

###### 分析
1. 只有带有下拉框的`ModelChoiceField(ForeignKey)`和`ModelMultiChoiceField(M2M)`才能添加popup功能
2. 每一个下拉框的popup按钮的超链接都需要有一个可以用来与其他下拉框区分的表示，这个表示就是`_popbackid`


###### popup工作原理及流程
1. 在页面"A"上单选框旁边创建一个按钮，绑定一个`click`事件，该事件的回调函数中
	- 回掉函数的参数打开页面的链接
	- 内部调用`window.open()`函数，打开一个页面
	- **注意，对于window.open()函数，其第二个参数是最好根url相同，这样就可以保证每一个popup按钮在点击的时候都会打开一个新的窗口，如果写死了，那么点击多个按钮时只能同时存在一个popup窗口**

```html
<form method="post" novalidate class="add_form">
    {% csrf_token %}
 {% for item in form %}
            <div class="col-sm-8">
                <div class="form-group per-item">
                    <label for="inputEmail3" class="col-sm-2 control-label">{{ item.bound_field.label }}</label>
                    <div class="col-sm-10 select_par">
                        {{ item.bound_field }}
                         {% if item.is_popup %}
                    <!-- popup中的a标签不要写href -->
                            <a onclick="popUp('{{ item.popup_url }}')" class="popup_link"><span class="glyphicon glyphicon-plus"
                                                                     aria-hidden="true"></span></a>
                    {% endif %}
                    <div class="err_msg">{{ item.bound_field.errors.0 }}</div>
                    </div>
                </div>


            </div>
    {% endfor %}
    <div class="col-sm-8 col-sm-offset-7"><p><input class="btn btn-primary" type="submit"></p></div>
</form>

<script>
    function popupCallback(response_data) {
        var ele_option = document.createElement('option');
        ele_option.id = response_data.id;
        ele_option.text = response_data.text;
        ele_option.setAttribute('selected', 'selected');

        var select = document.getElementById(response_data._popbackid);
        select.appendChild(ele_option)
    }
    function popUp(url) {
        var popupPage = window.open(url, url, "status=1, height:500, width:600, toolbar=0, resizeable=0");
    }
</script>
```

2. 比如打开的是添加页面的url，那么就会出来一个包含表单的页面，当添加完数据并提交之后，会进入`add_view`视图函数，在该视图函数中判断是否是popup标签页面提交的请求
	- 如果是，则返回`popback.html`，这个页面在打开时，会调用其内的一个`自执行函数`


```python
    def add_view(self, request):
        """ 添加记录路径对应的视图函数
        Args:
            request: 当前请求对象
        Return:
            HttpResponse: 包含响应结果的响应对象。如果是GET请求，返回页面，如果是POST请求，将重定向至列表页面
        """

        model_form_class = self.get_model_form_class()

        if request.method == 'GET':
            return render(request, 'curd/add.html', {"form":model_form_class()})
        else:
            form = model_form_class(data=request.POST)
            if form.is_valid():
                obj = form.save()
                _popbackid = request.GET.get('_popbackid')			# popup功能
                if _popbackid:
                    response_data = {
                        "id": obj.pk,
                        "text": str(obj),
                        "_popbackid": _popbackid
                    }
                    return render(request, "curd/popback.html", {"response_data": response_data})
                else:
                    return redirect(to=self.get_show_url())
            else:
                return render(request, 'curd/add.html', {"form": form})
```


```html
<script>
    (function () {
        var response_data = {{ response_data|safe }}
        opener.popupCallback(response_data);
        window.close();
    })()
</script>
```

3. 自执行函数会使用`opener`调用页面"A"中定义的的`popupCallback`方法，在该方法内部会将新添加的记录对象渲染到单选框/多选框中

```html
    function popupCallback(response_data) {
        var ele_option = document.createElement('option');
        ele_option.id = response_data.id;
        ele_option.text = response_data.text;
        ele_option.setAttribute('selected', 'selected');

        var select = document.getElementById(response_data._popbackid);
        select.appendChild(ele_option)
    }
```


#### 配置组合搜索
- 组合搜索利用记录对象的关联字段来实现筛选数据，如果你相对记录对象的普通字段进行搜索，可以配置`search_list`选项
- 配置组合搜索的配置项
	1. 在派生类中覆盖基类的`combain_search_field_list`
	2. 在`combain_search_field_list`中传入要配置的字段对应的`SearchOption`对象，该对象有6个参数
		- `field`要配置的关联字段，比如性别、部门等
		- `is_multi=False`是否是多选，如果该关联字段与当前记录之间是多对多的关系，那么就需要设置为True
		- `condition=None`用来约束每一个关联字段对应的选项。比如可以限制性别筛选行中，只有male选项，或者设置部门筛选行中只有公司主要几个部门
		- `is_choices=False`如果关联字段使用的是choices实现的关联关系，该选项就应该设置为True
		- 当关联字段比如`foreign key`关联的不是关联表的主键id而是其他字段，并且不是通过choices建立关联关系时，我们就需要使用下面两个参数来指定关联字段，并且定制表格
			- `text_func_name=None`
			- `val_func_name=None`
	3. 设置在页面显示组合搜索`show_combain_search=True`



```python
# models.py

class Department(models.Model):
    """ 部门表 """

    title = models.CharField(verbose_name='部门名称', max_length=16)
    numbering = models.IntegerField(verbose_name='部门编号', unique=True, null=False)

    def __str__(self):
        return self.title


class User(models.Model):
    """ 员工信息表 """
    name = models.CharField(verbose_name='员工姓名', max_length=16)
    login_name = models.CharField(verbose_name='用户名', max_length=32)
    login_password = models.CharField(verbose_name='密码', max_length=64)
    email = models.EmailField(verbose_name='邮箱', max_length=64)

    department = models.ForeignKey(verbose_name='部门', to="Department", to_field="numbering", on_delete=models.CASCADE)
```

```python
# curd.py

class UserConfig(CURDConfig):
    list_display = ['name', 'login_name', 'login_password', 'email', 'department']
    combain_search_field_list = [
        SearchOption(
            field_name='department',
            text_func_name=lambda x: str(x),
            val_func_name=lambda x: x.numbering  # 自定义的主键
        )
    ]
    edit_link = ['name']
    show_search_form = True
    search_list = ['name__contains', 'login_name__contains']
```



###### 组合搜索运行流程
1. 用户在派生配置类中指定`combain_search_field_list`，该列表中存放的是一个个`SearchOption`搜索选项对象，这些搜索选项对象内部封装了查询的条件及所代表的字段

2. 渲染页面时，调用的是`ShowView`类实例对象的`template_combain_search_field_list`方法，该方法内部返回的SearchRow可迭代对象包含了**一行搜索条件**

```python
# /curd/service/views.py

class ShowView(object):
    def template_combain_search_field_list(self):
        """ 生成器函数。渲染列表页面的组合搜索
        Return:
            返回一个可迭代的search_row对象。search_row对象内部实现了 "__iter__" 方法，
            遍历该对象时，返回的将是该对象data属性中存放的一个个记录对象对应搜索选项的超链接。
        """

        from django.db.models import ForeignKey, ManyToManyField

        for search_option_obj in self.combain_search_field_list:
            field = self.model_class._meta.get_field(search_option_obj.field_name)
            if isinstance(field, ForeignKey):               # 外键字段
                row = SearchRow(
                    option_obj=search_option_obj,
                    request=self.request,
                    data=search_option_obj.get_queryset(field)
                )
            elif isinstance(field, ManyToManyField):        # 多对多字段
                row = SearchRow(
                    option_obj=search_option_obj,
                    request=self.request,
                    data=search_option_obj.get_queryset(field)
                )
            else:                                           # choices字段
                row = SearchRow(
                    option_obj=search_option_obj,
                    request=self.request,
                    data=search_option_obj.get_choices(field)
                )
            yield row
```

3. 渲染页面时会遍历该生成器函数返回的生成器对象，并对结果row对象进行遍历，产生一个个搜索选项
	- 关于搜索选项以及其URL的生成等复杂逻辑会在介绍`SearchRow`类的介绍中详细解释

4. 当用户点击列表页面上的一个搜索选项的时候，实际上会发送一个GET请求给`show_view`视图函数，视图函数内部会通过GET请求url中的搜索信息。此时show_view中会有以下几个逻辑步骤
	1. 初始化一个字典condition，这个condition中将数据库查询使用到的键值对
	2. 遍历URL中的搜索条件的key
		- 如果该key代表的搜索选项在用户的搜索选项权限列表`combain_search_field_list`内，就将该key以及对应的value保存到condition字典中
		- 如果该key不存在于`combain_search_field_list`中，说明这个是前端伪造的搜索条件，我们只要不将这个key及其对应的value添加进`condition`字典中即可
	3. 组装好字典之后，只需要在从数据库获取记录对象的QuerySet对象后面添加上`fielter(condition)`就可以按照组合搜索条件对结果集进行进一步的过滤

```python
        combain_condition = {}
        option_list = self.get_combain_search_field_list()
        for key in request.GET.keys():
            value_list = request.GET.getlist(key)
            flag = False
            for option in option_list:
                if option.field_name == key:
                    flag = True
                    break
            if flag:
                combain_condition['%s__in' % key] = value_list
                
        objects = self.model_class.objects.filter(self.create_search_condition()).filter(**combain_condition)
```

#### 配置url
###### 扩展路由映射
- `CURDConfig`提供了一个用来扩展路由的钩子函数`extra_url`。
- 如果我们要扩展路由映射，一个完整的步骤应该这样
	1. 派生类中，使用钩子函数`extra_url`创建一个存放路由映射关系的列表，并作为返回值返回。
	2. 定义路由关系中的视图函数
	3. 定义该路径的反向解析函数，这样在调用该链接的时候，直接调用该方法就可以生成对应该视图函数的完整url(注意命名空间)

```python
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
    
```

#### 扩展功能

