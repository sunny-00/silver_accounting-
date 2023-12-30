from django.urls import path
from accountingapp import views

urlpatterns = [
    path('start',views.start),
    path('customer',views.customer),
    path('createcustomer',views.createcustomer),
    path('detailsOfCustomer/<name>',views.detailsOfCustomer),
    path('customerentry/debit/<name>',views.addCustomerEntryDebit),
    path('customerentry/credit/<name>',views.addCustomerEntryCredit),
    path('supplier',views.supplier),
    path('createsupplier',views.createsupplier),
    path('detailsOfSupplier/<name>',views.detailsOfSupplier),
    path('supplierentry/debit/<name>',views.addSupplierEntryDebit),
    path('supplierentry/credit/<name>',views.addSupplierEntryCredit),
    path('searchcustomer',views.searchcustomer),
    path('searchsupplier',views.searchsupplier),
    path('edit/<int:entry_id>/', views.edit_entry, name='edit_entry'),
    path('delete/<id>',views.delete),
    path('deleteuser/<name>',views.deleteuser),
    path('updatecustomer',views.updatecustomer),
    path('updatesupplier',views.updatesupplier),
    path('deletesup/<name>',views.deletesupplier),
    path('changepass',views.changepass),
    path('logout/', views.logoutuser),
    path('whatsapp/<number>',views.whatsapp),
    
    
    
]