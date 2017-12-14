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
