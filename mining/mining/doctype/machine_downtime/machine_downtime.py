# Copyright (c) 2024, ArkayApps and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from ..api import generate_machine_log
from ..enums import Machine_Log_Type


class MachineDowntime(Document):
	
	def on_submit(self):
		generate_machine_log(
			machine=self.machine,
			log_type=Machine_Log_Type.DOWNTIME.value,
			hours=self.downtime_hours,
			ref_doc_name="Machine Downtime",
			shift=self.shift,
			ref_doc_link=self,
			downtime_reason=self.downtime_reason
		)
	
