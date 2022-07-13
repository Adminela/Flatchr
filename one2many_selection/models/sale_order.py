# Copyright 2022 ELITE Advanced technologies.
# Copyright 2022 ELITE - Salim ROUMILI
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
	_inherit = 'sale.order'

	# Demo method that will delete your sale orde line as you select and press delete
	@api.model
	def delete_sale_order_lines(self, selected_ids):
        #return True
        #test = False
        #_logger.info("HELLO")
		orderline_test = self.env['sale.order.line'].sudo()
		order_lines = orderline_test.browse(selected_ids)
		for line in order_lines:
            #_logger.info("HELLO")
			line.unlink()
		return False