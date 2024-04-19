# Copyright (c) 2024, ArkayApps and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate
from ..enums import Stock, Stock_Purpose, BSB
from ..api import create_stock_entry
from ..batch_insights_api import update_batch_stock_breakdown

class BatchPacking(Document):
	def after_insert(self):
		self.date = nowdate()
		self.save()
	
	def on_submit(self):
		batch_doc = frappe.get_doc("Batch", self.batch)
		#packing qty should not be more than qc accepted qty
		if self.packing_quantity > batch_doc.qc_accepted_stock:
			frappe.throw(f"Packing Quantity Cannot be more than QC Accepted Stock: {batch_doc.qc_accepted_stock}!")
		
				#Check if enough pallet is issued before consuming
		if self.pallet_quantity > batch_doc.pallet_issued_qty: 
			frappe.throw(f"Not Enough Pallets are Issued for Conusmption! Please issue more pallets.")
		
		#Stock Entry for pallet consumption
		create_stock_entry(
                    stock_entry_for = "Material",
                    stock_entry_item = self.pallet_assigned,
                    stock_entry_type = Stock.STOCK_OUT.value,
                    stock_entry_purpose = Stock_Purpose.MATERIAL_CONSUMED.value,
                    source_warehouse = self.production_warehouse,
                    quantity = self.pallet_quantity,
                    created_from_doc = "Batch Packing",
                    doc_link = self.name
                )
  		#Add Pallet Consumption in batch insights
		update_batch_stock_breakdown(batch_doc, BSB.PALLET_CONSUMED_QTY.value, self.pallet_quantity)
  		#Deduct Qty from QC Accepted Stock
		update_batch_stock_breakdown(batch_doc, BSB.QC_ACCEPTED_STOCK.value, -self.packing_quantity)
		#Add QTY in Ready to dispatch Stock
		update_batch_stock_breakdown(batch_doc, BSB.PACKED_STOCK.value, self.packing_quantity)
		batch_doc.save()

	def on_cancel(self):
		batch_doc = frappe.get_doc("Batch", self.batch)
		#Revert Pallet Consumption
		update_batch_stock_breakdown(batch_doc, BSB.PALLET_CONSUMED_QTY.value, -self.pallet_quantity)
		#Add Qty in QC Accepted
		update_batch_stock_breakdown(batch_doc, BSB.QC_ACCEPTED_STOCK.value, self.packing_quantity)
		#Deduct Qty in ready to dispatch stock
		update_batch_stock_breakdown(batch_doc, BSB.PACKED_STOCK.value, -self.packing_quantity)
		batch_doc.save()