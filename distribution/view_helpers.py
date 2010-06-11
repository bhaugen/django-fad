from decimal import *
import datetime

from django.forms.formsets import formset_factory

from models import *
from forms import *

# shd plan_weeks go to the view and include headings?
# somebody needs headings!
def create_weekly_plan_forms(rows, data=None):
    form_list = []
    #rows = plan_weeks(member, from_date, to_date)
    PlanCellFormSet = formset_factory(PlanCellForm, extra=0)

    for row in rows:
        product = row[0]
        row_form = PlanRowForm(data, prefix=product.id, initial={'product_id': product.id})
        row_form.product = product.long_name
        cells = row[1:len(row)]
        initial_data = []
        for cell in cells:
            plan_id = ""
            if cell.plan:
                plan_id = cell.plan.id
            dict = {
                'plan_id': plan_id,
                'product_id': cell.product.id,
                'from_date': cell.from_date,
                'to_date': cell.to_date,
                'quantity': cell.quantity,
            }
            initial_data.append(dict)
        row_form.formset = PlanCellFormSet(data, prefix=product.id, initial=initial_data)
        form_list.append(row_form)
    return form_list
        

