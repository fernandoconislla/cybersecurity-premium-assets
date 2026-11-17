# Cybersecurity Premium Assets

Biblioteca de SVG premium para cursos de ciberseguridad.

**Asset maestro aprobado:** [Escudo con candado](assets/escudo-candado.svg). No modificar sin aprobación expresa.

## Contrato
- Parámetros: `nombre` obligatorio y `descripcion` opcional.
- Salida: SVG real editable, lienzo cuadrado 1024×1024, fondo transparente.
- Tres tokens cromáticos, exclusivamente: `--PRIMARY: #092B60`, `--SECONDARY: #38BDF8`, `--CONTRAST: #FFFFFF`. La paleta es parametrizable; las formas solo usan tokens.
- Sin degradados, cuarto color, sombras, semitransparencias, imágenes rasterizadas, filtros o texturas.
- Blanco solo en elementos internos. Exterior contrastante sobre blanco.
- Dimensión dominante visible ≈922 unidades (90 % ±2 %), centrado en ambos ejes, sin distorsión.
- Misma identidad geométrica y densidad visual que el asset maestro; no añadir escudos a temas que no lo requieran.
- Validar geometría, paleta y legibilidad a 64/128 px, y comparar cada propuesta con el maestro.
- No aprobar sin visto bueno del usuario.

## Uso
La skill está en [skills/cybersecurity-premium-assets/SKILL.md](skills/cybersecurity-premium-assets/SKILL.md).

**Guía visual general oficial:** [VISUAL_STYLE.md](skills/cybersecurity-premium-assets/VISUAL_STYLE.md). Para generar nuevos iconos, esta es la referencia interna de estilo; los SVG ya aprobados se consultan solamente para reutilización/revisión exacta y comprobaciones técnicas de integridad, no como plantillas visuales.

Ejemplos:
```json
{"nombre":"Base de datos"}
{"nombre":"Servidor","descripcion":"Tres bandejas apiladas con indicadores frontales"}
```

## Auditoría reproducible sin descargar 17 SVG uno por uno

Para diseñar, consultar **solo** [VISUAL_STYLE.md](skills/cybersecurity-premium-assets/VISUAL_STYLE.md), no los SVG maestros.

Para la **auditoría técnica oficial** se requieren los hashes de todos los maestros, pero ahora basta con llevar un único archivo [approved_masters_pack.json](scripts/approved_masters_pack.json) junto al [índice](scripts/approved_masters.json), el auditor oficial y [master_cache.py](scripts/master_cache.py). `audit_workflow.py` recupera bajo el directorio de salida los SVG faltantes, verifica **cada Git blob** contra el índice y genera la hoja comparativa real. Si el paquete está corrupto o desactualizado, el flujo falla; no se omite ningún control.

```bash
python scripts/validate_asset.py work/candidate.svg
python scripts/audit_workflow.py --repo-root . --manifest work/manifest.json
python scripts/approval_gate.py --repo-root . --manifest work/manifest.json --report work/audit/audit-report.json
```

Cuando se publique un asset aprobado, actualizar **ambos** `scripts/approved_masters.json` y `scripts/approved_masters_pack.json` con los bytes exactos del SVG. En un checkout completo, generar y verificar el paquete mediante:

```bash
python scripts/build_master_pack.py --write
python scripts/build_master_pack.py --check
python -m unittest discover -s tests -v
```

**Nota:** el paquete es un medio de transporte para QA, no una plantilla gráfica ni una autorización para publicar.

## Puerta de aprobación obligatoria

Una auditoría técnica correcta **no** habilita por sí sola la solicitud de aprobación. Antes de presentar cualquier nuevo candidato se exige evidencia explícita de investigación e inspección humana, ejecución de los dos scripts oficiales, hashes válidos de todos los maestros del índice, el SVG y sus previsualizaciones, y el recibo `APPROVAL GATE PASS`.

```bash
python scripts/validate_asset.py work/candidate.svg
python scripts/audit_workflow.py --repo-root . --manifest work/manifest.json
python scripts/approval_gate.py --repo-root . --manifest work/manifest.json --report work/audit/audit-report.json
```

El archivo `approval-authorization.json` autoriza **solo la presentación para aprobación del usuario**, nunca la publicación. El manifiesto requiere `manual_evidence` con cuatro verificaciones reales (referencias, previsualizaciones, comparación de familia y defectos críticos). Si faltan pruebas, el proceso se bloquea; no se pueden inventar hallazgos para completarlas.

## Validación
```bash
pip install -r requirements.txt
python -m unittest discover -s tests -v
python scripts/validate_asset.py assets/*.svg
```

SVG con variables CSS: el validador resuelve las variables solamente en una copia temporal para comprobar la geometría renderizada. El archivo fuente sigue editable.

## Estructura
`assets/` → originales SVG; `skills/` → procedimiento reutilizable; `scripts/` → validación; `tests/` → pruebas; `.github/workflows/` → CI.
