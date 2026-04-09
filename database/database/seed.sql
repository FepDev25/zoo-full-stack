-- ZOO MANAGEMENT SYSTEM - SEED DATA

-- 1. Departments
INSERT INTO departments (id, name, description, status) VALUES
    ('a1b2c3d4-1111-4aaa-bbbb-000000000001', 'Veterinary',       'Animal healthcare and medical services',       'active'),
    ('a1b2c3d4-1111-4aaa-bbbb-000000000002', 'Maintenance',      'Facility and enclosure maintenance',          'active'),
    ('a1b2c3d4-1111-4aaa-bbbb-000000000003', 'Nutrition',        'Animal diet planning and feeding',            'active'),
    ('a1b2c3d4-1111-4aaa-bbbb-000000000004', 'Education',        'Visitor education and conservation programs', 'active')
ON CONFLICT (name) DO NOTHING;

-- 2. Roles
INSERT INTO roles (id, name, description) VALUES
    ('b1b2c3d4-2222-4ccc-dddd-000000000001', 'Veterinarian',             'Animal healthcare professional'),
    ('b1b2c3d4-2222-4ccc-dddd-000000000002', 'Keeper',                   'Animal caretaker and handler'),
    ('b1b2c3d4-2222-4ccc-dddd-000000000003', 'Nutritionist',             'Animal diet specialist'),
    ('b1b2c3d4-2222-4ccc-dddd-000000000004', 'Maintenance Technician',   'Facility maintenance specialist'),
    ('b1b2c3d4-2222-4ccc-dddd-000000000005', 'Guide',                    'Visitor tour guide')
ON CONFLICT (name) DO NOTHING;

-- 3. Employees
INSERT INTO employees (id, full_name, email, phone, hire_date, birth_date, department_id, status) VALUES
    ('c1b2c3d4-3333-4eee-ffff-000000000001', 'Dr. Maria Rodriguez', 'm.rodriguez@zoo.example.com', '+1234567890', '2020-03-15', '1985-06-22', 'a1b2c3d4-1111-4aaa-bbbb-000000000001', 'active'),
    ('c1b2c3d4-3333-4eee-ffff-000000000002', 'John Smith',          'j.smith@zoo.example.com',     '+1234567891', '2021-07-10', '1990-11-05', 'a1b2c3d4-1111-4aaa-bbbb-000000000002', 'active'),
    ('c1b2c3d4-3333-4eee-ffff-000000000003', 'Anna Chen',           'a.chen@zoo.example.com',      '+1234567892', '2022-01-20', '1992-03-14', 'a1b2c3d4-1111-4aaa-bbbb-000000000003', 'active')
ON CONFLICT (email) DO NOTHING;

-- 4. Employee Roles (assign roles to employees)
INSERT INTO employee_roles (employee_id, role_id) VALUES
    ('c1b2c3d4-3333-4eee-ffff-000000000001', 'b1b2c3d4-2222-4ccc-dddd-000000000001'),
    ('c1b2c3d4-3333-4eee-ffff-000000000002', 'b1b2c3d4-2222-4ccc-dddd-000000000004'),
    ('c1b2c3d4-3333-4eee-ffff-000000000003', 'b1b2c3d4-2222-4ccc-dddd-000000000003')
ON CONFLICT (employee_id, role_id) DO NOTHING;

-- 5. Species
INSERT INTO species (id, common_name, scientific_name, conservation_status, diet_type, additional_info) VALUES
    ('d1b2c3d4-4444-4aaa-bbbb-000000000001', 'African Lion',     'Panthera leo',                'vulnerable',          'carnivore',   '{"family":"Felidae","habitat":"Savanna, grassland","lifespan_years":15,"weight_kg":{"male":190,"female":130}}'),
    ('d1b2c3d4-4444-4aaa-bbbb-000000000002', 'Asian Elephant',   'Elephas maximus',             'endangered',          'herbivore',   '{"family":"Elephantidae","habitat":"Forest, grassland","lifespan_years":60,"weight_kg":{"male":5000,"female":3000}}'),
    ('d1b2c3d4-4444-4aaa-bbbb-000000000003', 'Bald Eagle',       'Haliaeetus leucocephalus',    'least_concern',       'carnivore',   '{"family":"Accipitridae","habitat":"Near water bodies","wingspan_cm":180}')
ON CONFLICT (common_name) DO NOTHING;

-- 6. Zones
INSERT INTO zones (id, name, description, surface_area_m2, climate_type) VALUES
    ('e1b2c3d4-5555-4ccc-dddd-000000000001', 'African Savanna',  'Open area simulating African grasslands', 5000.0, 'tropical'),
    ('e1b2c3d4-5555-4ccc-dddd-000000000002', 'Asian Forest',     'Wooded area with Asian flora',            3000.0, 'subtropical'),
    ('e1b2c3d4-5555-4ccc-dddd-000000000003', 'Raptor Aviary',    'Large enclosure for birds of prey',        800.0,  'temperate')
ON CONFLICT (name) DO NOTHING;

-- 7. Enclosures
INSERT INTO enclosures (id, name, zone_id, type, capacity, area_m2, features, status) VALUES
    ('f1b2c3d4-6666-4eee-ffff-000000000001', 'Lion Pride Exhibit',  'e1b2c3d4-5555-4ccc-dddd-000000000001', 'open',     8, 1200.0, 'Rock formations, watering hole, observation deck', 'active'),
    ('f1b2c3d4-6666-4eee-ffff-000000000002', 'Elephant Sanctuary', 'e1b2c3d4-5555-4ccc-dddd-000000000002', 'open',     6, 2000.0, 'Mud wallow, feeding stations, shelter',             'active'),
    ('f1b2c3d4-6666-4eee-ffff-000000000003', 'Eagle Aviary',       'e1b2c3d4-5555-4ccc-dddd-000000000003', 'aviary',   4,  400.0, 'High perches, flight space, nest platform',          'active');

-- 8. Animals
INSERT INTO animals (id, name, species_id, enclosure_id, gender, birth_date, arrival_date, origin, status) VALUES
    ('a1b2c3d4-7777-4aaa-bbbb-000000000001', 'Simba',    'd1b2c3d4-4444-4aaa-bbbb-000000000001', 'f1b2c3d4-6666-4eee-ffff-000000000001', 'M',        '2021-07-15', '2022-01-10', 'Born in zoo',       'active'),
    ('a1b2c3d4-7777-4aaa-bbbb-000000000002', 'Nala',     'd1b2c3d4-4444-4aaa-bbbb-000000000001', 'f1b2c3d4-6666-4eee-ffff-000000000001', 'F',        '2022-03-20', '2022-06-01', 'Born in zoo',       'active'),
    ('a1b2c3d4-7777-4aaa-bbbb-000000000003', 'Kandula',  'd1b2c3d4-4444-4aaa-bbbb-000000000002', 'f1b2c3d4-6666-4eee-ffff-000000000002', 'M',        '2019-11-08', '2021-04-15', 'Rescue from sanctuary', 'active'),
    ('a1b2c3d4-7777-4aaa-bbbb-000000000004', 'Liberty',  'd1b2c3d4-4444-4aaa-bbbb-000000000003', 'f1b2c3d4-6666-4eee-ffff-000000000003', 'F',        '2020-05-01', '2022-09-12', 'Wildlife rehab center',   'active');

-- 9. Ticket Types
INSERT INTO ticket_types (id, name, price, max_daily_sales, description, status) VALUES
    ('a1b2c3d4-8888-4ccc-dddd-000000000001', 'General',        25.00, 500, 'Standard adult admission',  'active'),
    ('a1b2c3d4-8888-4ccc-dddd-000000000002', 'Child',          12.50, 300, 'Children under 12',        'active'),
    ('a1b2c3d4-8888-4ccc-dddd-000000000003', 'Senior',         18.00, 200, 'Adults over 65',           'active'),
    ('a1b2c3d4-8888-4ccc-dddd-000000000004', 'VIP Experience', 75.00,  50, 'Guided tour + feeding',    'active')
ON CONFLICT (name) DO NOTHING;

-- 10. Vaccines
INSERT INTO vaccines (id, name, description, validity_period) VALUES
    ('a1b2c3d4-9999-4eee-ffff-000000000001', 'Rabies Vaccine',      'Standard rabies vaccination',       INTERVAL '1 year'),
    ('a1b2c3d4-9999-4eee-ffff-000000000002', 'Tetanus Vaccine',     'Tetanus prophylaxis',               INTERVAL '5 years'),
    ('a1b2c3d4-9999-4eee-ffff-000000000003', 'West Nile Vaccine',   'West Nile virus prevention',        INTERVAL '6 months')
ON CONFLICT (name) DO NOTHING;

-- 11. Suppliers
INSERT INTO suppliers (id, name, address, contact_name, email, phone, website, status) VALUES
    ('a1b2c3d4-aaaa-4aaa-bbbb-000000000001', 'ZooFeed Co.',       '123 Animal Rd, Feed City',     'Carlos Mendez',  'orders@zoofeed.com',       '+5551112233', 'https://zoofeed.example.com',  'active'),
    ('a1b2c3d4-aaaa-4aaa-bbbb-000000000002', 'MedVet Supply',     '456 Health Ave, Med Town',     'Dr. Patel',      'sales@medvet.com',          '+5554445566', 'https://medvet.example.com',    'active'),
    ('a1b2c3d4-aaaa-4aaa-bbbb-000000000003', 'BuildAll Materials', '789 Construct Blvd',           'Mike Johnson',   'info@buildall.com',         '+5557778899', NULL,                              'active')
ON CONFLICT (name) DO NOTHING;

-- 12. Supply Categories
INSERT INTO supply_categories (id, name, description) VALUES
    ('a1b2c3d4-bbbb-4ccc-dddd-000000000001', 'Animal Feed',       'Food and dietary supplements for animals'),
    ('a1b2c3d4-bbbb-4ccc-dddd-000000000002', 'Medical Supplies',  'Medicines, vaccines and veterinary equipment'),
    ('a1b2c3d4-bbbb-4ccc-dddd-000000000003', 'Construction',      'Building and maintenance materials'),
    ('a1b2c3d4-bbbb-4ccc-dddd-000000000004', 'Cleaning',          'Hygiene and sanitation products')
ON CONFLICT (name) DO NOTHING;

-- 13. Sponsors
INSERT INTO sponsors (id, name, contact_name, email, phone, sponsor_type, notes) VALUES
    ('a1b2c3d4-cccc-4eee-ffff-000000000001', 'EcoTech Corp',      'Laura Fernandez', 'laura@ecotech.com',   '+5559990011', 'corporate',     'Annual donation for conservation programs'),
    ('a1b2c3d4-cccc-4eee-ffff-000000000002', 'Wildlife Foundation', 'James Park',      'james@wlf.org',      NULL,           'institutional', 'Grant for endangered species program')
ON CONFLICT DO NOTHING;

-- 14. Shows
INSERT INTO shows (id, name, description, start_time, duration_minutes, enclosure_id, max_capacity, days_of_week, status) VALUES
    ('a1b2c3d4-dddd-4aaa-bbbb-000000000001', 'Lion Feeding Show',    'Watch the pride during feeding time',     TIME '12:00', 30, 'f1b2c3d4-6666-4eee-ffff-000000000001', 200, '["Mon","Wed","Fri","Sat","Sun"]', 'active'),
    ('a1b2c3d4-dddd-4aaa-bbbb-000000000002', 'Eagle Flight Demo',    'Birds of prey in free flight display',    TIME '11:00', 20, 'f1b2c3d4-6666-4eee-ffff-000000000003', 150, '["Tue","Thu","Sat","Sun"]',       'active'),
    ('a1b2c3d4-dddd-4aaa-bbbb-000000000003', 'Elephant Bath Time',   'Educational demonstration with elephants', TIME '15:00', 45, 'f1b2c3d4-6666-4eee-ffff-000000000002', 250, '["Mon","Tue","Wed","Thu","Fri"]', 'active');