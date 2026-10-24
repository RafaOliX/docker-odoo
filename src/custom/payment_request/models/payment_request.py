from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError

class PaymentRequest(models.Model):
    _name = 'payment.request'
    _description = 'Solicitud de Pago'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Referencia", default="/", copy=False, readonly=True)
    partner_id = fields.Many2one('res.partner', string="Proveedor", required=True, tracking=True)
    requester_id = fields.Many2one('res.users', string="Solicitante", default=lambda self: self.env.user, readonly=True, tracking=True)
    amount = fields.Monetary(string="Monto", required=True, currency_field='currency_id', tracking=True)
    currency_id = fields.Many2one('res.currency', string="Moneda", default=lambda self: self.env.company.currency_id)
    date = fields.Date(string="Fecha", default=fields.Date.context_today, required=True, tracking=True)
    concept = fields.Text(string="Concepto", required=True, tracking=True)
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('submitted', 'Enviada'),
        ('approved', 'Aprobada'),
        ('paid', 'Pagada'),
        ('rejected', 'Rechazada'),
    ], string="Estado", default='draft', tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', '/') == '/':
                vals['name'] = self.env['ir.sequence'].next_by_code('payment.request') or '/'
        return super(PaymentRequest, self).create(vals_list)

    def write(self, vals):
        # Regla: Una solicitud enviada no se puede editar (excepto para cambiar de estado)
        if 'state' not in vals:
            for record in self:
                if record.state != 'draft':
                    raise UserError(_("Solo se pueden editar solicitudes en estado de Borrador."))
        return super(PaymentRequest, self).write(vals)

    @api.constrains('amount')
    def _check_amount(self):
        for record in self:
            if record.amount <= 0:
                raise ValidationError(_("El monto debe ser mayor a cero."))

    def action_submit(self):
        self.write({'state': 'submitted'})

    def action_approve(self):
        # Validar que el usuario realmente sea Aprobador (ni por código ni por RPC)
        if not self.env.user.has_group('payment_request.group_payment_request_approver'):
            raise UserError(_("No tienes permisos para aprobar solicitudes de pago."))
        self.write({'state': 'approved'})

    def action_reject(self):
        if not self.env.user.has_group('payment_request.group_payment_request_approver'):
            raise UserError(_("No tienes permisos para rechazar solicitudes de pago."))
        self.write({'state': 'rejected'})

    def action_pay(self):
        if not self.env.user.has_group('payment_request.group_payment_request_treasury'):
            raise UserError(_("No tienes permisos de Tesorería para pagar solicitudes."))
        self.write({'state': 'paid'})

    def action_reset_draft(self):
        self.write({'state': 'draft'})