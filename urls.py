from django.conf.urls.defaults import *
from distribution.views import *
from django.conf import settings
from django.views.generic.simple import direct_to_template
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^dashboard/$', dashboard, name="dashboard"),
    (r'^admin/(.*)', admin.site.root),
    url(r'^orderdeliveries/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', orders_with_deliveries),
    (r'^orderselection/$', order_selection),
    url(r'^orderupdate/(?P<cust_id>\d+)/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', order_update),
    url(r'^orderbylot/(?P<cust_id>\d+)/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', order_by_lot),
    (r'^orderentry/$', order_entry),
    url(r'^order/(?P<order_id>\d+)/$', order),
    url(r'^orderwithlots/(?P<order_id>\d+)/$', order_with_lots),
    (r'^planselection/$', plan_selection),
    url(r'^processselection/$', process_selection, name="process_selection"),
    url(r'^newprocess/(?P<process_type_id>\d+)/$', new_process),
    url(r'^process/(?P<process_id>\d+)/$', process, name="process"),
    url(r'^deleteprocessconfirmation/(?P<process_id>\d+)/$', delete_process_confirmation, name="delete_process_confirmation"),
    url(r'^deleteprocess/(?P<process_id>\d+)/$', delete_process, name="delete_process"),
    url(r'^editprocess/(?P<process_id>\d+)/$', edit_process, name="edit_process"),
    url(r'^planupdate/(?P<prod_id>\d+)/$', plan_update),
    url(r'^planningtable/(?P<member_id>\d+)/(?P<list_type>\w{1})/(?P<from_date>\w{10})/(?P<to_date>\w{10})/$', planning_table, name='planning_table'),
    (r'^inventoryselection/$', inventory_selection),
    url(r'^inventoryupdate/(?P<prod_id>\d+)/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', inventory_update),
    url(r'^meatupdate/(?P<prod_id>\d+)/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', meat_update),
    url(r'^producerpayments/(?P<prod_id>\d+)/(?P<from_date>\w{10})/(?P<to_date>\w{10})/(?P<due>\d{1})/(?P<paid_member>\w+)/$', producer_payments),
    (r'^deliveryselection/$', delivery_selection),
    url(r'^deliveryupdate/(?P<cust_id>\d+)/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', delivery_update),
    url(r'^producerplan/(?P<prod_id>\d+)/$', producerplan),
    url(r'^produceravail/(?P<prod_id>\d+)/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', produceravail),
    url(r'^meatavail/(?P<prod_id>\d+)/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', meatavail),
    (r'^ordertableselection/$', order_table_selection),
    url(r'^ordertable/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', order_table, name="order_table"),
    url(r'^ordertablebyproduct/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', order_table_by_product, name="order_table_by_product"),
    url(r'^shorts/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', shorts, name="shorts"),
    url(r'^shortschanges/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', shorts_changes, name="shorts_changes"),
    url(r'^ordercsv/(?P<order_date>\w{10})/$', order_csv, name="export_orders_as_csv"),
    url(r'^ordercsvbyproduct/(?P<order_date>\w{10})/$', order_csv_by_product, name="order_csv_by_product"),
    url(r'^jsoncustomer/(?P<customer_id>\d+)/$', json_customer_info),
    url(r'^jsonproducer/(?P<producer_id>\d+)/$', json_producer_info),
    (r'^accounts/login/$', 'django.contrib.auth.views.login'),
    (r'^producerpaymentselection/$', payment_selection),
    (r'^paymentupdateselection/$', payment_update_selection),
    url(r'^jsonpayments/(?P<producer_id>\d+)/$', json_payments),
    url(r'^paymentupdate/(?P<producer_id>\d+)/(?P<payment_id>\d+)/$', payment_update),
    url(r'^payment/(?P<payment_id>\d+)/$', payment),
    (r'^invoiceselection/$', invoice_selection),
    url(r'^invoices/(?P<cust_id>\d+)/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', invoices),
    (r'^statementselection/$', statement_selection),
    url(r'^statements/(?P<from_date>\w{10})/(?P<to_date>\w{10})/$', statements),
    url(r'^sendfreshlist/$', send_fresh_list, name="send_fresh_list"),
    url(r'^sendpickuplist/$', send_pickup_list, name="send_pickup_list"),
    url(r'^senddeliverylist/$', send_delivery_list, name="send_delivery_list"),
    url(r'^sendordernotices/$', send_order_notices, name="send_order_notices"),
    url(r'^sendshortchangenotices/$', send_short_change_notices, name="send_short_change_notices"),
    url(r'^supplydemand/(?P<from_date>\w{10})/(?P<to_date>\w{10})/$', supply_and_demand, name='supply_demand'),
    url(r'^membersupplydemand/(?P<from_date>\w{10})/(?P<to_date>\w{10})/(?P<member_id>\d+)/$',
        member_supply_and_demand, name='member_supply_demand'),
    url(r'^income/(?P<from_date>\w{10})/(?P<to_date>\w{10})/$', income, name='income'),
    url(r'^supplydemandweek/(?P<week_date>\w{10})/$', supply_and_demand_week, name='supply_and_demand_week'),
    url(r'^resetweek/$', reset_week, name='reset_week'),
    (r'^notices/', include('notification.urls')),
    url(r'^sendemail/$', send_email, name="send_email"),
    (r'^sendgaemail/$', send_ga_email),
    url(r'^email_sent/$', direct_to_template, {"template": "distribution/email_sent.html"}, name="email_sent"),
    url(r'^ga_email_sent/$', direct_to_template, {"template": "distribution/ga_email_sent.html"}, name="ga_email_sent"),
)
                           

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/home/bob/pbc/media', 'show_indexes': True}),
    )
