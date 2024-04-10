# Copyright (c) 2024, ArkayApps and contributors
# For license information, please see license.txt
import frappe
from frappe.model.document import Document
from frappe.utils import nowdate
from ..api import create_stock_entry
from ..batch_insights_api import batchTransferInsights
from ..enums import Material_Type, Warehouse, Stock, Stock_Purpose


class BatchTransfer(Document):
	def after_insert(self):
		self.date = nowdate()
		self.save()
	
	def validate(self):
		if self.from_batch == self.to_batch:
			frappe.throw("From Batch and To Batch Cannot Be Same!", title="Same Batch Error")
		if self.quantity <= 0:
			frappe.throw("Quantity cannot be less than or equal to zero!", title="Quantity Error")
	
	def on_submit(self):
		create_stock_entries(self)


def create_stock_entries(doc):
	#Stock Out Entry From from_batch
	stock_out_entry = create_stock_entry(
			stock_entry_for = "Batch",
			stock_entry_item = doc.from_batch,
			stock_entry_type = Stock.STOCK_OUT.value,
			stock_entry_purpose = Stock_Purpose.BATCH_TRANSFER.value, 
			source_warehouse = Warehouse.BATCH_WAREHOUSE.value,
			quantity = doc.quantity,
			created_from_doc = "Batch Transfer",
			doc_link = doc.name
		)
	
	#Stock In Entry From from_batch
	stock_in_entry = create_stock_entry(
			stock_entry_for = "Batch",
			stock_entry_item = doc.to_batch,
			stock_entry_type = Stock.STOCK_IN.value,
			stock_entry_purpose = Stock_Purpose.BATCH_TRANSFER.value, 
			target_warehouse = Warehouse.BATCH_WAREHOUSE.value,
			quantity = doc.quantity,
			created_from_doc = "Batch Transfer",
			doc_link = doc.name
		)

