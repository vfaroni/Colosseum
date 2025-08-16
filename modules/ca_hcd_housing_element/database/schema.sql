-- 🏛️ CALIFORNIA HCD HOUSING ELEMENT INTELLIGENCE DATABASE SCHEMA
-- Roman Engineering Standards: Built to Last 2000+ Years
-- Built by Structured Consultants LLC for Colosseum Platform

-- Enable PostGIS for spatial analysis
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- =============================================================================
-- CORE JURISDICTIONS TABLE - All 539 California Cities and Counties
-- =============================================================================

CREATE TABLE jurisdictions (
    jurisdiction_id SERIAL PRIMARY KEY,
    jurisdiction_name VARCHAR(255) NOT NULL,
    county_name VARCHAR(100) NOT NULL,
    jurisdiction_type VARCHAR(20) CHECK (jurisdiction_type IN ('City', 'County', 'Special District')),
    
    -- Geographic Information
    geometry GEOMETRY(POLYGON, 4326),
    centroid GEOMETRY(POINT, 4326),
    
    -- RHNA Cycle Information (6th Cycle 2021-2029)
    rhna_region VARCHAR(100),
    scag_jurisdiction BOOLEAN DEFAULT FALSE,
    
    -- Compliance Status
    compliance_status VARCHAR(50) DEFAULT 'Unknown' 
        CHECK (compliance_status IN ('Compliant', 'Non-Compliant', 'Under Review', 'Unknown')),
    streamlining_required BOOLEAN DEFAULT FALSE,
    streamlining_percentage INTEGER CHECK (streamlining_percentage IN (10, 50)),
    builders_remedy_active BOOLEAN DEFAULT FALSE,
    
    -- Pro-Housing Designation
    pro_housing_designation BOOLEAN DEFAULT FALSE,
    pro_housing_score INTEGER CHECK (pro_housing_score >= 0 AND pro_housing_score <= 30),
    pro_housing_date DATE,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_source VARCHAR(100) DEFAULT 'CA HCD'
);

-- =============================================================================
-- RHNA ALLOCATIONS TABLE - Regional Housing Needs by Income Category
-- =============================================================================

CREATE TABLE rhna_allocations (
    allocation_id SERIAL PRIMARY KEY,
    jurisdiction_id INTEGER REFERENCES jurisdictions(jurisdiction_id),
    rhna_cycle VARCHAR(20) DEFAULT '6th Cycle (2021-2029)',
    
    -- Income Category Allocations
    very_low_income_units INTEGER DEFAULT 0,     -- 0-50% AMI
    low_income_units INTEGER DEFAULT 0,          -- 50-80% AMI  
    moderate_income_units INTEGER DEFAULT 0,     -- 80-120% AMI
    above_moderate_units INTEGER DEFAULT 0,      -- >120% AMI
    total_units INTEGER GENERATED ALWAYS AS 
        (very_low_income_units + low_income_units + moderate_income_units + above_moderate_units) STORED,
    
    -- Extremely Low Income Subset (tracked separately)
    extremely_low_income_units INTEGER DEFAULT 0, -- 0-30% AMI (subset of very low)
    
    -- Allocation Metadata
    allocation_start_date DATE DEFAULT '2021-01-01',
    allocation_end_date DATE DEFAULT '2029-12-31',
    allocating_agency VARCHAR(100),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- BUILDING PERMITS TABLE - HCD Table A2 Data (Critical RHNA Compliance Metric)
-- =============================================================================

CREATE TABLE building_permits (
    permit_id SERIAL PRIMARY KEY,
    jurisdiction_id INTEGER REFERENCES jurisdictions(jurisdiction_id),
    
    -- Property Information
    prior_apn VARCHAR(50),
    apn VARCHAR(50),
    street_address TEXT,
    project_name VARCHAR(255),
    jurisdiction_tracking_id VARCHAR(100),
    
    -- Unit Details
    unit_category VARCHAR(20) CHECK (unit_category IN ('SFD', 'ADU', '2-4', '5+', 'MH', 'Other')),
    tenure VARCHAR(20) CHECK (tenure IN ('Owner', 'Renter', 'Mixed')),
    
    -- Income Category Units (Deed Restricted)
    vlow_income_dr INTEGER DEFAULT 0,
    vlow_income_ndr INTEGER DEFAULT 0,
    low_income_dr INTEGER DEFAULT 0,
    low_income_ndr INTEGER DEFAULT 0,
    mod_income_dr INTEGER DEFAULT 0,
    mod_income_ndr INTEGER DEFAULT 0,
    above_mod_income INTEGER DEFAULT 0,
    
    -- Building Permit Information
    bp_vlow_income_dr INTEGER DEFAULT 0,
    bp_vlow_income_ndr INTEGER DEFAULT 0,
    bp_low_income_dr INTEGER DEFAULT 0,
    bp_low_income_ndr INTEGER DEFAULT 0,
    bp_mod_income_dr INTEGER DEFAULT 0,
    bp_mod_income_ndr INTEGER DEFAULT 0,
    bp_above_mod_income INTEGER DEFAULT 0,
    bp_issue_date DATE,
    
    -- Certificate of Occupancy Information
    co_vlow_income_dr INTEGER DEFAULT 0,
    co_vlow_income_ndr INTEGER DEFAULT 0,
    co_low_income_dr INTEGER DEFAULT 0,
    co_low_income_ndr INTEGER DEFAULT 0,
    co_mod_income_dr INTEGER DEFAULT 0,
    co_mod_income_ndr INTEGER DEFAULT 0,
    co_above_mod_income INTEGER DEFAULT 0,
    co_issue_date DATE,
    
    -- Additional Details
    extremely_low_income_units INTEGER DEFAULT 0,
    sb35_approval BOOLEAN DEFAULT FALSE,
    density_bonus_total INTEGER DEFAULT 0,
    notes TEXT,
    
    -- Spatial Data
    location GEOMETRY(POINT, 4326),
    
    -- Metadata
    reporting_year INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- HOUSING APPLICATIONS TABLE - HCD Table A Data (Project Pipeline)
-- =============================================================================

CREATE TABLE housing_applications (
    application_id SERIAL PRIMARY KEY,
    jurisdiction_id INTEGER REFERENCES jurisdictions(jurisdiction_id),
    
    -- Property Information
    prior_apn VARCHAR(50),
    apn VARCHAR(50),
    street_address TEXT,
    project_name VARCHAR(255),
    jurisdiction_tracking_id VARCHAR(100),
    
    -- Application Details
    unit_category VARCHAR(20) CHECK (unit_category IN ('SFD', 'ADU', '2-4', '5+', 'MH', 'Other')),
    tenure VARCHAR(20) CHECK (tenure IN ('Owner', 'Renter', 'Mixed')),
    app_submit_date DATE,
    
    -- Income Category Proposed Units
    vlow_income_dr INTEGER DEFAULT 0,
    vlow_income_ndr INTEGER DEFAULT 0,
    low_income_dr INTEGER DEFAULT 0,
    low_income_ndr INTEGER DEFAULT 0,
    mod_income_dr INTEGER DEFAULT 0,
    mod_income_ndr INTEGER DEFAULT 0,
    above_mod_income INTEGER DEFAULT 0,
    
    total_proposed_units INTEGER,
    total_approved_units INTEGER,
    total_disapproved_units INTEGER,
    
    -- Application Status
    application_status VARCHAR(50) CHECK (application_status IN ('Pending', 'Approved', 'Disapproved', 'Withdrawn')),
    project_type VARCHAR(100),
    sb35_submission BOOLEAN DEFAULT FALSE,
    density_bonus_received BOOLEAN DEFAULT FALSE,
    density_bonus_approved BOOLEAN DEFAULT FALSE,
    
    notes TEXT,
    
    -- Spatial Data
    location GEOMETRY(POINT, 4326),
    
    -- Metadata
    reporting_year INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- COMPLIANCE STATUS TABLE - Real-time Enforcement Tracking
-- =============================================================================

CREATE TABLE compliance_status (
    status_id SERIAL PRIMARY KEY,
    jurisdiction_id INTEGER REFERENCES jurisdictions(jurisdiction_id),
    
    -- RHNA Progress Tracking
    rhna_cycle VARCHAR(20) DEFAULT '6th Cycle (2021-2029)',
    progress_very_low DECIMAL(5,2) DEFAULT 0.00,
    progress_low DECIMAL(5,2) DEFAULT 0.00,
    progress_moderate DECIMAL(5,2) DEFAULT 0.00,
    progress_above_moderate DECIMAL(5,2) DEFAULT 0.00,
    overall_progress DECIMAL(5,2) DEFAULT 0.00,
    
    -- Enforcement Actions
    letter_of_inquiry_date DATE,
    technical_assistance_date DATE,
    corrective_action_letter_date DATE,
    notice_of_violation_date DATE,
    
    -- Consequences
    state_funding_suspended BOOLEAN DEFAULT FALSE,
    builders_remedy_exposed BOOLEAN DEFAULT FALSE,
    fines_assessed DECIMAL(10,2) DEFAULT 0.00,
    
    -- SB 35 Streamlining Requirements
    sb35_10_percent_required BOOLEAN DEFAULT FALSE,
    sb35_50_percent_required BOOLEAN DEFAULT FALSE,
    ministerial_approval_required BOOLEAN DEFAULT FALSE,
    
    -- Status Date
    status_effective_date DATE DEFAULT CURRENT_DATE,
    next_review_date DATE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- PRO-HOUSING METRICS TABLE - 30-Point Scoring System
-- =============================================================================

CREATE TABLE pro_housing_metrics (
    metrics_id SERIAL PRIMARY KEY,
    jurisdiction_id INTEGER REFERENCES jurisdictions(jurisdiction_id),
    
    -- Category 1: Zoning Practices (Max 8 points)
    rezoning_rhna_150_percent INTEGER DEFAULT 0 CHECK (rezoning_rhna_150_percent <= 3),
    by_right_approval INTEGER DEFAULT 0 CHECK (by_right_approval <= 3),
    streamlined_approval INTEGER DEFAULT 0 CHECK (streamlined_approval <= 2),
    
    -- Category 2: Accelerated Production (Max 8 points)
    permitting_under_4_months INTEGER DEFAULT 0 CHECK (permitting_under_4_months <= 2),
    accelerated_timeline INTEGER DEFAULT 0 CHECK (accelerated_timeline <= 3),
    development_standards INTEGER DEFAULT 0 CHECK (development_standards <= 3),
    
    -- Category 3: Reduced Construction Costs (Max 8 points)
    fee_waivers INTEGER DEFAULT 0 CHECK (fee_waivers <= 3),
    standardized_processes INTEGER DEFAULT 0 CHECK (standardized_processes <= 3),
    reduced_parking INTEGER DEFAULT 0 CHECK (reduced_parking <= 2),
    
    -- Category 4: Financial Subsidies (Max 6 points)
    housing_trust_fund INTEGER DEFAULT 0 CHECK (housing_trust_fund <= 3),
    direct_subsidies INTEGER DEFAULT 0 CHECK (direct_subsidies <= 3),
    
    -- Calculated Total
    total_score INTEGER GENERATED ALWAYS AS 
        (rezoning_rhna_150_percent + by_right_approval + streamlined_approval + 
         permitting_under_4_months + accelerated_timeline + development_standards +
         fee_waivers + standardized_processes + reduced_parking +
         housing_trust_fund + direct_subsidies) STORED,
    
    -- Metrics Date
    assessment_date DATE DEFAULT CURRENT_DATE,
    designation_earned BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- TIME SERIES ANALYSIS TABLE - RHNA Progress Over Time
-- =============================================================================

CREATE TABLE rhna_progress_history (
    history_id SERIAL PRIMARY KEY,
    jurisdiction_id INTEGER REFERENCES jurisdictions(jurisdiction_id),
    
    -- Reporting Period
    reporting_year INTEGER NOT NULL,
    reporting_quarter INTEGER CHECK (reporting_quarter IN (1, 2, 3, 4)),
    report_date DATE NOT NULL,
    
    -- Cumulative Progress by Income Category
    cumulative_very_low INTEGER DEFAULT 0,
    cumulative_low INTEGER DEFAULT 0,
    cumulative_moderate INTEGER DEFAULT 0,
    cumulative_above_moderate INTEGER DEFAULT 0,
    cumulative_total INTEGER DEFAULT 0,
    
    -- Progress Percentages
    progress_very_low_pct DECIMAL(5,2) DEFAULT 0.00,
    progress_low_pct DECIMAL(5,2) DEFAULT 0.00,
    progress_moderate_pct DECIMAL(5,2) DEFAULT 0.00,
    progress_above_moderate_pct DECIMAL(5,2) DEFAULT 0.00,
    overall_progress_pct DECIMAL(5,2) DEFAULT 0.00,
    
    -- Performance Metrics
    units_added_quarter INTEGER DEFAULT 0,
    permits_issued_quarter INTEGER DEFAULT 0,
    cos_issued_quarter INTEGER DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- INDEXES FOR PERFORMANCE OPTIMIZATION
-- =============================================================================

-- Jurisdictions indexes
CREATE INDEX idx_jurisdictions_name ON jurisdictions(jurisdiction_name);
CREATE INDEX idx_jurisdictions_county ON jurisdictions(county_name);
CREATE INDEX idx_jurisdictions_compliance ON jurisdictions(compliance_status);
CREATE INDEX idx_jurisdictions_pro_housing ON jurisdictions(pro_housing_designation);
CREATE INDEX idx_jurisdictions_geometry ON jurisdictions USING GIST(geometry);
CREATE INDEX idx_jurisdictions_centroid ON jurisdictions USING GIST(centroid);

-- Building permits indexes
CREATE INDEX idx_building_permits_jurisdiction ON building_permits(jurisdiction_id);
CREATE INDEX idx_building_permits_year ON building_permits(reporting_year);
CREATE INDEX idx_building_permits_bp_date ON building_permits(bp_issue_date);
CREATE INDEX idx_building_permits_co_date ON building_permits(co_issue_date);
CREATE INDEX idx_building_permits_location ON building_permits USING GIST(location);

-- Housing applications indexes
CREATE INDEX idx_housing_applications_jurisdiction ON housing_applications(jurisdiction_id);
CREATE INDEX idx_housing_applications_year ON housing_applications(reporting_year);
CREATE INDEX idx_housing_applications_status ON housing_applications(application_status);
CREATE INDEX idx_housing_applications_submit_date ON housing_applications(app_submit_date);

-- Compliance status indexes
CREATE INDEX idx_compliance_status_jurisdiction ON compliance_status(jurisdiction_id);
CREATE INDEX idx_compliance_status_effective_date ON compliance_status(status_effective_date);
CREATE INDEX idx_compliance_status_builders_remedy ON compliance_status(builders_remedy_exposed);

-- Time series indexes
CREATE INDEX idx_rhna_progress_jurisdiction_year ON rhna_progress_history(jurisdiction_id, reporting_year);
CREATE INDEX idx_rhna_progress_report_date ON rhna_progress_history(report_date);

-- =============================================================================
-- TRIGGERS FOR AUTOMATIC UPDATES
-- =============================================================================

-- Update timestamps automatically
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_jurisdictions_updated_at
    BEFORE UPDATE ON jurisdictions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_building_permits_updated_at
    BEFORE UPDATE ON building_permits
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_housing_applications_updated_at
    BEFORE UPDATE ON housing_applications
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_compliance_status_updated_at
    BEFORE UPDATE ON compliance_status
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_pro_housing_metrics_updated_at
    BEFORE UPDATE ON pro_housing_metrics
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- =============================================================================
-- VIEWS FOR COMMON QUERIES
-- =============================================================================

-- Strategic Overview: Compliance Status Summary
CREATE VIEW v_strategic_overview AS
SELECT 
    j.jurisdiction_name,
    j.county_name,
    j.compliance_status,
    j.streamlining_required,
    j.streamlining_percentage,
    j.builders_remedy_active,
    j.pro_housing_designation,
    ra.total_units as rhna_total,
    cs.overall_progress,
    cs.state_funding_suspended,
    CASE 
        WHEN cs.overall_progress >= 100 THEN 'On Track'
        WHEN cs.overall_progress >= 50 THEN 'Behind Schedule'
        ELSE 'Critical'
    END as performance_category
FROM jurisdictions j
LEFT JOIN rhna_allocations ra ON j.jurisdiction_id = ra.jurisdiction_id
LEFT JOIN compliance_status cs ON j.jurisdiction_id = cs.jurisdiction_id
ORDER BY j.jurisdiction_name;

-- Tactical Intelligence: City Performance Comparison
CREATE VIEW v_city_performance AS
SELECT 
    j.jurisdiction_name,
    j.county_name,
    ra.total_units as rhna_allocation,
    COUNT(bp.permit_id) as total_permits,
    SUM(bp.bp_vlow_income_dr + bp.bp_vlow_income_ndr + 
        bp.bp_low_income_dr + bp.bp_low_income_ndr + 
        bp.bp_mod_income_dr + bp.bp_mod_income_ndr + 
        bp.bp_above_mod_income) as total_units_permitted,
    ROUND((SUM(bp.bp_vlow_income_dr + bp.bp_vlow_income_ndr + 
              bp.bp_low_income_dr + bp.bp_low_income_ndr + 
              bp.bp_mod_income_dr + bp.bp_mod_income_ndr + 
              bp.bp_above_mod_income)::DECIMAL / ra.total_units) * 100, 2) as progress_percentage,
    phm.total_score as pro_housing_score
FROM jurisdictions j
LEFT JOIN rhna_allocations ra ON j.jurisdiction_id = ra.jurisdiction_id
LEFT JOIN building_permits bp ON j.jurisdiction_id = bp.jurisdiction_id
LEFT JOIN pro_housing_metrics phm ON j.jurisdiction_id = phm.jurisdiction_id
GROUP BY j.jurisdiction_id, j.jurisdiction_name, j.county_name, ra.total_units, phm.total_score
ORDER BY progress_percentage DESC NULLS LAST;

-- GRANT PERMISSIONS (adjust as needed for your environment)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ca_hcd_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO ca_hcd_user;

-- =============================================================================
-- SCHEMA COMPLETION
-- =============================================================================

-- Create a summary table for monitoring
CREATE TABLE schema_info (
    schema_version VARCHAR(20) DEFAULT '1.0.0',
    creation_date DATE DEFAULT CURRENT_DATE,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT DEFAULT 'California HCD Housing Element Intelligence Database - Roman Engineering Standards'
);

INSERT INTO schema_info (description) VALUES 
('🏛️ California HCD Housing Element Intelligence Database - Built to Last 2000+ Years');

-- Add comments for documentation
COMMENT ON DATABASE ca_hcd_housing_element IS 'California HCD Housing Element Intelligence System - Colosseum Platform';
COMMENT ON TABLE jurisdictions IS 'All 539 California jurisdictions with compliance and performance data';
COMMENT ON TABLE rhna_allocations IS 'Regional Housing Needs Allocation targets by income category';
COMMENT ON TABLE building_permits IS 'HCD Table A2 - Building permits data (critical RHNA compliance metric)';
COMMENT ON TABLE housing_applications IS 'HCD Table A - Housing application pipeline data';
COMMENT ON TABLE compliance_status IS 'Real-time compliance and enforcement status tracking';
COMMENT ON TABLE pro_housing_metrics IS '30-point Pro-Housing Designation scoring system';
COMMENT ON TABLE rhna_progress_history IS 'Time-series RHNA progress tracking for trend analysis';