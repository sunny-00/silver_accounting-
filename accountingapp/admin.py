# admin.py

from django.contrib import admin
from .models import listOfNames, listOfAll

@admin.register(listOfNames)
class listOfNamesAdmin(admin.ModelAdmin):
    list_display = ('name', 'option', 'mobile', 'address')

@admin.register(listOfAll)
class listOfAllAdmin(admin.ModelAdmin):
    list_display = ('login', 'name_id', 'date', 'narration', 'weight', 'percentage', 'fine', 'amount', 'ledgeroption', 'ledger', 'rate')

