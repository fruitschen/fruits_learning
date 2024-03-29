# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-18 16:10


from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32)),
                ('slug', models.SlugField(unique=True)),
                ('main', models.BooleanField(default=False, verbose_name='\u662f\u5426\u4e3b\u8d26\u6237')),
                ('public', models.BooleanField(default=False, verbose_name='\u662f\u5426\u516c\u5f00')),
                ('display_summary', models.BooleanField(default=False, verbose_name='\u662f\u5426\u9ed8\u8ba4\u663e\u793a\u6982\u89c8')),
                ('initial_investment', models.DecimalField(blank=True, decimal_places=2, max_digits=14, null=True, verbose_name='\u521d\u59cb\u6295\u8d44')),
                ('initial_date', models.DateField(verbose_name='\u521d\u59cb\u6295\u8d44\u65f6\u95f4')),
                ('debt', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='\u8d1f\u503a')),
            ],
        ),
        migrations.CreateModel(
            name='AccountStock',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.IntegerField()),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stocks', to='stocks.Account')),
            ],
        ),
        migrations.CreateModel(
            name='PairTransaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sold_price', models.DecimalField(decimal_places=4, max_digits=10, verbose_name='\u5356\u51fa\u4ef7\u683c')),
                ('sold_amount', models.IntegerField(verbose_name='\u5356\u51fa\u6570\u91cf')),
                ('bought_price', models.DecimalField(decimal_places=4, max_digits=10, verbose_name='\u4e70\u5165\u4ef7\u683c')),
                ('bought_amount', models.IntegerField(verbose_name='\u4e70\u5165\u6570\u91cf')),
                ('started', models.DateTimeField(blank=True, null=True, verbose_name='\u4ea4\u6613\u65f6\u95f4')),
                ('finished', models.DateTimeField(blank=True, null=True, verbose_name='\u7ed3\u675f\u4ea4\u6613\u65f6\u95f4')),
                ('sold_bought_back_price', models.DecimalField(blank=True, decimal_places=4, max_digits=10, null=True, verbose_name='\u5356\u51fa\u540e\u4e70\u5165\u4ef7\u683c')),
                ('bought_sold_price', models.DecimalField(blank=True, decimal_places=4, max_digits=10, null=True, verbose_name='\u4e70\u5165\u540e\u5356\u51fa\u4ef7\u683c')),
                ('profit', models.DecimalField(blank=True, decimal_places=4, max_digits=10, null=True, verbose_name='\u5229\u6da6')),
                ('order', models.IntegerField(default=100)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='pair_transactions', to='stocks.Account')),
            ],
            options={
                'ordering': ['order', 'finished', '-started'],
            },
        ),
        migrations.CreateModel(
            name='Stock',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=6)),
                ('market', models.CharField(max_length=2)),
                ('name', models.CharField(max_length=10)),
                ('is_stock', models.BooleanField(default=True)),
                ('price', models.DecimalField(blank=True, decimal_places=3, max_digits=10, null=True)),
                ('price_updated', models.DateTimeField(blank=True, null=True)),
                ('star', models.BooleanField(default=False)),
                ('archive', models.BooleanField(default=False)),
                ('archived_reason', models.CharField(blank=True, default=b'', max_length=256)),
                ('comment', models.TextField(blank=True)),
            ],
            options={
                'ordering': ['-star'],
            },
        ),
        migrations.CreateModel(
            name='StockPair',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default=b'', max_length=256)),
                ('star', models.BooleanField(default=False)),
                ('current_value', models.DecimalField(blank=True, decimal_places=4, max_digits=10, null=True)),
                ('value_updated', models.DateTimeField(blank=True, null=True)),
                ('order', models.IntegerField(default=100)),
                ('started_stock', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pairs', to='stocks.Stock')),
                ('target_stock', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='targeted_pairs', to='stocks.Stock')),
            ],
            options={
                'ordering': ['star', 'order'],
            },
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bought_price', models.DecimalField(blank=True, decimal_places=4, max_digits=10, null=True, verbose_name='\u4e70\u5165\u4ef7\u683c')),
                ('bought_amount', models.IntegerField(verbose_name='\u4e70\u5165\u6570\u91cf')),
                ('started', models.DateTimeField(blank=True, null=True, verbose_name='\u4ea4\u6613\u65f6\u95f4')),
                ('finished', models.DateTimeField(blank=True, null=True, verbose_name='\u7ed3\u675f\u4ea4\u6613\u65f6\u95f4')),
                ('sold_price', models.DecimalField(blank=True, decimal_places=4, max_digits=10, null=True, verbose_name='\u5356\u51fa\u4ef7\u683c')),
                ('profit', models.DecimalField(blank=True, decimal_places=4, max_digits=10, null=True, verbose_name='\u5229\u6da6')),
                ('interest_rate', models.DecimalField(decimal_places=4, default=b'0.0835', max_digits=6, verbose_name='\u5229\u7387\u6210\u672c')),
                ('account', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='transactions', to='stocks.Account')),
                ('bought_stock', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='stocks.Stock', verbose_name='\u4e70\u5165\u80a1\u7968')),
            ],
        ),
        migrations.AddField(
            model_name='stock',
            name='pair_stocks',
            field=models.ManyToManyField(blank=True, through='stocks.StockPair', to='stocks.Stock'),
        ),
        migrations.AddField(
            model_name='pairtransaction',
            name='bought_stock',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bought_pair_transactions', to='stocks.Stock', verbose_name='\u4e70\u5165\u80a1\u7968'),
        ),
        migrations.AddField(
            model_name='pairtransaction',
            name='pair',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='stocks.StockPair'),
        ),
        migrations.AddField(
            model_name='pairtransaction',
            name='sold_stock',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sold_pair_transactions', to='stocks.Stock', verbose_name='\u5356\u51fa\u80a1\u7968'),
        ),
        migrations.AddField(
            model_name='accountstock',
            name='stock',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stocks.Stock'),
        ),
    ]
