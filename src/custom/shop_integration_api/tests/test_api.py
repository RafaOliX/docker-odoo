import json
from odoo.tests.common import HttpCase, tagged

@tagged('post_install', '-at_install')
class TestShopIntegrationApi(HttpCase):

    def setUp(self):
        super().setUp()
        # Autenticar la sesión como admin
        self.authenticate('admin', 'admin')

        # 2. Datos de prueba (Productos y Categoría)
        self.category = self.env['product.category'].create({'name': 'Test Cat'})

        self.product_1 = self.env['product.product'].create({
            'name': 'Producto de Prueba 1',
            'default_code': 'TEST001',
            'categ_id': self.category.id,
            'list_price': 150.0,
            'sale_ok': True,
            'active': True,
            'type': 'product',
        })
        self.env['stock.quant']._update_available_quantity(
            self.product_1, self.env.ref('stock.stock_location_stock'), 10.0
        )

        self.product_2 = self.env['product.product'].create({
            'name': 'Producto de Prueba 2',
            'default_code': 'TEST002',
            'list_price': 50.0,
            'sale_ok': True,
            'active': True,
        })

        # 3. Cliente para el test de la orden
        self.partner = self.env['res.partner'].create({'name': 'Cliente Test API', 'vat': 'J123456789'})

    def test_get_products_basic(self):
        response = self.url_open('/api/v1/products')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        test_products = [p for p in data if p['default_code'] in ('TEST001', 'TEST002')]
        self.assertEqual(len(test_products), 2)

    def test_filter_by_category(self):
        response = self.url_open(f'/api/v1/products?category_id={self.category.id}')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['default_code'], 'TEST001')

    def test_filter_only_stock(self):
        response = self.url_open('/api/v1/products?only_stock=true')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        test_products = [p for p in data if p['default_code'] == 'TEST001']
        self.assertEqual(len(test_products), 1)

    def test_invalid_date_format(self):
        response = self.url_open('/api/v1/products?modified_since=esto-no-es-una-fecha')
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data['error']['code'], 'INVALID_DATE')

    def test_create_order_success(self):
        payload = {
            "rif": "J123456789",
            "external_reference": "EXT-001",
            "lines": [{"default_code": "TEST001", "quantity": 2}]
        }
        headers = {'Content-Type': 'application/json'}
        response = self.url_open('/api/v1/orders', data=json.dumps(payload), headers=headers)
        
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data['state'], 'draft')
        self.assertEqual(data['external_reference'], 'EXT-001')
        
        log = self.env['shop.integration.api.log'].search([('endpoint', '=', '/api/v1/orders')], limit=1)
        self.assertEqual(log.status_code, 201)

    def test_create_order_invalid_product(self):
        payload = {
            "rif": "J123456789",
            "external_reference": "EXT-002",
            "lines": [{"default_code": "INVALID-CODE", "quantity": 1}]
        }
        headers = {'Content-Type': 'application/json'}
        response = self.url_open('/api/v1/orders', data=json.dumps(payload), headers=headers)
        
        self.assertEqual(response.status_code, 422)
        data = response.json()
        self.assertEqual(data['error']['code'], 'PRODUCT_NOT_FOUND')