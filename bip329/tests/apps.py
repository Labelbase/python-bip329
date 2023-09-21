# -*- coding: utf-8 -*-
from django.apps import AppConfig
from django.apps import apps as django_apps
from django.db.models.signals import post_delete



import logging
logger = logging.getLogger('cura')

class LSVConfig(AppConfig):
    name = 'cura.lsv'
    verbose_name = "LSVConfig"
    def ready(self):
        pass 
        # NOTE: Register targeting models is done in contacts module
        #from targeting.engine import register
        #register(django_apps.get_model('lsv', 'LSVTransfer'))

        # NOTE: Signals / Receivers are registered in contacts module
