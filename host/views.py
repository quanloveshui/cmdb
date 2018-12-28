#encoding: utf-8

from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

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

from django.conf import settings

from .models import Host



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



class AnsibleApi(object):
    def __init__(self):
        self.Options = namedtuple('Options',
                     ['connection',
                      'remote_user',
                      'ask_sudo_pass',
                      'verbosity',
                      'ack_pass',
                      'module_path',
                      'forks',
                      'become',
                      'become_method',
                      'become_user',
                      'check',
                      'listhosts',
                      'listtasks',
                      'listtags',
                      'syntax',
                      'sudo_user',
                      'sudo',
                      'diff'])
        self.options = self.Options(connection='smart',
                       remote_user=None,
                       ack_pass=None,
                       sudo_user=None,
                       forks=5,
                       sudo=None,
                       ask_sudo_pass=False,
                       verbosity=5,
                       module_path=None,
                       become=None,
                       become_method=None,
                       become_user=None,
                       check=False,
                       diff=False,
                       listhosts=None,
                       listtasks=None,
                       listtags=None,
                       syntax=None)

        self.loader = DataLoader()
        self.inventory = InventoryManager(loader=self.loader, sources=os.path.join(settings.BASE_DIR, 'etc', 'hosts'))
        self.variable_manager = VariableManager(loader=self.loader, inventory=self.inventory)
        self.callback = ModelResultsCollector()
        self.passwords = dict()
    
    def runansible(self,host_list):
        
        play_source = {
            'name' : 'fact',
            'hosts' : host_list,
            'gather_facts' : 'no',
            'tasks' : [
                {
                    'name' : 'fact',
                    'setup' : ''
                }
            ],
        }
    
        play = Play().load(play_source, variable_manager=self.variable_manager, loader=self.loader)    
        tqm = TaskQueueManager(
           inventory=self.inventory,
           variable_manager=self.variable_manager,
           loader=self.loader,
           options=self.options,
           passwords=self.passwords,
           stdout_callback=self.callback,
           )

        result = tqm.run(play)
        result = tqm.run(play)
        result_raw = {'success':{},'failed':{},'unreachable':{}}
        for host,result in self.callback.host_ok.items():
            result_raw['success'][host] = result._result
        for host,result in self.callback.host_failed.items():
            result_raw['failed'][host] = result._result
        for host,result in self.callback.host_unreachable.items():
            result_raw['unreachable'][host] = result._result

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
            os_v = dic.get('ansible_distribution_version','')
            Host.create_or_replace(name, ip, arch, os, mem, cpu,p_ip,os_v)
           

        fail = list(result_raw['failed'].keys())
        for i in fail:
            arch=''
            mem=0
            cpu=0
            os=''
            ip=i
            p_ip=i
            name=''
            os_v=''
            Host.create_or_replace(name, ip, arch, os, mem, cpu,p_ip,os_v) 


        unreachable = list(result_raw['unreachable'].keys())
        for i in unreachable:
            arch=''
            mem=0
            cpu=0
            os=''
            ip=i
            p_ip=i
            name=''
            os_v=''
            Host.create_or_replace(name, ip, arch, os, mem, cpu,p_ip,os_v)
            print(unreachable)



@login_required
def index(request):
    return render(request, 'host/index.html', {'objects' : Host.objects.all()})


@login_required
def homepage(request):
    service=Host.objects.all()
    redhat=Host.objects.filter(os='RedHat')
    centos=Host.objects.filter(os='CentOS')
    s_count=len(service)
    r_count=len(redhat)
    c_count=len(centos)
    data = {'s_count':s_count,'r_count':r_count,'c_count':c_count}
    return render(request, 'host/homepage.html',data)

@login_required
def delete(request):
    pk = request.GET.get("pk", 0)
    Host.objects.filter(pk=pk).delete()
    return redirect(reverse('host:index'))

#add主机信息页面
@login_required
def add(request):
    return render(request, 'host/add.html')

#添加信息后跳转到index页面
@login_required
def addresult(request):
    if request.POST:
        name = request.POST['name']
        mem = request.POST['mem']
        cpu = request.POST['cpu']
        os = request.POST['os']
        ip = request.POST['ip']
        p_ip = request.POST['p_ip']
        arch = request.POST['arch']
        os_v = request.POST['os_v']
    Host.create_or_replace(name, ip, arch, os, mem, cpu,p_ip,os_v)
    return redirect(reverse('host:index'))

#show每个主机详细信息
@login_required
def detalinfo(request,id):
    #pk = request.GET.get("id", 0)
    data=Host.objects.get(id=str(id))
    return render(request, 'host/info.html',{'data' : data})

#edit主机信息
@login_required
def edit(request,id):
    #pk = request.GET.get("id", 0)
    data=Host.objects.get(id=str(id))
    return render(request, 'host/edit.html',{'data' : data})



#update主机信息
@login_required
def update(request,id):
    data=Host.objects.get(id=str(id))
    ip=data.p_ip
    host_list=ip
    a = AnsibleApi()
    a.runansible(host_list)
    
    return redirect(reverse('host:index'))


#search主机信息
@login_required
def search(request):
    if request.GET:
        ip = request.GET['ip']
        data = Host.objects.filter(name__contains=ip)
        if data.count() == 0:
            data = Host.objects.filter(p_ip__contains=ip)
    return render(request, 'host/index.html', {'objects' : data})
