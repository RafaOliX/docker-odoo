# Comisiones de vendedores (`sale_commission`)

Calcula la comisión del vendedor en cada línea de pedido de venta y ofrece un análisis mensual por vendedor.

## Configuración

- **Porcentaje del vendedor:** Ajustes › Usuarios › pestaña *Comisiones* (solo gerentes de ventas).
- **Porcentaje por categoría (desde la 1.1):** Inventario/Ventas › Configuración › Categorías de producto,
  campo *Comisión (%)*. Si la categoría (o una categoría padre) tiene porcentaje, reemplaza al del vendedor.

## Cómo funciona

- Al confirmar el pedido se fija el porcentaje en cada línea y se calcula la comisión sobre el subtotal sin impuestos.
- El botón *Recalcular comisiones* del pedido vuelve a aplicar los porcentajes vigentes.
- Ventas › Reportes › *Comisiones*: tabla dinámica y gráfico por vendedor y mes. Cada vendedor ve solo lo suyo.

## Pruebas

```bash
./odoo test prueba-tecnica sale_commission
```
## Incidente T-200 (2026-10-23)

Ver [`INCIDENT.md`](./INCIDENT.md). Corrección aplicada en la rama
`hotfix/T-200`: se concedió lectura de `sale.commission.rule` al grupo
`sales_team.group_sale_salesman`. Commit: `[FIX] sale_commission: T-200 ...`.

### Limitaciones conocidas

- `_get_commission_percent()` usa `self.env.user.commission_percent` como
  fallback cuando no hay regla de categoría. Debería usar
  `order.user_id.commission_percent`. **No corregido en el hotfix** para no
  ampliar el alcance; registrado como ticket separado.
