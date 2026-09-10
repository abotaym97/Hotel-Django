from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies=[('hotels','0065_guest_booking_email')]
    operations=[
        migrations.CreateModel(name='PaymentInspection',fields=[
            ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
            ('gateway_status',models.CharField(max_length=40,blank=True)),('matched',models.BooleanField(default=False)),
            ('http_status',models.PositiveIntegerField(null=True,blank=True)),('error_code',models.CharField(max_length=40,blank=True)),
            ('error_message',models.CharField(max_length=400,blank=True)),('checked_at',models.DateTimeField(auto_now=True)),
            ('payment',models.OneToOneField(to='hotels.payment',on_delete=django.db.models.deletion.CASCADE,related_name='inspection'))]),
        migrations.CreateModel(name='PaymentEvent',fields=[
            ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
            ('kind',models.CharField(max_length=40)),('source',models.CharField(max_length=40,default='gateway')),
            ('gateway_status',models.CharField(max_length=40,blank=True)),('matched',models.BooleanField(default=False)),
            ('http_status',models.PositiveIntegerField(null=True,blank=True)),('error_code',models.CharField(max_length=40,blank=True)),
            ('error_message',models.CharField(max_length=400,blank=True)),('created_at',models.DateTimeField(auto_now_add=True)),
            ('payment',models.ForeignKey(to='hotels.payment',on_delete=django.db.models.deletion.CASCADE,related_name='diagnostic_events'))],options={'ordering':['-id']})]
