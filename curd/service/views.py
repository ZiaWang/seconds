class ShowView(object):
    """ 列表页面功能类

    """
    def __init__(self, config_obj, queryset):
        self.queryset = queryset
        self.config_obj = config_obj
        self.request = config_obj.request

        # 用于标注
        self.list_display = self.config_obj.get_list_display()
        self.show_add_btn = self.config_obj.get_add_url()
        self.search_list = self.config_obj.get_search_list()
        self.show_search_form = self.config_obj.get_show_search_form()
        self.action_list = self.config_obj.get_action_list()
        self.show_action_form = self.config_obj.get_show_action_form()

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
        return self.config_obj.get_add_url()
