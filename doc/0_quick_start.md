# 开始

## 0. 准备工作
- 在trial应用中我们先准备三张表，用来测试。
	- 建立完表之后请自行迁移并插入数据

```
from django.db import models


class Book(models.Model):
    """ 图书表
    普通字段:
        name, price
    关联字段:
        authors: ManyToManyField(to='Author')
        publish: ForeignKey(to='Publish')
    """

    book_name = models.CharField(max_length=32, verbose_name='书名')
    price = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='图书价格')

    authors = models.ManyToManyField(to='Author', verbose_name='作者')
    publish = models.ForeignKey(to='Publish', to_field='id', on_delete=True, verbose_name='出版社')

    def __str__(self):
        return self.book_name

    class Meta:
        verbose_name_plural = '图书表'


class Publish(models.Model):
    """ 出版社表
    普通字段:
        publish_name, city, email
    """

    publish_name = models.CharField(max_length=32, verbose_name='出版社名称')
    city = models.CharField(max_length=32, verbose_name='所在城市')
    email = models.EmailField(verbose_name='联系邮箱')

    def __str__(self):
        return self.publish_name

    class Meta:
        verbose_name_plural = '出版社表'


class Author(models.Model):
    """ 作者表
    普通字段:
        author_name, age, choices_list, gender
    """

    author_name = models.CharField(max_length=32, verbose_name='作者名称')
    age = models.IntegerField(verbose_name='年龄')
    choices_list = [
        ('male', 'male'),
        ('female', 'female'),
    ]

    gender = models.CharField(choices=choices_list, verbose_name='性别', max_length=32)

    def __str__(self):
        return self.author_name

    class Meta:
        verbose_name_plural = '作者表'

```

## 1. 制作项目启动文件
- 要想让curd组件在你的项目运行时同时开启，你需要先做下面两个步骤
	1. 在`settings.py`中注册curd
	2. 在其他应用下建立一个`curd.py`
	3. 在其他应用`apps.py`文件下定义`autodiscover_modules`

- 我们在项目的`trial`试用应用下的`apps.py`文件中这样做
	1. 导入`autodiscover_modules`。
	2. 在`ready`函数中调用`autodiscover_modules`
		- 这个函数会在项目启动的时候，自动的在每一个已经注册的应用下寻找`curd.py`模块并加载到内存

```python
from django.apps import AppConfig
from django.utils.module_loading import autodiscover_modules


class TrialConfig(AppConfig):
    name = 'trial'

    def ready(self):
        """ 项目启动时，自动加载已注册所有应用中的curd.py文件

        """
        autodiscover_modules('curd')
```

- 在`curd.py`文件中加上这句代码

```
print("start curd ！") 
```

- 你会发现在项目启动的时候，这句代码会被执行，并且执行两次(在执行数据库迁移的时候，也会被执行一次)

```
start curd !
start curd !
Performing system checks...

System check identified no issues (0 silenced).

You have 14 unapplied migration(s). Your project may not work properly until you apply the migrations for app(s): admin, auth, contenttypes, sessions.
Run 'python manage.py migrate' to apply them.
December 14, 2016 - 14:52:29
Django version 2.0, using settings 'seconds.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```
