import datetime
import time

from django.db.models import Q
from django.http import Http404
from django.views.generic import list_detail
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.template import RequestContext
from django.http import HttpResponse
from django.core import serializers
from django.contrib.auth.decorators import login_required
from django.core.exceptions import MultipleObjectsReturned
from django.core.mail import send_mail
from django.forms.models import inlineformset_factory

from distribution.models import *
from customer.forms import *
from customer.view_helpers import *
from distribution.view_helpers import plan_weeks, create_weekly_plan_forms

try:
    from notification import models as notification
except ImportError:
    notification = None


def customer_dashboard(request):
    food_network = FoodNetwork.objects.get(pk=1)
    #todo: all uses of the next statement shd be changed
    customer = request.user.parties.all()[0].party
    return render_to_response('customer/customer_dashboard.html', 
        {'customer': customer,
         'food_network': food_network,
         }, context_instance=RequestContext(request))

def order_selection(request):
    food_network = FoodNetwork.objects.get(pk=1)
    customer = request.user.parties.all()[0].party
    selection_form = NewOrderSelectionForm(customer, data=request.POST or None)

    if request.method == "POST":
        if selection_form.is_valid():
            sf_data = selection_form.cleaned_data
            ord_date = sf_data['order_date']
            return HttpResponseRedirect('/%s/%s/%s/%s/%s/'
               % ('customer/neworder', customer.id, ord_date.year, ord_date.month, ord_date.day))

    return render_to_response('customer/order_selection.html', 
        {'customer': customer,
         'food_network': food_network,
         'selection_form': selection_form,
         }, context_instance=RequestContext(request))

def list_selection(request):
    food_network = FoodNetwork.objects.get(pk=1)
    customer = request.user.parties.all()[0].party
    product_lists = MemberProductList.objects.filter(member=customer)
    return render_to_response('customer/list_selection.html', 
        {'customer': customer,
         'food_network': food_network,
         'product_lists': product_lists,
         }, context_instance=RequestContext(request))

def history_selection(request):
    food_network = FoodNetwork.objects.get(pk=1)
    customer = request.user.parties.all()[0].party
    return render_to_response('customer/history_selection.html', 
        {'customer': customer,
         'food_network': food_network,
         }, context_instance=RequestContext(request))

def plan_selection(request):
    food_network = FoodNetwork.objects.get(pk=1)
    customer = request.user.parties.all()[0].party
    if request.method == "POST":
        psform = MemberPlanSelectionForm(request.POST)  
        if psform.is_valid():
            psdata = psform.cleaned_data
            from_date = psdata['plan_from_date'].strftime('%Y_%m_%d')
            to_date = psdata['plan_to_date'].strftime('%Y_%m_%d')
            list_type = psdata['list_type']
            return HttpResponseRedirect('/%s/%s/%s/%s/%s/'
                % ('customer/planningtable', customer.id, list_type, from_date, to_date))
    else:
        from_date = datetime.date.today()
        # force from_date to Monday, to_date to Sunday
        from_date = from_date - datetime.timedelta(days=datetime.date.weekday(from_date))
        to_date = from_date + datetime.timedelta(weeks=16)
        to_date = to_date - datetime.timedelta(days=datetime.date.weekday(to_date)+1)
        to_date = to_date + datetime.timedelta(days=7)
        plan_init = {
            'plan_from_date': from_date,
            'plan_to_date': to_date,
            'list_type': 'M',
        }
        psform = MemberPlanSelectionForm(initial=plan_init)

    return render_to_response('customer/plan_selection.html', 
        {'customer': customer,
         'plan_form': psform,
         'food_network': food_network,
         }, context_instance=RequestContext(request))

@login_required
def new_product_list(request, cust_id):
    try:
        customer = Party.objects.get(pk=cust_id)
    except Party.DoesNotExist:
        raise Http404
    list_form = ProductListForm(data=request.POST or None)
    form_list = create_new_product_list_forms(data=request.POST or None)
    return render_to_response('customer/new_product_list.html', 
        {'customer': customer,
         'list_form': list_form,
         'form_list': form_list,
         }, context_instance=RequestContext(request))


@login_required
def edit_product_list(request, list_id):
    try:
        plist = MemberProductList.objects.get(pk=list_id)
    except MemberProductList.DoesNotExist:
        raise Http404
    list_form = ProductListForm(data=request.POST or None, instance=plist)
    ProductListInlineFormSet = inlineformset_factory(
        MemberProductList, CustomerProduct)
    formset = ProductListInlineFormSet(instance=plist)
    return render_to_response('customer/edit_product_list.html', 
        {'customer': plist.member,
         'list_form': list_form,
         'formset': formset,
         }, context_instance=RequestContext(request))


@login_required
def planning_table(request, member_id, list_type, from_date, to_date):
    try:
        member = Party.objects.get(pk=member_id)
    except Party.DoesNotExist:
        raise Http404
    role = "producer"
    plan_type = "Production"
    if member.is_customer():
        role = "consumer"
        plan_type = "Consumption"

    try:
        from_date = datetime.datetime(*time.strptime(from_date, '%Y_%m_%d')[0:5]).date()
        to_date = datetime.datetime(*time.strptime(to_date, '%Y_%m_%d')[0:5]).date()
    except ValueError:
            raise Http404
    # force from_date to Monday, to_date to Sunday
    from_date = from_date - datetime.timedelta(days=datetime.date.weekday(from_date))
    to_date = to_date - datetime.timedelta(days=datetime.date.weekday(to_date)+1)
    to_date = to_date + datetime.timedelta(days=7)
    products = None
    if list_type == "M":
        if role == "consumer":
            products = CustomerProduct.objects.filter(customer=member, planned=True)
        else:
            products = ProducerProduct.objects.filter(producer=member, planned=True)
    if not products:
        products = Product.objects.filter(plannable=True)
        list_type = "A"
    plan_table = plan_weeks(member, products, from_date, to_date)
    forms = create_weekly_plan_forms(plan_table.rows, data=request.POST or None)
    if request.method == "POST":
        #import pdb; pdb.set_trace()
        for row in forms:
            if row.formset.is_valid():
                for form in row.formset.forms:
                    data = form.cleaned_data
                    qty = data['quantity']
                    plan_id = data['plan_id']
                    from_dt = data['from_date']
                    to_dt = data['to_date']
                    product_id = data['product_id']
                    plan = None
                    if plan_id:
                        # what if plan was changed by prev cell?
                        plan = ProductPlan.objects.get(id=plan_id)
                        if plan.to_date < from_dt or plan.from_date > to_dt:
                            plan = None
                    if qty:
                        if plan:
                            #import pdb; pdb.set_trace()
                            if not qty == plan.quantity:
                                #import pdb; pdb.set_trace()
                                if plan.from_date >= from_dt and plan.to_date <= to_dt:
                                    plan.quantity = qty
                                    plan.save()
                                else:
                                    if plan.from_date < from_dt:
                                        new_to_dt = from_dt - datetime.timedelta(days=1)
                                        earlier_plan = ProductPlan(
                                            member=plan.member,
                                            product=plan.product,
                                            quantity=plan.quantity,
                                            from_date=plan.from_date,
                                            to_date=new_to_dt,
                                            role=plan.role,
                                            inventoried=plan.inventoried,
                                            distributor=plan.distributor,
                                        )
                                        earlier_plan.save()
                                    if plan.to_date > to_dt:
                                        new_plan = ProductPlan(
                                            member=plan.member,
                                            product=plan.product,
                                            quantity=qty,
                                            from_date=from_dt,
                                            to_date=to_dt,
                                            role=plan.role,
                                            inventoried=plan.inventoried,
                                            distributor=plan.distributor,
                                        )
                                        new_plan.save()
                                        plan.from_date = to_dt + datetime.timedelta(days=1)
                                        plan.save()
                                    else:
                                        plan.from_date=from_dt
                                        plan.quantity=qty
                                        plan.save()      
                        else:
                            product = Product.objects.get(id=product_id)
                            new_plan = ProductPlan(
                                member=member,
                                product=product,
                                quantity=qty,
                                from_date=from_dt,
                                to_date=to_dt,
                                role=role,
                                #inventoried=True,
                                #distributor,
                            )
                            new_plan.save()
                            #import pdb; pdb.set_trace()
                            if role == "producer":
                                listed_product, created = ProducerProduct.objects.get_or_create(
                                    product=product, producer=member)
                            elif role == "consumer":
                                #todo: shd these be auto-created at all?
                                # and if so, what MemberProductList?
                                listed_product, created = CustomerProduct.objects.get_or_create(
                                    product=product, customer=member)

                    else:
                        if plan:
                            if plan.from_date >= from_dt and plan.to_date <= to_dt:
                                #pass
                                plan.delete()
                            else:
                                #import pdb; pdb.set_trace()
                                if plan.to_date > to_dt:
                                    early_from_dt = plan.from_date              
                                    if plan.from_date < from_dt:
                                        early_to_dt = from_dt - datetime.timedelta(days=1)
                                        earlier_plan = ProductPlan(
                                            member=plan.member,
                                            product=plan.product,
                                            quantity=plan.quantity,
                                            from_date=early_from_dt,
                                            to_date=early_to_dt,
                                            role=plan.role,
                                            inventoried=plan.inventoried,
                                            distributor=plan.distributor,
                                         )
                                        earlier_plan.save()
                                    plan.from_date = to_dt + datetime.timedelta(days=1)
                                    plan.save()
                                else:
                                    plan.to_date= from_dt - datetime.timedelta(days=1)
                                    plan.save()
        from_date = from_date.strftime('%Y_%m_%d')
        to_date = to_date.strftime('%Y_%m_%d')
        return HttpResponseRedirect('/%s/%s/%s/%s/'
                    % ('distribution/membersupplydemand', from_date, to_date, member_id))
    return render_to_response('distribution/planning_table.html', 
        {
            'from_date': from_date,
            'to_date': to_date,
            'plan_table': plan_table,
            'forms': forms,
            'plan_type': plan_type,
            'member': member,
            'list_type': list_type,
            'tabnav': "customer/customer_tabnav.html",
            'nav_class': 'plans',
        })


#todo: split order_update into
# new_order
# change_order
# order_update(request, order)
# Q: do new and change need to do redirect, render_to_response, etc? 

@login_required
def new_order(request, cust_id, year, month, day):
    orderdate = datetime.date(int(year), int(month), int(day))
    availdate = orderdate

    order = None

    try:
        customer = Customer.objects.get(pk=int(cust_id))
    except Customer.DoesNotExist:
        raise Http404

    if request.method == "POST":
        ordform = OrderForm(data=request.POST)
        #import pdb; pdb.set_trace()
        itemforms = create_order_item_forms(order, availdate, orderdate, request.POST)     
        if ordform.is_valid() and all([itemform.is_valid() for itemform in itemforms]):
            the_order = ordform.save(commit=False)
            the_order.customer = customer
            the_order.order_date = orderdate
            the_order.save()

            update_order(order, itemforms)
            return HttpResponseRedirect('/%s/%s/'
               % ('customer/order', the_order.id))
    else:
        ordform = OrderForm(initial={'customer': customer, 'order_date': orderdate, })
        itemforms = create_order_item_forms(order, availdate, orderdate)
    return render_to_response('customer/order_update.html', 
        {'customer': customer, 
         'order': order, 
         'order_date': orderdate, 
         'avail_date': availdate, 
         'order_form': ordform, 
         'item_forms': itemforms}, context_instance=RequestContext(request))


@login_required
def change_order(request, order_id):
    try:
        order = Order.objects.get(id=int(order_id))
    except Order.DoesNotExist:
        raise Http404

    order_update(request, order.order_date, order.customer, order)

def update_order(order, itemforms):
    transportation_fee = order.transportation_fee
    distributor = order.distributor
    #import pdb; pdb.set_trace()
    if transportation_fee:
        transportation_tx = None
        try:
            transportation_tx = TransportationTransaction.objects.get(order=order)
            if transportation_fee != transportation_tx.amount:
                transportation_tx.amount = transportation_fee
                transportation_tx.save()
        except TransportationTransaction.DoesNotExist:
            pass
        if not transportation_tx:
            transportation_tx = TransportationTransaction(
                from_whom=distributor,
                to_whom=customer,
                order=the_order, 
                amount=transportation_fee,
                transaction_date=orderdate)
            transportation_tx.save()

    for itemform in itemforms:
        data = itemform.cleaned_data
        qty = data['quantity'] 
        if itemform.instance.id:
            if qty > 0:
                itemform.save()
            else:
                itemform.instance.delete()
        else:                    
            if qty > 0:
                # these product gyrations wd not be needed if I cd make the product field readonly
                # or display the product field value (instead of the input widget) in the template
                #todo: change to product_id
                prod_id = data['prod_id']
                product = Product.objects.get(id=prod_id)
                oi = itemform.save(commit=False)
                oi.order = the_order
                oi.product = product
                oi.save()
    return True

@login_required
def order_update(request, orderdate, customer, order=None):
    availdate = orderdate

    if request.method == "POST":
        if order:
            ordform = OrderForm(order=order, data=request.POST, instance=order)
        else:
            ordform = OrderForm(data=request.POST)
        #import pdb; pdb.set_trace()
        itemforms = create_order_item_forms(order, availdate, orderdate, request.POST)     
        if ordform.is_valid() and all([itemform.is_valid() for itemform in itemforms]):
            if order:
                the_order = ordform.save()
            else:
                the_order = ordform.save(commit=False)
                the_order.customer = customer
                the_order.order_date = orderdate
                the_order.save()

            order_data = ordform.cleaned_data
            transportation_fee = order_data["transportation_fee"]
            distributor = order_data["distributor"]
            #import pdb; pdb.set_trace()
            if transportation_fee:
                transportation_tx = None
                if order:
                    try:
                        transportation_tx = TransportationTransaction.objects.get(order=order)
                        if transportation_fee != transportation_tx.amount:
                            transportation_tx.amount = transportation_fee
                            transportation_tx.save()
                    except TransportationTransaction.DoesNotExist:
                        pass
                if not transportation_tx:
                    transportation_tx = TransportationTransaction(
                        from_whom=distributor,
                        to_whom=customer,
                        order=the_order, 
                        amount=transportation_fee,
                        transaction_date=orderdate)
                    transportation_tx.save()

            for itemform in itemforms:
                data = itemform.cleaned_data
                qty = data['quantity'] 
                if itemform.instance.id:
                    if qty > 0:
                        itemform.save()
                    else:
                        itemform.instance.delete()
                else:                    
                    if qty > 0:
                        # these product gyrations wd not be needed if I cd make the product field readonly
                        # or display the product field value (instead of the input widget) in the template
                        prod_id = data['prod_id']
                        product = Product.objects.get(id=prod_id)
                        oi = itemform.save(commit=False)
                        oi.order = the_order
                        oi.product = product
                        oi.save()
            return HttpResponseRedirect('/%s/%s/'
               % ('customer/order', the_order.id))
    else:
        if order:
            ordform = OrderForm(order=order, instance=order)
        else:
            ordform = OrderForm(initial={'customer': customer, 'order_date': orderdate, })
        itemforms = create_order_item_forms(order, availdate, orderdate)
    return render_to_response('customer/order_update.html', 
        {'customer': customer, 'order': order, 'order_date': orderdate, 'avail_date': availdate, 'order_form': ordform, 'item_forms': itemforms})



