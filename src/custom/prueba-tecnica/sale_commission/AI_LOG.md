# AI_LOG — sale_commission (T-200)

## Herramientas
- Claude 3.5 Sonnet — Utilizado como copiloto para el análisis del traceback, generación de boilerplate y redacción de documentación técnica.

## Prompts clave

1. **Análisis del traceback y contención de seguridad**
   - *Prompt*: "Analiza el siguiente traceback de Odoo 17: `AccessError: You are not allowed to access 'Comisión por categoría de producto' (sale.commission.rule)`. Ocurre al confirmar un pedido con un vendedor. Dime la causa raíz y dame la solución más segura. REGLA ESTRICTA: No uses `sudo()` y no añadas al vendedor al grupo de administradores."
   - *Resultado*: La IA identificó que el modelo `sale.commission.rule` carecía de ACLs para `sales_team.group_sale_salesman`. Me proporcionó la línea exacta con permisos de solo lectura (`1,0,0,0`). Validé que esta solución respetaba el principio de mínimo privilegio y la integré en el CSV.

2. **Diseño de la prueba de regresión (TDD)**
   - *Prompt*: "Genera un test en Odoo 17 con `TransactionCase` para reproducir este bug. RESTRICCIÓN CRÍTICA: Debes usar el método `with_user()` para simular al vendedor. Si no lo haces, el test correrá como `admin` y pasará en falso. El test debe validar el cálculo de la comisión tras confirmar."
   - *Resultado*: La IA generó el esqueleto de `test_salesman_can_confirm_order`. Ajusté manualmente las aserciones para que el porcentaje de comisión esperado fuera `8.0`, asegurando que el escenario de prueba coincidiera con la lógica de negocio del módulo.

3. **Estructuración del Post-Mortem**
   - *Prompt*: "Ayúdame a redactar la sección 'Por qué pasó la revisión' para el `INCIDENT.md`. Contexto: El commit `3f4d73f` introdujo el modelo pero eliminó el `with_user(user)` de los tests originales. Necesito un tono profesional y objetivo."
   - *Resultado*: Redactó un texto explicando cómo el cambio en la suite de pruebas provocó que estas perdieran el contexto de seguridad del vendedor, enmascarando el error de permisos en el entorno de integración.

## Lo que la IA hizo mal

- **Sesgo de solución rápida**: Inicialmente, para evitar el `AccessError`, la IA sugirió encapsular el método de búsqueda con `sudo()`. Descarté la propuesta de inmediato; hacer eso habría otorgado privilegios de administrador a los vendedores, violando el requerimiento de seguridad de la prueba.
- **Alucinación de versión (Odoo 16)**: Al solicitar un fragmento de código para modificar las vistas, propuso el uso de la directiva `attrs`. Le señalé el error basándome en la documentación oficial de Odoo 17, donde esta sintaxis está deprecada y debe reemplazarse por expresiones directas (`readonly`, `invisible`).

## Trabajo en entorno y validación (Human-in-the-loop)

Aunque utilicé la IA para generar el código base y la documentación, la ejecución, el diagnóstico del entorno y las pruebas de calidad (QA) fueron realizadas manualmente:

- **Resolución de bloqueos de base de datos**: Durante la actualización del módulo, PostgreSQL lanzó un `LockNotAvailable` en la tabla `res_users`. Diagnosticé que el contenedor web mantenía una transacción abierta. Para solucionarlo, detuve el contenedor de Odoo, ejecuté el `-u sale_commission` por consola y lo reinicié.
- **Gestión de la caché de Odoo**: Tras aplicar el fix del CSV, la interfaz seguía mostrando el `AccessError`. Identifiqué que Odoo cachea la tabla `ir.model.access` en el proceso del servidor; por lo tanto, fue necesario reiniciar el contenedor (`docker compose restart`) para que los nuevos permisos surtieran efecto.
- **Configuración de contabilidad y QA Manual**: La base de datos limpia no tenía un diario de ventas configurado, lo que bloqueaba la confirmación. Creé el diario (`account.journal`) manualmente desde la interfaz y realicé las pruebas End-to-End: confirmé que el vendedor ya podía cerrar pedidos y verifiqué que el gerente mantuviera sus accesos sin regresiones.
