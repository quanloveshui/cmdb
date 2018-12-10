from django.contrib import admin

# Register your models here.

from host.models import Host


class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name', 'ip','os') #列出显示的字段
    list_filter = ['ip'] #添加过滤器
    list_per_page = 15
    search_fields = ('name','ip')#添加搜索
    

admin.site.register(Host,AuthorAdmin)
