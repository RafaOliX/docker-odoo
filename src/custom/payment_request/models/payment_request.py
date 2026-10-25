from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError

class PaymentRequest(models.Model):
    _name = 'payment.request'
    _description = 'Solicitud de Pago'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Referencia", default="/", copy=False, readonly=True)
    partner_id = fields.Many2one('res.partner', string="Proveedor", required=True, tracking=True)
    requester_id = fields.Many2one('res.users', string="Solicitante", default=lambda self: self.env.user, readonly=True, tracking=True)
    
    company_id = fields.Many2one('res.company', string='Compañía', default=lambda self: self.env.company, required=True)
    company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string="Moneda de la Compañía", readonly=True)
    
    amount = fields.Monetary(string="Monto", required=True, currency_field='currency_id', tracking=True)
    currency_id = fields.Many2one('res.currency', string="Moneda", default=lambda self: self.env.company.currency_id)
    
    converted_currency_id = fields.Many2one('res.currency', string="Moneda Convertida", compute="_compute_amount_company_currency", store=True)
    amount_company_currency = fields.Monetary(string="Monto Convertido", compute="_compute_amount_company_currency", currency_field='converted_currency_id', store=True)
    
    approver_id = fields.Many2one('res.users', string="Aprobador asignado", readonly=True, tracking=True)
    approval_date = fields.Datetime(string="Fecha de Aprobación", readonly=True)
    payment_id = fields.Many2one('account.payment', string="Pago registrado", readonly=True)
    
    date = fields.Date(string="Fecha", default=fields.Date.context_today, required=True, tracking=True)
    concept = fields.Text(string="Concepto", required=True, tracking=True)
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('submitted', 'Enviada'),
        ('approved', 'Aprobada'),
        ('paid', 'Pagada'),
        ('rejected', 'Rechazada'),
    ], string="Estado", default='draft', tracking=True)

    @api.depends('amount', 'currency_id', 'date', 'company_id')
    def _compute_amount_company_currency(self):
        ves = self.env.ref('base.VES', raise_if_not_found=False)
        usd = self.env.ref('base.USD', raise_if_not_found=False)
        for record in self:
            if not record.currency_id:
                record.amount_company_currency = 0.0
                continue
            if record.currency_id == usd and ves:
                record.converted_currency_id = ves.id
                record.amount_company_currency = record.currency_id._convert(record.amount, ves, record.company_id, record.date or fields.Date.today())
            elif record.currency_id == ves and usd:
                record.converted_currency_id = usd.id
                record.amount_company_currency = record.currency_id._convert(record.amount, usd, record.company_id, record.date or fields.Date.today())
            else:
                record.converted_currency_id = record.company_currency_id.id
                record.amount_company_currency = record.currency_id._convert(record.amount, record.company_currency_id, record.company_id, record.date or fields.Date.today())

    @api.onchange('amount', 'currency_id', 'date')
    def _onchange_amount_currency(self):
        self._compute_amount_company_currency()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', '/') == '/':
                vals['name'] = self.env['ir.sequence'].next_by_code('payment.request') or '/'
        return super(PaymentRequest, self).create(vals_list)

    def write(self, vals):
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
        self.ensure_one()
        level = self.env['payment.approval.level'].sudo().search([
            ('min_amount', '<=', self.amount),
            ('company_id', '=', self.company_id.id)
        ], limit=1, order='min_amount desc')

        if not level:
            raise UserError(_("No hay un nivel de aprobación configurado para este monto."))

        self.write({'state': 'submitted', 'approver_id': level.approver_id.id})
        self.activity_schedule(
            'mail.mail_activity_data_todo', 
            user_id=level.approver_id.id, 
            summary=_("Aprobar solicitud %s") % self.name, 
            note=_("Monto: %s %s") % (self.amount, self.currency_id.name)
        )

    def action_approve(self):
        for record in self:
            # Bloqueo de base de datos (Tramo C)
            self.env.cr.execute("SELECT state FROM payment_request WHERE id = %s FOR UPDATE", (record.id,))
            record.invalidate_recordset(['state', 'approval_date'])
            
            if record.state == 'approved':
                raise UserError(_("Esta solicitud ya ha sido aprobada por otro usuario."))
                
            if self.env.user != record.approver_id and not self.env.user.has_group('payment_request.group_payment_request_manager'):
                raise UserError(_("Solo el aprobador asignado puede aprobar esta solicitud."))
                
            record.write({
                'state': 'approved',
                'approval_date': fields.Datetime.now()
            })

    def action_reject(self):
        for record in self:
            if self.env.user != record.approver_id:
                raise UserError(_("Solo el aprobador asignado puede rechazar esta solicitud."))
            record.state = 'rejected'

    def action_pay(self):
        for record in self:
            if not self.env.user.has_group('payment_request.group_payment_request_treasury'):
                raise UserError(_("No tienes permisos de Tesorería para pagar solicitudes."))
            record.state = 'paid'

    def action_reset_draft(self):
        self.write({'state': 'draft'})
