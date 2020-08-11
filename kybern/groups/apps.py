import importlib

from django.apps import AppConfig


class GroupsConfig(AppConfig):
    name = 'groups'
    verbose_name = 'Groups'

    def get_concord_module(self, module_name):
        """Helper method to let utils easily access specific files."""
        return importlib.import_module("groups." + module_name)
