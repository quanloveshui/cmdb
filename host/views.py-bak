#encoding: utf-8

from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import Host






@login_required
def index(request):
    return render(request, 'host/index.html', {'objects' : Host.objects.all()})


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

#展示每个主机详细信息
@login_required
def detalinfo(request,id):
    #pk = request.GET.get("id", 0)
    data=Host.objects.get(id=str(id))
    return render(request, 'host/info.html',{'data' : data})

#编辑主机信息
@login_required
def edit(request,id):
    #pk = request.GET.get("id", 0)
    data=Host.objects.get(id=str(id))
    return render(request, 'host/edit.html',{'data' : data})

