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
        (1, 'male'),
        (2, 'female'),
    ]

    gender = models.IntegerField(choices=choices_list, verbose_name='性别')

    def __str__(self):
        return self.author_name

    class Meta:
        verbose_name_plural = '作者表'
