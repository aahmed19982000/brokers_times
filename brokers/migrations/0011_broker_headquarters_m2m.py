from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('brokers', '0010_alter_broker_id_alter_brokeraccounttype_id_and_more'),
        ('categories', '0006_headquarters_country_code'),
    ]

    operations = [
        # Step 1: Add new M2M field with a temp name
        migrations.AddField(
            model_name='broker',
            name='headquarters_new',
            field=models.ManyToManyField(blank=True, related_name='brokers_m2m', to='categories.headquarters'),
        ),
        # Step 2: Copy existing FK data to M2M
        migrations.RunSQL(
            sql="""
                INSERT INTO brokers_broker_headquarters_new (broker_id, headquarters_id)
                SELECT id, headquarters_id FROM brokers_broker WHERE headquarters_id IS NOT NULL;
            """,
            reverse_sql="DELETE FROM brokers_broker_headquarters_new;",
        ),
        # Step 3: Remove old FK field
        migrations.RemoveField(
            model_name='broker',
            name='headquarters',
        ),
        # Step 4: Rename new field to headquarters
        migrations.RenameField(
            model_name='broker',
            old_name='headquarters_new',
            new_name='headquarters',
        ),
        # Step 5: Fix related_name
        migrations.AlterField(
            model_name='broker',
            name='headquarters',
            field=models.ManyToManyField(blank=True, related_name='brokers', to='categories.headquarters'),
        ),
    ]
