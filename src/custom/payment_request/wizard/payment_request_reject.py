from odoo import fields, models, _

class PaymentRequestReject(models.TransientModel):
    _name = 'payment.request.reject'
    _description = 'Wizard para rechazar pagos'

    request_id = fields.Many2one('payment.request', string="Solicitud", required=True)
    reason = fields.Text(string="Motivo del rechazo", required=True)

    def action_reject(self):
        # Publica el motivo en el chatter y cambia el estado
        self.request_id.message_post(body=_("Solicitud rechazada. Motivo: %s") % self.reason)
        self.request_id.write({'state': 'rejected'})
        return {'type': 'ir.actions.act_window_close'}
