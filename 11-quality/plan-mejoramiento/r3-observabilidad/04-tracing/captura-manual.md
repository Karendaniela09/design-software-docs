# Captura visual de la traza en Grafana Explore

> Estado: En revisión | Última actualización: 2026-10-20
> Autor: Kevin Andrey Culma Gómez | Equipo: Monitoring / ADSO 3145555

> Documento trasladado desde la entrega original. Las rutas de capturas y salidas se consultan en la carpeta local `EVIDENCIAS-PLAN-MEJORAMIENTO-R3`. Para el corte vigente, consultar el índice R3 y `estado-actual.md`; los resultados antiguos conservan su fecha y alcance.

VALIDACION EJECUTADA Y APROBADA el 19 de octubre de 2026. `tempo-trace.png` es una captura real del navegador, sin edicion: muestra ocho spans, monitoring-mfe, monitoring-service e INSERT monitoring_r3 (6,41 ms), con trace ID `1541ef6e05e37e0356b570c7b2c37b5c`.

La captura conserva un aviso auxiliar Unauthorized de Grafana; el resultado de Tempo esta cargado y se observa el arbol completo. La consulta tambien se verifico contra la API. No se oculto ni retoco el aviso.

Reproduccion desde design-software-web-shell:

```powershell
node scripts/r3-capture-trace.mjs
```

Alternativa manual: abrir http://localhost:13000/explore, elegir Tempo y TraceQL, pegar el trace ID de trace-summary.json y ejecutar. Expandir hasta INSERT. El ID debe seguir dentro de la retencion; si expiro ejecutar el E2E y recolector para generar uno nuevo.
