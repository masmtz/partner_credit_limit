from odoo import api, models, _
from odoo.exceptions import UserError, ValidationError

import datetime


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def check_limit(self):
        self.ensure_one()
        today = datetime.date.today()
        partner = self.partner_id
        user_id = self.env['res.users'].search([
            ('partner_id', '=', partner.id)], limit=1)
        payment_term = 'account.account_payment_term_immediate'
        due_invoices = []
        if self.payment_term_id == self.env.ref(payment_term):
            return True
        if user_id and not user_id.has_group('base.group_portal') or not \
                user_id:
            acc_moves = self.env['account.move'].search(
                [('partner_id', '=', partner.id),
                 ('payment_state', '!=', 'paid'),
                 ('invoice_payment_term_id', '!=', payment_term),
                 ('move_type', '=', 'out_invoice')])
            credit_used = 0.0
            days = partner.overdue_days
            for line in acc_moves:
                if line.invoice_date + datetime.timedelta(days=days) < today:
                    due_invoices.append(line.name)
                    # raise ValidationError(
                    #     _('You can not confirm this Sale Order, '
                    #       'there are some invoices '
                    #       'that need to be paid.')
                    #     )
                credit_used += line.amount_total

            if due_invoices:
                str_invoices = ''
                for i in due_invoices:
                    str_invoices += i + '\n'
                raise ValidationError(
                    _('You can not confirm this Sale Order, '
                      'there are some invoices '
                      'that need to be paid:\n {}'.format(str_invoices))
                    )

            if (credit_used + self.amount_total) > partner.credit_limit:
                if not partner.over_credit:
                    raise ValidationError(
                        _('You can not confirm Sale '
                          'Order. \nYour available credit'
                          ' limit Amount = %s \n'
                          'Check "%s" Accounts or Credit Limits.'
                          % ((partner.credit_limit - credit_used),
                             self.partner_id.name))
                         )
            return True

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for order in self:
            order.check_limit()
        return res

    @api.constrains('amount_total')
    def check_amount(self):
        for order in self:
            order.check_limit()
