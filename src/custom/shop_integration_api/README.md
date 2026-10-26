# Shop Integration API

Módulo de integración para la tienda en línea. Expone endpoints REST para consultar productos y crear pedidos.

## Tramos Completados
- [x] Tramo A: Endpoint GET con filtros.
- [x] Tramo B: Autenticación (nativa), creación de pedidos y log de llamadas.

## Endpoints

### `GET /api/v1/products`
Obtiene productos activos y vendibles.
- **Filtros (Query Params):** `category_id`, `only_stock` (true/false), `modified_since` (YYYY-MM-DD).
- **Error:** Si la fecha es inválida, devuelve HTTP 400 con JSON descriptivo.

### `POST /api/v1/orders`
Crea un pedido (cotización) en Odoo.
- **Payload:** `{"rif": "J123", "external_reference": "EXT-1", "lines": [{"default_code": "PROD1", "quantity": 2}]}`
- **Errores (HTTP 422):** Devuelve el formato exacto exigido `{"error": {"code": "PRODUCT_NOT_FOUND", "field": "lines[0].default_code", "message": "..."}}`.
- **Supuesto:** El pedido se crea en estado "Borrador" (Cotización) para que un vendedor lo revise antes de confirmar.

## Pruebas
Para correr la suite (6 tests, 89% cobertura):
```bash
./odoo test prueba shop_integration_api
