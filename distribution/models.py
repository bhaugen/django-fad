from django.db import models
import datetime
from decimal import *
from django.db.models import Q
from django.contrib.localflavor.us.models import PhoneNumberField
from django.contrib.contenttypes.models import ContentType
from django.db.models.query import QuerySet
import itertools


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
         

class FoodNetwork(Party):
    billing_contact = models.CharField(max_length=64, blank=True)
    billing_phone = PhoneNumberField(blank=True, null=True)
    billing_address = models.CharField(max_length=96, blank=True, null=True, 
            help_text='Enter commas only where you want to split address lines for formatting.')
    billing_email_address = models.EmailField(max_length=96, blank=True, null=True)
    customer_terms = models.IntegerField(blank=True, null=True,
        help_text='Net number of days for customer to pay invoice')
    member_terms = models.IntegerField(blank=True, null=True,
        help_text='Net number of days for network to pay member')
    customer_fee = models.DecimalField(max_digits=3, decimal_places=2, 
        help_text='Fee is a decimal fraction, not a percentage - for example, .05 instead of 5%')
    producer_fee = models.DecimalField(max_digits=3, decimal_places=2, 
        help_text='Fee is a decimal fraction, not a percentage - for example, .05 instead of 5%') 
    # next 2 fields are obsolete   
    charge = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True,
        help_text='Charge will be added to all orders unless overridden on the Customer')
    charge_name = models.CharField(max_length=32, blank=True, default='Delivery charge')
    current_week = models.DateField(default=datetime.date.today, 
        help_text='Current week for operations availability and orders')
    order_by_lot = models.BooleanField(default=False, 
        help_text='Assign lots when ordering, or assign them later')

    def __unicode__(self):
        return self.short_name
    def formatted_billing_address(self):
        return self.billing_address.split(',')
    
    @property
    def email(self):
        return self.email_address

    class Meta:
        ordering = ('short_name',)

    
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
    is_parent = models.BooleanField(default=False,
        help_text='Should this product appear in parent selections?')
    price = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal(0))
    customer_fee_override = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True, 
        help_text='Enter override as a decimal fraction, not a percentage - for example, .05 instead of 5%. Note: you cannot override to zero here, only on Order Items.')
    pay_producer = models.BooleanField(default=True,
        help_text='If checked, the Food Network pays the producer for issues, deliveries and damages of this product.')
    pay_producer_on_terms = models.BooleanField(default=True,
        help_text='If checked, producer paid on member terms. If not, producers paid based on customer order payments. Note: Issues always paid on member terms.')
    expiration_days = models.IntegerField(default=6,
        help_text='Inventory Items (Lots) of this product will expire in this many days.')

    def __unicode__(self):
        return self.long_name
    
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
    
    def deliveries_this_week(self, thisdate):
        weekstart = thisdate - datetime.timedelta(days=datetime.date.weekday(thisdate))
        weekend = weekstart + datetime.timedelta(days=5)
        deliveries = InventoryTransaction.objects.filter(transaction_type="Delivery")
        return deliveries.filter(
            order_item__product=self, transaction_date__range=(weekstart, weekend))
    
    def total_delivered(self, thisdate):
        deliveries = self.deliveries_this_week(thisdate)
        return sum(delivery.quantity for delivery in deliveries)
    
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

    class Meta:
        ordering = ('short_name',)

PLAN_ROLE_CHOICES = (
    ('consumer', 'consumer'),
    ('producer', 'producer'),
)


class SupplyDemandTable(object):
    def __init__(self, columns, rows):
         self.columns = columns
         self.rows = rows

def supply_demand_table(from_date, to_date):
    plans = ProductPlan.objects.filter(product__sellable=True)
    rows = {}    
    for plan in plans:
        wkdate = from_date
        row = []
        while wkdate <= to_date:
            row.append(Decimal("0"))
            wkdate = wkdate + datetime.timedelta(days=7)
        row.insert(0, plan.product)
        rows.setdefault(plan.product, row)
        wkdate = from_date
        week = 0
        while wkdate <= to_date:
            if plan.from_date <= wkdate and plan.to_date >= wkdate:
                if plan.role == "producer":
                    rows[plan.product][week + 1] += plan.quantity
                else:
                    rows[plan.product][week + 1] -= plan.quantity
            wkdate = wkdate + datetime.timedelta(days=7)
            week += 1
    label = "Product/Weeks"
    columns = [label]
    wkdate = from_date
    while wkdate <= to_date:
        #columns.append(wkdate.strftime('%m-%d'))
        columns.append(wkdate)
        wkdate = wkdate + datetime.timedelta(days=7)
    sdtable = SupplyDemandTable(columns, rows.values())
    return sdtable

def supply_demand_week(week_date):
    plans = ProductPlan.objects.filter(
        product__sellable=True,
        from_date__lte=week_date,
        to_date__gte=week_date,
    )
    columns = []
    rows = {}
    for plan in plans:
        columns.append(plan.member)
    columns = list(set(columns))
    columns.sort(lambda x, y: cmp(x.short_name, y.short_name))
    columns.insert(0, "Product/Member")
    columns.append("Balance")
    for plan in plans:
        if not rows.get(plan.product):
            row = []
            for i in range(0, len(columns)-1):
                row.append(Decimal("0"))
            row.insert(0, plan.product)
            rows[plan.product] = row
        if plan.role == "producer":
            rows[plan.product][columns.index(plan.member)] += plan.quantity
            rows[plan.product][len(columns)-1] += plan.quantity
        else:
            rows[plan.product][columns.index(plan.member)] -= plan.quantity
            rows[plan.product][len(columns)-1] -= plan.quantity
    rows = rows.values()
    rows.sort(lambda x, y: cmp(x[0].short_name, y[0].short_name))
    sdtable = SupplyDemandTable(columns, rows)
    return sdtable


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
            self.from_date.strftime('%Y-%m-%d'),
            str(self.quantity)])
        
    class Meta:
        ordering = ('product', 'member', 'from_date')
        

class InventoryItem(models.Model):
    producer = models.ForeignKey(Party, related_name="inventory_items") 
    custodian = models.ForeignKey(Party, blank=True, null=True, related_name="custody_items")
    product = models.ForeignKey(Product, limit_choices_to = {'plannable': True})
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
        return " ".join([
            self.producer.member_id,
            self.producer.short_name,
            self.product.long_name,
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
    """ In REA terms, this is a Duality
        but always assuming money in payment.
    """
    paid_event = models.ForeignKey(EconomicEvent, related_name="transaction_payments")
    payment = models.ForeignKey(Payment, related_name="paid_events")
    amount_paid = models.DecimalField(max_digits=8, decimal_places=2)


class Order(models.Model):
    customer = models.ForeignKey(Customer) 
    order_date = models.DateField()
    distributor = models.ForeignKey(Party, blank=True, null=True, related_name="orders")
    paid = models.BooleanField(default=False, verbose_name="Order paid")

    def __unicode__(self):
        return ' '.join([self.order_date.strftime('%Y-%m-%d'), self.customer.short_name])
    
    def delete(self):
        deliveries = InventoryTransaction.objects.filter(order_item__order=self) 
        for delivery in deliveries:
            delivery.delete()
        super(Order, self).delete()
    
    def charge_name(self):
        return charge_name()
    
    def charge(self):
        return self.customer.order_charge()

    def transportation_fee(self):
        try:
            transportation_tx = TransportationTransaction.objects.get(order=self)
            return transportation_tx.amount
        except TransportationTransaction.DoesNotExist:
            return Decimal("0")
    
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
        

    class Meta:
        ordering = ('order_date', 'customer')


class OrderItem(models.Model):
    order = models.ForeignKey(Order)
    product = models.ForeignKey(Product)
    quantity = models.DecimalField(max_digits=8, decimal_places=2)
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
        
    def producer_fee(self):
        return producer_fee()
    
    def extended_producer_fee(self):
        answer = self.quantity * self.unit_price * producer_fee()
        return answer.quantize(Decimal('.01'), rounding=ROUND_UP)
    
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
        
    def delete(self):
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
                return self.order_item.order.paid
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
                if delivery.order_item.order.paid:
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
        return self.order.paid

    def is_due(self):
        return self.order.paid

    def due_to_member(self):
        return self.amount.quantize(Decimal('.01'), rounding=ROUND_UP)

