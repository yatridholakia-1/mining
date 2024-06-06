# Copyright (c) 2024, ArkayApps and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from ..api import create_stock_entry
from ..enums import Warehouse, Stock, Stock_Purpose


class Material(Document):
    def after_insert(self):
    	if self.opening_stock and self.opening_stock > 0:
        	create_stock_entry(
            	stock_entry_for = "Material",
                    stock_entry_item = self.material_code,
                    stock_entry_type = Stock.STOCK_IN.value,
                    stock_entry_purpose = Stock_Purpose.MATERIAL_INWARD.value,
                    target_warehouse = Warehouse.STORE.value,
                    quantity = self.opening_stock,
					created_from_doc = "Material",
					doc_link = self.name
            	)
		

