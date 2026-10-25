from odoo.tests.common import TransactionCase, tagged
from odoo.exceptions import ValidationError, UserError

@tagged('post_install', '-at_install')
class TestPaymentRequest(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.user.email = 'admin@test.com'
        cls.partner = cls.env['res.partner'].create({'name': 'Proveedor Test'})
        
        cls.requester = cls.env['res.users'].create({'name': 'Req', 'login': 'req_t', 'email': 'req@t.com', 'groups_id': [(6, 0, [cls.env.ref('base.group_user').id, cls.env.ref('payment_request.group_payment_request_user').id])]})
        cls.approver = cls.env['res.users'].create({'name': 'App', 'login': 'app_t', 'email': 'app@t.com', 'groups_id': [(6, 0, [cls.env.ref('base.group_user').id, cls.env.ref('payment_request.group_payment_request_approver').id])]})
        cls.treasury = cls.env['res.users'].create({'name': 'Treas', 'login': 'treas_t', 'email': 'treas@t.com', 'groups_id': [(6, 0, [cls.env.ref('base.group_user').id, cls.env.ref('payment_request.group_payment_request_treasury').id])]})

        # LIMPIEZA CRÍTICA: Borrar niveles existentes para que el test sea determinista
        cls.env['payment.approval.level'].search([]).unlink()

        # Crear niveles desde cero
        cls.level1 = cls.env['payment.approval.level'].create({'name': 'Jefe', 'min_amount': 0.0, 'approver_id': cls.approver.id})
        cls.level2 = cls.env['payment.approval.level'].create({'name': 'Gerencia', 'min_amount': 100.0, 'approver_id': cls.env.ref('base.user_admin').id})

    def test_create_request_sequence(self):
        req = self.env['payment.request'].create({'partner_id': self.partner.id, 'amount': 10.0, 'concept': 'Test'})
        self.assertTrue(req.name.startswith('SP/'))

    def test_zero_amount_validation(self):
        with self.assertRaises(ValidationError):
            self.env['payment.request'].create({'partner_id': self.partner.id, 'amount': 0.0, 'concept': 'Test'})

    def test_cannot_edit_submitted(self):
        req = self.env['payment.request'].create({'partner_id': self.partner.id, 'amount': 50.0, 'concept': 'Test'})
        req.action_submit()
        with self.assertRaises(UserError):
            req.write({'amount': 200.0})

    def test_requester_cannot_approve(self):
        req = self.env['payment.request'].with_user(self.requester).create({'partner_id': self.partner.id, 'amount': 50.0, 'concept': 'Test'})
        req.action_submit()
        with self.assertRaises(UserError):
            req.with_user(self.requester).action_approve()

    def test_approval_level_assignment(self):
        # Monto de 50 debe ir al aprobador (Jefe)
        req1 = self.env['payment.request'].with_user(self.requester).create({'partner_id': self.partner.id, 'amount': 50.0, 'concept': 'Test'})
        req1.action_submit()
        self.assertEqual(req1.approver_id.id, self.approver.id)

        # Monto de 150 debe ir a Gerencia
        req2 = self.env['payment.request'].with_user(self.requester).create({'partner_id': self.partner.id, 'amount': 150.0, 'concept': 'Test'})
        req2.action_submit()
        self.assertEqual(req2.approver_id.id, self.env.ref('base.user_admin').id)

    def test_full_flow_and_double_payment(self):
        req = self.env['payment.request'].with_user(self.requester).create({'partner_id': self.partner.id, 'amount': 50.0, 'concept': 'Flow Test'})
        req.action_submit()
        req.with_user(req.approver_id).action_approve()
        self.assertEqual(req.state, 'approved')
        
        # Primer pago exitoso
        journal = self.env['account.journal'].search([('type', '=', 'bank')], limit=1)
        if not journal:
            journal = self.env['account.journal'].create({'name': 'Bank Test', 'type': 'bank', 'code': 'BNKT'})
            
        wizard = self.env['payment.request.pay'].with_user(self.treasury).create({'request_id': req.id, 'journal_id': journal.id})
        wizard.action_pay()
        self.assertEqual(req.state, 'paid')

        # Intento de doble pago (Debe fallar)
        with self.assertRaises(UserError):
            wizard2 = self.env['payment.request.pay'].with_user(self.treasury).create({'request_id': req.id, 'journal_id': journal.id})
            wizard2.action_pay()
