// Neo4j Graph Database Initialization Script
// This script sets up constraints and relationships for the OSINT platform
// Run manually with: cypher-shell -u neo4j -p password < init_graph.cql

// ============================================================================
// CONSTRAINTS AND INDEXES
// ============================================================================

// Create uniqueness constraints for core entities
CREATE CONSTRAINT person_id_unique IF NOT EXISTS FOR (p:Person) REQUIRE p.id IS UNIQUE;
CREATE CONSTRAINT phone_number_unique IF NOT EXISTS FOR (ph:Phone) REQUIRE ph.number IS UNIQUE;
CREATE CONSTRAINT email_address_unique IF NOT EXISTS FOR (e:Email) REQUIRE e.address IS UNIQUE;
CREATE CONSTRAINT username_handle_unique IF NOT EXISTS FOR (u:Username) REQUIRE u.handle IS UNIQUE;
CREATE CONSTRAINT domain_name_unique IF NOT EXISTS FOR (d:Domain) REQUIRE d.name IS UNIQUE;
CREATE CONSTRAINT ip_address_unique IF NOT EXISTS FOR (ip:IP) REQUIRE ip.address IS UNIQUE;
CREATE CONSTRAINT image_hash_unique IF NOT EXISTS FOR (img:Image) REQUIRE img.hash IS UNIQUE;

// Create indexes for performance optimization
CREATE INDEX person_name_index IF NOT EXISTS FOR (p:Person) ON (p.name);
CREATE INDEX person_first_seen_index IF NOT EXISTS FOR (p:Person) ON (p.first_seen);
CREATE INDEX person_last_seen_index IF NOT EXISTS FOR (p:Person) ON (p.last_seen);
CREATE INDEX phone_country_index IF NOT EXISTS FOR (ph:Phone) ON (ph.country);
CREATE INDEX email_domain_index IF NOT EXISTS FOR (e:Email) ON (e.domain);
CREATE INDEX username_platform_index IF NOT EXISTS FOR (u:Username) ON (u.platform);
CREATE INDEX domain_tld_index IF NOT EXISTS FOR (d:Domain) ON (d.tld);
CREATE INDEX ip_country_index IF NOT EXISTS FOR (ip:IP) ON (ip.country);
CREATE INDEX image_source_index IF NOT EXISTS FOR (img:Image) ON (img.source);

// Composite indexes for common queries
CREATE INDEX person_name_confidence IF NOT EXISTS FOR (p:Person) ON (p.name, p.confidence);
CREATE INDEX phone_country_number IF NOT EXISTS FOR (ph:Phone) ON (ph.country, ph.number);
CREATE INDEX email_domain_address IF NOT EXISTS FOR (e:Email) ON (e.domain, e.address);

// ============================================================================
// SCHEMA SETUP WITH SAMPLE STRUCTURE
// ============================================================================

// Create sample schema nodes (these will serve as templates)
MERGE (schema:Schema {name: 'OSINT_SCHEMA', version: '2.0', created: datetime()})

// Core entity types with their expected properties
MERGE (person_schema:EntityType {
    name: 'Person',
    description: 'Individual person entity',
    required_properties: ['id', 'name'],
    optional_properties: ['age', 'location', 'bio', 'confidence', 'first_seen', 'last_seen', 'valid_from', 'valid_to'],
    created: datetime()
})

MERGE (phone_schema:EntityType {
    name: 'Phone',
    description: 'Phone number entity',
    required_properties: ['number'],
    optional_properties: ['country', 'carrier', 'type', 'confidence', 'first_seen', 'last_seen', 'valid_from', 'valid_to'],
    created: datetime()
})

MERGE (email_schema:EntityType {
    name: 'Email',
    description: 'Email address entity',
    required_properties: ['address'],
    optional_properties: ['domain', 'provider', 'confidence', 'first_seen', 'last_seen', 'valid_from', 'valid_to'],
    created: datetime()
})

MERGE (username_schema:EntityType {
    name: 'Username',
    description: 'Social media or platform username',
    required_properties: ['handle'],
    optional_properties: ['platform', 'display_name', 'followers', 'confidence', 'first_seen', 'last_seen', 'valid_from', 'valid_to'],
    created: datetime()
})

MERGE (domain_schema:EntityType {
    name: 'Domain',
    description: 'Internet domain entity',
    required_properties: ['name'],
    optional_properties: ['tld', 'registrar', 'creation_date', 'confidence', 'first_seen', 'last_seen', 'valid_from', 'valid_to'],
    created: datetime()
})

MERGE (ip_schema:EntityType {
    name: 'IP',
    description: 'IP address entity',
    required_properties: ['address'],
    optional_properties: ['country', 'isp', 'type', 'confidence', 'first_seen', 'last_seen', 'valid_from', 'valid_to'],
    created: datetime()
})

MERGE (image_schema:EntityType {
    name: 'Image',
    description: 'Image or media entity',
    required_properties: ['hash'],
    optional_properties: ['url', 'source', 'description', 'confidence', 'first_seen', 'last_seen', 'valid_from', 'valid_to'],
    created: datetime()
})

// ============================================================================
// RELATIONSHIP TYPES
// ============================================================================

// Define relationship types with their properties
MERGE (owns_rel:RelationshipType {
    name: 'OWNS',
    description: 'Entity owns another entity (e.g., Person owns Phone)',
    allowed_properties: ['confidence', 'source', 'first_seen', 'last_seen', 'valid_from', 'valid_to'],
    created: datetime()
})

MERGE (uses_rel:RelationshipType {
    name: 'USES',
    description: 'Entity uses another entity (e.g., Person uses Username)',
    allowed_properties: ['confidence', 'source', 'first_seen', 'last_seen', 'valid_from', 'valid_to'],
    created: datetime()
})

MERGE (associated_rel:RelationshipType {
    name: 'ASSOCIATED_WITH',
    description: 'General association between entities',
    allowed_properties: ['confidence', 'source', 'first_seen', 'last_seen', 'valid_from', 'valid_to'],
    created: datetime()
})

MERGE (registered_rel:RelationshipType {
    name: 'REGISTERED_TO',
    description: 'Domain or service registered to entity',
    allowed_properties: ['confidence', 'source', 'first_seen', 'last_seen', 'valid_from', 'valid_to'],
    created: datetime()
})

MERGE (resolves_rel:RelationshipType {
    name: 'RESOLVES_TO',
    description: 'Domain resolves to IP address',
    allowed_properties: ['confidence', 'source', 'first_seen', 'last_seen', 'valid_from', 'valid_to'],
    created: datetime()
})

MERGE (posted_rel:RelationshipType {
    name: 'POSTED',
    description: 'Entity posted content or image',
    allowed_properties: ['confidence', 'source', 'first_seen', 'last_seen', 'valid_from', 'valid_to'],
    created: datetime()
})

// ============================================================================
// CONNECT SCHEMA ELEMENTS
// ============================================================================

// Connect schema to entity types
MERGE (schema)-[:DEFINES]->(person_schema)
MERGE (schema)-[:DEFINES]->(phone_schema)
MERGE (schema)-[:DEFINES]->(email_schema)
MERGE (schema)-[:DEFINES]->(username_schema)
MERGE (schema)-[:DEFINES]->(domain_schema)
MERGE (schema)-[:DEFINES]->(ip_schema)
MERGE (schema)-[:DEFINES]->(image_schema)

// Connect schema to relationship types
MERGE (schema)-[:DEFINES]->(owns_rel)
MERGE (schema)-[:DEFINES]->(uses_rel)
MERGE (schema)-[:DEFINES]->(associated_rel)
MERGE (schema)-[:DEFINES]->(registered_rel)
MERGE (schema)-[:DEFINES]->(resolves_rel)
MERGE (schema)-[:DEFINES]->(posted_rel)

// ============================================================================
// CONFIGURATION AND METADATA
// ============================================================================

// Create configuration node for system settings
MERGE (config:Configuration {
    confidence_threshold: 0.7,
    auto_merge_threshold: 0.9,
    temporal_window_days: 365,
    max_relationship_depth: 5,
    enable_entity_resolution: true,
    enable_temporal_analysis: true,
    created: datetime(),
    updated: datetime()
})

// Create metadata about the database initialization
MERGE (init_log:InitializationLog {
    script_version: '2.0',
    initialized_at: datetime(),
    constraints_created: 7,
    indexes_created: 12,
    schema_entities: 7,
    relationship_types: 6,
    status: 'completed'
})

// ============================================================================
// VERIFICATION QUERIES (commented out - uncomment to run verification)
// ============================================================================

// Verify constraints were created
// SHOW CONSTRAINTS;

// Verify indexes were created  
// SHOW INDEXES;

// Count schema elements
// MATCH (s:Schema)-[:DEFINES]->(e) RETURN s.name, count(e) as defined_elements;

// Show configuration
// MATCH (c:Configuration) RETURN c;

// Show initialization log
// MATCH (l:InitializationLog) RETURN l;

// ============================================================================
// SAMPLE DATA CREATION (optional - uncomment to create sample data)
// ============================================================================

/*
// Create sample entities for testing
MERGE (p1:Person {
    id: 'sample_001',
    name: 'John Doe',
    confidence: 0.85,
    first_seen: datetime(),
    last_seen: datetime()
})

MERGE (ph1:Phone {
    number: '+1234567890',
    country: 'US',
    confidence: 0.90,
    first_seen: datetime(),
    last_seen: datetime()
})

MERGE (e1:Email {
    address: 'john.doe@example.com',
    domain: 'example.com',
    confidence: 0.88,
    first_seen: datetime(),
    last_seen: datetime()
})

// Create sample relationships
MERGE (p1)-[:OWNS {confidence: 0.85, source: 'sample_data', first_seen: datetime()}]->(ph1)
MERGE (p1)-[:OWNS {confidence: 0.88, source: 'sample_data', first_seen: datetime()}]->(e1)
*/

// ============================================================================
// COMPLETION MESSAGE
// ============================================================================

// Log successful completion
MERGE (completion:CompletionStatus {
    message: 'Neo4j OSINT schema initialization completed successfully',
    timestamp: datetime(),
    script_version: '2.0'
})

// Return summary information
RETURN 'Neo4j OSINT Database Initialization Complete' as status,
       datetime() as completed_at,
       '2.0' as schema_version;
