# 列表页面功能实现

- 在`CURDConfig`类中，定义了`/curd/app_name/model_name/`对应的视图函数`show()`，整个函数虽然看起来只有三行，但是最终渲染成页面可不止这几行代码

#### 1. 自定义 inclusion tag
- `show`视图函数中的代码基本全部放在了自定义的inlcusion标签函数中，在这个函数内大量使用到了生成器。
	1. curd应用下创建`templatetags`目录，在该目录下创建`curd_list.py`文件，文件中我们来创建一个名为`list_table`的自定义标签函数
		- 具体注意事项这里不再详细说明，想要了解更详细可以看我在web开发目录django那一节中的介绍
	2. 我们需要为传递给后端的数据设计一个方便功能实现的结构，设计的结构如下，**在函数中我把他转换成了一个装饰器，这样可以节省内存。因为要处理的数据量大小个数是不确定的，如果数据两非常庞大，直接生成该结构会浪费较多的内存，使用生成器可以完美解决这个问题。**

- 结构

```
[
	[field1, field2, field3]，
	[field1, field2, field3]
]
```


- 代码实现 


```python
from django.template import Library
from django.utils.safestring import mark_safe

register = Library()


@register.inclusion_tag(filename='curd/includes/show_table.html')
def list_table(config_obj, objects):
    """ 渲染并生成列表页面标签
    Args:
        config_obj: CURBConfig对象
        objects: QuerySet对象
    Return:
        返回一个上下文对象，用来渲染指定模板
    """

    def generator_tr(objects):
        def generator_td(object):
            if config_obj.list_display:
                for field in config_obj.list_display:
                    if isinstance(field, str):
                        val = getattr(object, field)
                    else:
                        val = field(config_obj, object)
                    yield val
            else:
                yield from config_obj.model_class.objects.all()
        yield from [generator_td(object) for object in objects]
        '''
        [
            [name, age, gender],
            [name, age, gender]
        ]
        '''
    if config_obj.list_display:
        head_list = []
        for field in config_obj.list_display:
            if isinstance(field, str):
                verbose_name = config_obj.model_class._meta.get_field(field).verbose_name
            else:
                verbose_name = field(config_obj, is_header=True)
            head_list.append(verbose_name)
    else:
        head_list = [config_obj.model_class._meta.verbose_name_plural]

    return {"data": generator_tr(objects), "head_list": head_list}

```

###### 简单解释
1. 关于`list_display`中的`field`
	- 在`curd.py`中`CURDConfig`派生的配置类中，我们可以往`list_display`列表中传入函数名，在遍历`list_display`的时候调用函数，获取其返回值

```python
from curd.service import sites
from django.utils.safestring import mark_safe

from trial import models


class AuthorConfig(sites.CURDConfig):
    def edit(self, obj, is_header=False):
        if is_header:
            return '编辑'
        return mark_safe('<a href="/%s/change/">编辑</a>'%obj.id)

    list_display = ['author_name', 'age', 'gender']



sites.site.register(models.Publish)
sites.site.register(models.Author, AuthorConfig)
sites.site.register(models.Book)

```