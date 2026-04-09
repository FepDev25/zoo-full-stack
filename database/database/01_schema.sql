-- ZOO MANAGEMENT SYSTEM - SCHEMA DDL

-- GLOBAL: Updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 1. PERSONNEL (Gestion de Personal)

-- 1.1 Departments
CREATE TABLE departments (
    id              UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    name            VARCHAR(100) NOT NULL,
    description     TEXT,
    status          VARCHAR(50)  NOT NULL DEFAULT 'active',
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ,

    CONSTRAINT uq_departments_name UNIQUE (name),
    CONSTRAINT ck_departments_status CHECK (status IN ('active', 'inactive'))
);

COMMENT ON TABLE departments IS 'Departamentos del zoologico (veterinaria, mantenimiento, etc.)';
COMMENT ON COLUMN departments.name IS 'Nombre unico del departamento';
COMMENT ON COLUMN departments.status IS 'Estado del departamento: active, inactive';

CREATE INDEX idx_departments_status ON departments (status);

CREATE TRIGGER trg_departments_updated_at
    BEFORE UPDATE ON departments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 1.2 Roles
CREATE TABLE roles (
    id              UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    name            VARCHAR(80) NOT NULL,
    description     TEXT,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ,

    CONSTRAINT uq_roles_name UNIQUE (name)
);

COMMENT ON TABLE roles IS 'Catalogo de roles disponibles para los empleados del zoologico';
COMMENT ON COLUMN roles.name IS 'Nombre unico del rol (ej: veterinario, cuidador, guia)';

CREATE TRIGGER trg_roles_updated_at
    BEFORE UPDATE ON roles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 1.3 Employees
CREATE TABLE employees (
    id              UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    full_name       VARCHAR(100) NOT NULL,
    email           VARCHAR(100) NOT NULL,
    phone           VARCHAR(20),
    hire_date       DATE        NOT NULL,
    birth_date      DATE,
    department_id   UUID        NOT NULL REFERENCES departments (id) ON DELETE RESTRICT,
    status          VARCHAR(50)  NOT NULL DEFAULT 'active',
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ,
    deleted_at      TIMESTAMPTZ,

    CONSTRAINT uq_employees_email UNIQUE (email),
    CONSTRAINT ck_employees_phone CHECK (phone ~ '^\+?[0-9]{7,15}$' OR phone IS NULL),
    CONSTRAINT ck_employees_hire_date CHECK (hire_date <= CURRENT_DATE),
    CONSTRAINT ck_employees_birth_date CHECK (birth_date IS NULL OR birth_date <= CURRENT_DATE),
    CONSTRAINT ck_employees_birth_before_hire CHECK (birth_date IS NULL OR hire_date IS NULL OR birth_date < hire_date),
    CONSTRAINT ck_employees_status CHECK (status IN ('active', 'on_leave', 'inactive'))
);

COMMENT ON TABLE employees IS 'Empleados del zoologico con soft delete via deleted_at';
COMMENT ON COLUMN employees.email IS 'Email unico del empleado';
COMMENT ON COLUMN employees.phone IS 'Telefono con formato internacional opcional';
COMMENT ON COLUMN employees.hire_date IS 'Fecha de contratacion, no puede ser futura';
COMMENT ON COLUMN employees.birth_date IS 'Fecha de nacimiento opcional';
COMMENT ON COLUMN employees.deleted_at IS 'Soft delete: fecha de eliminacion logica';

CREATE INDEX idx_employees_department ON employees (department_id);
CREATE INDEX idx_employees_status ON employees (status);
CREATE INDEX idx_employees_deleted_at ON employees (deleted_at);

CREATE TRIGGER trg_employees_updated_at
    BEFORE UPDATE ON employees
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 1.4 Employee Roles (N:M)
CREATE TABLE employee_roles (
    id              UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    employee_id     UUID        NOT NULL REFERENCES employees (id) ON DELETE CASCADE,
    role_id         UUID        NOT NULL REFERENCES roles (id) ON DELETE CASCADE,
    assigned_at     TIMESTAMPTZ  NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_employee_role UNIQUE (employee_id, role_id)
);

COMMENT ON TABLE employee_roles IS 'Relacion N:M entre empleados y roles';

CREATE INDEX idx_employee_roles_employee ON employee_roles (employee_id);
CREATE INDEX idx_employee_roles_role ON employee_roles (role_id);

-- 2. ANIMALS (Gestion de Animales)

-- 2.1 Species
CREATE TABLE species (
    id                  UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    common_name         VARCHAR(150) NOT NULL,
    scientific_name     VARCHAR(150) NOT NULL,
    conservation_status VARCHAR(50)  NOT NULL DEFAULT 'data_deficient',
    habitat_description TEXT,
    diet_type           VARCHAR(100) NOT NULL,
    additional_info     JSONB,
    created_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ,

    CONSTRAINT uq_species_common_name UNIQUE (common_name),
    CONSTRAINT uq_species_scientific_name UNIQUE (scientific_name),
    CONSTRAINT ck_species_conservation CHECK (conservation_status IN (
        'extinct', 'extinct_in_wild', 'critically_endangered', 'endangered',
        'vulnerable', 'near_threatened', 'least_concern', 'data_deficient', 'not_evaluated'
    )),
    CONSTRAINT ck_species_diet CHECK (diet_type IN (
        'herbivore', 'carnivore', 'omnivore', 'insectivore', 'frugivore'
    ))
);

COMMENT ON TABLE species IS 'Catalogo de especies del zoologico con datos taxonomicos y de conservacion';
COMMENT ON COLUMN species.conservation_status IS 'Estado de conservacion segun IUCN';
COMMENT ON COLUMN species.diet_type IS 'Tipo de dieta principal de la especie';
COMMENT ON COLUMN species.additional_info IS 'Datos taxonomicos flexibles como JSONB';

CREATE INDEX idx_species_conservation ON species (conservation_status);

CREATE TRIGGER trg_species_updated_at
    BEFORE UPDATE ON species
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 2.2 Zones
CREATE TABLE zones (
    id              UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    name            VARCHAR(100) NOT NULL,
    description     TEXT,
    surface_area_m2 FLOAT       NOT NULL,
    climate_type    VARCHAR(50)  NOT NULL,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ,

    CONSTRAINT uq_zones_name UNIQUE (name),
    CONSTRAINT ck_zones_surface_area CHECK (surface_area_m2 > 0),
    CONSTRAINT ck_zones_climate CHECK (climate_type IN (
        'tropical', 'arid', 'temperate', 'aquatic', 'polar', 'subtropical', 'mediterranean'
    ))
);

COMMENT ON TABLE zones IS 'Zonas geograficas del zoologico que agrupan recintos';
COMMENT ON COLUMN zones.surface_area_m2 IS 'Superficie total de la zona en metros cuadrados';
COMMENT ON COLUMN zones.climate_type IS 'Tipo de clima mantenido en la zona';

CREATE TRIGGER trg_zones_updated_at
    BEFORE UPDATE ON zones
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 2.3 Enclosures
CREATE TABLE enclosures (
    id              UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    name            VARCHAR(150) NOT NULL,
    zone_id         UUID        NOT NULL REFERENCES zones (id) ON DELETE RESTRICT,
    type            VARCHAR(50)  NOT NULL,
    capacity        INT         NOT NULL,
    area_m2         FLOAT       NOT NULL,
    features        TEXT,
    status          VARCHAR(50)  NOT NULL DEFAULT 'active',
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ,

    CONSTRAINT ck_enclosures_capacity CHECK (capacity > 0),
    CONSTRAINT ck_enclosures_area CHECK (area_m2 > 0),
    CONSTRAINT ck_enclosures_type CHECK (type IN (
        'cage', 'open', 'aquarium', 'aviary', 'terrarium', 'mixed'
    )),
    CONSTRAINT ck_enclosures_status CHECK (status IN ('active', 'under_maintenance', 'closed'))
);

COMMENT ON TABLE enclosures IS 'Recintos individuales donde se alojan los animales';
COMMENT ON COLUMN enclosures.capacity IS 'Numero maximo de animales que puede albergar';
COMMENT ON COLUMN enclosures.type IS 'Tipo de recinto: cage, open, aquarium, aviary, terrarium, mixed';
COMMENT ON COLUMN enclosures.status IS 'Estado: active, under_maintenance, closed';

CREATE INDEX idx_enclosures_zone ON enclosures (zone_id);
CREATE INDEX idx_enclosures_status ON enclosures (status);

CREATE TRIGGER trg_enclosures_updated_at
    BEFORE UPDATE ON enclosures
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 2.4 Animals
CREATE TABLE animals (
    id              UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    name            VARCHAR(100),
    species_id      UUID        NOT NULL REFERENCES species (id) ON DELETE RESTRICT,
    enclosure_id    UUID        NOT NULL REFERENCES enclosures (id) ON DELETE RESTRICT,
    gender          VARCHAR(10)  NOT NULL DEFAULT 'unknown',
    birth_date      DATE,
    arrival_date    DATE        NOT NULL,
    origin          VARCHAR(255),
    status          VARCHAR(50)  NOT NULL DEFAULT 'active',
    notes           TEXT,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ,
    deleted_at      TIMESTAMPTZ,

    CONSTRAINT ck_animals_gender CHECK (gender IN ('M', 'F', 'unknown')),
    CONSTRAINT ck_animals_arrival CHECK (arrival_date <= CURRENT_DATE),
    CONSTRAINT ck_animals_status CHECK (status IN ('active', 'quarantine', 'transferred', 'deceased'))
);

COMMENT ON TABLE animals IS 'Registro individual de cada animal del zoologico con soft delete';
COMMENT ON COLUMN animals.name IS 'Nombre individual del animal, puede ser nulo para especies sin nombre';
COMMENT ON COLUMN animals.gender IS 'Genero: M (macho), F (hembra), unknown (desconocido)';
COMMENT ON COLUMN animals.arrival_date IS 'Fecha de llegada al zoologico, obligatoria';
COMMENT ON COLUMN animals.status IS 'Estado: active, quarantine, transferred, deceased';
COMMENT ON COLUMN animals.deleted_at IS 'Soft delete: fecha de eliminacion logica';

CREATE INDEX idx_animals_species ON animals (species_id);
CREATE INDEX idx_animals_enclosure ON animals (enclosure_id);
CREATE INDEX idx_animals_status ON animals (status);
CREATE INDEX idx_animals_deleted_at ON animals (deleted_at);

CREATE TRIGGER trg_animals_updated_at
    BEFORE UPDATE ON animals
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 2.5 Animal Transfers
CREATE TABLE animal_transfers (
    id                        UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    animal_id                 UUID        NOT NULL REFERENCES animals (id) ON DELETE RESTRICT,
    origin_enclosure_id       UUID        NOT NULL REFERENCES enclosures (id) ON DELETE RESTRICT,
    destination_enclosure_id  UUID        NOT NULL REFERENCES enclosures (id) ON DELETE RESTRICT,
    employee_id               UUID        NOT NULL REFERENCES employees (id) ON DELETE RESTRICT,
    transfer_date             TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    reason                    TEXT,

    CONSTRAINT ck_transfers_different_enclosures CHECK (origin_enclosure_id != destination_enclosure_id),
    CONSTRAINT ck_transfers_date CHECK (transfer_date <= NOW())
);

COMMENT ON TABLE animal_transfers IS 'Historial de traslados de animales entre recintos';
COMMENT ON COLUMN animal_transfers.origin_enclosure_id IS 'Recinto de origen del animal';
COMMENT ON COLUMN animal_transfers.destination_enclosure_id IS 'Recinto de destino del animal';
COMMENT ON COLUMN animal_transfers.employee_id IS 'Empleado que autorizo el traslado';
COMMENT ON COLUMN animal_transfers.reason IS 'Motivo del traslado';

CREATE INDEX idx_transfers_animal ON animal_transfers (animal_id);
CREATE INDEX idx_transfers_origin ON animal_transfers (origin_enclosure_id);
CREATE INDEX idx_transfers_destination ON animal_transfers (destination_enclosure_id);
CREATE INDEX idx_transfers_employee ON animal_transfers (employee_id);

-- 3. HEALTH (Salud)

-- 3.1 Medical Records
CREATE TABLE medical_records (
    id              UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    animal_id       UUID        NOT NULL REFERENCES animals (id) ON DELETE RESTRICT,
    performed_by    UUID        NOT NULL REFERENCES employees (id) ON DELETE RESTRICT,
    visit_date      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    diagnosis       VARCHAR(100),
    treatment       TEXT,
    observations    TEXT,
    urgency_level   VARCHAR(50)  NOT NULL DEFAULT 'normal',
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ,

    CONSTRAINT ck_medical_visit_date CHECK (visit_date <= NOW()),
    CONSTRAINT ck_medical_urgency CHECK (urgency_level IN ('low', 'normal', 'urgent', 'critical'))
);

COMMENT ON TABLE medical_records IS 'Registros medicos de cada consulta a un animal';
COMMENT ON COLUMN medical_records.performed_by IS 'Empleado (veterinario) que realizo la consulta';
COMMENT ON COLUMN medical_records.urgency_level IS 'Nivel de urgencia: low, normal, urgent, critical';

CREATE INDEX idx_medical_animal ON medical_records (animal_id);
CREATE INDEX idx_medical_performed_by ON medical_records (performed_by);
CREATE INDEX idx_medical_date ON medical_records (visit_date);
CREATE INDEX idx_medical_urgency ON medical_records (urgency_level);

CREATE TRIGGER trg_medical_records_updated_at
    BEFORE UPDATE ON medical_records
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 3.2 Vaccines
CREATE TABLE vaccines (
    id              UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    name            VARCHAR(150) NOT NULL,
    description     TEXT,
    validity_period INTERVAL,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ,

    CONSTRAINT uq_vaccines_name UNIQUE (name)
);

COMMENT ON TABLE vaccines IS 'Catalogo de vacunas disponibles con periodo de validez';
COMMENT ON COLUMN vaccines.validity_period IS 'Duracion de la inmunidad, usado para calcular proxima dosis';

CREATE TRIGGER trg_vaccines_updated_at
    BEFORE UPDATE ON vaccines
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 3.3 Medical Vaccinations
CREATE TABLE medical_vaccinations (
    id                  UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    medical_record_id   UUID        NOT NULL REFERENCES medical_records (id) ON DELETE CASCADE,
    vaccine_id          UUID        NOT NULL REFERENCES vaccines (id) ON DELETE RESTRICT,
    application_date    TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    next_due_date       TIMESTAMPTZ,
    batch_number        VARCHAR(100),
    notes               TEXT,

    CONSTRAINT ck_vaccination_app_date CHECK (application_date <= NOW())
);

COMMENT ON TABLE medical_vaccinations IS 'Registro de vacunaciones aplicadas a un animal';
COMMENT ON COLUMN medical_vaccinations.batch_number IS 'Numero de lote para trazabilidad';
COMMENT ON COLUMN medical_vaccinations.next_due_date IS 'Fecha calculada para la proxima dosis';

CREATE INDEX idx_vaccinations_record ON medical_vaccinations (medical_record_id);
CREATE INDEX idx_vaccinations_vaccine ON medical_vaccinations (vaccine_id);
CREATE INDEX idx_vaccinations_next_due ON medical_vaccinations (next_due_date);

-- 4. NUTRITION (Nutricion)

-- 4.1 Diets
CREATE TABLE diets (
    id              UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    animal_id       UUID        NOT NULL REFERENCES animals (id) ON DELETE RESTRICT,
    designed_by     UUID        NOT NULL REFERENCES employees (id) ON DELETE RESTRICT,
    name            VARCHAR(150) NOT NULL,
    description     TEXT,
    daily_rations   JSONB       NOT NULL,
    effective_from  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    effective_to    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ,

    CONSTRAINT ck_diets_period CHECK (effective_to IS NULL OR effective_from < effective_to)
);

COMMENT ON TABLE diets IS 'Dietas personalizadas para cada animal con periodo de vigencia';
COMMENT ON COLUMN diets.daily_rations IS 'Detalle de alimentos y cantidades diarias en formato JSONB';
COMMENT ON COLUMN diets.effective_from IS 'Fecha de inicio de vigencia de la dieta';
COMMENT ON COLUMN diets.effective_to IS 'Fecha de fin de vigencia, null si esta activa';

CREATE INDEX idx_diets_animal ON diets (animal_id);
CREATE INDEX idx_diets_designer ON diets (designed_by);
CREATE INDEX idx_diets_effective ON diets (effective_from, effective_to);

CREATE TRIGGER trg_diets_updated_at
    BEFORE UPDATE ON diets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 4.2 Feeding Schedules
CREATE TABLE feeding_schedules (
    id              UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    diet_id         UUID        NOT NULL REFERENCES diets (id) ON DELETE CASCADE,
    assigned_to     UUID        NOT NULL REFERENCES employees (id) ON DELETE RESTRICT,
    feeding_time    TIME        NOT NULL,
    frequency       VARCHAR(50)  NOT NULL DEFAULT 'daily',
    instructions    TEXT,
    status          VARCHAR(50)  NOT NULL DEFAULT 'active',
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ,

    CONSTRAINT ck_feeding_frequency CHECK (frequency IN ('daily', 'twice_daily', 'weekly', 'custom')),
    CONSTRAINT ck_feeding_status CHECK (status IN ('active', 'suspended', 'cancelled'))
);

COMMENT ON TABLE feeding_schedules IS 'Horarios de alimentacion vinculados a una dieta';
COMMENT ON COLUMN feeding_schedules.feeding_time IS 'Hora del dia para la alimentacion';
COMMENT ON COLUMN feeding_schedules.frequency IS 'Frecuencia: daily, twice_daily, weekly, custom';
COMMENT ON COLUMN feeding_schedules.assigned_to IS 'Empleado responsable de la alimentacion';

CREATE INDEX idx_feeding_diet ON feeding_schedules (diet_id);
CREATE INDEX idx_feeding_employee ON feeding_schedules (assigned_to);
CREATE INDEX idx_feeding_status ON feeding_schedules (status);

CREATE TRIGGER trg_feeding_schedules_updated_at
    BEFORE UPDATE ON feeding_schedules
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 5. VISITORS & TICKETS (Visitantes y Entradas)

-- 5.1 Ticket Types
CREATE TABLE ticket_types (
    id              UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    name            VARCHAR(100) NOT NULL,
    price           DECIMAL(10,2) NOT NULL,
    max_daily_sales INT         NOT NULL,
    description     TEXT,
    status          VARCHAR(50)  NOT NULL DEFAULT 'active',
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ,

    CONSTRAINT uq_ticket_types_name UNIQUE (name),
    CONSTRAINT ck_ticket_types_price CHECK (price >= 0),
    CONSTRAINT ck_ticket_types_max_sales CHECK (max_daily_sales > 0),
    CONSTRAINT ck_ticket_types_status CHECK (status IN ('active', 'inactive', 'seasonal'))
);

COMMENT ON TABLE ticket_types IS 'Tipos de entrada disponibles para los visitantes';
COMMENT ON COLUMN ticket_types.price IS 'Precio base del tipo de entrada';
COMMENT ON COLUMN ticket_types.max_daily_sales IS 'Limite maximo de ventas por dia';

CREATE INDEX idx_ticket_types_status ON ticket_types (status);

CREATE TRIGGER trg_ticket_types_updated_at
    BEFORE UPDATE ON ticket_types
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 5.2 Visitors
CREATE TABLE visitors (
    id              UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    full_name       VARCHAR(100) NOT NULL,
    email           VARCHAR(100),
    phone           VARCHAR(20),
    birth_date      DATE,
    country         VARCHAR(50),
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ
);

COMMENT ON TABLE visitors IS 'Datos de visitantes para estadisticas y contacto';
COMMENT ON COLUMN visitors.email IS 'Email opcional, unico si se proporciona';

CREATE UNIQUE INDEX uq_visitors_email ON visitors (email) WHERE email IS NOT NULL;

CREATE TRIGGER trg_visitors_updated_at
    BEFORE UPDATE ON visitors
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 5.3 Tickets
CREATE TABLE tickets (
    id              UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    visitor_id      UUID        NOT NULL REFERENCES visitors (id) ON DELETE CASCADE,
    ticket_type_id  UUID        NOT NULL REFERENCES ticket_types (id) ON DELETE RESTRICT,
    visit_date      DATE        NOT NULL,
    purchase_date   TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    price_paid      DECIMAL(10,2) NOT NULL,
    status          VARCHAR(50)  NOT NULL DEFAULT 'valid',

    CONSTRAINT ck_tickets_price_paid CHECK (price_paid >= 0),
    CONSTRAINT ck_tickets_status CHECK (status IN ('valid', 'used', 'expired', 'cancelled', 'refunded'))
);

COMMENT ON TABLE tickets IS 'Entradas vendidas a visitantes';
COMMENT ON COLUMN tickets.visit_date IS 'Fecha planificada de la visita';
COMMENT ON COLUMN tickets.price_paid IS 'Precio final pagado (puede incluir descuentos)';
COMMENT ON COLUMN tickets.status IS 'Estado: valid, used, expired, cancelled, refunded';

CREATE INDEX idx_tickets_visitor ON tickets (visitor_id);
CREATE INDEX idx_tickets_type ON tickets (ticket_type_id);
CREATE INDEX idx_tickets_visit_date ON tickets (visit_date);
CREATE INDEX idx_tickets_purchase_date ON tickets (purchase_date);
CREATE INDEX idx_tickets_status ON tickets (status);

-- 6. SHOWS (Espectaculos)

-- 6.1 Shows
CREATE TABLE shows (
    id              UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    name            VARCHAR(150) NOT NULL,
    description     TEXT,
    start_time      TIME        NOT NULL,
    duration_minutes INT        NOT NULL,
    enclosure_id    UUID        NOT NULL REFERENCES enclosures (id) ON DELETE RESTRICT,
    max_capacity    INT         NOT NULL,
    days_of_week    JSONB       NOT NULL,
    status          VARCHAR(50)  NOT NULL DEFAULT 'active',
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ,

    CONSTRAINT ck_shows_duration CHECK (duration_minutes > 0),
    CONSTRAINT ck_shows_capacity CHECK (max_capacity > 0),
    CONSTRAINT ck_shows_status CHECK (status IN ('active', 'cancelled', 'seasonal', 'under_review'))
);

COMMENT ON TABLE shows IS 'Espectaculos programados en recintos del zoologico';
COMMENT ON COLUMN shows.start_time IS 'Hora de inicio del espectaculo';
COMMENT ON COLUMN shows.duration_minutes IS 'Duracion en minutos';
COMMENT ON COLUMN shows.days_of_week IS 'Dias de la semana como array JSONB (ej: ["Mon","Wed","Fri"])';
COMMENT ON COLUMN shows.max_capacity IS 'Capacidad maxima de audiencia';

CREATE INDEX idx_shows_enclosure ON shows (enclosure_id);
CREATE INDEX idx_shows_status ON shows (status);

CREATE TRIGGER trg_shows_updated_at
    BEFORE UPDATE ON shows
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 6.2 Show Animals (N:M)
CREATE TABLE show_animals (
    id              UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    show_id         UUID        NOT NULL REFERENCES shows (id) ON DELETE CASCADE,
    animal_id       UUID        NOT NULL REFERENCES animals (id) ON DELETE RESTRICT,
    role_in_show    VARCHAR(100),
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_show_animal UNIQUE (show_id, animal_id)
);

COMMENT ON TABLE show_animals IS 'Animales participantes en cada espectaculo';
COMMENT ON COLUMN show_animals.role_in_show IS 'Funcion del animal: star, supporting, educational';

CREATE INDEX idx_show_animals_show ON show_animals (show_id);
CREATE INDEX idx_show_animals_animal ON show_animals (animal_id);

-- 7. CONSERVATION - SPONSORSHIPS (Padrinazgos)

-- 7.1 Sponsors
CREATE TABLE sponsors (
    id              UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    name            VARCHAR(150) NOT NULL,
    contact_name    VARCHAR(150),
    email           VARCHAR(100),
    phone           VARCHAR(20),
    sponsor_type    VARCHAR(50)  NOT NULL,
    notes           TEXT,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ,

    CONSTRAINT ck_sponsors_type CHECK (sponsor_type IN (
        'individual', 'corporate', 'institutional', 'governmental'
    )),
    CONSTRAINT ck_sponsors_phone CHECK (phone ~ '^\+?[0-9]{7,15}$' OR phone IS NULL)
);

COMMENT ON TABLE sponsors IS 'Padrinos y patrocinadores del zoologico';
COMMENT ON COLUMN sponsors.sponsor_type IS 'Tipo de patrocinador: individual, corporate, institutional, governmental';

CREATE INDEX idx_sponsors_type ON sponsors (sponsor_type);

CREATE TRIGGER trg_sponsors_updated_at
    BEFORE UPDATE ON sponsors
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 7.2 Sponsorships
CREATE TABLE sponsorships (
    id              UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    sponsor_id      UUID        NOT NULL REFERENCES sponsors (id) ON DELETE RESTRICT,
    animal_id       UUID        NOT NULL REFERENCES animals (id) ON DELETE RESTRICT,
    monthly_amount  DECIMAL(10,2) NOT NULL,
    start_date      DATE        NOT NULL,
    end_date        DATE,
    status          VARCHAR(50)  NOT NULL DEFAULT 'active',
    notes           TEXT,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ,

    CONSTRAINT ck_sponsorships_amount CHECK (monthly_amount > 0),
    CONSTRAINT ck_sponsorships_dates CHECK (end_date IS NULL OR start_date <= end_date),
    CONSTRAINT ck_sponsorships_status CHECK (status IN ('active', 'paused', 'expired', 'cancelled'))
);

COMMENT ON TABLE sponsorships IS 'Vinculos entre patrocinadores y animales para conservacion';
COMMENT ON COLUMN sponsorships.monthly_amount IS 'Monto mensual del padrinazgo';
COMMENT ON COLUMN sponsorships.start_date IS 'Fecha de inicio del padrinazgo';
COMMENT ON COLUMN sponsorships.end_date IS 'Fecha de fin, null si es indefinido';
COMMENT ON COLUMN sponsorships.status IS 'Estado: active, paused, expired, cancelled';

CREATE INDEX idx_sponsorships_sponsor ON sponsorships (sponsor_id);
CREATE INDEX idx_sponsorships_animal ON sponsorships (animal_id);
CREATE INDEX idx_sponsorships_status ON sponsorships (status);

CREATE TRIGGER trg_sponsorships_updated_at
    BEFORE UPDATE ON sponsorships
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 8. INVENTORY (Inventario y Suministros)

-- 8.1 Suppliers
CREATE TABLE suppliers (
    id              UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    name            VARCHAR(150) NOT NULL,
    address         VARCHAR(255),
    contact_name    VARCHAR(100),
    email           VARCHAR(100),
    phone           VARCHAR(20),
    website         VARCHAR(100),
    status          VARCHAR(50)  NOT NULL DEFAULT 'active',
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ,
    deleted_at      TIMESTAMPTZ,

    CONSTRAINT uq_suppliers_name UNIQUE (name),
    CONSTRAINT ck_suppliers_status CHECK (status IN ('active', 'inactive')),
    CONSTRAINT ck_suppliers_phone CHECK (phone ~ '^\+?[0-9]{7,15}$' OR phone IS NULL),
    CONSTRAINT ck_suppliers_email CHECK (email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$' OR email IS NULL)
);

COMMENT ON TABLE suppliers IS 'Proveedores de insumos del zoologico con soft delete';
COMMENT ON COLUMN suppliers.name IS 'Nombre unico del proveedor';
COMMENT ON COLUMN suppliers.deleted_at IS 'Soft delete: fecha de eliminacion logica';

CREATE INDEX idx_suppliers_status ON suppliers (status);
CREATE INDEX idx_suppliers_deleted_at ON suppliers (deleted_at);

CREATE TRIGGER trg_suppliers_updated_at
    BEFORE UPDATE ON suppliers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 8.2 Supply Categories
CREATE TABLE supply_categories (
    id              UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    name            VARCHAR(100) NOT NULL,
    description     TEXT,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ,

    CONSTRAINT uq_supply_categories_name UNIQUE (name)
);

COMMENT ON TABLE supply_categories IS 'Categorias de insumos para el inventario';
COMMENT ON COLUMN supply_categories.name IS 'Nombre unico de la categoria';

CREATE TRIGGER trg_supply_categories_updated_at
    BEFORE UPDATE ON supply_categories
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 8.3 Inventory Items
CREATE TABLE inventory_items (
    id              UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    name            VARCHAR(200) NOT NULL,
    description     TEXT,
    supplier_id     UUID        NOT NULL REFERENCES suppliers (id) ON DELETE RESTRICT,
    category_id     UUID        NOT NULL REFERENCES supply_categories (id) ON DELETE RESTRICT,
    unit_of_measure VARCHAR(50)  NOT NULL,
    current_stock   INT         NOT NULL DEFAULT 0,
    min_stock_level INT         NOT NULL DEFAULT 0,
    max_stock_level INT         NOT NULL DEFAULT 0,
    status          VARCHAR(50)  NOT NULL DEFAULT 'active',
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ,

    CONSTRAINT ck_inv_stock_current CHECK (current_stock >= 0),
    CONSTRAINT ck_inv_stock_min CHECK (min_stock_level >= 0),
    CONSTRAINT ck_inv_stock_max CHECK (max_stock_level >= 0),
    CONSTRAINT ck_inv_stock_levels CHECK (min_stock_level <= max_stock_level),
    CONSTRAINT ck_inv_unit CHECK (unit_of_measure IN ('kg', 'g', 'l', 'ml', 'unit', 'box', 'pack')),
    CONSTRAINT ck_inv_status CHECK (status IN ('active', 'discontinued'))
);

COMMENT ON TABLE inventory_items IS 'Items de inventario disponibles en el zoologico';
COMMENT ON COLUMN inventory_items.current_stock IS 'Stock actual, no puede ser negativo';
COMMENT ON COLUMN inventory_items.min_stock_level IS 'Nivel minimo para alerta de reorden';
COMMENT ON COLUMN inventory_items.max_stock_level IS 'Nivel maximo de stock permitido';
COMMENT ON COLUMN inventory_items.unit_of_measure IS 'Unidad de medida: kg, g, l, ml, unit, box, pack';

CREATE INDEX idx_inv_supplier ON inventory_items (supplier_id);
CREATE INDEX idx_inv_category ON inventory_items (category_id);
CREATE INDEX idx_inv_stock ON inventory_items (current_stock);

CREATE TRIGGER trg_inventory_items_updated_at
    BEFORE UPDATE ON inventory_items
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 8.4 Inventory Movements
CREATE TABLE inventory_movements (
    id              UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    item_id         UUID        NOT NULL REFERENCES inventory_items (id) ON DELETE RESTRICT,
    registered_by   UUID        NOT NULL REFERENCES employees (id) ON DELETE RESTRICT,
    movement_type   VARCHAR(20)  NOT NULL,
    quantity        INT         NOT NULL,
    new_stock_level INT         NOT NULL,
    reason          TEXT,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),

    CONSTRAINT ck_inv_movement_type CHECK (movement_type IN ('in', 'out', 'adjustment', 'return')),
    CONSTRAINT ck_inv_movement_qty CHECK (quantity > 0),
    CONSTRAINT ck_inv_movement_stock CHECK (new_stock_level >= 0)
);

COMMENT ON TABLE inventory_movements IS 'Registro de movimientos de inventario para auditoria';
COMMENT ON COLUMN inventory_movements.movement_type IS 'Tipo: in, out, adjustment, return';
COMMENT ON COLUMN inventory_movements.quantity IS 'Cantidad movida, siempre positiva';
COMMENT ON COLUMN inventory_movements.new_stock_level IS 'Stock resultante tras el movimiento';
COMMENT ON COLUMN inventory_movements.registered_by IS 'Empleado que registro el movimiento';

CREATE INDEX idx_inv_movements_item ON inventory_movements (item_id);
CREATE INDEX idx_inv_movements_registered ON inventory_movements (registered_by);
CREATE INDEX idx_inv_movements_type ON inventory_movements (movement_type);
CREATE INDEX idx_inv_movements_created ON inventory_movements (created_at);
