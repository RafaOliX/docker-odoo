from odoo.tests.common import TransactionCase, tagged
from odoo.exceptions import ValidationError, UserError

@tagged('post_install', '-at_install')
class TestPaymentRequest(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({'name': 'Proveedor Test'})
        cls.requester = cls.env['res.users'].create({
            'name': 'Requester Test',
            'login': 'requester_test',
            'groups_id': [(6, 0, [cls.env.ref('base.group_user').id, cls.env.ref('payment_request.group_payment_request_user').id])]
        })
        cls.approver = cls.env['res.users'].create({
            'name': 'Approver Test',
            'login': 'approver_test',
            'groups_id': [(6, 0, [cls.env.ref('base.group_user').id, cls.env.ref('payment_request.group_payment_request_approver').id])]
        })
        cls.treasury = cls.env['res.users'].create({
            'name': 'Treasury Test',
            'login': 'treasury_test',
            'groups_id': [(6, 0, [cls.env.ref('base.group_user').id, cls.env.ref('payment_request.group_payment_request_treasury').id])]
        })

    def test_create_request_sequence(self):
        req = self.env['payment.request'].create({
            'partner_id': self.partner.id,
            'amount': 100.0,
            'concept': 'Test concept',
        })
        self.assertNotEqual(req.name, '/')
        self.assertTrue(req.name.startswith('SP/'))

    def test_zero_amount_validation(self):
        with self.assertRaises(ValidationError):
            self.env['payment.request'].create({
                'partner_id': self.partner.id,
                'amount': 0.0,
                'concept': 'Test concept',
            })

    def test_requester_cannot_approve_by_method(self):
        """Prueba que el solicitante no puede aprobar ni siquiera usando código"""
        req = self.env['payment.request'].with_user(self.requester).create({
            'partner_id': self.partner.id,
            'amount': 50.0,
            'concept': 'Security test',
        })
        req.action_submit()
        
        # El solicitante intenta aprobar
        with self.assertRaises(UserError):
            req.with_user(self.requester).action_approve()

    def test_cannot_edit_submitted(self):
        """Prueba que no se puede editar una solicitud enviada"""
        req = self.env['payment.request'].create({
            'partner_id': self.partner.id,
            'amount': 50.0,
            'concept': 'Edit test',
        })
        req.action_submit()
        with self.assertRaises(UserError):
            req.write({'amount': 200.0})

    def test_flow(self):
        """Prueba el flujo completo (Borrador -> Enviada -> Aprobada -> Pagada)"""
        req = self.env['payment.request'].with_user(self.requester).create({
            'partner_id': self.partner.id,
            'amount': 50.0,
            'concept': 'Flow test',
        })
        self.assertEqual(req.state, 'draft')
        req.action_submit()
        self.assertEqual(req.state, 'submitted')
        
        # Aprobador aprueba
        req.with_user(self.approver).action_approve()
        self.assertEqual(req.state, 'approved')
        
        # Tesorería paga (Usando el usuario tesorería que creamos)
        req.with_user(self.treasury).action_pay()
        self.assertEqual(req.state, 'paid')