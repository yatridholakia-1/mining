# Copyright (c) 2024, ArkayApps and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import nowdate
from frappe.model.document import Document
from ..api import create_stock_entry
from ..batch_insights_api import update_batch_stock_breakdown, calulate_bag_consumption
from ..enums import Warehouse, Stock, Stock_Purpose, BSB, Batch_Insight_Headers, Batch_State


class ReadyMadeProduction(Document):
		def after_insert(self):
			self.date = nowdate()
			self.save()
		
		def on_submit(self):
			batch_doc = frappe.get_doc("Batch", self.batch)
			#If qty is more than required qty, show a waring
			if batch_doc.total_required_qty < (self.quantity + batch_doc.total_readymade_qty):
				frappe.msgprint("Quanitity Exceeding Total Required Quantity!", title="Warning")
	
			#Consume Bags
			for bag in batch_doc.batch_bag_insights:
				bag_qty_to_consume = calulate_bag_consumption(self.quantity, bag.bag_size)
				
				if bag.issued_qty < bag_qty_to_consume:
					frappe.throw(f"Not enough quantity of material: {bag.bag} is issued for consumption!")
				
				create_stock_entry(
							stock_entry_for = "Material",
							stock_entry_item = bag.bag,
							stock_entry_type = Stock.STOCK_OUT.value,
							stock_entry_purpose = Stock_Purpose.MATERIAL_CONSUMED.value,
							source_warehouse = Warehouse.READY_MADE_WAREHOUSE.value,
							quantity = bag_qty_to_consume,
							created_from_doc = "Ready-Made Production",
							doc_link = self.name
						)
				bag.consumed_qty += bag_qty_to_consume
			
			#stock in entry for batch
			create_stock_entry(
            stock_entry_for = "Batch",
                    stock_entry_item = self.batch,
                    stock_entry_type = Stock.STOCK_IN.value,
                    stock_entry_purpose = Stock_Purpose.READY_MADE_PROD.value,
                    target_warehouse = Warehouse.BATCH_WAREHOUSE.value,
                    quantity = self.quantity,
					created_from_doc = "Ready-Made Production",
					doc_link = self.name
            )
			
			#Batch Stock add
			update_batch_stock_breakdown(batch_doc, BSB.TOTAL_BATCH_STOCK.value, self.quantity)
			#QC Accepted Add
			update_batch_stock_breakdown(batch_doc, BSB.QC_ACCEPTED_STOCK.value, self.quantity)
			#total ready made qty add
			update_batch_stock_breakdown(batch_doc, BSB.TOTAL_READY_MADE_QTY.value, self.quantity)
			
			#update batch state
			batch_doc.batch_state = Batch_State.READY_MADE_PROD.value
			batch_doc.save(ignore_permissions=True)
			prod_progress = (batch_doc.total_readymade_qty / batch_doc.total_required_qty) * 100;
			# update_batch_stock_breakdown(batch_doc, BSB.TOTAL_PRODUCTION_PROGRESS.value, prod_progress)
			batch_doc.production_progress = prod_progress
   
			batch_doc.save(ignore_permissions=True)
			

		
		def on_cancel(self):
			#Cancel Stock Entries
			batch_doc = frappe.get_doc("Batch", self.batch)
			for bag in batch_doc.batch_bag_insights:
				bag_qty_to_consume = calulate_bag_consumption(self.quantity, bag.bag_size)
				bag.consumed_qty -= bag_qty_to_consume
			
			#Batch Stock deduct
			update_batch_stock_breakdown(batch_doc, BSB.TOTAL_BATCH_STOCK.value, -self.quantity)
			#QC Accepted Deduct
			update_batch_stock_breakdown(batch_doc, BSB.QC_ACCEPTED_STOCK.value, -self.quantity)
			#total ready made qty deduct
			update_batch_stock_breakdown(batch_doc, BSB.TOTAL_READY_MADE_QTY.value, -self.quantity)
			batch_doc.save(ignore_permissions=True)
			prod_progress = (batch_doc.total_readymade_qty / batch_doc.total_required_qty) * 100;
			batch_doc.production_progress = prod_progress
			#update_batch_stock_breakdown(batch_doc, BSB.TOTAL_PRODUCTION_PROGRESS.value, prod_progress)
			batch_doc.save(ignore_permissions=True)
			
			if batch_doc.total_readymade_qty <= 0 :
				batch_doc.batch_state = Batch_State.CREATED.value
				batch_doc.save(ignore_permissions=True)
		
		
