# Prueba Técnica Binaural - 2026-Q4

**Desarrollador:** Rafael Andrés Olivares Criollo
**Versión de Odoo:** 17.0
**Entorno:** Docker (basado en `binaural-dev/docker-odoo`)

## Resumen de la Entrega

1. **Ejercicio 1 (`shop_integration_api`):** Tramos A y B completados. (Rama: `feat/shop_integration_api`)
2. **Ejercicio 2 (`fleet_inspection`):** Tramo A completado (Migración a Odoo 17). (Rama: `mig/fleet_inspection`)
3. **Ejercicio 3 (`sale_commission` - T-200):** Tramo A completado (Hotfix y análisis). (Rama: `hotfix/T-200`)
4. **Ejercicio 4 (`payment_request`):** Pendiente por límite de tiempo.

## Cómo correr las pruebas
Para ejecutar las pruebas de los módulos entregados:
```bash
./odoo test prueba shop_integration_api,fleet_inspection,sale_commission -d prueba_limpia
