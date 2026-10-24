# Módulo de Inspecciones (`fleet_inspection`)

Este módulo permite registrar inspecciones de vehículos mediante un checklist configurable.

## Tabla de Migración (Odoo 16 → 17)

| Qué cambió | Por qué | Cómo lo resolví |
| :--- | :--- | :--- |
| **Manifest (`__manifest__.py`)** | Odoo 17 rechaza versiones de módulos que no coincidan con la versión base. | Actualicé la clave `version` de `16.0.1.0.0` a `17.0.1.0.0`. |
| **Vistas XML (`fleet_inspection_views.xml`)** | La directiva `attrs` fue eliminada en Odoo 17. Ahora se usan expresiones de dominio directas. | Reemplacé `attrs="{'invisible': [...]}"` por `invisible="..."` y `attrs="{'readonly': [...]}"` por `readonly="..."`. |
| **Botones del Formulario (`header`)** | El atributo `states` en los botones fue eliminado en Odoo 17. | Reemplacé `states="draft"` por `invisible="state != 'draft'"`. |
| **Modelos Python (`fleet_inspection.py`)** | El decorador `@api.model` para el método `create` está deprecado. Odoo 17 exige `@api.model_create_multi`. | Cambié el método `create` para recibir `vals_list`, iterar sobre él y llamar a `super()`. Eliminé el parámetro `states` de los campos. |
| **Reportes QWeb (`fleet_inspection_report.xml`)** | `t-esc` está deprecado y lanza advertencias en Odoo 17. | Reemplacé todas las etiquetas `t-esc` por `t-out`. |

## Pruebas

El módulo incluye una suite de pruebas unitarias que validan el flujo, las restricciones y los permisos. Para ejecutarlas:

```bash
./odoo test prueba fleet_inspection