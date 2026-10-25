# Arquitectura: Módulo de Solicitudes de Pago

## Decisiones de Diseño

### 1. Concurrencia de Aprobadores
Para evitar que dos gerentes aprueben la misma solicitud al mismo tiempo (condición de carrera), se implementó un bloqueo a nivel de base de datos usando `SELECT ... FOR UPDATE` (PostgreSQL). Esto garantiza que la primera transacción que bloquee el registro sea la única que pueda modificar el estado a "Aprobada", rechazando cualquier intento posterior.

### 2. Manejo de Fallos en el Pago
La creación del asiento contable (`account.payment`) se ejecuta dentro de un `cr.savepoint()`. Si el sistema contable falla (por ejemplo, por falta de configuración en el diario), se realiza un rollback automático y la solicitud permanece en estado "Aprobada", evitando que quede marcada como "Pagada" sin su correspondiente asiento contable.

### 3. Multi-compañía
Se implementaron reglas de registro (`ir.rule`) basadas en `company_ids`. Un usuario perteneciente a la Compañía B no podrá ver las solicitudes de pago creadas en la Compañía A, cumpliendo con el aislamiento de datos corporativos de Odoo.

### 4. Conversión de Moneda
Se utilizan los métodos nativos de Odoo (`res.currency._convert`) para calcular el monto en la moneda de la compañía basándose en la fecha de la solicitud. El asiento contable generado respeta la moneda original de la solicitud, dejando que el motor contable de Odoo (res.currency.rate) haga la conversión a VES en el diario correspondiente.
