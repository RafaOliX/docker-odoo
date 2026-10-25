# Solicitudes de Pago (`payment_request`)

Módulo para la gestión y aprobación de pagos a proveedores.

## Tramos Completados
- [x] Tramo A: Modelo base, flujo de estados, grupos de seguridad y conversión de moneda.
- [x] Tramo B: Niveles de aprobación configurables, wizards de rechazo y pago, reporte PDF.
- [x] Tramo C: Concurrencia con bloqueo de base de datos, multi-compañía y manejo de fallos transaccionales.

## Supuestos y preguntas al cliente (Carolina)

**Preguntas para Carolina:**
1. **Límite de montos:** Para configurar los niveles de aprobación, ¿cuál es el monto exacto que separa un pago "normal" de uno "grande"?
2. **Tasa de cambio:** ¿Qué tasa de cambio se debe utilizar para el pago de facturas en USD? ¿La tasa oficial del BCV del día del pago o una tasa interna?
3. **Contabilidad:** ¿Tesorería registrará el pago directamente en un diario de banco específico?

**Supuestos asumidos:**
- El sistema asigna al aprobador basándose en el nivel cuyo umbral sea el más alto que cubra el monto solicitado.
- Se implementó un `savepoint` transaccional: si la creación del asiento contable falla, la solicitud no cambia a estado "Pagada".
- Las solicitudes no pueden ser editadas por el solicitante una vez que han sido enviadas.

## Pruebas
```bash
./odoo test prueba payment_request
