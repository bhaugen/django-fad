
from django.test import TestCase
from django.test import Client
from django import template
from django.db.models import get_model
from django.contrib.auth.models import User

class Testmaker(TestCase):
    """ Test Operational Tabs

        Created by TestMaker and then modified 
        to add logged in user, eliminate fixture reloads,
        and remove irrelevant assertions that did not work.
    """

    fixtures = ["distribution_testmaker.json"]


    def test_operational_tabs(self):
        john = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')
        c = Client()
        logged_in = c.login(username='john', password='johnpassword')
        r = c.get('/dashboard/', {})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(unicode(r.context[-1]['week_form']), u'<tr><th><label for="id_current_week">Current week:</label></th><td><input name="current_week" value="2010-01-18" type="text" id="id_current_week" dojoType="dijit.form.DateTextBox" constraints="{datePattern:&#39;yyyy-MM-dd&#39;}" /></td></tr>')
        self.assertEqual(unicode(r.context[-1]['item_list']), u'[<InventoryItem: Vegetable Producer Beets 2010-01-18>, <InventoryItem: Vegetable Producer Carrots 2010-01-18>, <InventoryItem: Meat Producer Steer 2010-01-18>, <InventoryItem: Meat Producer Beef Roast 2010-01-18>, <InventoryItem: Meat Producer Beef Steak 2010-01-18>]')
        self.assertEqual(unicode(r.context[-1]['food_network_name']), u'Demo Food Network')
        self.assertEqual(unicode(r.context[-1]['order_date']), u'2010-01-18')
    #def test_resetweek_126687159098(self):
        r = c.post('/resetweek/', {'current_week': '2010-02-22', })
    #def test_dashboard_126687159104(self):
        r = c.get('/dashboard/', {})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(unicode(r.context[-1]['week_form']), u'<tr><th><label for="id_current_week">Current week:</label></th><td><input name="current_week" value="2010-02-22" type="text" id="id_current_week" dojoType="dijit.form.DateTextBox" constraints="{datePattern:&#39;yyyy-MM-dd&#39;}" /></td></tr>')
        self.assertEqual(unicode(r.context[-1]['item_list']), u'[]')
        self.assertEqual(unicode(r.context[-1]['food_network_name']), u'Demo Food Network')
        self.assertEqual(unicode(r.context[-1]['order_date']), u'2010-02-22')
    #def test_inventoryselection_126687159418(self):
        r = c.get('/inventoryselection/', {})
        #self.assertEqual(r.status_code, 302)
    #def test_jsonproducer3_126687160025(self):
        r = c.get('/jsonproducer/3/', {})
        self.assertEqual(r.status_code, 200)
    #def test_inventoryselection_126687160147(self):
        r = c.post('/inventoryselection/', {'avail_date': '2010-02-22', 'producer': '3', })
    #def test_inventoryupdate32010222_126687160153(self):
        r = c.get('/inventoryupdate/3/2010/2/22/', {})
    #def test_inventoryupdate32010222_126687163087(self):
        r = c.post('/inventoryupdate/3/2010/2/22/', {'Beets-notes': 'Baby beets', 'Beets-custodian': '', 'Carrots-notes': 'Giant carrots', 'Carrots-item_id': '', 'Beets-inventory_date': '2010-02-22', 'Beets-received': '0', 'Carrots-received': '0', 'Carrots-planned': '200', 'Beets-planned': '100', 'Beets-item_id': '', 'Beets-prodname': 'Beets', 'Carrots-custodian': '', 'Carrots-prodname': 'Carrots', 'Carrots-inventory_date': '2010-02-22', 'producer-id': '3', 'avail-date': '2010-02-22', })
        self.assertEqual(r.status_code, 302)
    #def test_produceravail32010222_126687163095(self):
        r = c.get('/produceravail/3/2010/2/22/', {})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(unicode(r.context[-1]['producer']), u'Vegetable Producer')
        self.assertEqual(unicode(r.context[-1]['avail_date']), u'2010-02-22')
        self.assertEqual(unicode(r.context[-1]['inventory']), u'[<InventoryItem: Vegetable Producer Beets 2010-02-22>, <InventoryItem: Vegetable Producer Carrots 2010-02-22>]')
    #def test_processselection_126687163609(self):
        r = c.get('/processselection/', {})
        #self.assertEqual(r.status_code, 302)
    #def test_processselection_126687164018(self):
        r = c.post('/processselection/', {'process_type': '1', })
    #def test_newprocess1_126687164022(self):
        r = c.get('/newprocess/1/', {})
    #def test_newprocess1_126687169121(self):
        r = c.post('/newprocess/1/', {'output-TOTAL_FORMS': '2', 'service-1-from_whom': '8', 'service-1-service_type': '2', 'inputcreation-planned': '1000', 'service-0-from_whom': '4', 'service-0-service_type': '1', 'output-1-producer': '2', 'service-0-amount': '200', 'output-INITIAL_FORMS': '0', 'inputcreation-product': '5', 'service-1-amount': '400', 'output-0-product': '7', 'output-1-product': '6', 'output-0-custodian': '8', 'output-1-custodian': '8', 'inputcreation-producer': '2', 'output-0-planned': '400', 'output-0-producer': '2', 'service-TOTAL_FORMS': '2', 'output-1-planned': '200', 'service-INITIAL_FORMS': '0', })
        self.assertEqual(r.status_code, 302)
    #def test_process5_126687169156(self):
        r = c.get('/process/5/', {})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(unicode(r.context[-1]['process']), u'Slaughter and Cut Beef D2 Meat Producer Steer per lb 2010-02-22')
    #def test_orderselection_126687169677(self):
        r = c.get('/orderselection/', {})
        #self.assertEqual(r.status_code, 302)
    #def test_jsoncustomer7_126687170087(self):
        r = c.get('/jsoncustomer/7/', {})
        self.assertEqual(r.status_code, 200)
    #def test_orderselection_126687170214(self):
        r = c.post('/orderselection/', {'customer': '7', 'order_date': '2010-02-22', })
    #def test_orderbylot72010222_126687170219(self):
        r = c.get('/orderbylot/7/2010/2/22/', {})
    #def test_orderbylot72010222_126687173196(self):
        r = c.post('/orderbylot/7/2010/2/22/', {'form-0-product_id': '7', 'form-2-notes': '', 'form-1-lot_id': '19', 'form-0-order_item_id': '', 'form-2-avail': '100', 'form-0-quantity': '200', 'form-3-unit_price': '10', 'form-1-unit_price': '10', 'distributor': '5', 'form-2-order_item_id': '', 'form-1-product_id': '6', 'form-3-lot_id': '16', 'transportation_fee': '40', 'form-3-notes': '', 'form-0-notes': '', 'form-3-order_item_id': '', 'form-3-quantity': '100', 'form-2-lot_id': '15', 'paid': 'on', 'form-TOTAL_FORMS': '4', 'form-2-unit_price': '15', 'form-2-product_id': '10', 'form-INITIAL_FORMS': '4', 'form-0-lot_id': '18', 'form-0-unit_price': '8', 'form-1-quantity': '100', 'form-0-avail': '400', 'form-3-product_id': '8', 'form-3-avail': '200', 'form-1-order_item_id': '', 'form-1-notes': '', 'form-2-quantity': '50', 'form-1-avail': '200', })
        self.assertEqual(r.status_code, 302)
    #def test_order3_126687173217(self):
        r = c.get('/order/3/', {})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(unicode(r.context[-1]['order']), u'2010-02-22 Demo Hospital')
    #def test_ordertableselection_12668717353(self):
        r = c.get('/ordertableselection/', {})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(unicode(r.context[-1]['dsform']), u'<tr><th><label for="id_selected_date">Selected date:</label></th><td><input name="selected_date" value="2010-02-22" type="text" id="id_selected_date" dojoType="dijit.form.DateTextBox" constraints="{datePattern:&#39;yyyy-MM-dd&#39;}" /></td></tr>')
    #def test_ordertableselection_126687174025(self):
        r = c.post('/ordertableselection/', {'selected_date': '2010-02-22', })
    #def test_ordertable2010222_126687174047(self):
        r = c.get('/ordertable/2010/2/22/', {})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(unicode(r.context[-1]['date']), u'2010-02-22')
        self.assertEqual(unicode(r.context[-1]['item_list']), u'[<OrderItem: 2010-02-22 Demo Hospital Beef Roast 200>, <OrderItem: 2010-02-22 Demo Hospital Beef Steak 100>, <OrderItem: 2010-02-22 Demo Hospital Beets 50>, <OrderItem: 2010-02-22 Demo Hospital Carrots 100>]')
        self.assertEqual(unicode(r.context[-1]['heading_list']), u"['Customer', 'Order', 'Lot', 'Custodian', 'Order Qty']")
        self.assertEqual(unicode(r.context[-1]['datestring']), u'2010_02_22')
        self.assertEqual(unicode(r.context[-1]['orders']), u'[<Order: 2010-02-22 Demo Hospital>]')
    #def test_invoiceselection_12668717432(self):
        r = c.get('/invoiceselection/', {})
        #self.assertEqual(r.status_code, 302)
    #def test_invoiceselection_126687174653(self):
        r = c.post('/invoiceselection/', {'customer': '0', 'order_date': '2010-02-22', })
    #def test_invoices02010222_126687174657(self):
        r = c.get('/invoices/0/2010/2/22/', {})
        #self.assertEqual(r.status_code, 302)
    #def test_producerpaymentselection_126687175205(self):
        r = c.get('/producerpaymentselection/', {})
        self.assertEqual(r.status_code, 200)
    #def test_producerpaymentselection_126687175536(self):
        r = c.post('/producerpaymentselection/', {'from_date': '2010-02-15', 'paid_producer': 'both', 'to_date': '2010-02-27', 'producer': '0', })
    #def test_producerpayments02010_02_152010_02_270both_126687175541(self):
        r = c.get('/producerpayments/0/2010_02_15/2010_02_27/0/both/', {})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(unicode(r.context[-1]['producers']), u'[<Party: Local Distributor>, <Party: Meat Processor>, <Party: Meat Producer>, <Party: Slicer and Dicer>, <Party: Vegetable Producer>]')
        self.assertEqual(unicode(r.context[-1]['from_date']), u'2010-02-15')
        self.assertEqual(unicode(r.context[-1]['to_date']), u'2010-02-27')
        self.assertEqual(unicode(r.context[-1]['show_payments']), u'True')
    #def test_producerpaymentselection_126687176353(self):
        r = c.get('/producerpaymentselection/', {})
        self.assertEqual(r.status_code, 200)
    #def test_producerpaymentselection_126687177591(self):
        r = c.post('/producerpaymentselection/', {'from_date': '2010-02-15', 'paid_producer': 'both', 'to_date': '2010-02-27', 'producer': '2', })
    #def test_producerpayments22010_02_152010_02_270both_126687177597(self):
        r = c.get('/producerpayments/2/2010_02_15/2010_02_27/0/both/', {})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(unicode(r.context[-1]['from_date']), u'2010-02-15')
        self.assertEqual(unicode(r.context[-1]['to_date']), u'2010-02-27')
        self.assertEqual(unicode(r.context[-1]['producer']), u'Meat Producer')
        self.assertEqual(unicode(r.context[-1]['show_payments']), u'True')
    #def test_paymentupdateselection_126687178171(self):
        r = c.get('/paymentupdateselection/', {})
        #self.assertEqual(r.status_code, 302)
    #def test_jsonpayments2_126687178576(self):
        #r = c.get('/jsonpayments/2/', {})
        #self.assertEqual(r.status_code, 200)
    #def test_paymentupdateselection_126687178742(self):
        r = c.post('/paymentupdateselection/', {'payment': '', 'producer': '2', })
    #def test_paymentupdate20_126687178746(self):
        r = c.get('/paymentupdate/2/0/', {})
    #def test_paymentupdate20_126687179533(self):
        r = c.post('/paymentupdate/2/0/', {'35-notes': '', '34-notes': '', 'to_whom': '2', '35-transaction_date': '2010-02-22', 'reference': 'Check 1234', '35-transaction_id': '35', '34-order': '3: Demo Hospital', '35-order': '3: Demo Hospital', '34-amount_due': '1504.00', '35-transaction_type': 'Delivery', 'amount': '2444', 'transaction_date': '2010-02-22', '35-quantity': '100', '34-quantity': '200', '34-transaction_id': '34', '35-amount_due': '940.00', '34-transaction_date': '2010-02-22', '34-paid': 'on', '35-paid': 'on', '34-transaction_type': 'Delivery', })
        self.assertEqual(r.status_code, 302)
    #def test_payment38_126687179546(self):
        r = c.get('/payment/38/', {})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(unicode(r.context[-1]['payment']), u'2010-02-22 Meat Producer $2444')
    #def test_paymentupdateselection_126687180056(self):
        r = c.get('/paymentupdateselection/', {})
        #self.assertEqual(r.status_code, 302)
    #def test_jsonpayments4_126687180382(self):
        #r = c.get('/jsonpayments/4/', {})
        #self.assertEqual(r.status_code, 200)
    #def test_paymentupdateselection_12668718054(self):
        r = c.post('/paymentupdateselection/', {'payment': '', 'producer': '4', })
    #def test_paymentupdate40_126687180545(self):
        r = c.get('/paymentupdate/4/0/', {})
    #def test_paymentupdate40_126687181906(self):
        r = c.post('/paymentupdate/4/0/', {'proc19-amount_due': '200', 'proc19-paid': 'on', 'proc19-transaction_date': '2010-01-18', 'reference': 'Check 4321', 'proc13-order': '', 'proc13-transaction_type': 'Processing', 'proc2-transaction_date': '2010-01-11', 'proc19-order': ' #2:Demo Hospital', 'proc2-transaction_type': 'Processing', 'proc13-paid': 'on', 'proc5-transaction_id': '5', 'proc5-quantity': '', 'proc13-quantity': '', 'proc13-transaction_id': '13', 'proc19-transaction_id': '19', 'proc2-paid': 'on', 'transaction_date': '2010-02-22', 'proc2-transaction_id': '2', 'proc19-notes': '', 'proc5-order': ' #1:Demo Hospital', 'proc13-notes': '', 'proc2-order': '', 'proc19-quantity': '', 'to_whom': '4', 'proc19-transaction_type': 'Processing', 'proc5-notes': '', 'proc13-transaction_date': '2010-01-11', 'proc5-amount_due': '100', 'proc5-paid': 'on', 'proc2-quantity': '', 'proc5-transaction_type': 'Processing', 'proc5-transaction_date': '2010-01-11', 'amount': '400', 'proc13-amount_due': '50', 'proc2-amount_due': '50', 'proc2-notes': '', })
        self.assertEqual(r.status_code, 302)
    #def test_payment39_126687181928(self):
        r = c.get('/payment/39/', {})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(unicode(r.context[-1]['payment']), u'2010-02-22 Meat Processor $400')
    #def test_paymentupdateselection_126687182359(self):
        r = c.get('/paymentupdateselection/', {})
        #self.assertEqual(r.status_code, 302)
    #def test_jsonpayments5_126687182996(self):
        #r = c.get('/jsonpayments/5/', {})
        #self.assertEqual(r.status_code, 200)
    #def test_paymentupdateselection_126687183102(self):
        r = c.post('/paymentupdateselection/', {'payment': '', 'producer': '5', })
    #def test_paymentupdate50_126687183106(self):
        r = c.get('/paymentupdate/5/0/', {})
    #def test_paymentupdate50_126687184221(self):
        r = c.post('/paymentupdate/5/0/', {'transport8-order': '2010-01-11 Demo Hospital', 'transport8-paid': 'on', 'to_whom': '5', 'reference': 'Check 1111', 'transport8-transaction_type': 'Transportation', 'transport33-order': '2010-02-22 Demo Hospital', 'transport33-paid': 'on', 'transport8-notes': '', 'transport33-notes': '', 'transport33-amount_due': '40', 'transport8-transaction_date': '2010-01-11', 'transport8-transaction_id': '8', 'amount': '80', 'transaction_date': '2010-02-22', 'transport33-quantity': '', 'transport33-transaction_date': '2010-02-22', 'transport33-transaction_id': '33', 'transport8-amount_due': '40', 'transport33-transaction_type': 'Transportation', 'transport8-quantity': '', })
        self.assertEqual(r.status_code, 302)
    #def test_payment40_126687184234(self):
        r = c.get('/payment/40/', {})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(unicode(r.context[-1]['payment']), u'2010-02-22 Local Distributor $80')
    #def test_statementselection_126687184595(self):
        r = c.get('/statementselection/', {})
        #self.assertEqual(r.status_code, 302)
    #def test_statementselection_126687185963(self):
        r = c.post('/statementselection/', {'from_date': '2010-02-15', 'to_date': '2010-02-22', })
    #def test_statements2010_02_152010_02_22_126687185966(self):
        r = c.get('/statements/2010_02_15/2010_02_22/', {})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(unicode(r.context[-1]['payments']), u'[<Payment: 2010-02-22 Meat Producer $2444>, <Payment: 2010-02-22 Meat Processor $400>, <Payment: 2010-02-22 Local Distributor $80>]')
        self.assertEqual(unicode(r.context[-1]['network']), u'Demo')
    #def test_planselection_126687187891(self):
        r = c.get('/planselection/', {})
        #self.assertEqual(r.status_code, 302)
    #def test_jsonproducer2_126687188798(self):
        r = c.get('/jsonproducer/2/', {})
        self.assertEqual(r.status_code, 200)
    #def test_planselection_126687188936(self):
        r = c.post('/planselection/', {'producer': '2', })
    #def test_planupdate2_126687188939(self):
        r = c.get('/planupdate/2/', {})
    #def test_planupdate2_126687191865(self):
        r = c.post('/planupdate/2/', {'Beets-from_date': '2010-02-22', 'Beef Steak-quantity': '10000', 'Beef, Side-from_date': '2010-01-01', 'Beef, Side-to_date': '2010-02-22', 'Carrots-parents': 'Vegetables', 'Beef Steak-item_id': '2', 'Beef Steak-prodname': 'Beef Steak', 'Carrots-quantity': '0', 'Beef Roast-from_date': '2010-01-01', 'Steer-distributor': '5', 'Steer-parents': 'Live Animal', 'Carrots-item_id': '', 'Beef Steak-from_date': '2010-01-01', 'Beets-quantity': '0', 'Beef Roast-distributor': '5', 'Steer-from_date': '2010-01-01', 'Beets-item_id': '', 'Beets-prodname': 'Beets', 'Beef, Side-parents': 'Beef Section', 'Carrots-distributor': '5', 'Beets-parents': 'Vegetables', 'Beef Steak-to_date': '2011-01-11', 'Steer-quantity': '20000', 'Steer-prodname': 'Steer', 'Beef, Side-item_id': '', 'Beets-to_date': '2010-02-22', 'Steer-to_date': '2011-01-11', 'Beef, Side-prodname': 'Beef, Side', 'Steer-item_id': '3', 'Beef, Side-quantity': '10000', 'Beef Steak-parents': 'Beef Cuts', 'Carrots-prodname': 'Carrots', 'Beef Steak-distributor': '5', 'Beef Roast-prodname': 'Beef Roast', 'producer-id': '2', 'Carrots-to_date': '2010-02-22', 'Beef Roast-to_date': '2011-01-11', 'Carrots-from_date': '2010-02-22', 'Beef Roast-parents': 'Beef Cuts', 'Beets-distributor': '5', 'Beef Roast-quantity': '10000', 'Beef Roast-item_id': '1', 'Beef, Side-distributor': '5', })
        self.assertEqual(r.status_code, 302)
    #def test_producerplan2_126687191878(self):
        r = c.get('/producerplan/2/', {})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(unicode(r.context[-1]['plans']), u'[<ProductPlan: Meat Producer Beef Roast 2010-01-01 2010-01-01 10000>, <ProductPlan: Meat Producer Beef Steak 2010-01-01 2010-01-01 10000>, <ProductPlan: Meat Producer Beef, Side 2010-01-01 2010-01-01 10000>, <ProductPlan: Meat Producer Steer 2010-01-01 2010-01-01 20000>]')
        self.assertEqual(unicode(r.context[-1]['producer']), u'Meat Producer')

