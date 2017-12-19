from django.template import Library
from curd.service.views import ShowView

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
    show_obj = ShowView(config_obj, objects)

    return {"data": show_obj.td_list(), "head_list": show_obj.th_list()}
