from django.db import models
import datetime

# Create your models here.

class listOfNames(models.Model):
    name=models.CharField(max_length=253)
    option=models.CharField(max_length=200)
    mobile=models.CharField(max_length=255)
    address=models.CharField(max_length=255)
    user=models.CharField(max_length=255)
    class Meta:
        # Define a unique constraint for the combination of name and user
        unique_together = (('name', 'user','option'))

class listOfAll(models.Model):
    login=models.CharField(max_length=200)
    name_id=models.ForeignKey(listOfNames,on_delete=models.CASCADE)
    date=models.DateField(default=datetime.datetime.now)
    narration=models.CharField(max_length=500)
    weight=models.FloatField()
    percentage=models.FloatField()
    fine=models.FloatField()
    amount=models.FloatField()
    ledgeroption=models.CharField(max_length=200)
    ledger=models.CharField(max_length=200)
    rate=models.FloatField()




