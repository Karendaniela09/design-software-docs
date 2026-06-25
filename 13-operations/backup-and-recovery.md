# Backup y recuperación

> Estado: 🟢 Estable | Última actualización: 2026-06-24
> Autor: Equipo ADSO 3145555 | Equipo: DevOps / Arquitectura

## Contexto

Este documento define la estrategia de backup y recuperación del sistema **Horarios SENA**. Se establecen los objetivos de recuperación (RPO y RTO), la frecuencia de backups y los procedimientos para restaurar el sistema en caso de fallo.

## Objetivos de recuperación

| Métrica | Valor | Descripción |
|---------|-------|-------------|
| **RPO** (Recovery Point Objective) | 24 horas | Pérdida máxima de datos aceptable (1 día). |
| **RTO** (Recovery Time Objective) | 4 horas | Tiempo máximo para restaurar el sistema. |

---

## Estrategia de backup

### Base de datos (PostgreSQL)

| Aspecto | Descripción |
|---------|-------------|
| **Frecuencia** | Diaria (backup completo). |
| **Herramienta** | `pg_dump` (formato personalizado). |
| **Almacenamiento** | Archivos comprimidos en almacenamiento separado (S3 / NFS). |
| **Retención** | 30 días (diarios), 90 días (semanales). |

**Comando de backup:**

```bash
#!/bin/bash
BACKUP_DIR="/backups/postgres"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="horarios_db"
DB_USER="horarios_user"

pg_dump -U $DB_USER -Fc -b -v -f "$BACKUP_DIR/${DB_NAME}_${DATE}.dump" $DB_NAME

# Comprimir y guardar en S3 (opcional)
gzip "$BACKUP_DIR/${DB_NAME}_${DATE}.dump"
aws s3 cp "$BACKUP_DIR/${DB_NAME}_${DATE}.dump.gz" s3://my-bucket/backups/