# INCIDENT — T-200: Fallo de permisos al confirmar pedidos

**Fecha**: 23 de Octubre de 2026  
**Severidad**: Crítica (Bloqueo de ventas)  
**Estado**: Resuelto  

## 1. Síntoma
Tras la actualización del módulo `sale_commission` (v1.1.0), cualquier usuario con el rol de **Vendedor** (`sales_team.group_sale_salesman`) recibía un error en pantalla al intentar confirmar un pedido de venta. El rol de **Gerente** (`sales_team.group_sale_manager`) no presentaba problemas.

## 2. Causa Raíz (Root Cause)
El commit `3f4d73f` introdujo el modelo `sale.commission.rule` y modificó la lógica de confirmación en `sale_order_line._get_commission_percent()` para consultar reglas por categoría. 

Sin embargo, el archivo `security/ir.model.access.csv` solo definió permisos para el grupo de gerentes. Al ejecutarse la confirmación, el vendedor lanzaba un `search()` sobre un modelo al que no tenía acceso de lectura, provocando el siguiente traceback:
`odoo.exceptions.AccessError: You are not allowed to access 'Comisión por categoría de producto' (sale.commission.rule) records.`

### ¿Por qué pasó la revisión? (Análisis de QA)
El mismo commit modificó los tests unitarios existentes. Se eliminó el uso de `with_user(user)` en la creación de pedidos de prueba. Esto provocó que los tests abandonaran el contexto del vendedor y se ejecutaran con el superusuario (`admin`). El superusuario ignora las reglas de ACL, por lo que las pruebas pasaban en verde (falso positivo) a pesar de que la funcionalidad estaba rota para los usuarios reales.

## 3. Solución Aplicada
Se modificó exclusivamente la capa de seguridad (`ir.model.access.csv`) aplicando el principio de mínimo privilegio (PoLP):
- Se añadió la regla `sale.commission.rule.salesman` otorgando permisos de **solo lectura** (`1,0,0,0`) al grupo `sales_team.group_sale_salesman`.
- Se descartó el uso de `sudo()` en el código Python, ya que habría otorgado privilegios excesivos e inseguros al vendedor.

## 4. Verificación
Se añadió el test de regresión `test_salesman_can_confirm_order` que fuerza el contexto del vendedor mediante `with_user(self.salesman)`. 
- **Antes del fix**: El test falla con `AccessError`.
- **Después del fix**: El test pasa y valida el cálculo correcto de la comisión.

## 5. Notas de Despliegue (SRE)
En Odoo, la tabla de accesos (`ir.model.access`) se carga en la caché del proceso web. Tras aplicar este fix, **no es suficiente** con actualizar el módulo (`-u`). Es obligatorio reiniciar el servicio de Odoo para invalidar la caché y forzar la recarga de los permisos desde la base de datos.
