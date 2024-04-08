# Copyright (c) 2024, ArkayApps and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from ..api import create_stock_entry
from ..enums import Stock, Stock_Purpose, Warehouse, Material_Type
from frappe.utils import nowdate


class MaterialInward(Document):
	def after_insert(self):
		self.date = nowdate()
		self.save()
	
	def on_submit(self):
		create_stock_entry(
                    stock_entry_for = "Material",
                    stock_entry_item = self.material,
                    stock_entry_type = Stock.STOCK_IN.value,
                    stock_entry_purpose = Stock_Purpose.MATERIAL_INWARD.value,
                    target_warehouse = Warehouse.STORE.value,
                    quantity = self.quantity if self.material_type != Material_Type.LUMPS.value else self.swell_well_weight,
                    created_from_doc = "Material Inward",
                    doc_link = self.name
                )

