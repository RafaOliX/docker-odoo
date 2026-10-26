from odoo import fields, models

class ShopIntegrationApiLog(models.Model):
    _name = 'shop.integration.api.log'
    _description = 'Log de llamadas a la API'

    endpoint = fields.Char(string="Endpoint", required=True)
    user_id = fields.Many2one('res.users', string="Usuario")
    status_code = fields.Integer(string="Código HTTP", required=True)
    duration = fields.Float(string="Duración (segundos)")
