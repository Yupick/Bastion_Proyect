# Guía de Despliegue, Rollback y Soporte - Qrypta

## Resumen

Este documento describe el proceso de despliegue a staging/producción, procedimientos de rollback y guía de soporte para el servidor Qrypta.

---

## 1. Despliegue a Staging

### Prerrequisitos
- Docker 24+ y Docker Compose 2+
- Acceso a GHCR (para imágenes publicadas) o capacidad de build local
- Servidor con puertos 8000 (HTTP) y 5432 (PostgreSQL) disponibles
- Dominio/subdominio configurado para staging

### Pasos de Despliegue

```bash
# 1. Preparar repositorio
git clone https://github.com/Yupick/Bastion_Proyect.git
cd Bastion_Proyect
git checkout main  # o tag de release vX.Y.Z

# 2. Configurar entorno staging
cd qrypta/servidor
cp .env.example .env.staging
# EDITAR .env.staging con valores seguros (ver sección Variables)

# 3. Desplegar
docker-compose -f docker-compose.staging.yml up -d --build

# 4. Verificar
docker-compose -f docker-compose.staging.yml ps
curl -f http://localhost:8000/health
curl -f http://localhost:8000/metrics
```

### Variables de Entorno Críticas (.env.staging)

| Variable | Requerida | Descripción |
|----------|-----------|-------------|
| `ADMIN_TOKEN` | **Sí** | Token seguro 32+ chars para dashboard admin |
| `POSTGRES_PASSWORD` | **Sí** | Password BD seguro |
| `MODO_DEBUG` | **Sí** | **false** en staging/prod |
| `CORS_ORIGINS` | **Sí** | Dominio staging (ej. `https://staging.qrypta.app`) |
| `RATE_LIMIT` | No | Ajustar según carga esperada |

---

## 2. Despliegue a Producción (GitHub Release Flow)

El despliegue a producción es **automatizado** via GitHub Actions:

```bash
# 1. Merge develop -> main (via PR)
# 2. Crear y pushear tag semver
git tag v1.0.0-beta.1
git push origin v1.0.0-beta.1

# 3. release.yml dispara automáticamente:
#    - Validación de tag semver
#    - Build Docker image -> GHCR
#    - GitHub Release con notas + info Docker
```

### Flujo Release.yml
```
push tag v* -> validate-tag -> build-docker-image (GHCR) -> publish-release (GitHub Release)
                                    \-> semver tags: latest, vX.Y.Z, vX.Y, vX, sha-<commit>
```

### Imagen Docker Publicada
```bash
# Pull manual si necesario
docker pull ghcr.io/yupick/bastion-proyect-servidor:v1.0.0-beta.1
# O latest
docker pull ghcr.io/yupick/bastion-proyect-servidor:latest
```

---

## 3. Rollback

### Rollback Rápido (Imagen Anterior)
```bash
# 1. Detener versión actual
docker-compose -f docker-compose.staging.yml down

# 2. Usar tag anterior
# Opción A: Imagen GHCR previa
docker pull ghcr.io/yupick/bastion-proyect-servidor:v1.0.0-beta.0
# Actualizar docker-compose.staging.yml para usar image: en lugar de build:
#   image: ghcr.io/yupick/bastion-proyect-servidor:v1.0.0-beta.0

# Opción B: Checkout tag anterior y rebuild
git checkout v1.0.0-beta.0
docker-compose -f docker-compose.staging.yml up -d --build

# 3. Verificar
curl -f http://localhost:8000/health
```

### Rollback de Base de Datos
```bash
# Backup antes de migraciones riesgosas
docker exec qrypta-postgres pg_dump -U qrypta qrypta_mensajes > backup_$(date +%F).sql

# Restaurar si necesario
docker exec -i qrypta-postgres psql -U qrypta qrypta_mensajes < backup_2026-01-15.sql
```

### Rollback de Configuración
```bash
# Restaurar .env.staging previo
git checkout HEAD~1 -- qrypta/servidor/.env.staging
docker-compose -f docker-compose.staging.yml up -d --force-recreate
```

---

## 4. Monitoreo y Logs

### Endpoints de Salud
```bash
# Health check básico
curl http://localhost:8000/health

# Métricas Prometheus
curl http://localhost:8000/metrics

# Auditoría (requiere ADMIN_TOKEN)
curl -H "Authorization: Bearer $ADMIN_TOKEN" http://localhost:8000/admin/audit
```

### Logs Estructurados
```bash
# Logs contenedor (JSON)
docker-compose -f docker-compose.staging.yml logs -f servidor | jq .

# Logs archivo (si configurado)
tail -f qrypta/servidor/logs/uvicorn.log

# Filtrar errores
docker-compose -f docker-compose.staging.yml logs servidor | grep -i error
```

### Alertas Básicas
- Healthcheck falla 3 veces -> Reinicio automático (Docker)
- Uso memoria > 80% -> Alerta
- Latencia p95 > 500ms -> Alerta
- Rate limit excedido -> Revisar logs auditoría

---

## 5. Soporte y Troubleshooting

### Problemas Comunes

| Síntoma | Causa Probable | Solución |
|---------|----------------|----------|
| Healthcheck fails | Puerto 8000 ocupado / BD no lista | Verificar `docker-compose ps`, esperar BD healthy |
| CORS error | `CORS_ORIGINS` incorrecto | Verificar dominio exacto en .env.staging |
| Rate limit 429 | Tráfico legítimo o ataque | Ajustar `RATE_LIMIT`, revisar logs auditoría |
| DB connection refused | Postgres no healthy | `docker-compose logs postgres`, verificar healthcheck |
| Imagen no pull | GHCR privado / token expirado | `docker login ghcr.io` con PAT válido |

### Comandos Útiles
```bash
# Reinicio limpio
docker-compose -f docker-compose.staging.yml down -v
docker-compose -f docker-compose.staging.yml up -d --build

# Ver configuración efectiva
docker-compose -f docker-compose.staging.yml config

# Acceso shell contenedor
docker-compose -f docker-compose.staging.yml exec servidor bash

# Backup BD manual
docker-compose -f docker-compose.staging.yml exec postgres pg_dump -U qrypta qrypta_mensajes > backup.sql
```

---

## 6. Contacto y Escalación

| Nivel | Contacto | SLA |
|-------|----------|-----|
| L1 - Operaciones | Equipo DevOps | 1h |
| L2 - Desarrollo | @core-team | 4h |
| L3 - Seguridad | @security-team | Inmediato |

### Reporte de Incidentes
1. Capturar: timestamp, endpoint, error, logs relevantes
2. Clasificar severidad (P1-P4)
3. Asignar owner
4. Documentar en GitHub Issues con label `incident`

---

## 7. Checklist de Release

### Pre-Release (develop -> main)
- [ ] CI verde en develop (todos workflows)
- [ ] `beta_clients_ready.sh` PASS
- [ ] Staging desplegado y validado
- [ ] CHANGELOG actualizado
- [ ] Version bump en código si aplica

### Release (tag v*)
- [ ] Tag semver válido (vX.Y.Z[-rc.N])
- [ ] release.yml pasa completo
- [ ] Imagen en GHCR verificada
- [ ] GitHub Release creado con notas
- [ ] Staging actualizado a nueva versión

### Post-Release
- [ ] Smoke tests en staging
- [ ] Monitoreo 24h sin alertas P1
- [ ] Documentación actualizada
- [ ] Comunicación a testers (si beta)