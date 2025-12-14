-- Initialize HealthGuard AI Database Schema

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Hospitals table
CREATE TABLE IF NOT EXISTS hospitals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    hospital_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    level VARCHAR(50),
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(50),
    zip_code VARCHAR(20),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    phone VARCHAR(20),
    emergency_phone VARCHAR(20),
    total_beds INTEGER DEFAULT 0,
    capabilities JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Bed availability table
CREATE TABLE IF NOT EXISTS bed_availability (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    hospital_id UUID REFERENCES hospitals(id),
    bed_type VARCHAR(50) NOT NULL,
    total_beds INTEGER NOT NULL,
    available_beds INTEGER NOT NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Ambulances table
CREATE TABLE IF NOT EXISTS ambulances (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ambulance_id VARCHAR(50) UNIQUE NOT NULL,
    unit_number VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'available',
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    equipment JSONB,
    crew JSONB,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Emergency cases table
CREATE TABLE IF NOT EXISTS emergency_cases (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    case_id VARCHAR(50) UNIQUE NOT NULL,
    case_type VARCHAR(50) NOT NULL,
    patient_age INTEGER,
    patient_sex VARCHAR(10),
    priority VARCHAR(20),
    status VARCHAR(50),
    ambulance_id UUID REFERENCES ambulances(id),
    destination_hospital_id UUID REFERENCES hospitals(id),
    vital_signs JSONB,
    incident_details JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Audit logs table
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type VARCHAR(100) NOT NULL,
    agent_id VARCHAR(100),
    user_id VARCHAR(100),
    action TEXT NOT NULL,
    details JSONB,
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_hospitals_hospital_id ON hospitals(hospital_id);
CREATE INDEX IF NOT EXISTS idx_bed_availability_hospital_id ON bed_availability(hospital_id);
CREATE INDEX IF NOT EXISTS idx_ambulances_status ON ambulances(status);
CREATE INDEX IF NOT EXISTS idx_emergency_cases_status ON emergency_cases(status);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at);

-- Insert sample data
INSERT INTO hospitals (hospital_id, name, level, city, state, latitude, longitude, total_beds, capabilities)
VALUES 
    ('HOSP-001', 'Metro General Hospital', 'Level 1 Trauma Center', 'Metro City', 'MC', 40.7128, -74.0060, 450, 
     '["trauma_surgery", "neurosurgery", "cardiac_cath_lab", "stroke_center", "burn_unit", "nicu", "picu"]'::jsonb),
    ('HOSP-002', 'City Medical Center', 'Level 1 Trauma Center', 'Metro City', 'MC', 40.7589, -73.9851, 380,
     '["trauma_surgery", "cardiac_cath_lab", "stroke_center", "nicu"]'::jsonb)
ON CONFLICT (hospital_id) DO NOTHING;

-- Insert sample bed availability
INSERT INTO bed_availability (hospital_id, bed_type, total_beds, available_beds)
SELECT h.id, 'icu', 50, 5 FROM hospitals h WHERE h.hospital_id = 'HOSP-001'
UNION ALL
SELECT h.id, 'medical_surgical', 200, 15 FROM hospitals h WHERE h.hospital_id = 'HOSP-001'
UNION ALL
SELECT h.id, 'telemetry', 80, 4 FROM hospitals h WHERE h.hospital_id = 'HOSP-001'
UNION ALL
SELECT h.id, 'icu', 40, 8 FROM hospitals h WHERE h.hospital_id = 'HOSP-002'
UNION ALL
SELECT h.id, 'medical_surgical', 180, 22 FROM hospitals h WHERE h.hospital_id = 'HOSP-002'
ON CONFLICT DO NOTHING;

-- Insert sample ambulances
INSERT INTO ambulances (ambulance_id, unit_number, status, latitude, longitude, crew)
VALUES 
    ('AMB-001', 'Medic 15', 'available', 40.7589, -73.9851, '["Paramedic Johnson", "EMT Smith"]'::jsonb),
    ('AMB-002', 'Medic 23', 'available', 40.7128, -74.0060, '["Paramedic Davis", "EMT Wilson"]'::jsonb)
ON CONFLICT (ambulance_id) DO NOTHING;

COMMENT ON TABLE hospitals IS 'Hospital facility information';
COMMENT ON TABLE bed_availability IS 'Real-time bed availability by type';
COMMENT ON TABLE ambulances IS 'Ambulance fleet tracking';
COMMENT ON TABLE emergency_cases IS 'Active emergency cases';
COMMENT ON TABLE audit_logs IS 'System audit trail';
