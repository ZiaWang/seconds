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
