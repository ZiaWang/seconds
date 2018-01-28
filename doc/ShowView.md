# ShowView类

## 代码

```python
class ShowView(object):
    """ 列表页面功能类

    """
    def __init__(self, config_obj, queryset):
        self.queryset = queryset
        self.config_obj = config_obj
        self.request = config_obj.request
        self.model_class = self.config_obj.model_class

        # 用于标注
        self.list_display = self.config_obj.get_list_display()
        self.show_add_btn = self.config_obj.get_add_url()
        self.search_list = self.config_obj.get_search_list()
        self.show_search_form = self.config_obj.get_show_search_form()
        self.action_list = self.config_obj.get_action_list()
        self.show_action_form = self.config_obj.get_show_action_form()
        self.combain_search_field_list = self.config_obj.get_combain_search_field_list()

        from curd.service.pagintator import Paingator

        page_obj = Paingator(
            base_url=self.request.path_info,
            obj_count=queryset.count(),     # 所有记录的总个数
            params=self.request.GET,
            per_page_count=2,
            init_page_count=3,
            request=self.request
        )
        self.page_obj = page_obj
        self.page_data_list = queryset[page_obj.start:page_obj.end]     # 用于生成指定页码对应页面记录

    def th_list(self):
        """ 用于列表页面生成表头数据
        Return:
            返回值为包含表头数据的列表
        """

        if self.list_display:
            head_list = []
            for field in self.list_display:
                if isinstance(field, str):
                    verbose_name = self.config_obj.model_class._meta.get_field(field).verbose_name
                else:
                    verbose_name = field( self.config_obj, is_header=True)
                head_list.append(verbose_name)
        else:
            head_list = [self.config_obj.model_class._meta.verbose_name_plural]
        return head_list

    def td_list(self):
        """ 用于生成表格数据
        Return:
            返回一个包含了单元格数据的生成器
        """

        def generator_tr(objects):
            def generator_td(obj):
                if self.config_obj.get_list_display():
                    for field in self.list_display:
                        if isinstance(field, str):
                            val = getattr(obj, field)
                        else:
                            val = field(self.config_obj, obj, is_header=False)
                        yield val
                else:
                    yield from self.config_obj.model_class.objects.all()
            yield from [generator_td(obj) for obj in objects]
        return generator_tr(self.page_data_list)

    def template_modify_action_list(self):
        """ 为批量操作的actions下拉框提供渲染时使用的数据
        Return:
            返回存放了action批量操作的函数的函数名以及该函数的func_description属性组成的俩表
        """

        result = []
        for func in self.action_list:
            temp = {
                'func_description': func.func_description,
                'func_name': func.__name__
            }
            result.append(temp)
        return result

    def add_url(self):
        """ 获取添加功能对应的url路径

        """

        return self.config_obj.get_add_url()

    def template_combain_search_field_list(self):
        """  一个生成器函数，用于渲染组合搜索条件以及每一个条件对应的选项
        Return:
            返回值为包含每一行搜索条件选项的SearchRow对象
        """

        from django.db.models import ForeignKey, ManyToManyField
        for search_option_obj in self.combain_search_field_list:
            field = self.model_class._meta.get_field(search_option_obj.field_name)
            if isinstance(field, ForeignKey):
                row = SearchRow(
                    option_obj=search_option_obj,
                    request=self.request,
                    data=search_option_obj.get_queryset(field)
                )
            elif isinstance(field, ManyToManyField):
                row = SearchRow(
                    option_obj=search_option_obj,
                    request=self.request,
                    data=search_option_obj.get_queryset(field)
                )
            else:
                row = SearchRow(
                    option_obj=search_option_obj,
                    request=self.request,
                    data=search_option_obj.get_choices(field)
                )
            yield row
```



## 功能
- `ShowView`是列表页面的功能类，用来渲染列表页面的各种功能

#### 渲染表格
- 这个功能会**利用用户在CURDConfig派生类中指定在`list_display`中的字段或者函数配合数据库数据生成一张数据信息表**

###### 生成表头
- ``


#### 分页

#### 渲染组合搜索
###### 1. 组合搜索保存页面搜索条件原理
- 前提条件：
	- 使用GET请求发送包含搜索条件的URL
	- 搜索条件附在在URL路径的键值对字符串中

- 原理阐述：
	- 每次搜索页面的请求发送给视图函数时，视图函数会获取URL之后的键值对，并**使用深拷贝复制一份QueryDict对象（记得设置_mutable=True），当生成每一个组合搜索的查询选项时，会在这个QueryDict对象中添加上选项对应的键值对，并将该键值对使用QueryDict的`urlencode()`方法组装到URL路径上，每一次点击一个选项，都会刷新一次列表页面，并将当前的查询条件与每一个选项组合附再选项的URL后面**
	- 组合搜索一般放在列表页面，假设现在点击列表页面的添加按钮，会跳转到添加页面，用来添加一条记录，如果想要在创建完记录并保存时，跳转回列表页面并附带搜索条件，现在有两种方案
		1. 进入添加页面之前获取列表页面URL的条件，并将该条件添加到`add`按钮`url`上，当`添加页面`提交数据时，`form`表单的`action`指定的url地址中传入列表页面在`add`按钮上传递的条件，这样实现返回列表页面时保存搜索条件
			- 缺点: **添加页面如果也存在搜索条件的话，会产生冲突，比如当列表页面和添加页面都有分页共呢个时，`?page=1`将会出现冲突**
		2. 针对上面缺点，**参考Django admin的源码发现，Django中在进入`add`页面时，会将列表页面的搜索条件打包成一个`QueryDict`，并将该QueryDict调用自身`urlencode()`方法的value作为值传递给一个新的QueryDict上，然后将新的QueryDict`urlencode()`的返回值负载`URL`上**，当添加页面提交数据时，从GET请求的URL之中获取作为`value`打包到url之后的QueryDict，拼接URL，再重定向至列表页面

```python	

```


- 为什么生成每一个选项的超链接都是用深拷贝得到的QueryDict？
	- 因为在每一次生成URL的时候，都会对QueryDict进行插入新值的操作（插入当前选项对应的键值对），**如果是浅拷贝，那么会破坏原有的搜索条件**

###### 2. 组合搜索配置流程

###### 3. 组合搜索功能实现流程


#### 渲染action批量操作

## 细节解释

# SearchOption类

## 代码

```python
```

## 功能
#### 配置组合搜索选项


#### 获取选项的列表(两种)

## 细节解释


# SearchRow类
## 代码

```python
```

## 功能
#### 生成搜索url



## 细节解释