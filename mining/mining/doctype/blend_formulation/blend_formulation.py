# Copyright (c) 2024, ArkayApps and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate
from ..api import check_stock_balance, create_stock_entry
from ..enums import Stock, Stock_Purpose


class BlendFormulation(Document):
	def after_insert(self):
		self.date = nowdate()
		self.save()

	def on_submit(self):
		blend = frappe.get_doc("Blend", self.blend)
		for row in blend.lumps:
			qty_to_deduct = row.percentage / 100 * self.quantity
			#frappe.msgprint(f"{row.lumps} : {qty_to_deduct}")
			is_qty_available = check_stock_balance(
                    entry_for="Material",
                    entry_item= row.lumps,
                    warehouse = "Store",
                    check_for_quantity=qty_to_deduct)
            
			if not is_qty_available:
				frappe.throw(f"Quantity Not Available In Warehouse: 'Store' for Material: '{row.lumps}'")

			#Deduct Lumps
			stock_entry = create_stock_entry(
                stock_entry_for = "Material",
                stock_entry_item = row.lumps,
                stock_entry_type = Stock.STOCK_OUT.value,
                stock_entry_purpose = Stock_Purpose.MATERIAL_CONSUMED.value,
                source_warehouse = "Store",
                quantity = qty_to_deduct,
                created_from_doc = "Blend Formulation",
                doc_link = self.name
            )
			
		#Increase Blend
		stock_entry = create_stock_entry(
            stock_entry_for = "Blend",
            stock_entry_item = self.blend,
            stock_entry_type = Stock.STOCK_IN.value,
            stock_entry_purpose = Stock_Purpose.MATERIAL_INWARD.value,
            target_warehouse = "Blend Warehouse",
            quantity = self.quantity,
            created_from_doc = "Blend Formulation",
            doc_link = self.name
        )
	
        


