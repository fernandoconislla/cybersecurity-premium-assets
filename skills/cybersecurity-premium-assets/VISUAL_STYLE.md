# Guía visual maestra — Cybersecurity Premium Assets

**Estado:** referencia oficial del **estilo visual** de la familia. **Base de observación:** 17 SVG aprobados en el catálogo de GitHub al 17-11-2026. **Alcance:** síntesis general de lo que comparten; no es una plantilla de un asset concreto ni un inventario de sus siluetas.

## 1. Identidad visual

Iconografía tecnológica y de ciberseguridad **premium, minimalista, sólida, reconocible y didáctica**. Cada icono debe comunicar una idea principal casi de inmediato, sin necesitar un rótulo. Es un **símbolo vectorial plano y rotundo**, no una ilustración narrativa, foto, clipart, emoji, pictograma lineal frágil ni un conjunto de objetos decorativos.

**Fórmula de familia:** una silueta semánticamente precisa + un contorno marino bien definido + superficies cian + separaciones blancas interiores discretas + pocos detalles útiles. El peso gráfico debe sentirse consistente entre iconos muy distintos sin copiar la geometría de ninguno.

## 2. Lenguaje cromático (regla rígida)

Los **únicos tres colores sólidos** son:
- `PRIMARY #092B60`: contorno exterior, estructura, divisiones funcionales, siluetas secundarias y énfasis.
- `SECONDARY #38BDF8`: superficies principales y zonas que requieren lectura clara.
- `CONTRAST #FFFFFF`: filetes, huecos y separaciones **internos**, delimitados por superficies más oscuras.

Definir exactamente `--PRIMARY`, `--SECONDARY`, `--CONTRAST` y las clases SVG `.primary`, `.secondary`, `.contrast`. Las formas pintadas solo usan estas clases. Fondo **transparente**; el blanco de la captura o vista previa no forma parte del SVG. No cuarto color, tonos alternativos, gradiente, sombra, brillo, textura, opacidad ni filtros.

**Distribución no mecánica:** muchos iconos tienen cara cian uniforme, un borde marino y un filete blanco. Otros muestran componentes azul marino por función o superficies partidas cuando **la geometría o la semántica** lo justifica (por ejemplo, distinguir caras o piezas). **No dividir verticalmente una figura solo por reproducir la paleta.** El blanco no debe formar un perímetro externo invisible sobre una página blanca.

## 3. Geometría, curvas y contornos

- Contornos exteriores **visibles, continuos, compactos, limpios y relativamente gruesos**, sin volverse pesados ni competir con el centro del icono. El espesor se elige en relación con el tamaño de la figura; **no existe un grosor universal obligatorio** para todos los objetos.
- Filete blanco interior **más contenido** que el contorno marino. Equilibrar las bandas blancas por distancia visual, incluidas diagonales y curvas. Evitar que se ensanchen accidentalmente en vértices, parte superior, laterales o parte inferior.
- Curvas Bézier fluidas, uniones y tangentes bien resueltas; terminaciones redondeadas o aristas precisas **según el objeto**. No redondear indiscriminadamente todo.
- Uso deliberado del espacio negativo. Simetría exacta cuando corresponde, pero **no forzar** simetría en formas naturalmente orientadas, diagonales o con perspectiva.
- Formas sólidas separadas y editables, agrupadas con identificadores descriptivos. Nada de piezas flotantes, solapes accidentales, anatomía antinatural, cortes desconectados ni filetes que terminan prematuramente.
- Representar volumen solo con **dos o tres planos vectoriales legibles** cuando mejora la comprensión del objeto (por ejemplo, dispositivos o cajas); no usar perspectiva compleja, sombreados ni degradados.

## 4. Composición y escala

- Lienzo exacto `1024 × 1024`, `viewBox="0 0 1024 1024"`, relación 1:1.
- **Dimensión visible dominante ≈ 922 unidades (90 % ±2 %)**; la menor conserva la proporción natural. Centro geométrico en ambos ejes; aplicar pequeños ajustes ópticos únicamente cuando estén justificados.
- Un protagonista visual, centro de atención inmediato, proporciones equilibradas y margen de seguridad. El concepto se reconoce primero por la **silueta global**, después por el detalle central.
- No imponer marcos, círculos, escudos, badges, etiquetas, papeles, pantallas, cadenas, candados, chips ni estrellas a un concepto que no los requiere.
- Los detalles complementarios se integran **en el cuerpo del protagonista** y son pocos, claros y útiles; evitar que se conviertan en un segundo protagonista. Una figura más grande o una marca distintiva se usa solo si el significado la exige.

## 5. Densidad de detalle y legibilidad

El diseño debe conservar su significado a **1024, 128 y 64 px** sobre blanco:
- A 64 px, deben sobrevivir los contornos, los vacíos esenciales y el gesto o rasgo distintivo.
- Priorizar elementos amplios, pocas ventanas o controles, contactos simplificados, símbolos nítidos y separaciones suficientemente grandes.
- No optimizar solo para la vista grande: eliminar microdetalles que colapsan en manchas a 64 px.
- Evitar letras pequeñas; cuando un término es indispensable, usar trazados vectoriales breves y auditarlos a tamaño reducido.
- Jerarquía de capas clara: exterior marino → interior o campo principal → detalle funcional mínimo.

## 6. Semántica antes que decoración

Diferenciar con precisión conceptos que se parecen: equipo vs organización, usuario genérico vs autenticado, router lógico vs equipo Wi-Fi, switch vs router, amenaza digital vs insecto genérico, proveedor tecnológico vs caja común. El emblema añadido **cambia el significado**; solo incluirlo si el nombre, la descripción o la referencia expresamente suministrada lo ameritan.

**La referencia visual aportada por el usuario tiene precedencia en composición y silueta**, siempre dentro de las reglas duras de formato, paleta y seguridad. Interpretar la referencia con geometría vectorial original y editable; no copiar trazados protegidos ni limitarse a incrustar una imagen.

## 7. Cómo decidir el tratamiento de color

Antes de dibujar, responder internamente:
1. ¿Qué silueta reconocerá alguien a 64 px?
2. ¿Cuál es el objeto principal y cuáles son, como máximo, los detalles semánticos indispensables?
3. ¿El cuerpo debe ser cian uniforme, marino uniforme o estar diferenciado en varias piezas?
4. ¿Una división de color explica **volumen, función o componentes**, o es puramente ornamental?
5. ¿Los contornos y filetes mantienen espesor visual coherente en rectas, diagonales y curvas?
6. ¿El icono se siente parte de la misma familia sin repetir la silueta de otro?

**Respuesta predeterminada:** campo cian uniforme, contorno marino, separador blanco interno discreto, énfasis marino solamente donde aporte información.

## 8. Lista visual de aceptación

Inspeccionar siempre el SVG real y sus renders a 1024/128/64, cubriendo al menos: reconocimiento, refinamiento de curvas, composición, geometría, equilibrio óptico, coherencia con **esta guía**, roles cromáticos, lectura pequeña, fidelidad a la referencia del usuario/fuente, y balance relativo cian/marino/blanco.

Se rechaza si aparece cualquiera de estos defectos: concepto ambiguo evitable, contornos de espesor errático, bandas blancas desiguales, descentrado, objetos flotantes, detalles que desaparecen a 64 px, contraste insuficiente, doble protagonista no pedido o adornos técnicos innecesarios.

**La conformidad estética no reemplaza los scripts de auditoría oficiales.**

## 9. Política de consulta — fuente de verdad y excepciones

**Diseñar / revisar estilo de un asset NUEVO:** leer **este archivo** como **única referencia interna de estilo de la familia**. No abrir ni inspeccionar los 17 SVG aprobados para “averiguar cómo debe verse”; investigar aparte las referencias **semánticas externas** y usar la imagen del usuario cuando exista. Evaluar la coherencia por las reglas aquí documentadas.

**Revisar un asset EXISTENTE:** recuperar los **bytes exactos del SVG objetivo**, su hash y la versión previa cuando corresponda. La guía describe la familia; **no sustituye el asset que se está editando**.

**Auditar / publicar:** los 17 masters continúan siendo **originales inmutables**. Los scripts oficiales actuales pueden exigir sus bytes/hashes y la hoja comparativa para integridad y trazabilidad. Ese acceso es **verificación técnica**, **no investigación de estilo** y **no autoriza copiar su geometría**. No omitir ni falsear un control porque la guía ya exista.

**Después de publicar:** actualizar el catálogo/hash como siempre. Modificar esta guía **solo si una aprobación introduce una regla visual general nueva**; no agregar una descripción de cada icono aprobado ni reescribirla en cada generación.

**Prioridad normativa:** instrucciones explícitas del usuario y sus imágenes de referencia (composición) + reglas técnicas duras > esta guía (identidad de familia) > decisiones estéticas optativas. Ante contradicciones con los validadores, aplicar las reglas duras, informar y no declarar aprobación hasta completar la puerta de calidad.

---

Esta guía resume propiedades transversales observadas en los 17 assets aprobados. **No es una autorización de publicación, no contiene las geometrías maestras y no pretende que todos los iconos sean iguales.**
