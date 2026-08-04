# Capibara Tripo — Expresiones Alpha 0.2

## Base artística

Esta alpha reemplaza los modelos procedurales anteriores por el archivo `capibara.glb` suministrado por el usuario. El modelo conserva sus tres texturas PBR incrustadas y su geometría original.

## Implementación entregada

- Aplicación Android WebView con render WebGL/Babylon.
- GLB original empaquetado dentro de la APK.
- Controles táctiles para girar la vista.
- Estados faciales: neutral, feliz, sorpresa, sueño, enojado y guiño.
- Parpadeo automático.
- Interfaz adaptable a vertical y horizontal.
- APK sin bibliotecas nativas, por lo que no queda limitada a ARM32 o ARM64.

## Limitación de esta alpha

El GLB de Tripo no incluye armature, animaciones ni morph targets. Las expresiones 0.2 se implementan como una capa facial animada sobre el modelo 3D; todavía no deforman físicamente la malla.

La siguiente etapa debe crear una versión móvil del personaje mediante retopología y horneado de texturas, seguida de rig corporal y blend shapes faciales reales en Blender.

## Compresión del modelo

El GLB utiliza `EXT_meshopt_compression`. El modelo y sus texturas están dentro de la APK, pero esta alpha obtiene el decodificador meshoptimizer desde el CDN de Babylon al abrir la escena; por ello la primera carga requiere conexión a Internet.

## Validaciones realizadas

- GLB incluido: 13.168.280 bytes.
- SHA-256 GLB: `de01c18f6fdb37f353c3ed76924361e543aa30b8872f17a6cd957529f30191ce`.
- APK verificada como archivo ZIP sin errores.
- Permiso `android.permission.INTERNET` incorporado.
- Firma de desarrollo RSA-3072 con SHA-256.
- No se realizó instalación física porque el entorno no tiene un teléfono Android conectado.
