from django.apps import AppConfig


class GroupsConfig(AppConfig):
    name = 'groups'
    verbose_name = 'Groups'

    def get_state_changes_module(cls):
        import importlib
        return importlib.import_module("groups.state_changes")
