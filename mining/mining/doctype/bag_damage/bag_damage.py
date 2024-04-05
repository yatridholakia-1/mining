# Copyright (c) 2024, ArkayApps and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate
from ..api import validate_issue, create_stock_entry
from ..batch_insights_api import update_batch_insights
from ..enums import Material_Type, Stock, Stock_Purpose, Batch_Insight_Headers


class BagDamage(Document):
	def after_insert(self):
		self.date = nowdate()
		self.save()

	def on_submit(self):
		#validate issue
		issued = validate_issue(self.batch, Material_Type.BAG.value, self.bag, self.damaged_quantity)
		if not issued:
			frappe.throw(f"Not Enough Qty issued for Bag: {self.bag} against Batch:{self.batch}")
		
		#stock out from production warehouse
		stock_out_from_production_warehouse(self)

  		#update damage bag batch insights
		update_damage_bag_batch_insights(self, "submit")
	
	def on_cancel(self):
		#cancel stock entry
		#update batch insights
  		update_damage_bag_batch_insights(self, "cancel")

def stock_out_from_production_warehouse(doc):
	stock_transfer_entry = create_stock_entry(
				stock_entry_for = "Material",
				stock_entry_item = doc.bag,
				stock_entry_type = Stock.STOCK_OUT.value,
				stock_entry_purpose = Stock_Purpose.DAMAGE.value, 
				source_warehouse = doc.production_warehouse,
				quantity = doc.damaged_quantity,
				created_from_doc = "Bag Damage",
				doc_link = doc.name
			)


def update_damage_bag_batch_insights(doc, method):
	update_batch_insights(
		batch=doc.batch,
		material_type=Material_Type.BAG.value,
		header_name=Batch_Insight_Headers.DAMAGED.value,
		quantity=doc.damaged_quantity if method == "submit" else -doc.damaged_quantity,
		material_code=doc.bag
	)
