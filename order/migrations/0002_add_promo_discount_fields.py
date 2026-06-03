from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='promo_code',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='discount_amount',
            field=models.FloatField(default=0),
        ),
    ]
