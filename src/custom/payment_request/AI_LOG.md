# AI_LOG — payment_request

## Herramientas
- Claude 3.5 Sonnet.

## Prompts clave
1. **Lógica de Niveles de Aprobación**
   - *Prompt*: "En Odoo 17, necesito implementar la asignación automática de aprobadores al enviar una solicitud. El sistema debe consultar el modelo `payment.approval.level` y asignar al aprobador cuyo `min_amount` sea el umbral más alto que no exceda el monto de la solicitud. Proporciona la consulta ORM."
   - *Resultado*: Se obtuvo la estructura de búsqueda con el parámetro `order='min_amount desc'` y `limit=1`. Se implementó la lógica dentro del método `action_submit`.

2. **Wizard de Pago Contable**
   - *Prompt*: "Genera un `TransientModel` que herede de `account.journal` para registrar un pago de proveedor (outbound) y vincularlo a un modelo transaccional."
   - *Resultado*: Se generó el esqueleto base. Se procedió a añadir validaciones de idempotencia (evitar doble pago) y el manejo de transacciones con `cr.savepoint()` para asegurar la integridad de los datos.

3. **Plantilla QWeb para Reporte PDF**
   - *Prompt*: "Genera una plantilla QWeb para un reporte PDF en Odoo 17 que incluya una tabla de auditoría con la fecha de aprobación."
   - *Resultado*: Se obtuvo la estructura inicial. Se ajustó la sintaxis para el motor de renderizado de Odoo 17, eliminando directivas obsoletas.

## Lo que la IA hizo mal
- **Concurrencia de Aprobadores**: Para el Tramo C, la IA sugirió inicialmente validar el estado del registro con una condicional en Python. Se rechazó dicha propuesta tras analizar el requerimiento del PDF, implementando en su lugar un bloqueo a nivel de base de datos (`SELECT ... FOR UPDATE`) para prevenir condiciones de carrera reales.
- **Renderizado de Moneda (QWeb)**: La IA propuso el uso de `t-options` para formatear el campo monetario, lo cual generaba una excepción (`AttributeError`) en el motor de QWeb de Odoo 17. Se diagnosticó mediante el análisis del traceback y se resolvió delegando la inferencia de la moneda al ORM (`currency_field`).

## Lo que escribiste tú sin IA
- La configuración de la capa de seguridad (`ir.model.access.csv` y `ir.rule`), asegurando el aislamiento de datos por compañía y la segregación de funciones entre Solicitante, Aprobador y Tesorería.
- La refactorización de la vista XML, reemplazando el atributo obsoleto `active_id` por `id` en los contextos de los botones, según los estándares de Odoo 17.
- La implementación del diseño del reporte QWeb utilizando las clases utilitarias nativas de Bootstrap (`table-bordered`, `bg-light`) proporcionadas por Odoo, garantizando la consistencia visual y el correcto renderizado del documento en formato PDF.
