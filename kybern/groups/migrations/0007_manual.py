# Generated by Django 3.0.7 on 2020-10-13 22:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('conditionals', '0007_auto_20201009_1809'),
        ('groups', '0006_auto_20201013_2227'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='governor_condition',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='groups_group_governor_conditioned', to='conditionals.ConditionManager'),
        ),
        migrations.AddField(
            model_name='group',
            name='owner_condition',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='groups_group_owner_conditioned', to='conditionals.ConditionManager'),
        ),
    ]
