# Incidencias encontradas y correcciones

> Estado: En revisión | Última actualización: 2026-10-20
> Autor: Kevin Andrey Culma Gómez | Equipo: Monitoring / ADSO 3145555

> Documento trasladado desde la entrega original. Las rutas de capturas y salidas se consultan en la carpeta local `EVIDENCIAS-PLAN-MEJORAMIENTO-R3`. Para el corte vigente, consultar el índice R3 y `estado-actual.md`; los resultados antiguos conservan su fecha y alcance.

| Hallazgo real | Corrección | Validación |
|---|---|---|
| SQLAlchemy 2.1.5 fuera del rango del instrumentador | Restringir `<2.1` y fijar runtime 2.0.55 en lock | Span INSERT real en Tempo; test PostgreSQL |
| `_IncludedRouter` sin propiedad `path` en FastAPI resuelto | Verificar rutas mediante OpenAPI público | Suite backend aprobada |
| UUID serializado con `isoformat()` provoca HTTP 500 | Serializar UUID con `str()` | Regresión unitaria, catálogo y fila PostgreSQL |
| Paginación `total` no coincide con contrato `total_items/total_pages` | Devolver campos del contrato | Navegador comprueba ausencia de NaN |
| Catálogos cerrados paginados donde MFE esperaba array | Adaptador acepta datos paginados del backend real | Pruebas MFE y montaje real |
| Nginx dirige al hostname interno no permitido por Vite | Conservar Host del navegador | Playwright sobre shell real |
| Nginx conserva dirección vieja después de recrear API | DNS Docker con resolución periódica para API | Reinicios y comprobación del flujo HTTP |
| Montaje MFE impedía resolver `file:../design-software-design-system` | Montar repositorios hermanos en `/workspace` | Federation real y build MFE |
| Credencial RabbitMQ del entorno no coincide con definitions oficiales | Rotar usuario app solo en proyecto aislado y conservar secreto en `.env` ignorado | Readiness y prueba de negocio sobre broker real |
| Detalle de seguimiento permite OWN pero rechaza FULL | Permitir ambas capacidades de consulta existentes | Flujo real de plan/resolución y consulta posterior |
| Harness imprime Unicode con codificación Windows incompatible | Configurar stdout/stderr UTF-8 | Registros de builds y pruebas posteriores |
| Selector de conflicto HTTP 409 coincide con dos mensajes legítimos | Acotar la aserción al diálogo | Prueba de navegador con conflicto real y rollback |
| Explore no accesible para visitante Viewer | Rol Editor limitado al Grafana local enlazado a 127.0.0.1; dashboards provisionados | Verificación de datasource, dashboard y acceso a Tempo |

Las advertencias de SQLAlchemy sobre defaults del servidor y la deprecación del TestClient se conservan en las salidas; no se ocultaron ni se declararon errores de prueba. Las bases PostgreSQL reales aplicaron los defaults y las pruebas de persistencia pasaron. Las métricas históricas contienen errores de arranque y de pruebas anteriores: no se borraron para presentar gráficos artificialmente limpios.

Las capturas conservan el estado observado. La vista anónima de alertas pudo mostrar un aviso Unauthorized para una acción auxiliar mientras sí cargaba las reglas; los estados utilizados como prueba se verifican independientemente mediante las API de Prometheus y Grafana y el panel ALERTS.

Al retomar la sesi?n se observaron timeouts transitorios de conexi?n AMQP alrededor de las 17:13 (America/Bogota). Se conservaron como errores hist?ricos; despu?s, readiness y el flujo de negocio real pasaron. VERIFY registra el historial, exige readiness y ausencia de errores nuevos en una ventana expl?cita de cinco minutos. No se borraron logs ni se desactiv? la validaci?n.

GitHub Actions detect? que el checkout independiente no conten?a el repositorio hermano privado design-software-docs. La prueba ahora conserva la validaci?n completa y usa, cuando falta ese repositorio, el contrato oficial sin modificar fijado al commit e1d9b06a8710f97b7f5361b46af98a6ba257ca39. tests/contracts/monitoring.source.json registra origen y SHA-256; .gitattributes conserva LF para verificar los mismos bytes en Windows y Linux. No se omite la prueba ni se requiere un token adicional.


CI remoto aprobado en el commit 6aa50a4: [Actions 39335723068](https://github.com/code-sena/design-software-monitoring-service/actions/runs/39335723068). La suite de CI omite las cuatro pruebas que requieren PostgreSQL; estas si se ejecutaron y aprobaron en la suite local de 26 pruebas. Evidencia: `08-pruebas/github-ci-success.json`.


## Integracion adicional con servicios reales

- IAM emite tokens de usuario sin aud: el perfil explicito usa JWKS y admite ese contrato, conservando firma, emisor, exp y sub. El perfil R3 previo sigue requiriendo aud=monitoring.
- Reference Data expone las rutas sin /api/v1 y permite JWKS HTTP solo en loopback: el perfil usa su ruta real y comparte namespace local con IAM, sin desactivar esa validacion.
- Academic guardaba outbox sin relay activo: corregido en PR #17, con regresion de contexto y evento real consumido por Monitoring.
- Nginx conservaba la direccion anterior del shell despues de recrearlo: resolucion DNS dinamica tanto para API como shell; nginx -t aprobado.
- El selector del harness buscaba el texto exacto Ficha aunque el label incluia opciones: corregido para usar el combobox accesible. La aplicacion ya mostraba las fichas reales.
- Los intentos iniciales del navegador y de Maven se conservan como fallidos. El flujo posterior aprobado esta en main-flow-browser.json y main-flow-ipv4.*; la regresion de Academic aprobada esta en academic-relay-context-build.*.
