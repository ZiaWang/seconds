from django.apps import AppConfig
from django.utils.module_loading import autodiscover_modules


class TrialConfig(AppConfig):
    name = 'trial'

    def ready(self):
        """ 项目启动时，自动加载已注册所有应用中的curd.py文件

        """
        autodiscover_modules('curd')
