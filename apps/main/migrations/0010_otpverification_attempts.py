from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0009_alter_restaurant_budget_friendly'),
    ]

    operations = [
        migrations.AddField(
            model_name='otpverification',
            name='attempts',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='Failed Attempts'),
        ),
    ]
