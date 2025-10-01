// ============================================
// GraphRAG Query Templates for E-Commerce System
// ============================================

// ============================================
// 1. CRUD Matrix Analysis Queries
// ============================================

// Complete CRUD matrix showing all operations per table
MATCH (app:Application)-[:IMPLEMENTS]->(crud:CRUDOperation)-[:TARGETS]->(table:Table)
WHERE app.type = 'module'
RETURN table.name AS table_name,
       app.name AS application_module,
       collect(DISTINCT crud.operation_type) AS crud_operations,
       count(crud) AS total_operations,
       table.business_criticality AS table_criticality
ORDER BY table_criticality DESC, total_operations DESC;

// High-risk CRUD operations for testing priority
MATCH (app:Application)-[:IMPLEMENTS]->(crud:CRUDOperation)-[:TARGETS]->(table:Table)
WHERE crud.risk_score >= 3 OR crud.testing_priority = 'critical'
RETURN app.name AS application,
       crud.function_name AS operation,
       crud.operation_type AS type,
       table.name AS target_table,
       crud.risk_score AS risk,
       crud.testing_priority AS priority,
       crud.performance_category AS performance,
       CASE WHEN crud.cascade_impact IS NOT NULL THEN 'Yes' ELSE 'No' END AS has_cascade
ORDER BY crud.risk_score DESC, crud.testing_priority;

// ============================================
// 2. Impact Analysis for Integration Testing
// ============================================

// Identify operations with cascade effects
MATCH (crud:CRUDOperation)-[:TARGETS]->(t1:Table)-[:REFERENCES]->(t2:Table)
WHERE crud.operation_type IN ['UPDATE', 'DELETE']
RETURN crud.function_name AS operation,
       t1.name AS source_table,
       collect(DISTINCT t2.name) AS dependent_tables,
       size(collect(DISTINCT t2.name)) AS dependency_count,
       crud.risk_score AS risk_level
ORDER BY dependency_count DESC, risk_level DESC;

// Data flow analysis - operations that write and read from same tables
MATCH (writeOp:CRUDOperation)-[:TARGETS]->(table:Table)<-[:TARGETS]-(readOp:CRUDOperation)
WHERE writeOp.operation_type IN ['CREATE', 'UPDATE', 'DELETE'] 
  AND readOp.operation_type = 'READ'
  AND writeOp <> readOp
RETURN table.name AS shared_table,
       writeOp.function_name AS writer,
       collect(DISTINCT readOp.function_name) AS readers,
       table.business_criticality AS criticality,
       size(collect(DISTINCT readOp.function_name)) AS reader_count
ORDER BY reader_count DESC, criticality DESC;

// ============================================
// 3. Performance Risk Assessment
// ============================================

// Identify slow operations on high-volume tables
MATCH (crud:CRUDOperation)-[:TARGETS]->(table:Table)
WHERE crud.performance_category = 'slow' 
   OR table.estimated_records > 50000
RETURN crud.function_name AS operation,
       table.name AS target_table,
       table.estimated_records AS estimated_volume,
       crud.performance_category AS performance,
       crud.complexity AS complexity,
       CASE 
         WHEN crud.performance_category = 'slow' AND table.estimated_records > 100000 THEN 'CRITICAL'
         WHEN crud.performance_category = 'slow' OR table.estimated_records > 100000 THEN 'HIGH'
         ELSE 'MEDIUM'
       END AS performance_risk
ORDER BY table.estimated_records DESC, performance_risk DESC;

// Batch operations analysis
MATCH (crud:CRUDOperation)-[:TARGETS]->(table:Table)
WHERE crud.complexity = 'batch' OR crud.bulk_operation = true
RETURN crud.function_name AS operation,
       table.name AS target_table,
       crud.operation_type AS type,
       table.estimated_records AS table_size,
       crud.performance_category AS expected_performance,
       'Requires load testing' AS recommendation
ORDER BY table.estimated_records DESC;

// ============================================
// 4. Security and Business Critical Analysis  
// ============================================

// Security-sensitive operations requiring special testing
MATCH (app:Application)-[:IMPLEMENTS]->(crud:CRUDOperation)-[:TARGETS]->(table:Table)
WHERE crud.security_sensitive = true 
   OR crud.business_critical = true 
   OR table.business_criticality = 'high'
RETURN app.name AS module,
       crud.function_name AS operation,
       table.name AS target_table,
       CASE WHEN crud.security_sensitive = true THEN 'Yes' ELSE 'No' END AS security_sensitive,
       CASE WHEN crud.business_critical = true THEN 'Yes' ELSE 'No' END AS business_critical,
       table.business_criticality AS table_criticality,
       'Requires security testing' AS recommendation
ORDER BY table.business_criticality DESC, crud.function_name;

// ============================================
// 5. Test Coverage Analysis
// ============================================

// Applications with low test coverage on critical operations
MATCH (app:Application)-[impl:IMPLEMENTS]->(crud:CRUDOperation)-[:TARGETS]->(table:Table)
WHERE table.business_criticality IN ['high', 'medium']
RETURN app.name AS application,
       table.name AS critical_table,
       count(crud) AS total_operations,
       avg(CASE WHEN impl.test_coverage IS NOT NULL THEN impl.test_coverage ELSE 0.5 END) AS avg_coverage,
       collect(DISTINCT crud.operation_type) AS operation_types,
       CASE 
         WHEN avg(CASE WHEN impl.test_coverage IS NOT NULL THEN impl.test_coverage ELSE 0.5 END) < 0.6 THEN 'URGENT'
         WHEN avg(CASE WHEN impl.test_coverage IS NOT NULL THEN impl.test_coverage ELSE 0.5 END) < 0.8 THEN 'NEEDS_ATTENTION'
         ELSE 'ADEQUATE'
       END AS coverage_status
ORDER BY avg_coverage ASC, total_operations DESC;

// ============================================
// 6. Complex JOIN Operations Analysis
// ============================================

// Operations involving multiple tables (JOINs)
MATCH (crud:CRUDOperation)-[:TARGETS]->(table:Table)
WHERE crud.joins_tables IS NOT NULL OR crud.uses_aggregation = true
RETURN crud.function_name AS operation,
       table.name AS primary_table,
       crud.joins_tables AS joined_tables,
       CASE WHEN crud.uses_aggregation = true THEN 'Yes' ELSE 'No' END AS uses_aggregation,
       CASE WHEN crud.uses_like_query = true THEN 'Yes' ELSE 'No' END AS uses_like,
       crud.performance_category AS performance,
       'Requires integration testing' AS recommendation
ORDER BY size(crud.joins_tables) DESC;

// ============================================
// 7. Database Schema Relationship Mapping
// ============================================

// Complete foreign key relationship map
MATCH (t1:Table)-[r:REFERENCES]->(t2:Table)
RETURN t1.name AS source_table,
       t2.name AS target_table,
       r.constraint_name AS fk_constraint,
       r.cascade_type AS cascade_behavior,
       r.relationship_type AS relationship,
       t1.table_type AS source_type,
       t2.table_type AS target_type
ORDER BY t1.name;

// Self-referencing tables (hierarchical structures)
MATCH (table:Table)-[r:REFERENCES]->(table)
RETURN table.name AS table_name,
       r.constraint_name AS self_reference,
       r.business_rule AS purpose,
       'Requires recursive testing' AS recommendation;

// ============================================
// 8. Application Architecture Analysis
// ============================================

// Module dependency analysis based on shared table access
MATCH (app1:Application)-[:USES]->(table:Table)<-[:USES]-(app2:Application)
WHERE app1 <> app2 AND app1.type = 'module' AND app2.type = 'module'
RETURN app1.name AS module1,
       app2.name AS module2,
       collect(DISTINCT table.name) AS shared_tables,
       size(collect(DISTINCT table.name)) AS shared_count
ORDER BY shared_count DESC;

// Application usage patterns
MATCH (app:Application)-[uses:USES]->(table:Table)
WHERE app.type = 'module'
RETURN app.name AS module,
       table.name AS table_name,
       uses.frequency AS access_frequency,
       uses.access_pattern AS pattern,
       uses.dependency_level AS dependency,
       table.table_type AS table_type
ORDER BY app.name, uses.dependency_level DESC;

// ============================================
// 9. Test Scenario Generation Queries
// ============================================

// Generate end-to-end test scenarios
MATCH path = (app1:Application)-[:IMPLEMENTS]->(crud1:CRUDOperation)-[:TARGETS]->(table:Table)<-[:TARGETS]-(crud2:CRUDOperation)<-[:IMPLEMENTS]-(app2:Application)
WHERE crud1.operation_type IN ['CREATE', 'UPDATE'] 
  AND crud2.operation_type = 'READ'
  AND app1 <> app2
  AND app1.type = 'module' 
  AND app2.type = 'module'
RETURN app1.name AS producer_module,
       crud1.function_name AS write_operation,
       table.name AS shared_table,
       app2.name AS consumer_module,
       crud2.function_name AS read_operation,
       table.business_criticality AS importance,
       'End-to-end integration test required' AS test_type
ORDER BY table.business_criticality DESC;

// Error handling test scenarios
MATCH (crud:CRUDOperation)-[:TARGETS]->(table:Table)
WHERE crud.error_handling = true AND table.business_criticality = 'high'
RETURN crud.function_name AS operation,
       table.name AS target_table,
       crud.operation_type AS type,
       'Error boundary testing required' AS test_type,
       CASE 
         WHEN crud.operation_type = 'CREATE' THEN 'Test duplicate key, constraint violations'
         WHEN crud.operation_type = 'UPDATE' THEN 'Test concurrent updates, lock timeouts'
         WHEN crud.operation_type = 'DELETE' THEN 'Test referential integrity violations'
         WHEN crud.operation_type = 'READ' THEN 'Test not found, access denied scenarios'
         ELSE 'Generic error scenarios'
       END AS suggested_error_tests
ORDER BY table.business_criticality DESC;

// ============================================
// 10. Performance Testing Scenarios
// ============================================

// Load testing candidates
MATCH (crud:CRUDOperation)-[:TARGETS]->(table:Table)
WHERE table.estimated_records > 25000 
   OR crud.performance_category IN ['slow', 'normal']
RETURN crud.function_name AS operation,
       table.name AS target_table,
       table.estimated_records AS data_volume,
       crud.performance_category AS expected_performance,
       crud.complexity AS complexity,
       CASE 
         WHEN table.estimated_records > 100000 AND crud.performance_category = 'slow' THEN 'High-volume load test'
         WHEN table.estimated_records > 50000 THEN 'Medium-volume load test'
         ELSE 'Standard performance test'
       END AS test_type,
       CASE 
         WHEN crud.uses_like_query = true THEN 'Include text search patterns'
         WHEN crud.uses_aggregation = true THEN 'Include aggregation performance'
         WHEN crud.joins_tables IS NOT NULL THEN 'Include JOIN performance'
         ELSE 'Standard operation test'
       END AS special_considerations
ORDER BY table.estimated_records DESC, crud.performance_category DESC;

// ============================================
// 11. Data Quality and Integrity Tests
// ============================================

// Referential integrity test scenarios
MATCH (t1:Table)-[r:REFERENCES]->(t2:Table)
RETURN t1.name AS child_table,
       t2.name AS parent_table,
       r.cascade_type AS cascade_behavior,
       CASE r.cascade_type
         WHEN 'CASCADE' THEN 'Test cascade delete operations'
         WHEN 'RESTRICT' THEN 'Test referential integrity enforcement'
         WHEN 'SET_NULL' THEN 'Test null value handling'
         ELSE 'Test foreign key constraints'
       END AS integrity_test_type,
       'Data consistency verification required' AS requirement
ORDER BY t1.name;

// Data validation test requirements
MATCH (table:Table)-[:CONTAINS]->(column:Column)
WHERE column.has_unique_constraint = true OR column.is_primary_key = true
RETURN table.name AS table_name,
       collect(column.name) AS unique_columns,
       'Uniqueness constraint testing required' AS test_requirement
ORDER BY table.name;

// ============================================
// 12. Summary Statistics for Reporting
// ============================================

// Overall system complexity metrics
MATCH (app:Application), (table:Table), (crud:CRUDOperation), (column:Column)
RETURN count(DISTINCT CASE WHEN app.type = 'module' THEN app END) AS total_modules,
       count(DISTINCT table) AS total_tables,
       count(DISTINCT crud) AS total_crud_operations,
       count(DISTINCT column) AS total_columns,
       count(DISTINCT CASE WHEN table.business_criticality = 'high' THEN table END) AS high_criticality_tables,
       count(DISTINCT CASE WHEN crud.testing_priority = 'critical' THEN crud END) AS critical_operations;

// Testing effort estimation
MATCH (crud:CRUDOperation)
RETURN crud.testing_priority AS priority,
       count(crud) AS operation_count,
       CASE crud.testing_priority
         WHEN 'critical' THEN operation_count * 8
         WHEN 'high' THEN operation_count * 5  
         WHEN 'medium' THEN operation_count * 3
         ELSE operation_count * 1
       END AS estimated_test_hours
ORDER BY priority;