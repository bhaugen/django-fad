import datetime
from decimal import *
import itertools

from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q
from django.contrib.localflavor.us.models import PhoneNumberField
from django.contrib.contenttypes.models import ContentType
from django.db.models.query import QuerySet


def customer_fee():
    answer = 0
    try:
        answer = FoodNetwork.objects.get(pk=1).customer_fee
    except FoodNetwork.DoesNotExist:
        answer = 0
    return answer

def producer_fee():
    answer = 0
    try:
        answer = FoodNetwork.objects.get(pk=1).producer_fee
    except FoodNetwork.DoesNotExist:
        answer = 0
    return answer

def default_charge():
    charge = 0
    try:
        charge = FoodNetwork.objects.get(pk=1).charge
    except FoodNetwork.DoesNotExist:
        charge = 0
    return charge

def current_week():
    answer = datetime.date.today()
    try:
        answer = FoodNetwork.objects.get(pk=1).current_week
    except FoodNetwork.DoesNotExist:
        answer = datetime.date.today()
    return answer

def ordering_by_lot():
    try:
        answer = FoodNetwork.objects.get(pk=1).order_by_lot
    except FoodNetwork.DoesNotExist:
        answer = False
    return answer

def charge_name():
    try:
        answer = FoodNetwork.objects.get(pk=1).charge_name
    except:
        answer = 'Delivery Charge'
    return answer

def customer_terms():
    return FoodNetwork.objects.get(pk=1).customer_terms


def member_terms():
    return FoodNetwork.objects.get(pk=1).member_terms

class ProductAndProducers(object):
     def __init__(self, product, qty, price, producers):
         self.product = product
         self.qty = qty
         self.price = price
         self.producers = producers

         
class ProductAndLots(object):
     def __init__(self, product, qty, price, lots):
         self.product = product
         self.qty = qty
         self.price = price
         self.lots = lots


class ProductQuantity(object):
     def __init__(self, product, qty):
         self.product = product
         self.qty = qty


class PickupCustodian(object):
     def __init__(self, custodian, address, products):
         self.custodian = custodian
         self.address = address
         self.products = products
 
         
class PickupDistributor(object):
     def __init__(self, distributor, email, custodians):
         self.distributor = distributor
         self.email = email
         self.custodians = custodians
         
         
class OrderToBeDelivered(object):
     def __init__(self, customer, address, products):
         self.customer = customer
         self.address = address
         self.products = products
         
class DeliveryDistributor(object):
     def __init__(self, distributor, email, customers):
         self.distributor = distributor
         self.email = email
         self.customers = customers

# inheritance approach based on
# http://www.djangosnippets.org/snippets/1034/
class SubclassingQuerySet(QuerySet):
    def __getitem__(self, k):
        result = super(SubclassingQuerySet, self).__getitem__(k)
        if isinstance(result, models.Model):
            return result.as_leaf_class()
        else:
            return result
    def __iter__(self):
        for item in super(SubclassingQuerySet, self).__iter__():
            yield item.as_leaf_class()

    
class PartyManager(models.Manager):
    
    def get_query_set(self):
        return SubclassingQuerySet(self.model)
    
    def planned_producers(self):
        producers = []
        all_prods = Party.subclass_objects.all()
        for prod in all_prods:
            if prod.is_producer():
                if prod.product_plans.all().count():
                    producers.append(prod)
        return producers

    def all_distributors(self):
        parties = Party.objects.all()
        dists = []
        for party in parties:
            if isinstance(party.as_leaf_class(), Distributor):
                dists.append(party)
        return dists

    def all_planners(self):
        parties = Party.objects.all()
        dists = []
        for party in parties:
            if isinstance(party.as_leaf_class(), Producer):
                dists.append(party)
            if isinstance(party.as_leaf_class(), Customer):
                dists.append(party)
        return dists


    def payable_members(self):
        parties = Party.objects.all().exclude(pk=1)
        pms = []
        for party in parties:
            if not isinstance(party.as_leaf_class(), Customer):
                pms.append(party)
        return pms

    def possible_custodians(self):
        parties = Party.objects.all().exclude(pk=1)
        pcs = []
        for party in parties:
            if isinstance(party.as_leaf_class(), Processor) or isinstance(party.as_leaf_class(), Distributor):
                pcs.append(party)
        return pcs
    
class Party(models.Model):
    member_id = models.CharField(max_length=12, blank=True)
    short_name = models.CharField(max_length=32, unique=True)
    long_name = models.CharField(max_length=64, blank=True)
    contact = models.CharField(max_length=64, blank=True)
    phone = PhoneNumberField(blank=True)
    cell = PhoneNumberField(blank=True)
    fax = PhoneNumberField(blank=True)
    address = models.CharField(max_length=96, blank=True)
    email_address = models.EmailField(max_length=96, blank=True, null=True)
    content_type = models.ForeignKey(ContentType,editable=False,null=True)
    
    objects = models.Manager()
    subclass_objects = PartyManager()

    def __unicode__(self):
        return self.short_name
    
    @property
    def email(self):
        return self.email_address

    class Meta:
        ordering = ('short_name',)
        
    def as_leaf_class(self):
        if self.content_type:
            content_type = self.content_type
            model = content_type.model_class()
            if (model == Party):
                return self
            return model.objects.get(id=self.id)
        else:
            return self

    def is_customer(self):
        if isinstance(self.as_leaf_class(), Customer):
            return True
        else:
            return False

    def is_producer(self):
        if isinstance(self.as_leaf_class(), Producer):
            return True
        else:
            return False

        
    def save(self, force_insert=False, force_update=False):
        #import pdb; pdb.set_trace()
        if not self.content_type:
            self.content_type = ContentType.objects.get_for_model(self.__class__)
        self.save_base(force_insert=False, force_update=False)
        
    def formatted_address(self):
        return self.address.split(',')


class PartyUser(models.Model):
    party = models.ForeignKey(Party, related_name="users")
    user = models.ForeignKey(User, related_name="parties")

         

class FoodNetwork(Party):
    billing_contact = models.CharField(max_length=64, blank=True)
    billing_phone = PhoneNumberField(blank=True, null=True)
    billing_address = models.CharField(max_length=96, blank=True, null=True, 
            help_text='Enter commas only where you want to split address lines for formatting.')
    billing_email_address = models.EmailField(max_length=96, blank=True, null=True)
    customer_terms = models.IntegerField(default=0,
        help_text='Net number of days for customer to pay invoice')
    member_terms = models.IntegerField(blank=True, null=True,
        help_text='Net number of days for network to pay member')
    customer_fee = models.DecimalField(max_digits=3, decimal_places=2, default=Decimal("0"),
        help_text='Fee is a decimal fraction, not a percentage - for example, .05 instead of 5%')
    producer_fee = models.DecimalField(max_digits=3, decimal_places=2, default=Decimal("0"),
        help_text='Fee is a decimal fraction, not a percentage - for example, .05 instead of 5%') 
    # next 2 fields are obsolete   
    charge = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal("0"),
        help_text='Charge will be added to all orders unless overridden on the Customer')
    charge_name = models.CharField(max_length=32, blank=True, default='Delivery charge')
    current_week = models.DateField(default=datetime.date.today, 
        help_text='Current week for operations availability and orders')
    order_by_lot = models.BooleanField(default=False, 
        help_text='Assign lots when ordering, or assign them later')


    class Meta:
        ordering = ('short_name',)


    def __unicode__(self):
        return self.short_name
    def formatted_billing_address(self):
        return self.billing_address.split(',')
    
    @property
    def email(self):
        return self.email_address

    def transportation_fee(self):
        return self.charge
    
    def fresh_list(self, thisdate = None):
        if not thisdate:
            thisdate = current_week()
        prods = Product.objects.all()
        item_list = []
        for prod in prods:
            #item_chain = prod.avail_items(thisdate)
            #items = []
            #for item in item_chain:
            #    items.append(item)
            items = prod.avail_items(thisdate)
            avail_qty = sum(item.avail_qty() for item in items)
            if avail_qty > 0:
                price = prod.price.quantize(Decimal('.01'), rounding=ROUND_UP)
                #producers = []
                #for item in items:
                #    producer = item.producer.long_name
                #    if not producer in producers:
                #        producers.append(producer)
                #item_list.append(ProductAndProducers(prod.long_name, avail_qty, price, producers))
                item_list.append(ProductAndLots(prod.long_name, avail_qty, price, items))
        return item_list
    
    def pickup_list(self, thisdate = None):
        if not thisdate:
            thisdate = current_week()
        prods = Product.objects.all()
        distributors = {}
        network = self
        for prod in prods:
            items = prod.ready_items(thisdate)            
            for item in items:
                distributor = item.distributor()
                if not distributor:
                    distributor = network
                if item.custodian:
                    custodian = item.custodian.long_name
                    address = item.custodian.address
                else:
                    custodian = item.producer.long_name
                    address = item.producer.address
                # eliminate items to be delivered by producer or custodian
                if not distributor.id == item.producer.id:
                    if not distributor in distributors:
                        if distributor.email_address:
                            email = distributor.email_address
                        else:
                            email = network.email_address
                        distributors[distributor] = PickupDistributor(distributor.long_name, email, {})
                    this_distributor = distributors[distributor]
                    if not custodian in this_distributor.custodians:
                        this_distributor.custodians[custodian] = PickupCustodian(custodian, address, [])
                    this_distributor.custodians[custodian].products.append(ProductQuantity(item.pickup_label(), item.planned))
        return distributors
        
    def delivery_list(self, thisdate = None):
        if not thisdate:
            thisdate = current_week()
        weekstart = thisdate - datetime.timedelta(days=datetime.date.weekday(thisdate))
        weekend = weekstart + datetime.timedelta(days=5)
        ois = OrderItem.objects.filter(order__order_date__range=(weekstart, weekend))
        
        #customers = {}
        #product_producers = {}
        
        distributors = {}
        network = self
        for oi in ois:
            customer = oi.order.customer.long_name
            product = oi.product.id
            txs = oi.inventorytransaction_set.all()
            # what if no txs, i.e. no lot assignments?
            lots = []
            for tx in txs:
                lots.append(tx.inventory_item)
            for lot in lots:
                distributor = lot.distributor()
                if not distributor:
                    distributor = network
                if not distributor in distributors:
                    if distributor.email_address:
                        email = distributor.email_address
                    else:
                        email = network.email_address
                    distributors[distributor] = DeliveryDistributor(distributor.long_name, email, {})
                this_distributor = distributors[distributor]
                
                if not customer in this_distributor.customers:
                    this_distributor.customers[customer] = OrderToBeDelivered(customer, oi.order.customer.address, {})
                otbd = this_distributor.customers[customer]
                if not product in otbd.products:
                    otbd.products[product] = ProductAndLots(oi.product.long_name, oi.quantity, oi.product.price,[])
                otbd.products[product].lots.append(lot)
        for dist in distributors:
            dd = distributors[dist]
            for cust in dd.customers:
                otbd = dd.customers[cust]
                otbd.products = otbd.products.values()
        return distributors
                
        #    customer = item.order.customer.long_name
        #    product = item.product.id
        #    if not product in product_producers:
        #            product_producers[product] = item.product.avail_producers(thisdate)
        #    producers = product_producers[product]             
        #    if not customer in customers:
        #        customers[customer] = OrderToBeDelivered(customer, item.order.customer.address, [])
        #    customers[customer].products.append(ProductAndProducers(item.product.long_name, item.quantity, item.product.price, producers))
        #item_list = customers.values()
        #item_list.sort(lambda x, y: cmp(x.customer, y.customer))   
        #return item_list
    
    def all_avail_items(self, thisdate=None):
        if not thisdate:
            thisdate = current_week()
        weekstart = thisdate - datetime.timedelta(days=datetime.date.weekday(thisdate))
        expired_date = weekstart + datetime.timedelta(days=5)
        items = InventoryItem.objects.filter(
            inventory_date__lte=expired_date,
            expiration_date__gte=expired_date)
        items = items.filter(Q(remaining__gt=0) | Q(onhand__gt=0))
        return items
    
    def all_active_items(self, thisdate = None):
        # todo: this and dashboard need work
        # e.g. shows steers with no avail or orders, but some were consumed
        # delivery column commented out because order-by-lot delivers at same time as ordered
        if not thisdate:
            thisdate = current_week()
        weekstart = thisdate - datetime.timedelta(days=datetime.date.weekday(thisdate))
        weekend = weekstart + datetime.timedelta(days=5)
        return InventoryItem.objects.filter(
            inventory_date__lte=weekend,
            expiration_date__gte=weekend)
          

class ProducerManager(models.Manager):

    def planned_producers(self):
        producers = []
        all_prods = Producer.objects.all()
        for prod in all_prods:
            if prod.product_plans.all().count():
                producers.append(prod)
        return producers


class Producer(Party):
    delivers = models.BooleanField(default=False,
        help_text='Delivers products directly to customers?')


class Processor(Party):
    pass


class Distributor(Party):
    pass


class Customer(Party):
    charge = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True,
        help_text='Any value but 0 in this field will override the default charge from the Food Network')
    apply_charge = models.BooleanField(default=True,
        help_text='Add the extra charge to all orders for this customer, or not?')

    def __unicode__(self):
        return self.short_name

    def formatted_address(self):
        return self.address.split(',')

    def order_charge(self):
        answer = Decimal(0)
        if self.apply_charge:
            if self.charge:
                answer = self.charge
            else:
                answer = default_charge()
        return answer
    
    def distributor(self):
        #todo: revise when 5S distributor assignments are clear
        # maybe add distributor field to Customer or some logic on FoodNetwork 
        return Distributor.objects.all()[0]

    def transportation_fee(self):
        #todo: revise when 5S fees are clear
        # maybe add transportation_fee field to Customer or some logic on FoodNetwork
        return FoodNetwork.objects.get(pk=1).transportation_fee()

    @property
    def email(self):
        return self.email_address

    class Meta:
        ordering = ('short_name',)

# based on dfs from threaded_comments
def nested_objects(node, all_nodes):
     to_return = [node,]
     for subnode in all_nodes:
         if subnode.parent and subnode.parent.id == node.id:
             to_return.extend([nested_objects(subnode, all_nodes),])
     return to_return

def flattened_children(node, all_nodes, to_return):
     to_return.append(node)
     for subnode in all_nodes:
         if subnode.parent and subnode.parent.id == node.id:
             flattened_children(subnode, all_nodes, to_return)
     return to_return


class Product(models.Model):
    parent = models.ForeignKey('self', blank=True, null=True, related_name='children',
        limit_choices_to = {'is_parent': True})
    short_name = models.CharField(max_length=32, unique=True)
    long_name = models.CharField(max_length=64)
    sellable = models.BooleanField(default=True,
        help_text='Should this product appear in Order form?')
    plannable = models.BooleanField(default=True,
        help_text='Should this product appear in Plan form?')
    stockable = models.BooleanField(default=True,
        help_text='Should this product be stored as Inventory Items?')
    is_parent = models.BooleanField(default=False,
        help_text='Should this product appear in parent selections?')
    price = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal(0))
    customer_fee_override = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True, 
        help_text='Enter override as a decimal fraction, not a percentage - for example, .05 instead of 5%. Note: you cannot override to zero here, only on Order Items.')
    pay_producer = models.BooleanField(default=True,
        help_text='If checked, the Food Network pays the producer for issues, deliveries and damages of this product.')
    pay_producer_on_terms = models.BooleanField(default=False,
        help_text='If checked, producer paid on member terms. If not, producers paid based on customer order payments. Note: Issues always paid on member terms.')
    expiration_days = models.IntegerField(default=6,
        help_text='Inventory Items (Lots) of this product will expire in this many days.')

    def __unicode__(self):
        return self.long_name

    def formatted_unit_price(self):
        return self.price.quantize(Decimal('.01'), rounding=ROUND_UP)
    
    def avail_items(self, thisdate):
        weekstart = thisdate - datetime.timedelta(days=datetime.date.weekday(thisdate))
        weekend = weekstart + datetime.timedelta(days=5)
        expired_date = weekstart + datetime.timedelta(days=5)
        items = InventoryItem.objects.filter(product=self, 
            inventory_date__lte=weekend,
            expiration_date__gte=expired_date)
        items = items.filter(Q(remaining__gt=0) | Q(onhand__gt=0))
        return items
    
    def current_items(self, thisdate):
        weekstart = thisdate - datetime.timedelta(days=datetime.date.weekday(thisdate))
        weekend = weekstart + datetime.timedelta(days=5)
        expired_date = weekstart + datetime.timedelta(days=5)
        items = InventoryItem.objects.filter(product=self, 
            inventory_date__lte=weekend,
            expiration_date__gte=expired_date)
        #items = items.filter(Q(remaining__gt=0) | Q(onhand__gt=0))
        return items
    
    def ready_items(self, thisdate):
        weekstart = thisdate - datetime.timedelta(days=datetime.date.weekday(thisdate))
        weekend = weekstart + datetime.timedelta(days=5)
        items = InventoryItem.objects.filter(product=self, 
            inventory_date__range=(weekstart, weekend),
            planned__gt=0, onhand__exact=0,  received__exact=0)
        return items
    
    def total_avail(self, thisdate):
        return sum(item.avail_qty() for item in self.avail_items(thisdate))
    
    def avail_producers(self, thisdate):
        producers = []
        myavails = self.avail_items(thisdate)
        for av in myavails:
            producers.append(av.producer.short_name)
        producers = list(set(producers))
        producer_string = ", ".join(producers)
        return producer_string
    
    def active_producers(self, thisdate):
        producers = []
        myavails = self.avail_items(thisdate)
        for av in myavails:
            producers.append(av.producer.short_name)
        deliveries = self.deliveries_this_week(thisdate)
        for delivery in deliveries:
            producers.append(delivery.inventory_item.producer.short_name)
        producers = list(set(producers))
        producer_string = ", ".join(producers)
        return producer_string
    
    def total_ordered(self, thisdate):
        weekstart = thisdate - datetime.timedelta(days=datetime.date.weekday(thisdate))
        weekend = weekstart + datetime.timedelta(days=5)
        myorders = OrderItem.objects.filter(product=self, order__order_date__range=(weekstart, weekend))
        return sum(order.quantity for order in myorders)

    def avail_for_customer(self, thisdate):
        return self.total_avail(thisdate) - self.total_ordered(thisdate)
    
    def deliveries_this_week(self, thisdate):
        weekstart = thisdate - datetime.timedelta(days=datetime.date.weekday(thisdate))
        weekend = weekstart + datetime.timedelta(days=5)
        deliveries = InventoryTransaction.objects.filter(transaction_type="Delivery")
        return deliveries.filter(
            order_item__product=self, transaction_date__range=(weekstart, weekend))
    
    def total_delivered(self, thisdate):
        deliveries = self.deliveries_this_week(thisdate)
        return sum(delivery.amount for delivery in deliveries)
    
    def decide_fee(self):
        prod_fee = self.customer_fee_override
        if prod_fee:
            my_fee = prod_fee
        else:
            my_fee = customer_fee()
        return my_fee
    
    def parent_string(self):
        answer = ''
        prod = self
        parents = []
        while not prod.parent is None:
            parents.append(prod.parent.short_name)
            prod = prod.parent
        if len(parents) > 0:
            parents.reverse()
            answer = ', '.join(parents)
        return answer

    def supply_demand_product(self):
        answer = self
        prod = self
        while not prod.parent is None:
            if prod.parent.plannable:
                answer = prod.parent
                break
            else:
                prod = prod.parent
        return answer

    def sellable_children(self):
        kids = flattened_children(self, Product.objects.all(), [])
        sellables = []
        for kid in kids:
            if kid.sellable:
                sellables.append(kid)
        return sellables

    def plannable_children(self):
        kids = flattened_children(self, Product.objects.all(), [])
        plannables = []
        for kid in kids:
            if kid.plannable:
                plannables.append(kid)
        return plannables

    def stockable_children(self):
        kids = flattened_children(self, Product.objects.all(), [])
        stockables = []
        for kid in kids:
            if kid.stockable:
                stockables.append(kid)
        return stockables


    class Meta:
        ordering = ('short_name',)

PLAN_ROLE_CHOICES = (
    ('consumer', 'consumer'),
    ('producer', 'producer'),
)


class ProductPlan(models.Model):
    member = models.ForeignKey(Party, related_name="product_plans") 
    product = models.ForeignKey(Product, limit_choices_to = {'plannable': True})
    from_date = models.DateField()
    to_date = models.DateField()
    quantity = models.DecimalField(max_digits=8, decimal_places=2,
        default=Decimal('0'), verbose_name='Qty per week')
    role = models.CharField(max_length=12, choices=PLAN_ROLE_CHOICES,
                            default="producer")
    inventoried = models.BooleanField(default=True,
        help_text="If not inventoried, the planned qty per week will be used for ordering")
    distributor = models.ForeignKey(Party, related_name="plan_distributors", blank=True, null=True)
    
    def __unicode__(self):
        return " ".join([
            self.member.short_name,
            self.product.short_name,
            self.from_date.strftime('%Y-%m-%d'),
            self.to_date.strftime('%Y-%m-%d'),
            str(self.quantity)])
        
    class Meta:
        ordering = ('product', 'member', 'from_date')


class ProducerProduct(models.Model):
    producer = models.ForeignKey(Party, related_name="producer_products") 
    product = models.ForeignKey(Product)
    default_quantity = models.DecimalField(max_digits=8, decimal_places=2,
        default=Decimal('0'), verbose_name='Qty per week')
    inventoried = models.BooleanField(default=True,
        help_text="If not inventoried, the default or planned qty per week will be used for ordering")
    planned = models.BooleanField(default=True,
        help_text='Should this product appear in Plan forms?')
    distributor = models.ForeignKey(Party, related_name="producer_distributors", blank=True, null=True)
    
    def __unicode__(self):
        return " ".join([
            self.producer.short_name,
            self.product.short_name])
        
    class Meta:
        ordering = ('producer', 'product')

#todo: obsolete
#def product_list_names(customer):
#    names = MemberProductList.objects.filter(
#        customer=customer,
#    ).values_list("list_name")
#    names = (name[0] for name in names)
#    return list(set(names))


class MemberProductList(models.Model):
    member = models.ForeignKey(Party, related_name="product_lists")
    list_name = models.CharField(max_length=64)
    description = models.CharField(max_length=255)

    def __unicode__(self):
        return " ".join([
            self.member.short_name,
            self.list_name,])


class CustomerProduct(models.Model):
    customer = models.ForeignKey(Party, related_name="customer_products") 
    product = models.ForeignKey(Product, limit_choices_to = {'plannable': True})
    product_list = models.ForeignKey(MemberProductList, blank=True, null=True,
        help_text='You may separate products into different lists.')
    list = models.CharField(max_length=64, blank=True,
        help_text='You may separate products into different lists.')
    default_quantity = models.DecimalField(max_digits=8, decimal_places=2,
        default=Decimal('0'), verbose_name='Default quantity per week or order')
    planned = models.BooleanField(default=True,
        help_text='Should this product appear in Plan forms?')

        
    class Meta:
        ordering = ('customer', 'product')

    def __unicode__(self):
        return " ".join([
            self.customer.short_name,
            self.product.short_name,])


class InventoryItem(models.Model):
    freeform_lot_id = models.CharField("Lot Id", max_length=64, blank=True,
        help_text='Optional - if you do not enter a Lot Id, one will be created.')
    producer = models.ForeignKey(Party, related_name="inventory_items")
    field_id = models.CharField("Field", max_length=12, blank=True)
    custodian = models.ForeignKey(Party, blank=True, null=True, related_name="custody_items")
    product = models.ForeignKey(Product, limit_choices_to = {'stockable': True})
    inventory_date = models.DateField()
    expiration_date = models.DateField()
    planned = models.DecimalField("Ready", max_digits=8, decimal_places=2, default=Decimal('0'))
    remaining = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0'),
        help_text='If you change Ready here, you most likely should also change Remaining. The Avail Update page changes Remaining automatically when you enter Ready, but this Admin form does not.')
    received = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0'))
    onhand = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0'),
        help_text='If you change Received here, you most likely should also change Onhand. The Avail Update page changes Onhand automatically when you enter Received, but this Admin form does not.')
    notes = models.CharField(max_length=64, blank=True)
    
    class Meta:
        ordering = ('product', 'producer', 'inventory_date')

    def __unicode__(self):
        return " ".join([
            self.producer.short_name,
            self.product.short_name,
            self.inventory_date.strftime('%Y-%m-%d')])

    def lot_id(self):
        if self.freeform_lot_id:
            return self.freeform_lot_id
        else:
            return " ".join([
                self.producer.member_id,
                self.producer.short_name,
                self.product.short_name,
                self.inventory_date.strftime('%Y-%m-%d')])        
    
    def avail_qty(self):
        if self.onhand:
            return self.onhand
        else:
            return self.remaining
        
    def ordered_qty(self):
        return self.delivered_qty()

    def deliveries(self):
        return self.inventorytransaction_set.filter(transaction_type="Delivery")
        
    def delivered_qty(self):
        return sum(delivery.amount for delivery in self.deliveries())

    def issues(self):
        return self.inventorytransaction_set.filter(transaction_type="Issue")
        
    def issued_qty(self):
        return sum(delivery.amount for delivery in self.issues())

    def delivery_label(self):
        return " ".join([
            self.producer.short_name,
            'qty', str(self.avail_qty()),
            'at', self.inventory_date.strftime('%m-%d')])
            
    def pickup_label(self):
        return self.lot_id()
        
    def distributor(self):
        plans = ProductPlan.objects.filter(
            product = self.product,
            producer = self.producer,
            from_date__lte=self.inventory_date,
            to_date__gte=self.inventory_date)
        if plans:
            return plans[0].distributor
        else:
            return None
        
    def customers(self):
        buyers = []
        for delivery in self.deliveries():
            if delivery.order_item:
                buyers.append(delivery.order_item.order.customer.short_name)
        buyers = list(set(buyers))
        buyer_string = ", ".join(buyers)
        return buyer_string
            
    def update_from_transaction(self, qty): 
        """ update remaining or onhand

        Onhand trumps remaining.
        Qty could be positive or negative.
        """

        if self.onhand + self.received > Decimal('0'):
            # to deal with Django bug, fixed in 1.1
            onhand = Decimal(self.onhand)
            onhand += qty
            self.onhand = max([Decimal("0"), onhand])
            self.save()
        else:
            # to deal with Django bug, fixed in 1.1
            remaining = Decimal(self.remaining)
            #print self, "remaining:", remaining, "qty:", qty
            remaining += qty
            self.remaining = max([Decimal("0"), remaining])
            self.save()
                
    def save(self, force_insert=False, force_update=False):
        if not self.pk:
            self.expiration_date = self.inventory_date + datetime.timedelta(days=self.product.expiration_days)
        super(InventoryItem, self).save(force_insert, force_update)

# EconomicEventType is not ripe
#class EconomicEventType(models.Model):
#    name = models.CharField(max_length=255)

class EconomicEventManager(models.Manager):
    
    def get_query_set(self):
        return SubclassingQuerySet(self.model)

    def all_payments(self):
        events = EconomicEvent.raw_objects.all()
        payments = []
        for event in events:
            if isinstance(event.as_leaf_class(), Payment):
                payments.append(event)
        return payments

    def payments_to_party(self, party):
        events = EconomicEvent.raw_objects.filter(to_whom=party)
        payments = []
        for event in events:
            if isinstance(event.as_leaf_class(), Payment):
                payments.append(event)
        return payments

    def payments_to_members(self):
        fn = FoodNetwork.objects.get(pk=1)
        payments = Payment.objects.all().exclude(to_whom=fn)
        return payments

class EconomicEvent(models.Model):
    transaction_date = models.DateField()
    from_whom = models.ForeignKey(Party, related_name="given_events")
    to_whom = models.ForeignKey(Party, related_name="taken_events")
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    notes = models.CharField(max_length=64, blank=True)
    content_type = models.ForeignKey(ContentType,editable=False,null=True)

    raw_objects = models.Manager()
    objects = EconomicEventManager()

    def as_leaf_class(self):
        if self.content_type:
            content_type = self.content_type
            model = content_type.model_class()
            if (model == EconomicEvent):
                return self
            return model.objects.get(id=self.id)
        else:
            return self
        
    def save(self, force_insert=False, force_update=False):
        if not self.content_type:
            self.content_type = ContentType.objects.get_for_model(self.__class__)
        self.save_base(force_insert=False, force_update=False)

    def payments(self):
        if isinstance(self.as_leaf_class(), Payment):
            return []
        answer = []
        for d in self.transaction_payments.all():
            answer.append(d.payment)
        return answer

    def paid_amount(self):
        answer = False
        paid = Decimal("0")
        for payment in self.transaction_payments.all():
             paid += payment.amount_paid
        return paid.quantize(Decimal('.01'), rounding=ROUND_UP)

    def due_to_member(self):
        return self.as_leaf_class().due_to_member()

    def is_paid(self):
        return self.paid_amount() >= self.due_to_member()

    def payment_string(self):
        ps = []
        for payment in self.payments():
            ps.append(payment.as_string())
        ps = list(set(ps))
        ps_string = ", ".join(ps)
        return ps_string

    def delete_payments(self):
        for tp in self.transaction_payments.all():
            tp.delete()

        
class Payment(EconomicEvent):
    reference = models.CharField(max_length=64, blank=True)

    def __unicode__(self):
        amount_string = '$' + str(self.amount)
        return ' '.join([
            self.transaction_date.strftime('%Y-%m-%d'),
            self.to_whom.short_name,
            amount_string])

    class Meta:
        ordering = ('transaction_date',)

    def as_string(self):
        return self.__unicode__()

    def paid_transactions(self):
        paid = []
        for d in self.paid_events.all():
            paid.append(d.paid_event.as_leaf_class())
        return paid

    def paid_inventory_transactions(self):
        paid = []
        for p in self.paid_transactions():
            if isinstance(p, InventoryTransaction):
                paid.append(p)
        return paid

    def paid_service_transactions(self):
        paid = []
        for p in self.paid_transactions():
            if isinstance(p, ServiceTransaction):
                paid.append(p)
        return paid

    def paid_transportation_transactions(self):
        paid = []
        for p in self.paid_transactions():
            if isinstance(p, TransportationTransaction):
                paid.append(p)
        return paid


class TransactionPayment(models.Model):
    """ Payment to Producer or Service provider
        for an EconomicEvent.
        In REA terms, this is a Duality
        but always assuming money in payment.
    """
    paid_event = models.ForeignKey(EconomicEvent, related_name="transaction_payments")
    payment = models.ForeignKey(Payment, related_name="paid_events")
    amount_paid = models.DecimalField(max_digits=8, decimal_places=2)


ORDER_STATES = (
    ('Unsubmitted', 'Unsubmitted'),
    ('Submitted', 'Submitted'),
    ('Delivered', 'Delivered'),
    ('Paid', 'Paid'),
    ('Paid-Delivered', 'Paid and Delivered'),
    ('Delivered-Paid', 'Delivered and Paid'),
)


class Order(models.Model):
    customer = models.ForeignKey(Customer) 
    order_date = models.DateField()
    distributor = models.ForeignKey(Party, blank=True, null=True, related_name="orders")
    #todo: obsolete, or leave in for no-customer-app situations?
    paid = models.BooleanField(default=False, verbose_name="Order paid")
    state = models.CharField(max_length=16, choices=ORDER_STATES, default='Submitted', blank=True)
    product_list = models.ForeignKey(MemberProductList, blank=True, null=True,
        related_name="orders", 
        help_text="Optional: The product list this order was created from. Maintained by customer.")

    class Meta:
        ordering = ('order_date', 'customer')

    def __unicode__(self):
        return ' '.join([self.order_date.strftime('%Y-%m-%d'), self.customer.short_name])

    def save(self, force_insert=False, force_update=False):
        if self.paid:
            state_reset = self.set_paid_state()
        self.save_base(force_insert=False, force_update=False)
    
    def delete(self):
        deliveries = InventoryTransaction.objects.filter(order_item__order=self) 
        for delivery in deliveries:
            delivery.delete()
        super(Order, self).delete()

    def is_paid(self):
        #todo: what about partials?
        if self.paid:
            return True
        if self.state == "Paid" or self.state == "Paid-Delivered" or self.state == "Delivered-Paid":
            return True
        return False
    
    def is_delivered(self):
        #todo: what about partials?
        if self.state == "Delivered" or self.state == "Paid-Delivered" or self.state == "Delivered-Paid":
            return True
        return False

    def register_delivery(self):
        if self.state.find("Delivered") < 0:
            #print "registering delivery for order", self
            if self.state == "Paid":
                self.state = "Paid-Delivered"
            else:
                self.state = "Delivered"
            self.save()

    def set_paid_state(self):
        """ This method is for internal use
            (by order.save() and order.register_customer_payment())
            and so does not include self.save().
        """

        if self.state.find("Paid") < 0:
            if self.state == "Delivered":
                self.state = "Delivered-Paid"
            else:
                self.state = "Paid"
            return True
        else:
            return False

    def register_customer_payment(self):
        if self.set_paid_state():
            self.save()

    def charge_name(self):
        return charge_name()
    
    def charge(self):
        return self.customer.order_charge()

    def transportation_fee(self):
        try:
            transportation_tx = TransportationTransaction.objects.get(order=self)
            return transportation_tx.amount
        except TransportationTransaction.DoesNotExist:
            return FoodNetwork.objects.get(pk=1).transportation_fee()
    
    def total_price(self):
        items = self.orderitem_set.all()
        total = self.transportation_fee()
        for item in items:
            total += item.extended_price()
            total += item.service_cost()
        return total.quantize(Decimal('.01'), rounding=ROUND_UP)
    
    def coop_fee(self):
        total = self.total_price()
        fee = customer_fee()
        answer = total * fee
        return answer.quantize(Decimal('.01'), rounding=ROUND_UP)
    
    def grand_total(self):
        return self.total_price() + self.coop_fee()
    
    def payment_due_date(self):
        term_days = customer_terms()
        return self.order_date + datetime.timedelta(days=term_days)
    
    def display_transportation_fee(self):
        return self.transportation_fee().quantize(Decimal('.01'), rounding=ROUND_UP)
    
    def coop_fee_label(self):
        fee = int(customer_fee() * 100)
        return "".join([str(fee), "% Co-op Fee"])

    def short_items(self):
        shorts = []
        for item in self.orderitem_set.all():
            if item.qty_short():
                shorts.append(item)
        return shorts


#todo: implement this class for order payments
# and replace order.paid field with a method
class CustomerPayment(models.Model):
    """ Payment from a Customer to FoodNetwork
        for a delivered Order.
        In REA terms, this is a Duality
        where the Order is a bundle of EconomicEvents
        and assuming money in payment.
    """
    paid_order = models.ForeignKey(Order, related_name="customer_payments")
    payment = models.ForeignKey(Payment, related_name="paid_orders")
    amount_paid = models.DecimalField(max_digits=8, decimal_places=2)
        

class ShortOrderItems(object):
    def __init__(self, product, total_avail, total_ordered, quantity_short, order_items):
         self.product = product
         self.total_avail = total_avail
         self.total_ordered = total_ordered
         self.quantity_short = quantity_short
         self.order_items = order_items


def shorts_for_date(order_date):
    shorts = []
    maybes = {}
    ois = OrderItem.objects.filter(order__order_date=order_date).exclude(order__state="Unsubmitted")
    for oi in ois:
        if not oi.product in maybes:
            maybes[oi.product] = ShortOrderItems(oi.product, 
                oi.product.total_avail(order_date), Decimal("0"), Decimal("0"), [])
        maybes[oi.product].total_ordered += (oi.quantity -oi.delivered_quantity())    
        maybes[oi.product].order_items.append(oi)
    for maybe in maybes:
        qty_short = maybes[maybe].total_ordered - maybes[maybe].total_avail
        if qty_short > Decimal("0"):
            maybes[maybe].quantity_short = qty_short
            shorts.append(maybes[maybe])
    return shorts


class OrderItem(models.Model):
    order = models.ForeignKey(Order)
    product = models.ForeignKey(Product)
    quantity = models.DecimalField(max_digits=8, decimal_places=2)
    orig_qty = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0'))
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)
    fee = models.DecimalField(max_digits=3, decimal_places=2, default=Decimal('0'),
        help_text='Fee is a decimal fraction, not a percentage - for example, .05 instead of 5%')
    notes = models.CharField(max_length=64, blank=True)

    def __unicode__(self):
        return ' '.join([
            str(self.order),
            self.product.short_name,
            str(self.quantity)])
    
    def delete(self):
        deliveries = self.inventorytransaction_set.all()
        for delivery in deliveries:
            delivery.delete()
        super(OrderItem, self).delete()
    
    def total_avail(self):
        return self.product.total_avail(self.order.order_date)
    
    def total_ordered(self):
        return self.product.total_ordered(self.order.order_date)

    def qty_short(self):
        avail = self.total_avail()
        ordered = self.total_ordered()
        if ordered > avail:
            return ordered - avail
        else:
            return Decimal("0")

    def short_adjusted_qty(self):
        return self.quantity - self.qty_short()

    def short_adjusted_extended_price(self):
        answer = self.short_adjusted_qty() * self.unit_price
        return answer.quantize(Decimal('.01'), rounding=ROUND_UP)
  
    def producers(self):
        txs = self.inventorytransaction_set.all()
        producers = []
        for tx in txs:
            producers.append(tx.inventory_item.producer.short_name)
        return ', '.join(list(set(producers)))
    
    def services(self):
        svs = []
        try:
            deliveries = self.inventorytransaction_set.all()
            for delivery in deliveries:
                svs.extend(delivery.services())
        except:
            pass
        return svs
    
    def service_cost(self):
        cost = Decimal(0)
        for delivery in self.inventorytransaction_set.all():
            cost += delivery.invoiced_service_cost()
        return cost.quantize(Decimal('.01'))
    
    def processors(self):
        procs = []
        for svc in self.services():
            procs.append(svc.from_whom.short_name)
        procs = list(set(procs))
        return ", ".join(procs)
    
    def distributor(self):
        order_date = self.order.order_date
        plans = ProductPlan.objects.filter(
            product = self.product,
            producer = self.producer,
            from_date__lte=order_date,
            to_date__gte=order_date)
        if plans:
            return plans[0].distributor
        else:
            return None
    
    def extended_price(self):
        answer = self.quantity * self.unit_price
        # todo: think about this, is it correct?
        #if self.processing():
        #    answer += self.processing().cost
        return answer.quantize(Decimal('.01'), rounding=ROUND_UP)
    
    def lot(self):
        # this is a hack
        # PBC's order_by_lot means one delivery InventoryTransaction
        # and thus one InventoryItem per OrderItem
        deliveries = self.inventorytransaction_set.all()
        if deliveries.count():
            delivery = deliveries[0]
            item = delivery.inventory_item
            return item
        else:
            return None
    
    def delivered_quantity(self):
        return sum(tx.amount for tx in self.inventorytransaction_set.all())
        
    def producer_fee(self):
        return producer_fee()
    
    def extended_producer_fee(self):
        answer = self.quantity * self.unit_price * producer_fee()
        return answer.quantize(Decimal('.01'), rounding=ROUND_UP)
    
    def formatted_unit_price(self):
        return self.unit_price.quantize(Decimal('.01'), rounding=ROUND_UP)

    def customer_fee(self):
        return customer_fee()

    class Meta:
        ordering = ('order', 'product',)



class ServiceType(models.Model):
    name = models.CharField(max_length=64)
    invoiced_separately = models.BooleanField(default=False,
        help_text='If checked, the cost of services appear as separate line items on invoices. If not, they are included in the prices of resulting products.')
    pay_provider_on_terms = models.BooleanField(default=True,
        help_text='If checked, the Food Network pays the service provider on member terms. If not, the provider payment is based on customer order payment.')

    def __unicode__(self):
        return self.name


class ProcessType(models.Model):
    name = models.CharField(max_length=64)
    input_type = models.ForeignKey(Product, related_name='input_types')
    use_existing_input_lot = models.BooleanField(default=True)
    number_of_processing_steps = models.IntegerField(default=1)
    output_type = models.ForeignKey(Product, related_name='output_types')
    number_of_output_lots = models.IntegerField(default=1)
    notes = models.TextField(blank=True)

    def __unicode__(self):
        return self.name


def previous_process_collector(process, collector):
    for proc in process.previous_processes():
        collector.append(proc)
        previous_process_collector(proc, collector)
    return collector


class Process(models.Model):
    process_type = models.ForeignKey(ProcessType)
    process_date = models.DateField()
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ('process_date',)
        verbose_name_plural = "Processes"

    def __unicode__(self):
        return " ".join([
            self.process_type.name,
            self.input_lot_id()
            #self.process_date.strftime('%Y-%m-%d')
            ])


    def inputs(self):
        return self.inventory_transactions.filter(transaction_type="Issue")

    def outputs(self):
        return self.inventory_transactions.filter(transaction_type="Production")

    def services(self):
        return self.service_transactions.all()

    def invoiced_services(self):
        return self.service_transactions.filter(service_type__invoiced_separately=True)

    def input_lot_id(self):
        inputs = self.inventory_transactions.filter(transaction_type="Issue")
        try:
            return inputs[0].inventory_item.lot_id()
        except:
            return ""

    def output_lot_ids(self):
        answer = ""
        outputs = self.inventory_transactions.filter(transaction_type="Production")
        lot_ids = []
        for output in outputs:
            lot_ids.append(output.inventory_item.lot_id())
        answer = ", ".join(lot_ids)
        return answer

    def next_processes(self):
        processes = []
        for output in self.outputs():
            lot = output.inventory_item
            for issue in lot.inventorytransaction_set.filter(transaction_type="Issue"):
                if issue.process:
                    processes.append(issue.process)
        return processes

    def previous_processes_recursive(self):
        processes = previous_process_collector(self, []) 
        return processes 

    def previous_processes(self):
        processes = []
        for inp in self.inputs():
            lot = inp.inventory_item
            for tx in lot.inventorytransaction_set.filter(transaction_type="Production"):
                if tx.process:
                    processes.append(tx.process)
        return processes 

    def previous_process(self):       
        # for PBC now, processes will have one or None previous_processes
        processes = self.previous_processes()
        if processes:
            return processes[0]
        else:
            return None

    def service_cost(self):
        cost = Decimal("0")
        for s in self.services():
            cost += s.amount
        return cost

    def invoiced_service_cost(self):
        cost = Decimal("0")
        for s in self.invoiced_services():
            cost += s.amount
        return cost

    def unit_service_cost(self):
        """ Allocating the same cost to each output unit 
        """
        cost = self.service_cost()
        output = sum(op.amount for op in self.outputs())
        return cost / output

    def cumulative_service_cost(self):
        cost = self.service_cost()
        for proc in self.previous_processes_recursive():
            cost += proc.service_cost()
        return cost

    def cumulative_unit_service_cost(self):
        """ Allocating the same cost to each output unit 
        """
        cost = self.cumulative_service_cost()
        output = sum(op.amount for op in self.outputs())
        return cost / output

    def cumulative_invoiced_service_cost(self):
        cost = self.invoiced_service_cost()
        for proc in self.previous_processes_recursive():
            cost += proc.invoiced_service_cost()
        return cost

    def cumulative_invoiced_unit_service_cost(self):
        """ Allocating the same cost to each output unit 
        """
        cost = self.cumulative_invoiced_service_cost()
        output = sum(op.amount for op in self.outputs())
        return cost / output

    def cumulative_services(self):
        svs = list(self.services())
        for proc in self.previous_processes_recursive():
            svs.extend(proc.services())
        return svs

    def is_deletable(self):
        answer = True
        for output in self.outputs():
            lot = output.inventory_item
            other_types = ["Issue", "Delivery", "Damage", "Reject", "Receipt", "Transfer"]
            if lot.inventorytransaction_set.filter(transaction_type__in=other_types).count() > 0:
                answer = False
        return answer


TX_TYPES = (
    ('Receipt', 'Receipt'),         # inventory was received from outside the system
    ('Delivery', 'Delivery'),       # inventory was delivered to a customer
    ('Transfer', 'Transfer'),       # combination delivery and receipt inside the system
    ('Issue', 'Issue'),             # a process consumed inventory
    ('Production', 'Production'),   # a process created inventory
    ('Damage', 'Damage'),           # inventory was damaged and must be paid for
    ('Reject', 'Reject'),           # inventory was rejected by a customer and does not need to be paid for
)

class InventoryTransaction(EconomicEvent):
    transaction_type = models.CharField(max_length=10, choices=TX_TYPES, default='Delivery')
    inventory_item = models.ForeignKey(InventoryItem)
    process = models.ForeignKey(Process, blank=True, null=True, related_name='inventory_transactions')
    order_item = models.ForeignKey(OrderItem, blank=True, null=True)
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)

    def __unicode__(self):
        if self.order_item:
            label = ' '.join(['Order Item:', str(self.order_item)])
        else:
            label = ' '.join(['Type:', self.transaction_type])
        return " ".join([
            label, 
            'Inventory Item:', str(self.inventory_item), 
            'Qty:', str(self.amount)])
        
    def save(self, force_insert=False, force_update=False):
        initial_qty = Decimal("0")
        if self.pk:
            prev_state = InventoryTransaction.objects.get(pk=self.pk)
            initial_qty = prev_state.amount
        else:
            if self.order_item:
                self.unit_price = self.order_item.unit_price
            else:
                self.unit_price = self.inventory_item.product.price
        super(InventoryTransaction, self).save(force_insert, force_update)
        qty_delta = self.amount - initial_qty
        if self.transaction_type=="Receipt" or self.transaction_type=="Production":
            self.inventory_item.update_from_transaction(qty_delta)
        else:
            self.inventory_item.update_from_transaction(-qty_delta)
        if self.order_item:
            if self.transaction_type=="Delivery":
                self.order_item.order.register_delivery()
        
    def delete(self):
        #todo: admin deletes do not call this delete method
        # need a signal or something...
        if self.transaction_type=="Receipt" or self.transaction_type=="Production":
            self.inventory_item.update_from_transaction(-self.amount)
        else:
            self.inventory_item.update_from_transaction(self.amount)
        super(InventoryTransaction, self).delete()
        
    def order_customer(self):
        return self.order_item.order.customer
    
    def product(self):
        return self.inventory_item.product
    
    def producer(self):
        return self.inventory_item.producer
    
    def inventory_date(self):
        return self.inventory_item.inventory_date
    
    def due_to_member(self):
        if self.transaction_type=='Reject' or self.transaction_type=="Production" :
            return Decimal(0)
        if not self.inventory_item.product.pay_producer:
            return Decimal(0)
        
        fee = producer_fee()
        #unit_price = self.unit_price
        return (self.unit_price * self.amount * (1 - fee)).quantize(Decimal('.01'), rounding=ROUND_UP)

    def is_due(self):
        if not self.due_to_member():
            return False
        if self.inventory_item.product.pay_producer_on_terms:
            term_days = member_terms()
            due_date = self.transaction_date + datetime.timedelta(days=term_days)
            if datetime.date.today() >= due_date:
                return True
            else:
                return False
        else:
            if self.order_item:
                return self.order_item.order.is_paid()
            else:
                return False

    def should_be_paid(self):
        if self.is_paid():
            return False
        return self.is_due()

    def extended_producer_fee(self):
        if self.order_item:
            return self.order_item.extended_producer_fee()
        else:
            unit_price = self.unit_price
            answer = self.amount * unit_price * producer_fee()
            return answer.quantize(Decimal('.01'), rounding=ROUND_UP)
    
    def service_cost(self):
        cost = Decimal(0)
        item = self.inventory_item
        for tx in item.inventorytransaction_set.filter(transaction_type="Production"):
            cost += self.amount * tx.process.cumulative_unit_service_cost()
        return cost

    def invoiced_service_cost(self):
        cost = Decimal(0)
        item = self.inventory_item
        for tx in item.inventorytransaction_set.filter(transaction_type="Production"):
            cost += self.amount * tx.process.cumulative_invoiced_unit_service_cost()
        return cost

    def services(self):
        svs = []
        item = self.inventory_item
        for tx in item.inventorytransaction_set.filter(transaction_type="Production"):
            svs.extend(list(tx.process.cumulative_services()))
        return svs

    class Meta:
        ordering = ('-transaction_date',)


class ServiceTransaction(EconomicEvent):
    service_type = models.ForeignKey(ServiceType)
    process = models.ForeignKey(Process, related_name='service_transactions')


    def __unicode__(self):
        return " ".join([
            self.service_type.name,
            self.from_whom.long_name,
            ])

    def order_paid(self):
        # todo: shd be recursive for next processes?
        for output in self.process.outputs():
            for delivery in output.inventory_item.deliveries():
                if delivery.order_item.order.is_paid():
                    return True
        return False

    def is_due(self):
        if self.service_type.pay_provider_on_terms:
            term_days = member_terms()
            due_date = self.transaction_date + datetime.timedelta(days=term_days)
            if datetime.date.today() >= due_date:
                return True
            else:
                return False
        else:
            return self.order_paid()

    def should_be_paid(self):
        if self.is_paid():
            return False
        return self.is_due()


    def downstream_orders(self):
        # todo: shd be recursive for next processes
        orders = []
        for output in self.process.outputs():
            for delivery in output.inventory_item.deliveries():
                orders.append(delivery.order_item.order)
        return orders
        
    def order_string(self):
        os = []
        for order in self.downstream_orders():
            os.append("".join([" #", str(order.id), ":", order.customer.short_name]))
        os = list(set(os))
        os_string = ", ".join(os)
        return os_string

    def delivered_items(self):
        # todo: shd be recursive for next processes
        items = []
        for output in self.process.outputs():
            items.append(output.inventory_item)
        return items

    def product_string(self):
        ps = []
        for item in self.delivered_items():
            ps.append(item.product.short_name)
        ps = list(set(ps))
        ps_string = ", ".join(ps)
        return ps_string

    def due_to_member(self):
        return self.amount.quantize(Decimal('.01'), rounding=ROUND_UP)


class TransportationTransaction(EconomicEvent):
    service_type = models.ForeignKey(ServiceType)
    order = models.ForeignKey(Order)

    def __unicode__(self):
        return " ".join([
            self.service_type.name,
            self.from_whom.long_name,
            "for",
            unicode(self.order),
            ])

    def save(self, force_insert=False, force_update=False):
        if not self.pk:
            tt, created = ServiceType.objects.get_or_create(name="Transportation")
            self.service_type = tt
        super(TransportationTransaction, self).save(force_insert, force_update)

    def should_be_paid(self):
        if self.is_paid():
            return False
        return self.order.is_paid()

    def is_due(self):
        return self.order.is_paid()

    def due_to_member(self):
        return self.amount.quantize(Decimal('.01'), rounding=ROUND_UP)

