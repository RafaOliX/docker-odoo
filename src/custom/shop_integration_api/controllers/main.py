import json
import time
from odoo import http, fields
from odoo.http import request, Response

class ShopIntegrationController(http.Controller):

    def _log_call(self, endpoint, user, status_code, start_time):
        duration = time.time() - start_time
        request.env['shop.integration.api.log'].sudo().create({
            'endpoint': endpoint,
            'user_id': user.id if user and user.id else False,
            'status_code': status_code,
            'duration': duration,
        })

    def _error_response(self, status, code, field, message):
        return Response(
            json.dumps({"error": {"code": code, "field": field, "message": message}}),
            status=status,
            content_type='application/json'
        )

    @http.route('/api/v1/products', type='http', auth='user', methods=['GET'], csrf=False)
    def get_products(self, **kwargs):
        start_time = time.time()
        endpoint = '/api/v1/products'
        user = request.env.user

        date_str = kwargs.get('modified_since')
        date_filter = None
        if date_str:
            try:
                date_filter = fields.Datetime.to_datetime(date_str)
            except Exception:
                self._log_call(endpoint, user, 400, start_time)
                return self._error_response(400, "INVALID_DATE", "modified_since", "Formato de fecha inválido. Use ISO 8601 (YYYY-MM-DD)")

        domain = [('active', '=', True), ('sale_ok', '=', True)]

        category_id = kwargs.get('category_id')
        if category_id:
            domain.append(('categ_id', '=', int(category_id)))

        only_stock = kwargs.get('only_stock')
        if only_stock and only_stock.lower() == 'true':
            domain.append(('qty_available', '>', 0))

        if date_filter:
            domain.append(('write_date', '>=', date_filter))

        products = request.env['product.product'].with_user(user).search(domain)

        result = []
        for p in products:
            result.append({
                "id": p.id,
                "default_code": p.default_code or "",
                "name": p.name,
                "list_price": p.list_price,
                "qty_available": p.qty_available,
            })

        self._log_call(endpoint, user, 200, start_time)
        return Response(json.dumps(result), status=200, content_type='application/json')

    @http.route('/api/v1/orders', type='http', auth='user', methods=['POST'], csrf=False)
    def create_order(self, **kwargs):
        start_time = time.time()
        endpoint = '/api/v1/orders'
        user = request.env.user

        try:
            data = json.loads(request.httprequest.data)
        except Exception:
            self._log_call(endpoint, user, 400, start_time)
            return self._error_response(400, "INVALID_JSON", "body", "El cuerpo debe ser un JSON válido")

        rif = data.get('rif')
        external_ref = data.get('external_reference')
        lines = data.get('lines', [])

        partner = request.env['res.partner'].with_user(user).search([('vat', '=', rif)], limit=1)
        if not partner:
            self._log_call(endpoint, user, 422, start_time)
            return self._error_response(422, "PARTNER_NOT_FOUND", "rif", f"No existe un cliente con el RIF {rif}")

        order_lines = []
        for idx, line in enumerate(lines):
            code = line.get('default_code')
            qty = line.get('quantity', 0)

            if qty <= 0:
                self._log_call(endpoint, user, 422, start_time)
                return self._error_response(422, "INVALID_QUANTITY", f"lines[{idx}].quantity", "La cantidad debe ser mayor a cero")

            product = request.env['product.product'].with_user(user).search([('default_code', '=', code)], limit=1)
            if not product:
                self._log_call(endpoint, user, 422, start_time)
                return self._error_response(422, "PRODUCT_NOT_FOUND", f"lines[{idx}].default_code", f"No existe un producto con el código {code}")

            order_lines.append((0, 0, {
                'product_id': product.id,
                'product_uom_qty': qty,
            }))

        order = request.env['sale.order'].with_user(user).create({
            'partner_id': partner.id,
            'client_order_ref': external_ref,
            'order_line': order_lines,
        })

        result = {
            "id": order.id,
            "name": order.name,
            "state": order.state,
            "external_reference": external_ref
        }

        self._log_call(endpoint, user, 201, start_time)
        return Response(json.dumps(result), status=201, content_type='application/json')