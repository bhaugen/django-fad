from django.contrib import admin
from distribution.models import *
from distribution.forms import CustomerForm, DistributorForm, ProcessorForm, ProducerForm

class FoodNetworkAdmin(admin.ModelAdmin):
    list_display = ('short_name', 'long_name', 'contact', 'customer_fee', 'producer_fee', 'charge', 'charge_name')

admin.site.register(FoodNetwork, FoodNetworkAdmin)


class ProducerAdmin(admin.ModelAdmin):
    form = ProducerForm
    list_display = ('short_name', 'member_id', 'long_name', 'contact', 'phone', 'delivers')
    
admin.site.register(Producer, ProducerAdmin)


class ProcessorAdmin(admin.ModelAdmin):
    form = ProcessorForm
    list_display = ('short_name', 'long_name', 'contact', 'phone')
    
admin.site.register(Processor, ProcessorAdmin)


class DistributorAdmin(admin.ModelAdmin):
    form = DistributorForm
    list_display = ('short_name', 'member_id', 'long_name', 'contact', 'phone')
    
admin.site.register(Distributor, DistributorAdmin)


class CustomerAdmin(admin.ModelAdmin):
    form = CustomerForm
    list_display = ('short_name', 'member_id', 'long_name', 'contact', 'phone', 'charge', 'apply_charge')
    
admin.site.register(Customer, CustomerAdmin)


class ProductAdmin(admin.ModelAdmin):
    list_display = ('short_name', 'long_name', 'parent', 'price',
        'expiration_days', 'pay_producer', 'sellable', 'plannable', 'stockable')
    list_filter = [ 'sellable', 'plannable', 'stockable', 'parent']
    search_fields = ['short_name', 'long_name']
    
admin.site.register(Product, ProductAdmin)


class ProductPlanAdmin(admin.ModelAdmin):
    list_display = ('product', 'member', 'role', 'from_date', 'to_date', 'quantity',
                    'inventoried', 'distributor')
    list_filter = ['role', 'inventoried', 'member', 'product']
    date_hierarchy = 'from_date'
    
admin.site.register(ProductPlan, ProductPlanAdmin)


class ProducerProductAdmin(admin.ModelAdmin):
    list_display = ('producer', 'product', 'default_quantity',
                    'inventoried', 'planned', 'distributor')
    list_filter = ['inventoried', 'producer', 'product']
    
admin.site.register(ProducerProduct, ProducerProductAdmin)


class CustomerProductAdmin(admin.ModelAdmin):
    list_display = ('customer', 'product', 'default_quantity',
                     'planned', 'product_list')
    list_filter = ['product_list', 'customer', 'product']
    
admin.site.register(CustomerProduct, CustomerProductAdmin)


class MemberProductListAdmin(admin.ModelAdmin):
    list_display = ('member', 'list_name', 'description')
    list_filter = ['member', ]
    
admin.site.register(MemberProductList, MemberProductListAdmin)

class PartyUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'party')
    
admin.site.register(PartyUser, PartyUserAdmin)


class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'producer', 'lot_id', 'field_id', 'custodian', 'inventory_date', 'expiration_date', 'planned', 'remaining', 'received', 'onhand', 'notes')
    list_filter = ['producer', 'product']
    search_fields = ['producer__short_name, product__short_name']
    date_hierarchy = 'inventory_date'
    
admin.site.register(InventoryItem, InventoryItemAdmin)


class OrderItemInline(admin.TabularInline):
    model = OrderItem

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'order_date', 'customer', 'distributor', 'state',
                    'product_list' )
    ordering = ('order_date',)
    list_filter = ['customer', 'paid']
    date_hierarchy = 'order_date'
    inlines = [ OrderItemInline, ]
  
admin.site.register(Order, OrderAdmin)


#class OrderItemAdmin(admin.ModelAdmin):
#    list_display = ('order', 'product', 'quantity', 'unit_price', 'extended_price')
  
#admin.site.register(OrderItem, OrderItemAdmin)


class ProcessTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'input_type', 'use_existing_input_lot', 'number_of_processing_steps', 'output_type', 'number_of_output_lots', 'notes')
  
admin.site.register(ProcessType, ProcessTypeAdmin)

class ServiceTypeAdmin(admin.ModelAdmin):
    list_display = ('name','invoiced_separately', 'pay_provider_on_terms')
  
admin.site.register(ServiceType, ServiceTypeAdmin)

class ProcessAdmin(admin.ModelAdmin):
    list_display = ('process_type', 'process_date')
  
admin.site.register(Process, ProcessAdmin)


class InventoryTransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_type', 'transaction_date',  'from_whom', 'to_whom', 'order_item', 'process', 'product', 'inventory_item', 'unit_price', 'amount', 'notes')
    list_filter = ['transaction_type', 'inventory_item']
    search_fields = ['inventory_item__producer__short_name', 'order_item__order__customer__short_name', 'inventory_item__product__short_name']
    date_hierarchy = 'transaction_date'
  
admin.site.register(InventoryTransaction, InventoryTransactionAdmin)

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('transaction_date', 'from_whom', 'to_whom', 'amount', 'reference')
  
admin.site.register(Payment, PaymentAdmin)


class ServiceTransactionAdmin(admin.ModelAdmin):
    date_hierarchy = 'transaction_date'
    list_display = ('service_type', 'process', 'from_whom', 'to_whom', 'transaction_date', 'amount')
  
admin.site.register(ServiceTransaction, ServiceTransactionAdmin)


class TransportationTransactionAdmin(admin.ModelAdmin):
    date_hierarchy = 'transaction_date'
    list_display = ('service_type', 'order', 'from_whom', 'to_whom', 'transaction_date', 'amount')
  
admin.site.register(TransportationTransaction, TransportationTransactionAdmin)

