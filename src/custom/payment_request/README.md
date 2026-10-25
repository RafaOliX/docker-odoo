# Solicitudes de Pago (`payment_request`)

## Supuestos y preguntas al cliente (Carolina)

**Preguntas que le haría a Carolina:**
1. **Límite de montos:** Mencionas que los pagos normales los aprueba el jefe y los grandes gerencia. ¿Cuál es el monto exacto que separa un pago "normal" de uno "grande"? (Ej: ¿A partir de $500?).
2. **Tasa de cambio:** Mencionas que facturan en dólares pero pagan en bolívares. Para el asiento contable del pago, ¿qué tasa de cambio debemos usar? ¿La del Banco Central de Venezuela (BCV) del día del pago, o manejan una tasa interna?
3. **Contabilidad:** Cuando tesorería registre el pago, ¿en qué diario contable específico (banco) se debe reflejar?

**Supuestos asumidos para avanzar sin respuesta:**
- El sistema utiliza una lógica de "Monto Mínimo" para escalar la aprobación: si una solicitud supera el monto mínimo del nivel 2 (Gerencia), se le asigna automáticamente a Gerencia, ignorando al jefe de área.
- Las solicitudes en moneda extranjera (USD) se convierten automáticamente a la moneda de la compañía (VES) usando la tasa de cambio configurada en Odoo para la fecha de la solicitud.
- Si se rechaza, la solicitud vuelve a estado Borrador para que el empleado pueda corregir y reenviar.
- Una solicitud enviada no puede ser editada por el solicitante.
- El pago se registra como un `account.payment` de tipo proveedor (outbound) y se vincula a la solicitud.
