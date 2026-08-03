# Roadmap — Capibara 3D de calidad comercial

## Objetivo

Crear un personaje 3D original, tierno y reconocible como capibara explorador, con una calidad visual cercana a la referencia aprobada para **Capibara: Álbum de Láminas**.

Este roadmap se limita al personaje: modelado, materiales, pelaje, rig, expresiones y animaciones faciales. No incluye escenarios, menús ni mecánicas del juego.

> Proyecto familiar desarrollado para la hija del creador. La dirección visual debe ser amable, alegre, infantil y nunca inquietante.

## Regla de validación

Cada iteración debe entregar capturas reales generadas desde Blender o Godot, no imágenes conceptuales generadas por IA:

1. Frontal.
2. Perfil izquierdo.
3. Tres cuartos frontal.
4. Tres cuartos posterior.
5. Primer plano del rostro.
6. Prueba dentro de Godot en un teléfono Android.

La siguiente iteración comienza solamente cuando la silueta, el rostro o la deformación de la etapa anterior estén aceptados.

## Referencia visual objetivo

Rasgos que deben preservarse:

- Cuerpo redondeado, compacto y adorable.
- Cabeza grande, pero sin parecer oso, castor ni hámster.
- Hocico ancho y alargado, característico de una capibara.
- Nariz oscura, ancha y suave.
- Ojos grandes, brillantes y muy expresivos.
- Mejillas suaves, sonrisa amistosa y dos incisivos visibles.
- Orejas pequeñas y redondeadas.
- Patas cortas y manos simples pero expresivas.
- Pelaje marrón cálido con variación natural.
- Sombrero de explorador, mochila y cámara como accesorios separados.
- Apariencia estilizada 3D premium, no realismo fotográfico.

## Presupuesto técnico para Android

| Elemento | Meta inicial | Límite recomendado |
|---|---:|---:|
| Personaje sin accesorios | 25.000 triángulos | 40.000 |
| Personaje con accesorios | 35.000 triángulos | 55.000 |
| Textura principal | 2048 × 2048 | 2048 × 2048 |
| Texturas de accesorios | 1024 × 1024 | 2048 × 2048 |
| Materiales | 4–6 | 8 |
| Huesos deformantes | 45–65 | 80 |
| Blendshapes faciales | 35–50 | 60 |
| Draw calls del personaje | 4–7 | 10 |

El modelo debe funcionar en `armeabi-v7a` y `arm64-v8a`, usando el renderizador móvil de Godot.

---

# Iteraciones

## Iteración 1 — Silueta, cabeza y rostro base

**Estado:** EN CURSO en la rama `agent/capibara-alpha-godot`.

### Trabajo

- Ajustar proporción cabeza/cuerpo.
- Reducir apariencia de hámster.
- Ensanchar y adelantar el hocico.
- Separar mejor frente, mejillas, mandíbula y nariz.
- Reducir orejas y ubicarlas en la parte superior posterior.
- Mejorar ojos con esclerótica cálida, iris, pupila y reflejos.
- Corregir sonrisa, lengua e incisivos.
- Crear sombrero provisional para verificar la silueta final.

### Criterio de aprobación

- Se reconoce como capibara desde frontal, perfil y tres cuartos.
- La expresión neutra se ve tierna y no extraña.
- Los ojos miran al mismo punto.
- El sombrero no atraviesa las orejas ni la cabeza.

### Entregables

- `capibara_iter1_front.png`
- `capibara_iter1_profile.png`
- `capibara_iter1_three_quarter.png`
- `capibara_iter1_face.png`
- `.blend`, `.glb` y APK de revisión.

---

## Iteración 2 — Topología limpia y anatomía estilizada

### Trabajo

- Retopología completa del cuerpo y rostro.
- Bucles de deformación alrededor de ojos, boca, nariz y mejillas.
- Manos y pies con silueta clara.
- Unión limpia entre cabeza, cuello y torso.
- Reducir intersecciones entre piezas procedurales.
- Crear versión simétrica editable y aplicar asimetría sutil al final.

### Criterio de aprobación

- La malla puede deformarse sin quiebres visibles.
- No existen polígonos estirados ni normales invertidas.
- Perfil y espalda se ven coherentes.
- El personaje conserva su ternura sin depender del ángulo de cámara.

---

## Iteración 3 — UV y materiales base

### Trabajo

- Desplegado UV consistente y sin solapamientos no intencionales.
- Materiales PBR móviles para:
  - pelaje,
  - hocico,
  - nariz,
  - ojos,
  - dientes/lengua,
  - uñas.
- Paleta marrón cálida con hocico ligeramente más claro.
- Roughness diferenciada entre pelaje, nariz y ojos.
- Normal map suave, sin ruido excesivo.

### Criterio de aprobación

- El personaje se ve bien con luz neutra y cálida.
- No hay costuras UV visibles a distancia de juego.
- Nariz y ojos destacan sin parecer plástico barato.

---

## Iteración 4 — Pelaje estilizado optimizado

### Trabajo

- Crear textura direccional de pelo corto.
- Añadir variación de color en cabeza, lomo, vientre y extremidades.
- Usar cards o geometría de pelo solo en siluetas críticas:
  - mejillas,
  - coronilla,
  - brazos,
  - contorno del torso.
- Hornear detalles de Blender a mapas compatibles con Godot.
- Preparar dos niveles de calidad:
  - `Mobile_Low`,
  - `Mobile_High`.

### Criterio de aprobación

- El pelaje se percibe suave en primer plano.
- El modelo mantiene al menos 30 FPS en el Infinix Smart 9 dentro de la escena de prueba.
- No aparecen parpadeos, transparencias rotas ni exceso de overdraw.

---

## Iteración 5 — Accesorios definitivos

### Trabajo

- Sombrero de explorador con tela, costuras y cinta.
- Mochila con correas, bolsillos, hebillas y deformación ligera.
- Cámara con cuerpo, lente, correa y materiales propios.
- Lupa como accesorio opcional.
- Pivotes correctos para equipar y quitar cada accesorio.
- Colisiones simples para evitar intersecciones notorias.

### Criterio de aprobación

- Los accesorios se leen claramente en pantalla pequeña.
- No atraviesan el cuerpo durante la pose neutra.
- Pueden ocultarse o reemplazarse desde Godot.

---

## Iteración 6 — Rig corporal

### Trabajo

- Esqueleto principal:
  - root,
  - pelvis,
  - columna,
  - pecho,
  - cuello,
  - cabeza,
  - mandíbula,
  - brazos,
  - manos,
  - piernas,
  - pies.
- Huesos secundarios para barriga, mejillas, orejas, mochila y cámara.
- IK para brazos y piernas.
- Controles de mirada y cabeza.
- Weight painting limpio.

### Criterio de aprobación

- Puede sentarse, caminar, saludar y levantar objetos sin colapsar.
- Axilas, hombros, cuello y cadera no se pinzan.
- La mochila acompaña el cuerpo sin vibraciones.

---

## Iteración 7 — Rig facial y catálogo de blendshapes

### Ojos y párpados

- `blink_L`, `blink_R`, `blink_both`
- `eye_wide_L`, `eye_wide_R`
- `eye_squint_L`, `eye_squint_R`
- `look_up`, `look_down`, `look_left`, `look_right`

### Cejas y frente

- `brow_up_L`, `brow_up_R`
- `brow_down_L`, `brow_down_R`
- `brow_inner_up`
- `brow_sad`

### Hocico, nariz y mejillas

- `cheek_puff`
- `cheek_raise_L`, `cheek_raise_R`
- `nose_scrunch`
- `snout_up`
- `snout_left`, `snout_right`

### Boca y mandíbula

- `jaw_open`
- `mouth_smile`
- `mouth_frown`
- `mouth_o`
- `mouth_pucker`
- `mouth_left`, `mouth_right`
- `upper_lip_up`
- `lower_lip_down`
- `tongue_out`

### Criterio de aprobación

- Cada control funciona por separado y combinado.
- La boca no rompe los dientes ni atraviesa el hocico.
- Los párpados siguen la curvatura ocular.
- Las expresiones se leen en una pantalla de teléfono.

---

## Iteración 8 — Expresiones faciales esenciales

Crear poses completas combinando los controles de la iteración 7:

1. Neutro amable.
2. Sonrisa suave.
3. Sonrisa amplia.
4. Risa.
5. Sorpresa.
6. Curiosidad.
7. Concentración.
8. Alegría por encontrar una lámina.
9. Tristeza leve.
10. Frustración infantil suave.
11. Cansancio.
12. Sueño.
13. Miedo cómico y no traumático.
14. Orgullo.
15. Confusión.
16. Guiño izquierdo.
17. Guiño derecho.
18. Beso.
19. Comer.
20. Oler o investigar.

### Criterio de aprobación

- Las veinte expresiones son distinguibles sin texto.
- Ninguna se ve agresiva o inquietante.
- La identidad del personaje permanece estable.

---

## Iteración 9 — Animación facial y sincronización corporal

### Trabajo

- Parpadeo irregular natural.
- Micro movimientos oculares.
- Respiración y movimientos de nariz.
- Sonrisa progresiva.
- Reacción de sorpresa.
- Mirada hacia una lámina.
- Secuencia: detectar → sorprenderse → sonreír → celebrar.
- Sincronizar cara, cabeza, orejas, manos y postura.

### Criterio de aprobación

- El personaje no permanece congelado en reposo.
- Las transiciones no hacen saltos.
- Ojos, cabeza y manos dirigen la atención al mismo objetivo.

---

## Iteración 10 — Animaciones de presentación

Crear clips definitivos:

- `idle_cute`
- `idle_look_around`
- `wave`
- `happy_jump`
- `find_sticker`
- `show_sticker`
- `put_sticker_in_backpack`
- `open_album`
- `page_turn_reaction`
- `celebrate_collection`
- `sleepy`
- `camera_photo`
- `magnifying_glass_search`

### Criterio de aprobación

- Cada clip tiene pose inicial y final compatibles con `AnimationTree`.
- Las animaciones pueden mezclarse sin deslizamientos fuertes.
- Accesorios y expresiones están sincronizados.

---

## Iteración 11 — Shader, iluminación y apariencia final en Godot

### Trabajo

- Shader móvil de pelaje estilizado.
- Rim light muy sutil.
- Sombras suaves.
- Corrección de color cálida.
- Reflejos controlados en ojos y nariz.
- Escena neutra de evaluación con tres configuraciones de luz.
- Configuración `Low`, `Medium` y `High`.

### Criterio de aprobación

- La apariencia en Godot se mantiene cercana a Blender.
- El rostro conserva volumen en sombra y contraluz.
- No depende de bloom excesivo para verse atractivo.

---

## Iteración 12 — Optimización y personaje candidato a producción

### Trabajo

- LOD0, LOD1 y LOD2.
- Compresión de texturas para Android.
- Reducción de materiales y draw calls.
- Limpieza de huesos no utilizados.
- Pruebas de memoria y temperatura.
- Exportación GLB final y escena Godot reusable.
- Documentar nombres de huesos, blendshapes y animaciones.

### Criterio final

- 30 FPS sostenidos como mínimo en el Infinix Smart 9 en la escena de personaje.
- El personaje se ve atractivo en primer plano y a distancia de juego.
- Todas las expresiones funcionan dentro de Godot.
- El modelo puede utilizarse en menú, exploración y álbum sin duplicar assets.

---

# Flujo de trabajo por iteración

1. Modificar el generador o archivo `.blend` fuente.
2. Generar el `.blend` reproducible.
3. Exportar `.glb` con materiales, rig y animaciones.
4. Importar en Godot sin errores.
5. Ejecutar escena de validación.
6. Generar las seis capturas reales obligatorias.
7. Compilar APK para `armeabi-v7a` y `arm64-v8a`.
8. Probar en Infinix Smart 9.
9. Registrar observaciones.
10. Aprobar o repetir la iteración.

# Registro de avance

| Iteración | Estado | Versión prevista |
|---|---|---|
| 1. Silueta y rostro base | En curso | Alpha 0.2 |
| 2. Topología | Pendiente | Alpha 0.3 |
| 3. UV y materiales | Pendiente | Alpha 0.4 |
| 4. Pelaje | Pendiente | Alpha 0.5 |
| 5. Accesorios | Pendiente | Alpha 0.6 |
| 6. Rig corporal | Pendiente | Alpha 0.7 |
| 7. Rig facial | Pendiente | Alpha 0.8 |
| 8. Expresiones | Pendiente | Alpha 0.9 |
| 9. Animación facial | Pendiente | Alpha 0.10 |
| 10. Animaciones de presentación | Pendiente | Alpha 0.11 |
| 11. Shader e iluminación | Pendiente | Alpha 0.12 |
| 12. Optimización final | Pendiente | Beta 1.0 |

## Definición de terminado

El capibara estará listo para producción cuando:

- sea inmediatamente reconocible como el mismo personaje en todas las vistas;
- alcance una apariencia tierna y premium dentro de Godot;
- disponga de rig corporal y facial estable;
- cuente con al menos veinte expresiones y trece animaciones de presentación;
- funcione correctamente en Android de 32 y 64 bits;
- y mantenga rendimiento aceptable en el Infinix Smart 9.
