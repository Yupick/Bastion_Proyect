# Guía de Estilo de Programación - Qrypta

## Principios generales
- Código modular y auditable.
- Comentarios en español, explicando la lógica de cada módulo.
- Funciones cortas (máx. 30 líneas).
- Preferir reutilización antes que duplicación.
- Toda función crítica debe tener pruebas unitarias.

## Nomenclatura
- Variables: camelCase (ej. `clavePrivadaKyber`).
- Clases y módulos: PascalCase (ej. `GestorAlias`).
- Constantes: MAYÚSCULAS_CON_GUIONES (ej. `MAX_INTENTOS`).
- Archivos: snake_case (ej. `registro_verificacion.py`).

## Seguridad
- Nunca exponer claves privadas en logs.
- Usar librerías de cifrado auditadas.
- Validar entradas de usuario siempre.

## Documentación
- Cada módulo debe incluir un encabezado con:
  - Propósito
  - Autor
  - Fecha
  - Ejemplo de uso

## Versionado con Gitflow
- Rama principal: `main` (solo versiones estables).
- Rama de desarrollo: `develop`.
- Nuevas funcionalidades: `feature/nombre-funcionalidad`.
- Correcciones: `hotfix/nombre-correccion`.
- Versiones de lanzamiento: `release/x.y.z`.

### Ejemplo de flujo
1. Crear rama `feature/registro-inicial` desde `develop`.
2. Desarrollar y hacer commits siguiendo las reglas de estilo.
3. Merge a `develop` mediante Pull Request.
4. Cuando se acumulan varias features, crear `release/1.0.0`.
5. Testear y mergear a `main`.
6. Si hay errores críticos en producción, crear `hotfix/1.0.1`.

## Commits
- Mensajes en español, claros y concisos.
- Formato: `[tipo]: descripción`
  - `feat: agregar verificación de alias`
  - `fix: corregir bug en exportación de backup`
  - `docs: actualizar README`
