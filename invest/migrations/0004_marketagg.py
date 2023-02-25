# Generated by Django 4.1 on 2023-02-22 23:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('invest', '0003_alter_asset_options_alter_wallet_options_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='MarketAgg',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('market', models.CharField(max_length=50, verbose_name='Mercado')),
                ('cost', models.FloatField(verbose_name='Custo')),
                ('value', models.FloatField(verbose_name='Valor')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('wallet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='invest.wallet')),
            ],
        ),
    ]