# Copyright (c) 2024, ArkayApps and contributors
# For license information, please see license.txt
import frappe
from frappe.model.document import Document
from frappe.utils import nowdate
from ..enums import Stock, Stock_Purpose, BSB, Warehouse, Batch_State
from ..api import create_stock_entry
from ..batch_insights_api import update_batch_stock_breakdown

class Dispatch(Document):
	def after_insert(self):
		self.date = nowdate()
		self.save()

	def on_submit(self):
		batch_doc = frappe.get_doc("Batch", self.batch)
		#dispatch qty should not be more than packed qty
		if self.quantity > batch_doc.packed_stock:
			frappe.throw(f"Dispatch Quantity Cannot be more than Packed Stock: {batch_doc.packed_stock}!")
		
		#Stock Out Entry for Batch
		create_stock_entry(
                    stock_entry_for = "Batch",
                    stock_entry_item = self.batch,
                    stock_entry_type = Stock.STOCK_OUT.value,
                    stock_entry_purpose = Stock_Purpose.DELIVERY.value,
                    source_warehouse = Warehouse.BATCH_WAREHOUSE.value,
                    quantity = self.quantity,
                    created_from_doc = "Dispatch",
                    doc_link = self.name
                )
		#Add Total Dispatch in batch insights
		update_batch_stock_breakdown(batch_doc, BSB.TOTAL_DISPATCHED_QTY.value, self.quantity)

		#Deduct Qty from Batch Stock
		update_batch_stock_breakdown(batch_doc, BSB.TOTAL_BATCH_STOCK.value, -self.quantity)

		#Deduct Qty from Packed Stock
		update_batch_stock_breakdown(batch_doc, BSB.PACKED_STOCK.value, -self.quantity)
		batch_doc.save()
		#Total delivered qty == batch required, set batch status as delivered
		if batch_doc.total_delivered_qty >= batch_doc.total_required_qty:
			batch_doc.batch_state = Batch_State.DELIVERED.value
			batch_doc.save()


	def on_cancel(self):
		batch_doc = frappe.get_doc("Batch", self.batch)
		#Add Qty in Batch Stock
		update_batch_stock_breakdown(batch_doc, BSB.TOTAL_BATCH_STOCK.value, self.quantity)
  		#Add Qty in Packed Stock
		update_batch_stock_breakdown(batch_doc, BSB.PACKED_STOCK.value, self.quantity)
		#Deduct Qty from Total Dispatch in batch insights
		update_batch_stock_breakdown(batch_doc, BSB.TOTAL_DISPATCHED_QTY.value, -self.quantity)
		batch_doc.save()
		
		if batch_doc.total_delivered_qty < batch_doc.total_required_qty:
			batch_doc.batch_state = Batch_State.PRODUCTION.value
			batch_doc.save()