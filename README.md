# Prototipo de solicitud de préstamo de equipamiento

Prototipo de escritorio en Python para el flujo CU-04 (catálogo) y CU-07
(solicitud). Permite buscar y seleccionar equipamiento, completar una solicitud,
validar sus datos y guardar la solicitud y sus reservas en SQLite.

El diseño y la trazabilidad de requisitos, reglas de negocio y casos de prueba
se mantienen en [RFC_CU07.md](./RFC_CU07.md), aprobado en la versión 2.0.

## Funcionalidad implementada

### Catálogo CU-04 e interfaz

- Catálogo consultado desde SQLite, con búsqueda por nombre, categoría o gama.
- Selección de uno o más equipos y transferencia de esa selección al formulario.
- Interfaz Tkinter modernizada para catálogo y solicitud, con una paleta azul y
  blanca compartida.
- Botones, campos y avisos propios de la aplicación con estilo coherente, sin
  depender del color beige del tema del sistema operativo.
- No se agregaron dependencias de Python externas.

### Formulario CU-07 y validaciones

- Selección del rol Alumno o Docente. El año académico es obligatorio para
  alumnos y no aplica a docentes.
- Materia/Proyecto, docente y justificación obligatorios.
- Materias y docentes en listas desplegables conectadas con SQLite y filtradas
  según sus asignaciones. Si el docente tiene una única materia disponible, se
  precarga esa opción. Para el rol Docente, la identidad seleccionada queda
  bloqueada.
- Validación de gama y de la restricción de gama alta por año académico.
- Fechas obligatorias, estrictas en formato `YYYY-MM-DD`; no se aceptan fechas
  imposibles, retiro anterior al día actual ni devolución anterior o igual al
  retiro.
- Plazos: gama alta requiere al menos 48 horas y gama media permite como máximo
  48 horas.
- Las reglas de fechas y datos obligatorios se validan también en la capa de
  persistencia, no solamente en la pantalla.
- Al confirmar, valida disponibilidad y cantidades y guarda la solicitud,
  detalle de equipos y reservas dentro de una transacción SQLite. Si la
  operación falla, no conserva una solicitud parcial.

### Estado inicial de la solicitud

La marca `es_materia_proyecto` de la materia es la fuente de verdad para
determinar la aprobación:

| Solicitud | Estado inicial |
| --- | --- |
| Materia regular | `APROBADA` |
| Materia Proyecto solicitada por un alumno | `PENDIENTE` |
| Materia Proyecto solicitada por un docente asociado | `APROBADA` |
| Gama alta | `PENDIENTE` |

## Requisitos

- Python 3.
- Tkinter disponible en el sistema.
- SQLite, incluido en la biblioteca estándar de Python.

No hace falta instalar paquetes adicionales para ejecutar el prototipo o las
pruebas.

## Inicializar y ejecutar

Desde la carpeta del proyecto:

```bash
python3 init_db.py
python3 catalogo_cu04.py
```

La inicialización crea el esquema si no existe y aplica la migración aditiva a
las bases existentes, conservando las solicitudes históricas. Las solicitudes
anteriores a los catálogos académicos pueden mantener materia y docente sin
asignar; las solicitudes nuevas deben elegir ambos.

Al inicializar una base vacía, el prototipo agrega equipos de demostración si el
inventario no contiene equipos. Las materias y docentes ficticios se agregan
solo si las tablas académicas están vacías, para no mezclarlos con registros
institucionales existentes. Están identificados como datos `DEMO` y no son datos
institucionales reales.

En la interfaz:

1. Buscar y seleccionar uno o más equipos del catálogo; luego pulsar
   **Solicitar préstamo**.
2. Elegir el rol y, para Alumno, el año académico.
3. Seleccionar Materia/Proyecto y docente de las listas relacionadas.
4. Completar la justificación, revisar las fechas y ajustar las cantidades.
5. Pulsar **Confirmar solicitud**.

La aplicación informa errores de validación y disponibilidad en pantalla y
confirma el resultado de la operación. También puede abrirse el formulario
simple por consola:

```bash
python3 formulario_cu07.py
```

## Pruebas y validación visual

Ejecutar las pruebas unitarias:

```bash
python3 -m unittest -v test_init_db.py test_persistencia.py test_validaciones_cu07.py
```

La suite cubre el esquema y su migración, integridad referencial, catálogos y
filtros académicos, campos requeridos, reglas de aprobación, fechas, stock y
persistencia transaccional. En la última validación de esta implementación,
pasaron 19 pruebas.

Para comprobar la interfaz, iniciar CU-04, seleccionar equipos, recorrer CU-07
y verificar los avisos de error, advertencia y confirmación. Los colores de los
diálogos también se comprobaron con Tkinter; no forman parte de la suite
unitaria.

## Archivos principales

| Archivo | Responsabilidad |
| --- | --- |
| `catalogo_cu04.py` | Búsqueda y selección de equipos del CU-04; inicia el formulario con la selección. |
| `gui_cu07.py` | Formulario, filtros de catálogos, validaciones de pantalla y confirmación. |
| `ui_theme.py` | Paleta compartida y diálogos de la aplicación para Tkinter. |
| `validaciones.py` | Reglas de gama, año académico, fechas, plazos y cuenta activa simulada. |
| `persistencia.py` | Consultas de inventario y catálogos; registro transaccional de solicitudes y reservas. |
| `init_db.py` | Creación y migración aditiva del esquema SQLite. |
| `prestamos.db` | Base SQLite local usada por la aplicación. |
| `formulario_cu07.py` | Demostración simple por consola. |
| `test_init_db.py` | Pruebas del esquema, integridad e inicialización repetible (TC-17). |
| `test_persistencia.py` | Pruebas de catálogos, solicitudes, estados y stock (incluye TC-18, TC-19 y TC-21). |
| `test_validaciones_cu07.py` | Pruebas de fechas y plazos (TC-03, TC-05 y TC-06). |
| `RFC_CU07.md` | Alcance aprobado, decisiones, criterios de aceptación y seguimiento del trabajo. |

## Alcance y trabajo pendiente

Este es un prototipo local; no es una integración con los servicios
institucionales:

- La cuenta activa y la autenticación están simuladas.
- Los equipos y, cuando se cargan, las materias y docentes iniciales son datos
  de demostración.
- Las notificaciones no se envían por correo ni mensajería externa.
- La gestión completa de transiciones de estado, sanciones y vencimientos aún
  está pendiente.
- La derivación completa desde CU-11 y las reservas de aula no están integradas
  de extremo a extremo.
- No se controla equipamiento físico.

Las tareas y los casos de prueba pendientes están registrados en el plan de
trabajo y checklist de [RFC_CU07.md](./RFC_CU07.md).
