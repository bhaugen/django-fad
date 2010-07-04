from django.conf.urls.defaults import *
from django.conf import settings
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('',
    url(r'^customerdashboard/$', "customer.views.customer_dashboard", name="customer_dashboard"),
    url(r'^orderselection/$', "customer.views.order_selection", name="customer_order_selection"),
    url(r'^neworder/(?P<cust_id>\d+)/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/(?P<list_id>\d+)/$',
        "customer.views.new_order", name="new_order"),
    url(r'^changeorder/(?P<order_id>\d+)/$', "customer.views.edit_order",
        name="edit_order"),
    url(r'^deleteorderconfirmation/(?P<order_id>\d+)/$',
        "customer.views.delete_order_confirmation", name="delete_order_confirmation"),
    url(r'^deleteorder/(?P<order_id>\d+)/$', "customer.views.delete_order",
        name="delete_order"),
    url(r'^order/(?P<order_id>\d+)/$', "customer.views.order", name="order"),
    url(r'^listselection/$', "customer.views.list_selection", name="list_selection"),
    url(r'^historyselection/$', "customer.views.history_selection", name="history_selection"),
    url(r'^planselection/$', "customer.views.plan_selection", name="plan_selection"),
    url(r'^planningtable/(?P<member_id>\d+)/(?P<list_type>\w{1})/(?P<from_date>\w{10})/(?P<to_date>\w{10})/$', 
        "customer.views.planning_table", name='customer_planning_table'),
    url(r'^newproductlist/(?P<cust_id>\d+)/$',
        "customer.views.new_product_list", name="create_product_list"),
    url(r'^editproductlist/(?P<list_id>\d+)/$',
        "customer.views.edit_product_list", name="edit_product_list"),

)

