# Copyright (c) 2024, ArkayApps and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from ..batch_insights_api import consume_material_for_production
from ..api import create_stock_entry
from ..enums import Stock, Stock_Purpose, Warehouse

class Production(Document):
	pass


				


