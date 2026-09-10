from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [("hotels", "0064_roomtype_area_m2_roomtype_bed_type_and_more")]
    operations = [
        migrations.AddField(model_name="booking", name="guest_checkout_email_sent_at", field=models.DateTimeField(blank=True, null=True)),
        migrations.AddField(model_name="booking", name="guest_failure_email_sent_at", field=models.DateTimeField(blank=True, null=True)),
    ]
