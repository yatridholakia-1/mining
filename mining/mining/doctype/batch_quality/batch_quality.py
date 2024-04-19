# Copyright (c) 2024, ArkayApps and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate
from ..batch_insights_api import batchQualityInsights, update_batch_stock_breakdown
from ..api import create_stock_entry
from ..enums import BSB, Stock, Stock_Purpose, Warehouse

class BatchQuality(Document):
		def after_insert(self):
			self.date = nowdate()
			self.save()
		
		def on_submit(self):
			#Batch Insights
			batch_doc = frappe.get_doc("Batch", self.batch)
			self.batch_insights_row = batchQualityInsights(
				batch=batch_doc,
				accepted_qty=self.accepted_quantity,
				rejected_qty=self.rejected_quantity,
				date=self.date,
				qty=self.for_quantity
			)
			self.save()
			
			update_batch_stock_breakdown(batch_doc, BSB.QC_ACCEPTED_STOCK.value, self.accepted_quantity)
			update_batch_stock_breakdown(batch_doc, BSB.QC_REMAINING_STOCK.value, -self.for_quantity)
			
			
			if self.rejected_quantity > 0:
				create_stock_entry(
                    stock_entry_for = "Batch",
                    stock_entry_item = self.batch,
                    stock_entry_type = Stock.STOCK_TRANSFER.value,
                    stock_entry_purpose = Stock_Purpose.QUALITY_REJECTED.value,
					source_warehouse = Warehouse.BATCH_WAREHOUSE.value,
                    target_warehouse = Warehouse.DEAD_STOCK_WAREHOUSE.value,
                    quantity = self.rejected_quantity,
                    created_from_doc = "Batch Quality",
                    doc_link = self.name
                )
			update_batch_stock_breakdown(batch_doc, BSB.TOTAL_QC_REJECTED.value, self.rejected_quantity)
			update_batch_stock_breakdown(batch_doc, BSB.TOTAL_BATCH_STOCK.value, -self.rejected_quantity)
			batch_doc.save()


		def on_cancel(self):
			batch_doc = frappe.get_doc("Batch", self.batch)
			for entry in batch_doc.quality_insights:
				if entry.name == self.batch_insights_row:
					batch_doc.quality_insights.remove(entry)
					break
			update_batch_stock_breakdown(batch_doc, BSB.QC_ACCEPTED_STOCK.value, -self.accepted_quantity)
			update_batch_stock_breakdown(batch_doc, BSB.QC_REMAINING_STOCK.value, self.for_quantity)
			if self.rejected_quantity > 0:
				update_batch_stock_breakdown(batch_doc, BSB.TOTAL_QC_REJECTED.value, -self.rejected_quantity)
				update_batch_stock_breakdown(batch_doc, BSB.TOTAL_BATCH_STOCK.value, self.rejected_quantity)
			batch_doc.save()