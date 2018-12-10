#encoding: utf-8

from host.models import Host
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    def handle(self, *args, **options):
        a='11'

    arch = "x86_64"
    mem = "100"
    cpu = "24"
    os = "Centos"
    ip = "127.0.0.1"
    p_ip="127.0.0.1"
    name = "test"
    Host.create_or_replace(name, ip, arch, os, mem, cpu,p_ip)
