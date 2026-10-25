from odoo import fields, models, _
from odoo.exceptions import UserError

class PaymentRequestPay(models.TransientModel):
    _name = 'payment.request.pay'
    _description = 'Wizard para pagar solicitudes'

    request_id = fields.Many2one('payment.request', string="Solicitud", required=True)
    journal_id = fields.Many2one('account.journal', string="Diario de pago", required=True, domain="[('type', 'in', ('bank', 'cash'))]")
    amount = fields.Monetary(related='request_id.amount', string="Monto")
    currency_id = fields.Many2one(related='request_id.currency_id')

    def action_pay(self):
        if self.request_id.state != 'approved':
            raise UserError(_("Solo se pueden pagar solicitudes en estado Aprobada."))
        
        # Si ya tiene un pago, bloqueamos la doble ejecución (Exigencia del PDF)
        if self.request_id.payment_id:
            raise UserError(_("Esta solicitud ya tiene un pago registrado."))

        # Creación del asiento contable (account.payment)
        payment = self.env['account.payment'].create({
            'partner_id': self.request_id.partner_id.id,
            'partner_type': 'supplier',
            'payment_type': 'outbound',
            'amount': self.request_id.amount,
            'currency_id': self.request_id.currency_id.id,
            'journal_id': self.journal_id.id,
            'date': self.request_id.date,
            'ref': self.request_id.name,
        })
        payment.action_post()

        # Vinculamos el pago y cambiamos el estado
        self.request_id.write({
            'state': 'paid',
            'payment_id': payment.id
        })
        return {'type': 'ir.actions.act_window_close'}
