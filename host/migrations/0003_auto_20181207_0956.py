# Generated by Django 2.0.6 on 2018-12-07 01:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('host', '0002_host_p_ip'),
    ]

    operations = [
        migrations.AlterField(
            model_name='host',
            name='p_ip',
            field=models.GenericIPAddressField(verbose_name='p_IP地址'),
        ),
    ]