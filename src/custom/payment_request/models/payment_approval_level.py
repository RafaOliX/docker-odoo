from odoo import fields, models

class PaymentApprovalLevel(models.Model):
    _name = 'payment.approval.level'
    _description = 'Nivel de aprobación para pagos'
    _order = 'min_amount desc'

    name = fields.Char(string="Nombre del nivel", required=True)
    min_amount = fields.Monetary(string="Monto Mínimo", required=True, currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string="Moneda", default=lambda self: self.env.company.currency_id)
    approver_id = fields.Many2one('res.users', string="Aprobador asignado", required=True)
    company_id = fields.Many2one('res.company', string="Compañía", default=lambda self: self.env.company)
