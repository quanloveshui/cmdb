# -*- coding: utf-8 -*-
__author__ = 'young'

#核心类
from collections import namedtuple
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.inventory.manager import InventoryManager
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.plugins.callback import CallbackBase
from django.core.management.base import BaseCommand
import ansible.constants as C
import json
import os
from collections import namedtuple
import shutil

from host.models import Host
from django.conf import settings

class ModelResultsCollector(CallbackBase):
    """
    重写callbackBase类的部分方法
    """
    def __init__(self, *args, **kwargs):
        super(ModelResultsCollector, self).__init__(*args, **kwargs)
        self.host_ok = {}
        self.host_unreachable = {}
        self.host_failed = {}
        self.host_fact ={}
    def v2_runner_on_unreachable(self, result):
        self.host_unreachable[result._host.get_name()] = result
    def v2_runner_on_ok(self, result):
        self.host_ok[result._host.get_name()] = result
    def v2_runner_on_failed(self, result,ignore_errors=False):
        self.host_failed[result._host.get_name()] = result


class Command(BaseCommand):
    def handle(self, *args, **options):
        Options = namedtuple('Options', 
                 ['connection', 'module_path', 'forks', 'become', 'become_user', 'become_method', 'check', 'diff'])
        options = Options(connection='smart', 
                  module_path=[], forks=10, become=None, become_user=None,  become_method=None, check=False, diff=False)

        result_callback = ModelResultsCollector()

        loader = DataLoader()
        inventory = InventoryManager(loader=loader, sources=["etc/hosts/"])
        variable_manager = VariableManager(loader=loader, inventory=inventory)
        passwords = {}

        play_source = {
            'name' : 'fact',
            'hosts' : 'all',
            'gather_facts' : 'no',
            'tasks' : [
                {
                    'name' : 'fact',
                    'setup' : ''
                }
            ],
        }

        play = Play().load(play_source, variable_manager=variable_manager, loader=loader)

        tqm = None
        try:
            tqm = TaskQueueManager(
                    inventory=inventory,
                    variable_manager=variable_manager,
                    loader=loader,
                    options=options,
                    passwords=passwords,
                    stdout_callback=result_callback,
                )
            result = tqm.run(play)
            result_raw = {'success':{},'failed':{},'unreachable':{}}
            for host,result in result_callback.host_ok.items():
                result_raw['success'][host] = result._result
            for host,result in result_callback.host_failed.items():
                result_raw['failed'][host] = result._result
            for host,result in result_callback.host_unreachable.items():
                result_raw['unreachable'][host] = result._result
        

            #js = json.dumps(result_raw, sort_keys=False, indent=4)
            sucess = list(result_raw['success'].keys())
            for i in sucess:
                dic=result_raw['success'][i]["ansible_facts"]
                arch=dic.get('ansible_architecture','')
                mem=dic.get('ansible_memtotal_mb',0)
                cpu=dic.get('ansible_processor_vcpus',0)
                os=dic.get('ansible_os_family','')
                ip=dic.get('ansible_default_ipv4',{}).get('address', '')
                p_ip=i              #公网IP
                name=dic.get('ansible_nodename',i)
                Host.create_or_replace(name, ip, arch, os, mem, cpu,p_ip)
           

            fail = list(result_raw['failed'].keys())
            for i in fail:
                arch=''
                mem=0
                cpu=0
                os=''
                ip=i
                p_ip=i
                name=''
                Host.create_or_replace(name, ip, arch, os, mem, cpu,p_ip) 


            unreachable = list(result_raw['unreachable'].keys())
            for i in unreachable:
                arch=''
                mem=0
                cpu=0
                os=''
                ip=i
                p_ip=i
                name=''
                Host.create_or_replace(name, ip, arch, os, mem, cpu,p_ip)

        finally:
            if tqm:
                tqm.cleanup()
            shutil.rmtree(C.DEFAULT_LOCAL_TMP, True)
