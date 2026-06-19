from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('brokers', '0011_broker_headquarters_m2m'),
    ]

    operations = [
        migrations.AddField(
            model_name='broker',
            name='founded_year',
            field=models.PositiveIntegerField(blank=True, help_text='Year the broker was founded', null=True),
        ),
    ]
