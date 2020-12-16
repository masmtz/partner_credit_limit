# See LICENSE file for full copyright and licensing details.
from odoo import _, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    over_credit = fields.Boolean('Allow Over Credit?')
    overdue_days = fields.Integer('Overdue Days', default=30)
