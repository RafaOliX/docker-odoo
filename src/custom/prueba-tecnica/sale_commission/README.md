# Comisiones de Vendedores (`sale_commission`)

Módulo para el cálculo de comisiones por línea de venta y análisis mensual de rendimiento.

## Características
- Cálculo automático de comisión sobre el subtotal (sin impuestos) al confirmar el pedido.
- Configuración de porcentaje global por vendedor (Ajustes > Usuarios).
- Configuración de porcentaje por categoría de producto (con soporte para herencia de subcategorías).
- Tablero analítico mensual por vendedor.

## Instalación y Uso
1. Instalar el módulo en una base de datos con `sale` y `account`.
2. Configurar el porcentaje base en el perfil del usuario vendedor.
3. (Opcional) Configurar porcentajes específicos en las categorías de producto.
4. Al confirmar un pedido, el porcentaje se congela en la línea para evitar alteraciones retroactivas.

## Historial de Incidentes
- **T-200 (Hotfix)**: Se corrigió un error de acceso (`AccessError`) al confirmar pedidos con el rol de vendedor. Ver [INCIDENT.md](./INCIDENT.md) para el análisis técnico completo.

## Deuda Técnica Conocida
Durante el análisis del código para el T-200, se identificó el siguiente comportamiento que **no fue corregido** en el hotfix para no alterar el alcance ni el comportamiento en producción, pero debe abordarse en un futuro ticket:
- En el método `_get_commission_percent()`, si no existe una regla por categoría, el sistema usa `self.env.user.commission_percent` en lugar de `order.user_id.commission_percent`. Esto genera un bug silencioso cuando un gerente confirma un pedido en nombre de un vendedor: la comisión se calcula con el porcentaje del gerente, no del vendedor.

## Pruebas
Para ejecutar la suite de pruebas unitarias de este módulo:
```bash
./odoo test prueba sale_commission
