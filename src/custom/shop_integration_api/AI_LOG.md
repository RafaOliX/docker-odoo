# AI_LOG — shop_integration_api

## Herramientas
- Claude 3.5 Sonnet.

## Prompts clave

1. **Manejo de errores HTTP**
   - *Prompt*: "Necesito que un error de validación en Odoo devuelva un JSON con el formato específico `{"error": {"code": "X", "field": "Y", "message": "Z"}}` y un código HTTP 422 en lugar de un 500 por defecto."
   - *Resultado*: Sugirió el uso de `Response` de `odoo.http` con el diccionario estructurado y el status code. Implementé la lógica de validación manual (RIF, producto, cantidad) para lanzar estos errores.

2. **Modelo de auditoría (Log)**
   - *Prompt*: "Genera un modelo en Odoo 17 para guardar un log de llamadas API (endpoint, usuario, status_code, duración) que no requiera permisos especiales para el cliente de la API."
   - *Resultado*: Me dio la estructura del modelo `shop.integration.api.log`. Añadí el uso de `sudo()` al crear el registro en el controlador para asegurar que siempre se guarde, independientemente del usuario que haga la petición.

## Lo que la IA hizo mal
- **Confusión de versión en autenticación**: Para el Tramo B (API Keys), me sugirió usar `auth='bearer'` en el decorador `@http.route`, argumentando que era la forma nativa de Odoo 17. Al probar, Odoo arrojaba un error interno (`ir.http has no attribute _auth_method_bearer`) porque esa característica es en realidad de Odoo 18. Lo detecté al leer el traceback y lo solucioné volviendo a `auth='user'` y forzando la autenticación por sesión en los tests, lo cual es más seguro para esta versión.

## Lo que escribiste tú sin IA
- **Lógica de los filtros de dominio**: La construcción del dominio para el ORM de Odoo (`[('active', '=', True), ('sale_ok', '=', True)]`) combinando los filtros de stock y categoría.
- **Instalación y Depuración**: La creación manual del diario contable en la base de datos (para evitar el error de "No journal found") y la validación visual de la API a través del navegador con el usuario administrador.
