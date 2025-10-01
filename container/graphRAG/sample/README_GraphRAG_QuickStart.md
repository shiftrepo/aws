# E-Commerce GraphDB Quick Start Guide

## Overview
This directory contains a complete GraphDB representation of a C-based e-commerce application with Oracle database backend, designed for GraphRAG and testing scenario generation.

## Files Structure
```
sample/
├── ddl/                          # Original DDL files (8 tables)
├── src/                          # Original C source code (4 modules) 
├── create_graphdb.cypher         # Complete graph creation script
├── execute_graphdb.py           # Python execution utility
├── graphrag_queries.cypher      # 50+ analysis query templates
├── graphdb_analysis_results.md  # Detailed analysis results
├── final_summary_report.md      # Executive summary
└── README_GraphRAG_QuickStart.md # This file
```

## Quick Start

### 1. Verify Neo4j Connection
```bash
curl -u neo4j:password http://localhost:7474/
# Should return Neo4j version info
```

### 2. Create the Graph Database
```bash
cd /root/aws.git/container/graphRAG/sample
python3 execute_graphdb.py
```

### 3. Verify Graph Creation
```bash
curl -u neo4j:password -H "Content-Type: application/json" -X POST \
http://localhost:7474/db/neo4j/tx/commit -d \
'{"statements":[{"statement":"MATCH (n) RETURN labels(n)[0] as type, count(n) as count ORDER BY count DESC"}]}'
```

Expected output:
- CRUDOperation: 41 nodes
- Column: 27 nodes  
- Table: 8 nodes
- Application: 5 nodes

## Key GraphRAG Queries

### 1. CRUD Matrix Analysis
```cypher
MATCH (app:Application)-[:IMPLEMENTS]->(crud:CRUDOperation)-[:TARGETS]->(table:Table)
WHERE app.type = 'module'
RETURN table.name, app.name, collect(DISTINCT crud.operation_type) AS operations
ORDER BY table.name;
```

### 2. High-Risk Operations for Testing
```cypher
MATCH (crud:CRUDOperation)-[:TARGETS]->(table:Table)
WHERE crud.risk_score >= 3 OR crud.testing_priority = 'critical'
RETURN crud.function_name, table.name, crud.operation_type, crud.risk_score
ORDER BY crud.risk_score DESC;
```

### 3. Cascade Impact Analysis
```cypher
MATCH (crud:CRUDOperation)-[:TARGETS]->(t1:Table)-[:REFERENCES]->(t2:Table)
WHERE crud.operation_type = 'DELETE'
RETURN crud.function_name, t1.name, collect(t2.name) AS affected_tables
ORDER BY size(collect(t2.name)) DESC;
```

### 4. Performance Testing Candidates
```cypher
MATCH (crud:CRUDOperation)-[:TARGETS]->(table:Table)
WHERE table.estimated_records > 25000 OR crud.performance_category = 'slow'
RETURN crud.function_name, table.name, table.estimated_records, 
       crud.performance_category
ORDER BY table.estimated_records DESC;
```

### 5. Integration Test Scenarios
```cypher
MATCH (app1:Application)-[:IMPLEMENTS]->(crud1:CRUDOperation)-[:TARGETS]->(table:Table)
      <-[:TARGETS]-(crud2:CRUDOperation)<-[:IMPLEMENTS]-(app2:Application)
WHERE crud1.operation_type IN ['CREATE', 'UPDATE'] 
  AND crud2.operation_type = 'READ' 
  AND app1 <> app2
RETURN app1.name AS producer, crud1.function_name AS write_op,
       table.name, app2.name AS consumer, crud2.function_name AS read_op;
```

## Graph Schema

### Node Types
- **Application**: C modules and main system
- **Table**: Database tables with metadata
- **Column**: Table columns with constraints
- **CRUDOperation**: Individual C functions

### Relationship Types  
- **IMPLEMENTS**: Application implements CRUD operation
- **TARGETS**: CRUD operation targets table
- **CONTAINS**: Table contains column
- **REFERENCES**: Foreign key relationships
- **USES**: Application usage patterns

### Key Properties
- **risk_score**: 1-5 scale for testing priority
- **performance_category**: fast/normal/slow
- **business_criticality**: low/medium/high
- **testing_priority**: low/medium/high/critical

## Analysis Results Summary

### Database Schema
- 8 tables covering complete e-commerce domain
- 11 foreign key relationships
- 3 cascade delete patterns  
- 1 hierarchical structure (categories)

### Application Analysis
- 4 C modules analyzed
- 41 CRUD operations identified
- 20 READ operations (48% of total)
- 8 high-risk operations flagged

### Testing Priorities
- **Critical**: 8 operations (authentication, orders, cascade deletes)
- **High**: 12 operations (batch operations, complex JOINs)  
- **Medium**: 21 operations (standard CRUD)

## Using for Test Generation

### 1. Load Testing Identification
```cypher
MATCH (crud:CRUDOperation)-[:TARGETS]->(table:Table)
WHERE table.estimated_records > 50000
RETURN crud.function_name, table.estimated_records;
```

### 2. Security Testing Scenarios  
```cypher
MATCH (crud:CRUDOperation)
WHERE crud.security_sensitive = true
RETURN crud.function_name, 'Requires penetration testing';
```

### 3. Data Integrity Tests
```cypher
MATCH (t1:Table)-[r:REFERENCES]->(t2:Table)
RETURN t1.name, t2.name, r.cascade_type,
       'Test referential integrity' AS test_type;
```

## Browser Visualization

Access Neo4j Browser at: http://localhost:7474

Use these queries for visualization:
```cypher
// Overall graph structure
MATCH (n)-[r]->(m) RETURN n,r,m LIMIT 50;

// Application module relationships  
MATCH (app:Application)-[r]-(n) 
WHERE app.type = 'module' 
RETURN app,r,n;

// Table relationships
MATCH (t1:Table)-[r:REFERENCES]->(t2:Table) 
RETURN t1,r,t2;
```

## Extending the Analysis

### Adding New Modules
1. Analyze new C source files
2. Add Application and CRUDOperation nodes
3. Create IMPLEMENTS and TARGETS relationships
4. Update risk scores and testing priorities

### Adding More Metadata
1. Extend Column properties with business rules
2. Add performance metrics to CRUDOperation nodes
3. Include test coverage data in IMPLEMENTS relationships
4. Add deployment information to Application nodes

## Support Files

- **graphrag_queries.cypher**: 12 categories of analysis queries
- **final_summary_report.md**: Complete analysis with statistics
- **execute_graphdb.py**: Automated graph creation utility

This GraphRAG implementation provides a comprehensive foundation for test scenario generation, impact analysis, and system understanding for the e-commerce application.