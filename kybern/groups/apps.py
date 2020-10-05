import importlib

from concord.actions.apps import ConcordAppConfig


class GroupsConfig(ConcordAppConfig):
    name = 'groups'
    verbose_name = 'Groups'

    def ready(self):
        from groups import signals
