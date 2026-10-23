# INCIDENT — T-200 · Vendedores no pueden confirmar pedidos

**Fecha del incidente:** 2026-10-23 (tarde)
**Severidad:** Crítica (bloquea ventas)
**Estado:** Resuelto

## Síntoma reportado

Desde la actualización del módulo `sale_commission` aplicada al mediodía, ningún
usuario con rol **Vendedor** (`sales_team.group_sale_salesman`) puede confirmar
pedidos de venta: la acción `action_confirm()` falla con error rojo.

El **Gerente de Ventas** (`sales_team.group_sale_manager`) sí puede confirmar
pedidos sin problema. Por eso, durante la tarde, el gerente estuvo confirmando
pedidos en nombre de todos los vendedores.

## Cómo se reproduce

Escenario mínimo automatizado (ver `tests/test_sale_commission.py::test_salesman_can_confirm_order`):

1. Crear un usuario con solo el grupo `sales_team.group_sale_salesman`.
2. Crear un pedido de venta con una línea de un producto cuya categoría tenga
   una regla de comisión configurada.
3. Llamar `order.with_user(vendedor).action_confirm()`.
4. Resultado: `AccessError` sobre `sale.commission.rule`.

Reproducción manual equivalente (UI):
1. Settings → Users → crear un usuario con "Sales: User" (no "Sales: Administrator").
2. Con ese usuario, crear un pedido con una línea y pulsar **Confirmar**.
3. Error rojo.

## Causa raíz

El commit `3f4d73f` ("[FEAT] sale_commission: porcentaje de comisión por
categoría de producto", desplegado esa mañana) introdujo el modelo nuevo
`sale.commission.rule` y su uso en `sale_order_line._get_commission_percent()`,
que hace `self.env["sale.commission.rule"].search([...])` durante
`action_confirm()`.

El `security/ir.model.access.csv` de ese mismo commit **solo concedió
permisos al grupo `sales_team.group_sale_manager`** sobre el modelo nuevo.
No se añadió ninguna regla para `sales_team.group_sale_salesman`.

Resultado: el `search()` que hace el vendedor al confirmar el pedido choca
con el control de acceso de Odoo y lanza `AccessError`.

El gerente sí funciona porque pertenece al grupo con permiso.

## Por qué pasó la revisión

En el mismo commit `3f4d73f`, los tests existentes fueron modificados así:

```diff
-        return self.env["sale.order"].with_user(user).create({
+        return self.env["sale.order"].create({


### Nota de despliegue

Tras actualizar el módulo (`-u sale_commission`), es necesario **reiniciar el
servicio de Odoo** para invalidar la caché de permisos (`ir.model.access`) que
mantiene el proceso web en memoria. Solo con la actualización, el proceso HTTP
sigue usando la tabla de accesos antigua aunque la base de datos ya tenga la
nueva, y el bug persiste hasta el reinicio.

En este entorno Docker:
```bash
docker compose -f docker-compose.generated.yml restart odoo-prueba
