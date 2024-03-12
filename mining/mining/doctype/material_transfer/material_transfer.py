# Copyright (c) 2024, ArkayApps and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate
from ..enums import Stock, Stock_Purpose
from ..api import create_stock_entry, check_stock_balance


class MaterialTransfer(Document):
	def after_insert(self):
		self.date = nowdate()
		self.save()

	def on_submit(self):
		#Validate Stock is present in source warehosue
		#Check if balance exists
		
		for row in self.material_transfer:
			# exists = frappe.db.exists(
			# 	'Stock Balance',
			# 	{
			# 		'entry_for': "Material",
			# 		'entry_item': row.material,
			# 		'warehouse': row.source_warehouse,
			# 		'docstatus': 1,    
			# 	},
			# )

			# if exists:
			# 	quantity = frappe.get_value("Stock Balance", filters={
			# 		'entry_for': "Material",
			# 		'entry_item': row.material,
			# 		'warehouse': row.source_warehouse,
			# 		'docstatus': 1
			# 	}, fieldname="quantity")

			# 	if quantity < row.quantity:
			# 		is_qty_available = False
			# else:
			# 	is_qty_available = False
			
			# if not is_qty_available:
				is_qty_available = check_stock_balance(
					entry_for="Material",
					entry_item= row.material,
					warehouse = row.source_warehouse,
					check_for_quantity=row.quantity)
				
				if not is_qty_available:
					frappe.throw(f"Quantity Not Available In Warehouse: '{row.source_warehouse}' for Material: '{row.material}'")
			
			#Create Stock Transfer Entry In Stock Mamagement
			# stock_transfer = frappe.new_doc("Stock Management")
			# stock_transfer.stock_entry_for = "Material"
			# stock_transfer.stock_entry_item = row.material
			# stock_transfer.stock_entry_type = Stock.STOCK_TRANSFER.value
			# stock_transfer.stock_entry_purpose = Stock_Purpose.MATERIAL_TRANSFER.value if self.type == "Material Issue" else Stock_Purpose.MATERIAL_RETURN.value
			# stock_transfer.source_warehouse = row.source_warehouse
			# stock_transfer.target_warehouse = row.target_warehouse
			# stock_transfer.quantity = row.quantity
			# stock_transfer.created_from_doc = "Material Transfer"
			# stock_transfer.doc_link = self.name
			# stock_transfer.save()
			# stock_transfer.submit()
			# row.stock_entry = stock_transfer.name
			# self.save()
				
				stock_transfer_entry = create_stock_entry(
				stock_entry_for = "Material",
				stock_entry_item = row.material,
				stock_entry_type = Stock.STOCK_TRANSFER.value,
				stock_entry_purpose = Stock_Purpose.MATERIAL_TRANSFER.value if self.type == "Material Issue" else Stock_Purpose.MATERIAL_RETURN.value,
				source_warehouse = row.source_warehouse,
				target_warehouse = row.target_warehouse,
				quantity = row.quantity,
				created_from_doc = "Material Transfer",
				doc_link = self.name
			)
				row.stock_entry = stock_transfer_entry
				self.save()


	
	def on_cancel(self):
		for row in self.material_transfer:
			try:
				frappe.get_doc("Stock Management", row.stock_entry).cancel()
			except Exception as e:
				frappe.throw(f"Failed to cancel Stock Management Document: {e}")








