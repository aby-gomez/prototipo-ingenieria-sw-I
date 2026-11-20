# Prototipo CU-07: Solicitud de Prestamo

Prototipo grafico en Python para probar el caso de uso de solicitud de prestamo de equipamiento. Incluye validaciones de rol, año academico, gama y fechas.

## Que se implemento

- Interfaz grafica con Tkinter.
- Seleccion de rol Alumno o Docente.
- El año solo es obligatorio para alumnos.
- Validacion de gama alta y gama media.
- Validacion de fechas en formato `YYYY-MM-DD`.
- Rechazo de fechas vacias, inexistentes o anteriores al dia de solicitud.
- Rechazo de devolucion anterior al retiro.
- Validacion de plazos:
  - Gama alta: minimo 48 horas.
  - Gama media: maximo 48 horas.
- Reglas para combinar gamas y restriccion de gama alta segun el año.

La especificacion y trazabilidad se encuentran en [RFC_CU07.md](./RFC_CU07.md).

## Requisitos

- Python 3.
- Tkinter disponible en el sistema.
- Acceso a la base de datos local `prestamos.db`, si se activa una funcionalidad que la utilice.

## Inicializar la base de datos

Para crear las tablas localmente:

```bash
python3 init_db.py
```

Este comando usa SQLite y crea o conserva `prestamos.db`.

## Ejecucion

Desde la carpeta del proyecto:

```bash
python3 gui_cu07.py
```

Completar:

1. Seleccionar Alumno o Docente.
2. Si es alumno, seleccionar el año.
3. Seleccionar la gama.
4. Ingresar fecha de retiro y fecha de devolucion.
5. Presionar **Solicitar**.

Las fechas deben usar el formato `YYYY-MM-DD`. El sistema mostrara un mensaje de error por cada validacion que no se cumpla.

También puede ejecutarse la demostracion por consola:

```bash
python3 formulario_cu07.py
```



## Archivos principales

| Archivo | Descripcion |
| --- | --- |
| `gui_cu07.py` | Interfaz grafica principal del CU-07. Recibe el rol, año, gama y fechas, y muestra los resultados de las validaciones. |
| `validaciones.py` | Contiene la logica compartida de validacion: mezcla de gamas, restriccion de alumnos, plazos, fechas y cuenta activa simulada. |
| `formulario_cu07.py` | Version simple por consola del formulario. Permite ejecutar ejemplos y muestras de los casos TC-01 a TC-04 sin Tkinter. |
| `catalogo_cu04.py` | Interfaz grafica prototipo del CU-04. Muestra equipos de prueba y simula la redireccion hacia la solicitud. |
| `init_db.py` | Crea las tablas SQLite `equipo` y `solicitud` en `prestamos.db`. |
| `test_validaciones_cu07.py` | Pruebas unitarias de fechas y plazos para los casos TC-03, TC-05 y TC-06. |

## Documentacion y especificaciones

| Archivo | Descripcion |
| --- | --- |
| `RFC_CU07.md` | RFC del caso de uso CU-07. Define alcance, arquitectura, interfaces, reglas, casos de prueba y estado del trabajo. |
| `DOCUMENTO SISTEMA.txt` | Relevamiento general del sistema: casos de uso, reglas funcionales y restricciones del prestamo de equipamiento. |
| `SDD_PLAYBOOK.md` | Proceso Plan - Build - Validate que guia la implementacion asistida por IA. |
| `RFC_TEMPLATE.md` | Plantilla usada para preparar o actualizar RFC de nuevas funcionalidades. |
| `AGENTS.md` | Reglas internas para asistentes de IA que modifican el repositorio. |
| `spect critico prestamo.docx.txt` | Texto extraido de la especificacion critica relacionada con el prestamo. |

## Otros recursos

- `prestamos.db`: base SQLite creada o utilizada por el prototipo.
- `diagrama de clases-diagrama clase 2.jpg`: representa relaciones entre las clases del dominio.
- `diagrama-maquinas-estado.png`: muestra estados o transiciones relevantes del sistema.
- `__pycache__/`: carpeta automatica de archivos bytecode generados por Python; no contiene codigo fuente ni debe editarse.

## Limites del prototipo

Algunos componentes estan simulados o pendientes de integracion completa:

- El catalogo usa una lista de equipos de prueba, no consultas definitivas a la base.
- La cuenta activa se valida mediante una simulacion.
- La redireccion del catalogo al formulario CU-07 todavia no pasa una seleccion real.
- La disponibilidad de stock no esta integrada completamente con SQLite.
- Las restricciones derivadas de reservas de aula usan datos simulados.
