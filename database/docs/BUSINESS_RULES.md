# Business Rules - Zoo Management System

> Documento generado por @Architect. Define las reglas de negocio, restricciones lógicas y casos borde del sistema.

---

## 1. Gestion de Personal

### 1.1 Departamentos
- Cada departamento tiene un nombre unico.
- Estados validos: `active`, `inactive`.
- Un departamento no puede eliminarse si tiene empleados activos asignados.

### 1.2 Roles
- Cada rol tiene un nombre unico.
- Un empleado puede tener uno o mas roles simultaneamente (N:M).
- Los roles pueden ser: `veterinario`, `cuidador`, `nutricionista`, `guia`, `administrador`, `mantenimiento`.

### 1.3 Empleados
- El email del empleado debe ser unico en todo el sistema.
- El telefono es opcional pero si se proporciona debe tener formato valido.
- `hire_date` no puede ser una fecha futura.
- `birth_date` no puede ser una fecha futura ni posterior a `hire_date`.
- Un empleado solo puede pertenecer a un departamento a la vez.
- Estados validos: `active`, `on_leave`, `inactive`.
- **Soft delete** via `deleted_at`. Un empleado eliminado logicamente no debe aparecer en asignaciones nuevas.
- Caso borde: Al transferir un animal, el empleado autorizador debe estar en estado `active`.

---

## 2. Gestion de Animales

### 2.1 Especies
- El `common_name` y `scientific_name` deben ser unicos.
- `conservation_status` debe ser un valor del estandar IUCN: `extinct`, `extinct_in_wild`, `critically_endangered`, `endangered`, `vulnerable`, `near_threatened`, `least_concern`, `data_deficient`, `not_evaluated`.
- `diet_type` puede ser: `herbivore`, `carnivore`, `omnivore`, `insectivore`, `frugivore`.
- Los datos taxonomicos adicionales se almacenan en `additional_info` como JSONB.

### 2.2 Zonas
- Cada zona tiene un nombre unico.
- `surface_area_m2` debe ser mayor a 0.
- `climate_type` describe el tipo de clima simulado/mantenido (ej: `tropical`, `arido`, `templado`, `acuatico`, `polar`).

### 2.3 Recintos (Enclosures)
- Cada recinto pertenece a exactamente una zona.
- `capacity` debe ser mayor a 0 y no puede ser excedido por la cantidad de animales activos.
- `area_m2` debe ser mayor a 0.
- `type` describe el tipo de recinto: `cage`, `open`, `aquarium`, `aviary`, `terrarium`, `mixed`.
- Estados validos: `active`, `under_maintenance`, `closed`.
- **Regla critica:** No se puede asignar un animal a un recinto en estado `under_maintenance` o `closed`.
- Caso borde: Si un recinto pasa a mantenimiento, todos los animales deben ser reasignados antes o simultaneamente.

### 2.4 Animales
- `name` es obligatorio para animales nombrados, pero algunas especies (ej: insectos en exhibicion) pueden no tener nombre individual.
- `gender` debe ser `M`, `F` o `unknown`.
- `birth_date` puede ser estimada. `arrival_date` es obligatoria.
- `arrival_date` no puede ser futura.
- Estados validos: `active`, `quarantine`, `transferred`, `deceased`.
- Un animal activo debe estar asignado a exactamente un recinto activo.
- Un animal en `quarantine` no participa en espectaculos ni es visible al publico.
- Un animal `deceased` no puede ser reactivado ni modificado.
- Caso borde: Que pasa si un animal en cuarentena necesita atencion medica? Se permite, y el empleado asignado debe notificar la cuarentena en el registro medico.

### 2.5 Traslados (Animal Transfers)
- `origin_enclosure_id` y `destination_enclosure_id` deben ser diferentes.
- `transfer_date` no puede ser futura.
- El animal debe estar en estado `active` para ser trasladado.
- El empleado autorizador (`employee_id`) debe estar activo.
- Caso borde: No se puede trasladar un animal a un recinto que ya alcanzo su capacidad maxima.

---

## 3. Salud y Nutricion

### 3.1 Registros Medicos
- Cada registro esta asociado a un animal y un empleado (el que realizo la consulta).
- `visit_date` no puede ser futura.
- `urgency_level` debe ser: `low`, `normal`, `urgent`, `critical`.
- Un registro medico no puede ser eliminado, solo complementado.
- Caso borde: Un animal `deceased` puede tener registros medicos historicos pero no nuevos.

### 3.2 Vacunas
- Cada vacuna del catalogo tiene un nombre unico y un periodo de validez.
- `validity_period` define cada cuanto debe reaplicarse.
- `batch_number` en la aplicacion ayuda con trazabilidad.

### 3.3 Vacunaciones (Medical Vaccinations)
- Cada vacunacion se vincula a un registro medico y a una vacuna del catalogo.
- `application_date` no puede ser futura.
- `next_due_date` se calcula como `application_date + validity_period` de la vacuna.

### 3.4 Dietas
- Cada dieta esta disenada para un animal especifico por un empleado (nutricionista).
- `daily_rations` se almacena como JSONB con detalle de alimentos y cantidades.
- `effective_from` no puede ser posterior a `effective_to`.
- Una dieta puede tener un periodo de vigencia. Solo debe haber una dieta activa por animal a la vez.
- Caso borde: Si un animal cambia de dieta, la anterior se cierra (effective_to = NOW()) y la nueva comienza (effective_from = NOW()).

### 3.5 Horarios de Alimentacion
- Cada horario pertenece a una dieta.
- `feeding_time` define la hora del dia.
- `frequency` puede ser: `daily`, `twice_daily`, `weekly`, `custom`.
- `assigned_to` es el empleado responsable de alimentar.
- Estados validos: `active`, `suspended`, `cancelled`.

---

## 4. Visitantes y Entradas

### 4.1 Tipos de Entrada
- Cada tipo tiene un precio y un limite maximo de ventas diarias.
- `price` debe ser mayor o igual a 0.
- `max_daily_sales` debe ser mayor a 0.
- Estados validos: `active`, `inactive`, `seasonal`.

### 4.2 Visitantes
- El email del visitante no es obligatorio, pero si se proporciona debe ser unico.
- Los datos del visitante son para fines estadisticos y de contacto (no para autenticacion).

### 4.3 Entradas (Tickets)
- Cada entrada esta vinculada a un visitante y un tipo de entrada.
- `visit_date` es la fecha planificada de la visita.
- `price_paid` puede diferir del precio base del tipo (descuentos, promociones).
- `price_paid` debe ser mayor o igual a 0.
- Estados validos: `valid`, `used`, `expired`, `cancelled`, `refunded`.
- Caso borde: Una entrada cancelada no puede reutilizarse. Una entrada reembolsada tampoco.

---

## 5. Espectaculos

### 5.1 Shows
- Cada espectaculo ocurre en un recinto especifico.
- `days_of_week` almacena los dias (ej: `Mon,Wed,Fri`).
- `max_capacity` limita la audiencia simultanea.
- `start_time` y `duration_minutes` definen la ventana horaria.
- Un espectaculo en estado `cancelled` no genera participaciones nuevas.
- Estados validos: `active`, `cancelled`, `seasonal`, `under_review`.

### 5.2 Participacion en Espectaculos
- Un animal solo puede participar si esta en estado `active`.
- `role_in_show` describe la funcion del animal (ej: `star`, `supporting`, `educational`).
- Un animal no puede participar en dos espectaculos que se traslapen en horario.

---

## 6. Conservacion - Padrinazgos

### 6.1 Padrinos (Sponsors)
- `sponsor_type` puede ser: `individual`, `corporate`, `institutional`, `governmental`.
- Un padrinazgo requiere un sponsor y un animal.

### 6.2 Padrinazgos (Sponsorships)
- `monthly_amount` debe ser mayor a 0.
- `start_date` no puede ser futura al momento de creacion.
- `end_date` puede ser null (padrinazgo indefinido). Si tiene valor, no puede ser anterior a `start_date`.
- Un animal puede tener multiples padrinos activos simultaneamente.
- Un padrinazgo en `expired` o `cancelled` no genera cobros.
- Estados validos: `active`, `paused`, `expired`, `cancelled`.
- Caso borde: Si un animal fallece, todos sus padrinazgos activos deben pasar a `expired` automaticamente.

---

## 7. Inventario y Suministros

### 7.1 Proveedores
- Cada proveedor tiene un nombre unico.
- Estados validos: `active`, `inactive`.
- **Soft delete** via `deleted_at`.

### 7.2 Categorias de Insumos
- Cada categoria tiene un nombre unico.
- Ejemplos: `alimento_animal`, `medicamento`, `limpieza`, `herramienta`, `material_veterinario`.

### 7.3 Items de Inventario
- Cada item esta vinculado a un proveedor y una categoria.
- `unit_of_measure` puede ser: `kg`, `g`, `l`, `ml`, `unit`, `box`, `pack`.
- `current_stock` no puede ser negativo.
- `min_stock_level` y `max_stock_level` deben ser >= 0.
- `min_stock_level` debe ser <= `max_stock_level`.
- Caso borde: Si `current_stock` <= `min_stock_level`, se debe generar una alerta de reorden.

### 7.4 Movimientos de Inventario
- `movement_type` puede ser: `in` (entrada), `out` (salida), `adjustment` (ajuste), `return` (devolucion).
- `quantity` siempre debe ser positiva (el signo se infiere del tipo de movimiento).
- `new_stock_level` se calcula y almacena para auditoria.
- Todo movimiento debe ser registrado por un empleado activo.

---

## 8. Reglas Transversales

- **Timestamps:** Todas las tablas tienen `created_at` (auto) y `updated_at` (manual).
- **Soft Deletes:** Solo `employees`, `animals`, y `suppliers` usan soft delete.
- **Ids:** Todas las PK son UUID v4 generados automaticamente.
- **Eliminacion en cascada:** Se usa `RESTRICT` por defecto para prevenir eliminaciones accidentales. `CASCADE` solo donde tenga sentido logico (ej: eliminar employee_roles al eliminar un empleado).
- **Nomenclatura:** Todo en `snake_case`, tablas en plural.
