# Requisitos No Funcionales (NFR)

> Estado: 🟡 Borrador | Última actualización: 2026-08-28
> Fuente: [problem-framing.md](../03-product/problem-framing.md) · [overview.md](../05-architecture/overview.md)
> Cada NFR es verificable y tiene una métrica objetivo.

> **Evidencia en `dev`.** Varios NFR ya están **ejercidos y verificados en el ambiente `dev`** por los servicios construidos (`iam-service`, `notification-service`). Se marcan abajo con **✅ Evidencia dev** y la observación concreta. El resto siguen como objetivo de diseño. Los ambientes `qa`/`staging`/`main` aún no tienen estos servicios promovidos.

## 1. Rendimiento

| ID | Requisito | Métrica objetivo | Cómo se verifica |
|----|-----------|------------------|------------------|
| NFR-PERF-01 | Consulta de ambientes disponibles | < 300 ms (p95) | Prueba de carga sobre `GET /environments/available` |
| NFR-PERF-02 | Consulta de instructores disponibles | < 300 ms (p95) | Prueba de carga sobre `GET /instructors/available` |
| NFR-PERF-03 | Validación de horario completo (20 sesiones) | < 2 s | Prueba con horario de tamaño real |
| NFR-PERF-04 | Consulta de horario por instructor/semana | < 500 ms (p95) | Prueba de carga |
| NFR-PERF-05 | Lectura de catálogos (cacheada) | < 50 ms | Prueba contra Redis |
| NFR-PERF-06 | Publicación de evento al broker | < 100 ms | Métrica del publisher; no bloquea respuesta HTTP |

## 2. Disponibilidad

| ID | Requisito | Métrica objetivo | Ventana |
|----|-----------|------------------|---------|
| NFR-AVAIL-01 | Disponibilidad de iam-service | 99.9 % | 24/7 |
| NFR-AVAIL-02 | Disponibilidad de scheduling-service | 99.5 % | 06:00–22:00 (hora Colombia) |
| NFR-AVAIL-03 | Disponibilidad del resto de servicios | 99 % | Horas laborales |
| NFR-AVAIL-04 | Degradación parcial tolerada | scheduling opera aunque actors/environment estén caídos | Vía read models (ADR-002) |

## 3. Escalabilidad

| ID | Requisito | Métrica objetivo |
|----|-----------|------------------|
| NFR-SCALE-01 | Fichas activas concurrentes por centro | Soportar 100+ sin degradación |
| NFR-SCALE-02 | Usuarios concurrentes por centro | 200+ (coordinadores, instructores, aprendices) |
| NFR-SCALE-03 | Escalado horizontal | Cada servicio escala por réplicas sin estado compartido (JWT stateless) |
| NFR-SCALE-04 | Crecimiento a nivel nacional | Arquitectura soporta múltiples centros sin rediseño |

## 4. Seguridad

| ID | Requisito | Verificación |
|----|-----------|--------------|
| NFR-SEC-01 | Autenticación en todos los endpoints (excepto login y reset) | Revisión de contratos; pruebas de acceso sin token → 401 · **✅ Evidencia dev**: `iam` responde 401 a peticiones sin token |
| NFR-SEC-02 | Autorización por feature + scope | Pruebas de acceso cruzado entre centros → 403 SCOPE_VIOLATION · **✅ Evidencia dev**: `iam` deniega por scope/centro (403) |
| NFR-SEC-03 | Cifrado en tránsito | TLS 1.2+ en todos los canales |
| NFR-SEC-04 | Cifrado en reposo de PII y credenciales | AES-256 a nivel de BD |
| NFR-SEC-05 | Sin PII en logs | Auditoría de logs; solo IDs |
| NFR-SEC-06 | Cumplimiento Ley 1581/2012 (Habeas Data) | Ver [security-threat-model.md](../05-architecture/security-threat-model.md) |
| NFR-SEC-07 | Protección contra fuerza bruta | Bloqueo de cuenta + rate limiting · **✅ Evidencia dev**: lockout 5/10 intentos verificado en `iam` |
| NFR-SEC-08 | JWT verificable localmente y rotación de llaves | Clave pública publicada vía JWKS (`/.well-known/jwks.json`); rotación de llaves de firma (DEC-008) · **✅ Evidencia dev**: JWKS servido y rotación operativa en `iam` |

## 5. Mantenibilidad

| ID | Requisito | Métrica objetivo |
|----|-----------|------------------|
| NFR-MAINT-01 | Cobertura de pruebas en servicios CORE | ≥ 80 % (scheduling, monitoring) |
| NFR-MAINT-02 | Cobertura de pruebas en servicios SUPPORTING/GENERIC | ≥ 60 % |
| NFR-MAINT-03 | Separación de capas (hexagonal) | Dominio sin imports de infraestructura (checklist de PR) · **✅ Evidencia dev**: `iam` con **162 tests** verdes en CI |
| NFR-MAINT-04 | Documentación de cada servicio | README + data-model + contract + decisions |
| NFR-MAINT-05 | Naming técnico en inglés | HALT-DB-NAMING; sin términos de dominio en español en código/contratos |

## 6. Observabilidad

| ID | Requisito | Verificación |
|----|-----------|--------------|
| NFR-OBS-01 | Correlation ID en cada request | `X-Request-ID` propagado entre servicios |
| NFR-OBS-02 | Logs estructurados JSON | Campos: timestamp, level, service, request_id, event |
| NFR-OBS-03 | Métricas RED por endpoint | Rate, Errors, Duration |
| NFR-OBS-04 | Trazas distribuidas | OpenTelemetry → Jaeger/Tempo · **✅ Evidencia dev**: trazas de `iam` visibles en Tempo |
| NFR-OBS-05 | Auditoría de acciones de negocio | audit-service consume todos los eventos |
| NFR-OBS-06 | Exportación OTLP por stack | Cada stack exporta a su colector según su runtime: **Java** (`iam`) por **OTLP/HTTP en `:4318`** (`http/protobuf`); **Go** (`notification`) por **OTLP/gRPC en `:4317`**; **Python** (`monitoring`) por **OTLP/HTTP en `:4318`** (el exportador que se importa decide el protocolo; ver [local-setup](../10-devops/local-setup.md#gotchas-de-observabilidad--deploy)) · **✅ Evidencia dev** |
| NFR-OBS-07 | Sondas de salud diferenciadas | Split **`/health`** (liveness) vs **`/ready`** (readiness con dependencias: BD + broker); un servicio no queda `ready` hasta que sus dependencias respondan · **✅ Evidencia dev** en `iam` |

## 7. Usabilidad

| ID | Requisito | Métrica objetivo |
|----|-----------|------------------|
| NFR-USA-01 | Tiempo de creación de horario semanal | < 1 h (vs. 4–8 h manual actual) |
| NFR-USA-02 | Web responsive (desktop-first, móvil para consulta) | Funciona en pantallas ≥ 360 px |
| NFR-USA-03 | Accesibilidad | WCAG 2.1 nivel AA (objetivo) |
| NFR-USA-04 | Idioma de la interfaz | Español (audiencia SENA) |

## 8. Portabilidad / Despliegue

| ID | Requisito | Métrica objetivo |
|----|-----------|------------------|
| NFR-PORT-01 | Ambientes consistentes | DEV → QA → PROD con misma imagen (object storage compatible S3, ADR-003) |
| NFR-PORT-02 | Despliegue independiente por servicio | Cada servicio se despliega sin coordinar con otros |
| NFR-PORT-03 | Configuración por variables de entorno | Sin valores hardcodeados; secrets en Secret Manager |

## 9. Recuperación ante fallos

| ID | Requisito | Métrica objetivo |
|----|-----------|------------------|
| NFR-REC-01 | RPO (Recovery Point Objective) | ≤ 1 h (backups incrementales) |
| NFR-REC-02 | RTO (Recovery Time Objective) | ≤ 4 h por servicio |
| NFR-REC-03 | Entrega de eventos garantizada | At-least-once + DLQ + Outbox (scheduling) · **✅ Evidencia dev**: outbox en `iam` (→ `iam-events`); DLQ + idempotencia por `event_id` probados en `notification` |
| NFR-REC-04 | Inmutabilidad de auditoría | audit_record solo INSERT; retención 7 años |

---

## Trazabilidad NFR → Arquitectura

| NFR | Decisión arquitectónica que lo soporta |
|-----|----------------------------------------|
| NFR-PERF-01/02 | Read models locales en scheduling (ADR-002) + índices optimizados |
| NFR-AVAIL-04 | Read models desacoplan scheduling de actors/environment (ADR-002) |
| NFR-SCALE-03 / NFR-SEC-08 | JWT stateless verificable localmente + JWKS y rotación de llaves (DEC-008) |
| NFR-SEC-02 | RBAC por feature+scope (rbac-design.md) |
| NFR-REC-03 | Broker con DLQ (ADR-001) + Outbox pattern |
| NFR-PORT-01 | Adaptador de storage compatible S3 (ADR-003) |
