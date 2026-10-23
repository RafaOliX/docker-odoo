# AI_LOG — sale_commission

## Herramientas
- Claude (Anthropic) — asistencia durante la investigación del T-200.

## Prompts clave
1. Análisis del commit `3f4d73f` para identificar la causa del `AccessError`.
   - Se revisó junto conmigo; la causa (falta de ACLs para `group_sale_salesman`)
     se confirmó ejecutando el test `test_salesman_can_confirm_order`.
2. Redacción del `INCIDENT.md`.
   - Se ajustó el contenido a los hechos verificados con logs y pruebas.

## Lo que la IA hizo mal
- La primera hipótesis de causa raíz fue "sudo() ausente en el compute". Era
  incorrecta: el problema real era la tabla de ACLs. Se detectó al inspeccionar
  el `ir.model.access.csv` del commit y confirmar con la prueba ejecutable.

## Lo que escribiste tú sin IA
- Aplicación del fix mínimo (1 línea en CSV), ejecución de los tests antes y
  después, y validación con `with_user(self.salesman)`.
