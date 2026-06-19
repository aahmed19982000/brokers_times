from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0005_alter_category_id_alter_depositlimit_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='headquarters',
            name='country_code',
            field=models.CharField(blank=True, help_text='ISO 2-letter country code (e.g. gb, us, cy)', max_length=2),
        ),
    ]
