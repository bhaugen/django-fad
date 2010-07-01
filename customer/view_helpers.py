from django.forms.formsets import formset_factory

from distribution.models import *

from customer.forms import *

def create_new_product_list_forms(data=None):
    #todo: shd these be plannable instead of sellable?
    products = list(Product.objects.filter(sellable=True))
    #CustomerProductFormSet = formset_factory(CustomerProductForm, extra=0)
    form_list = []
    for prod in products:
        prod.parents = prod.parent_string()
    products.sort(lambda x, y: cmp(x.parents, y.parents))
    for prod in products:
        form = CustomerProductForm(data, prefix=prod.id, initial={
            'prod_id': prod.id, 
        })
        form.product_name = prod.long_name
        form.category = prod.parents
        form_list.append(form)
    return form_list


def create_edit_product_list_forms(customer, data=None):
    return


def create_order_item_forms(order, availdate, orderdate, data=None):
    form_list = []
    item_dict = {}
    if order:
        items = order.orderitem_set.all()
        for item in items:
            item_dict[item.product.id] = item
    prods = list(Product.objects.filter(sellable=True))
    for prod in prods:
        prod.parents = prod.parent_string()
    prods.sort(lambda x, y: cmp(x.parents, y.parents))
    for prod in prods:
        totavail = prod.total_avail(availdate)
        totordered = prod.total_ordered(orderdate)
        try:
            item = item_dict[prod.id]
        except KeyError:
            item = False
        if item:
            #todo: these fields shd be form initial data 
            # (or can they be? got an instance)
            # cd also use formsets - see d.view_helpers.create_weekly_plan_forms
            # Can't find an example of instance + initial in a ModelForm in my
            # code, but see http://django-reversion.googlecode.com/svn/tags/1.1.2/src/reversion/admin.py
            # ModelForm(request.POST, request.FILES, instance=obj, initial=self.get_revision_form_data(request, obj, version))
            producers = prod.avail_producers(availdate)
            # maybe like this?
            initial_data = {
                'prod_id': prod.id,
                'avail': totavail,
                'ordered': totordered,
            }
            oiform = OrderItemForm(data, prefix=prod.id, instance=item,
                                   initial=initial_data)
            #oiform.fields['prod_id'].widget.attrs['value'] = prod.id
            #oiform.fields['avail'].widget.attrs['value'] = totavail
            #oiform.fields['ordered'].widget.attrs['value'] = totordered
            oiform.producers = producers
            oiform.description = prod.long_name
            oiform.parents = prod.parents
            form_list.append(oiform)
        else:
            if totavail > 0:
                producers = prod.avail_producers(availdate)
                oiform = OrderItemForm(data, prefix=prod.id, initial={
                    'parents': prod.parents, 
                    'prod_id': prod.id, 
                    'description': prod.long_name, 
                    'avail': totavail, 
                    'ordered': totordered, 
                    'unit_price': prod.price, 
                    'quantity': 0})
                oiform.description = prod.long_name
                oiform.producers = producers
                oiform.parents = prod.parents
                form_list.append(oiform)
    return form_list

