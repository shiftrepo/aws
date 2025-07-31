#!/usr/bin/env python3
"""
Category Name Impact Analysis Tool
Analyzes the impact of changes to the 'category_name' column in Neo4j GraphDB
"""

import json
from neo4j import GraphDatabase
from typing import Dict, List, Any
import sys

class CategoryNameImpactAnalyzer:
    def __init__(self, uri: str, username: str, password: str):
        """Initialize Neo4j connection"""
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
        
    def close(self):
        """Close Neo4j connection"""
        self.driver.close()
        
    def test_connection(self) -> bool:
        """Test Neo4j connection"""
        try:
            with self.driver.session() as session:
                result = session.run("RETURN 1 as test")
                return result.single()["test"] == 1
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
            
    def get_graph_schema(self) -> Dict[str, Any]:
        """Get current graph schema information"""
        with self.driver.session() as session:
            # Get all node labels
            node_labels = session.run("CALL db.labels() YIELD label RETURN label").data()
            
            # Get all relationship types
            relationship_types = session.run("CALL db.relationshipTypes() YIELD relationshipType RETURN relationshipType").data()
            
            # Get constraints
            constraints = session.run("SHOW CONSTRAINTS YIELD name, type, labelsOrTypes, properties RETURN name, type, labelsOrTypes, properties").data()
            
            # Get indexes
            indexes = session.run("SHOW INDEXES YIELD name, type, labelsOrTypes, properties RETURN name, type, labelsOrTypes, properties").data()
            
            return {
                "node_labels": [item["label"] for item in node_labels],
                "relationship_types": [item["relationshipType"] for item in relationship_types],
                "constraints": constraints,
                "indexes": indexes
            }
    
    def find_category_name_references(self) -> Dict[str, List[Any]]:
        """Find all references to category_name in the graph"""
        with self.driver.session() as session:
            results = {}
            
            # Search for Column nodes with name 'category_name'
            category_columns = session.run("""
                MATCH (col:Column)
                WHERE col.name CONTAINS 'category_name' OR col.name CONTAINS 'category'
                RETURN col.name as column_name, col.data_type as data_type, 
                       col.is_primary_key as is_pk, col.is_foreign_key as is_fk,
                       col.is_nullable as nullable, col.table_name as table_name,
                       col.business_meaning as business_meaning
            """).data()
            results["category_columns"] = category_columns
            
            # Search for Table nodes related to categories
            category_tables = session.run("""
                MATCH (table:Table)
                WHERE table.name CONTAINS 'category' OR table.name CONTAINS 'categories'
                RETURN table.name as table_name, table.schema as schema,
                       table.type as table_type, table.business_criticality as criticality
            """).data()
            results["category_tables"] = category_tables
            
            # Search for CRUD operations that might access category_name
            crud_operations = session.run("""
                MATCH (crud:CRUDOperation)
                WHERE crud.method_name CONTAINS 'category' OR 
                      crud.file_path CONTAINS 'category' OR
                      crud.method_name CONTAINS 'Category'
                RETURN crud.operation_type as operation_type,
                       crud.method_name as method_name,
                       crud.file_path as file_path,
                       crud.line_number as line_number,
                       crud.complexity as complexity,
                       crud.performance_category as performance,
                       crud.application_name as app_name,
                       crud.target_table as target_table
            """).data()
            results["crud_operations"] = crud_operations
            
            return results
    
    def analyze_column_dependencies(self, column_name: str = "category_name") -> Dict[str, List[Any]]:
        """Analyze dependencies for a specific column"""
        with self.driver.session() as session:
            results = {}
            
            # Find tables containing the column
            tables_with_column = session.run("""
                MATCH (table:Table)-[:CONTAINS]->(col:Column)
                WHERE col.name = $column_name
                RETURN table.name as table_name, table.schema as schema,
                       table.business_criticality as criticality,
                       col.data_type as data_type, col.is_primary_key as is_pk,
                       col.is_foreign_key as is_fk, col.is_nullable as nullable
            """, column_name=column_name).data()
            results["tables_with_column"] = tables_with_column
            
            # Find CRUD operations targeting these tables
            crud_targeting_tables = session.run("""
                MATCH (table:Table)-[:CONTAINS]->(col:Column)
                WHERE col.name = $column_name
                WITH table
                MATCH (crud:CRUDOperation)-[:TARGETS]->(table)
                RETURN crud.operation_type as operation_type,
                       crud.method_name as method_name,
                       crud.file_path as file_path,
                       crud.application_name as app_name,
                       table.name as target_table,
                       crud.performance_category as performance,
                       crud.complexity as complexity
            """, column_name=column_name).data()
            results["crud_targeting_tables"] = crud_targeting_tables
            
            # Find applications using these tables
            apps_using_tables = session.run("""
                MATCH (table:Table)-[:CONTAINS]->(col:Column)
                WHERE col.name = $column_name
                WITH table
                MATCH (app:Application)-[:USES]->(table)
                RETURN app.name as app_name, app.type as app_type,
                       app.language as language, app.framework as framework,
                       table.name as table_name
            """, column_name=column_name).data()
            results["apps_using_tables"] = apps_using_tables
            
            # Find foreign key relationships
            fk_relationships = session.run("""
                MATCH (table1:Table)-[:CONTAINS]->(col1:Column)
                WHERE col1.name = $column_name
                WITH table1
                MATCH (table1)-[ref:REFERENCES]->(table2:Table)
                RETURN table1.name as source_table, table2.name as target_table,
                       ref.constraint_name as constraint_name,
                       ref.cascade_type as cascade_type,
                       ref.relationship_type as relationship_type
                UNION
                MATCH (table1:Table)-[:CONTAINS]->(col1:Column)
                WHERE col1.name = $column_name
                WITH table1
                MATCH (table2:Table)-[ref:REFERENCES]->(table1)
                RETURN table2.name as source_table, table1.name as target_table,
                       ref.constraint_name as constraint_name,
                       ref.cascade_type as cascade_type,
                       ref.relationship_type as relationship_type
            """, column_name=column_name).data()
            results["fk_relationships"] = fk_relationships
            
            return results
    
    def assess_impact_severity(self, analysis_results: Dict[str, Any]) -> Dict[str, str]:
        """Assess impact severity based on analysis results"""
        severity_assessment = {}
        
        # Assess based on number of affected applications
        app_count = len(analysis_results.get("apps_using_tables", []))
        if app_count > 5:
            severity_assessment["application_impact"] = "HIGH"
        elif app_count > 2:
            severity_assessment["application_impact"] = "MEDIUM"
        else:
            severity_assessment["application_impact"] = "LOW"
            
        # Assess based on CRUD operations
        crud_count = len(analysis_results.get("crud_targeting_tables", []))
        if crud_count > 10:
            severity_assessment["crud_impact"] = "HIGH"
        elif crud_count > 5:
            severity_assessment["crud_impact"] = "MEDIUM"
        else:
            severity_assessment["crud_impact"] = "LOW"
            
        # Assess based on foreign key relationships
        fk_count = len(analysis_results.get("fk_relationships", []))
        if fk_count > 3:
            severity_assessment["relationship_impact"] = "HIGH"
        elif fk_count > 1:
            severity_assessment["relationship_impact"] = "MEDIUM"
        else:
            severity_assessment["relationship_impact"] = "LOW"
            
        # Overall severity
        high_count = sum(1 for v in severity_assessment.values() if v == "HIGH")
        medium_count = sum(1 for v in severity_assessment.values() if v == "MEDIUM")
        
        if high_count > 0:
            severity_assessment["overall"] = "HIGH"
        elif medium_count > 0:
            severity_assessment["overall"] = "MEDIUM"
        else:
            severity_assessment["overall"] = "LOW"
            
        return severity_assessment
    
    def generate_test_scenarios(self, analysis_results: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate test scenarios based on analysis results"""
        test_scenarios = []
        
        # Test scenarios for each CRUD operation
        for crud in analysis_results.get("crud_targeting_tables", []):
            test_scenarios.append({
                "scenario_type": "CRUD Operation Test",
                "description": f"{crud['operation_type']} operation in {crud['method_name']}",
                "test_focus": f"Verify {crud['operation_type']} functionality after column change",
                "file_path": crud["file_path"],
                "risk_level": crud.get("complexity", "MEDIUM")
            })
            
        # Test scenarios for foreign key relationships
        for fk in analysis_results.get("fk_relationships", []):
            test_scenarios.append({
                "scenario_type": "Foreign Key Constraint Test",
                "description": f"Relationship between {fk['source_table']} and {fk['target_table']}",
                "test_focus": "Verify referential integrity after column change",
                "constraint_name": fk["constraint_name"],
                "risk_level": "HIGH"
            })
            
        # Test scenarios for applications
        for app in analysis_results.get("apps_using_tables", []):
            test_scenarios.append({
                "scenario_type": "Application Integration Test",
                "description": f"Application {app['app_name']} accessing {app['table_name']}",
                "test_focus": "Verify application functionality after column change",
                "app_type": app["app_type"],
                "risk_level": "HIGH"
            })
            
        return test_scenarios

def main():
    # Connection parameters
    uri = "bolt://localhost:7687"
    username = "neo4j"
    password = "password"
    
    print("=== Category Name Impact Analysis ===")
    print("Connecting to Neo4j...")
    
    analyzer = CategoryNameImpactAnalyzer(uri, username, password)
    
    # Test connection
    if not analyzer.test_connection():
        print("Failed to connect to Neo4j database")
        sys.exit(1)
    
    print("Connected successfully!")
    
    try:
        # Get graph schema
        print("\n1. Analyzing graph schema...")
        schema = analyzer.get_graph_schema()
        print(f"Node labels: {schema['node_labels']}")
        print(f"Relationship types: {schema['relationship_types']}")
        
        # Find category_name references
        print("\n2. Finding category_name references...")
        references = analyzer.find_category_name_references()
        
        # Analyze column dependencies
        print("\n3. Analyzing column dependencies...")
        dependencies = analyzer.analyze_column_dependencies("category_name")
        
        # Assess impact severity
        print("\n4. Assessing impact severity...")
        severity = analyzer.assess_impact_severity(dependencies)
        
        # Generate test scenarios
        print("\n5. Generating test scenarios...")
        test_scenarios = analyzer.generate_test_scenarios(dependencies)
        
        # Print results
        print("\n" + "="*50)
        print("ANALYSIS RESULTS")
        print("="*50)
        
        print(f"\nSeverity Assessment: {severity}")
        print(f"\nColumn References Found: {len(references.get('category_columns', []))}")
        print(f"Related Tables: {len(references.get('category_tables', []))}")
        print(f"CRUD Operations: {len(references.get('crud_operations', []))}")
        print(f"Test Scenarios Generated: {len(test_scenarios)}")
        
        # Save detailed results to JSON
        results = {
            "schema": schema,
            "references": references,
            "dependencies": dependencies,
            "severity": severity,
            "test_scenarios": test_scenarios
        }
        
        with open("/root/aws.git/container/graphRAG/sample/category_name_impact_report.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print("\nDetailed results saved to: category_name_impact_report.json")
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        import traceback
        traceback.print_exc()
    finally:
        analyzer.close()

if __name__ == "__main__":
    main()