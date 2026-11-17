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

## Inicialización verificable antes de auditar

La skill utiliza [VISUAL_STYLE.md](skills/cybersecurity-premium-assets/VISUAL_STYLE.md) para la identidad gráfica. Los originales aprobados sirven para la auditoría técnica, no para copiar la geometría de otros iconos.

**Nuevo punto de entrada:** [bootstrap_audit.py](scripts/bootstrap_audit.py). Obtiene y verifica un único [audit_runtime_bundle.json](scripts/audit_runtime_bundle.json) que incluye los scripts oficiales, el índice de los maestros y los 17 SVG exactos empaquetados. No requiere descargar cada maestro por separado.

```bash
python scripts/bootstrap_audit.py --repo-root . --manifest work/manifest.json --execute
```

**Si el Python está aislado de GitHub (DNS/red bloqueada):** recuperar los dos archivos anteriores con el conector de GitHub, transferirlos efectivamente al sistema de archivos local (no basta con verlos en la respuesta del conector) y ejecutar:

```bash
python scripts/bootstrap_audit.py --repo-root . --bundle /ruta/local/audit_runtime_bundle.json --offline --manifest work/manifest.json --execute
```

El bootstrap verifica los Git blobs del bundle, la correspondencia completa de los hashes de maestros, la procedencia del validador, las dependencias instaladas, el manifiesto y el hash del SVG candidato/anterior, y ejecuta `validate_asset.py`, `audit_workflow.py` y `approval_gate.py`. **No inventa evidencia de inspección y nunca publica assets.** La ausencia de un puente entre el conector y Python se informa como bloqueo explícito; no se simula una auditoría.

Para mantener actualizado el paquete después de modificar scripts oficiales o publicar otro SVG aprobado (solo tras aprobación explícita):

```bash
python scripts/build_master_pack.py --write
python scripts/build_audit_runtime_bundle.py --write
python scripts/build_master_pack.py --check
python scripts/build_audit_runtime_bundle.py --check
python -m unittest discover -s tests -v
```

Con una validación de contenidos satisfactoria, los 17 maestros permanecen inalterados. Un paquete desactualizado se rechaza y no habilita el formulario de aprobación.

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
