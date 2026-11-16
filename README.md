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

Ejemplos:
```json
{"nombre":"Base de datos"}
{"nombre":"Servidor","descripcion":"Tres bandejas apiladas con indicadores frontales"}
```

## Validación
```bash
pip install -r requirements.txt
python -m unittest discover -s tests -v
python scripts/validate_asset.py assets/*.svg
```

SVG con variables CSS: el validador resuelve las variables solamente en una copia temporal para comprobar la geometría renderizada. El archivo fuente sigue editable.

## Estructura
`assets/` → originales SVG; `skills/` → procedimiento reutilizable; `scripts/` → validación; `tests/` → pruebas; `.github/workflows/` → CI.
