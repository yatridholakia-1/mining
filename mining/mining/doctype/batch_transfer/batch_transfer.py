# Copyright (c) 2024, ArkayApps and contributors
# For license information, please see license.txt
import frappe
from frappe.model.document import Document
from frappe.utils import nowdate
from ..api import create_stock_entry
from ..batch_insights_api import update_batch_stock_breakdown, batchTransferInsights
from ..enums import BatchTransferInsightsStock, Warehouse, Stock, Stock_Purpose, BSB


class BatchTransfer(Document):
	def after_insert(self):
		self.date = nowdate()
		self.from_insights_row = ""
		self.to_insights_row = ""
		self.save()
	
	def validate(self):
		if self.from_batch == self.to_batch:
			frappe.throw("From Batch and To Batch Cannot Be Same!", title="Same Batch Error")
		if self.quantity <= 0:
			frappe.throw("Quantity cannot be less than or equal to zero!", title="Quantity Error")
	
	def on_submit(self):
		create_stock_entries(self)
		from_batch_doc = frappe.get_doc("Batch", self.from_batch)
		to_batch_doc = frappe.get_doc("Batch", self.to_batch)
		#Deduct Batch Stock from code in From Batch
		update_batch_stock_breakdown(from_batch_doc, BSB.TOTAL_BATCH_STOCK.value, -self.quantity)
		#Add Batch Stock in to Batch
		update_batch_stock_breakdown(to_batch_doc, BSB.TOTAL_BATCH_STOCK.value, self.quantity)
		#Total Transferred Stock in To Batch
		update_batch_stock_breakdown(to_batch_doc, BSB.TOTAL_TRANSFERRED_STOCK.value, self.quantity)
		#add qty to QC Remaining Stock in to_batch
		update_batch_stock_breakdown(to_batch_doc, BSB.QC_REMAINING_STOCK.value, self.quantity)
		#Batch Insights row in from Batch
		self.from_insights_row = batchTransferInsights(from_batch_doc, BatchTransferInsightsStock.OUT.value, to_batch_doc.name, self.date, self.quantity)
  		#Batch Insights row in To Batch
		self.to_insights_row = batchTransferInsights(to_batch_doc, BatchTransferInsightsStock.IN.value, from_batch_doc.name, self.date, self.quantity)
		self.save()
		from_batch_doc.save()
		to_batch_doc.save()

	def on_cancel(self):
		from_batch_doc = frappe.get_doc("Batch", self.from_batch)
		to_batch_doc = frappe.get_doc("Batch", self.to_batch)
		#Add Batch Stock from code in From Batch
		update_batch_stock_breakdown(from_batch_doc, BSB.TOTAL_BATCH_STOCK.value, self.quantity)
		#Deduct Batch Stock in to Batch
		update_batch_stock_breakdown(to_batch_doc, BSB.TOTAL_BATCH_STOCK.value, -self.quantity)
		#Deduct Total Transferred Stock in To Batch
		update_batch_stock_breakdown(to_batch_doc, BSB.TOTAL_TRANSFERRED_STOCK.value, -self.quantity)
		#Deduct qty to QC Remaining Stock in to_batch
		update_batch_stock_breakdown(to_batch_doc, BSB.QC_REMAINING_STOCK.value, -self.quantity)
		#Remove Batch Insights row in from Batch
		for entry in from_batch_doc.batch_transfer_insights:
				if entry.name == self.from_insights_row:
					from_batch_doc.batch_transfer_insights.remove(entry)
					break
  		#Remove Batch Insights row in To Batch
		for entry in to_batch_doc.batch_transfer_insights:
				if entry.name == self.to_insights_row:
					to_batch_doc.batch_transfer_insights.remove(entry)
					break
		from_batch_doc.save()
		to_batch_doc.save()

def create_stock_entries(doc):
	#Stock Out Entry From from_batch
	stock_out_entry = create_stock_entry(
			stock_entry_for = "Batch",
			stock_entry_item = doc.from_batch,
			stock_entry_type = Stock.STOCK_OUT.value,
			stock_entry_purpose = Stock_Purpose.BATCH_TRANSFER.value, 
			source_warehouse = Warehouse.BATCH_WAREHOUSE.value if doc.transfer_type == "Batch To Batch" else Warehouse.DEAD_STOCK_WAREHOUSE.value,
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

