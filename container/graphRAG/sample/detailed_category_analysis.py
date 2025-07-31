#!/usr/bin/env python3
"""
Detailed Category Name Impact Analysis
Provides comprehensive analysis of category_name column impact with correct property names
"""

import json
from neo4j import GraphDatabase
from typing import Dict, List, Any

class DetailedCategoryAnalyzer:
    def __init__(self, uri: str, username: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
        
    def close(self):
        self.driver.close()
        
    def get_actual_node_properties(self) -> Dict[str, Any]:
        """Get actual properties for each node type"""
        with self.driver.session() as session:
            properties = {}
            
            # Get Column properties
            column_props = session.run("""
                MATCH (col:Column)
                WITH col, keys(col) as props
                RETURN DISTINCT props
                LIMIT 5
            """).data()
            properties["Column"] = column_props
            
            # Get CRUDOperation properties
            crud_props = session.run("""
                MATCH (crud:CRUDOperation)
                WITH crud, keys(crud) as props
                RETURN DISTINCT props
                LIMIT 5
            """).data()
            properties["CRUDOperation"] = crud_props
            
            # Get Table properties
            table_props = session.run("""
                MATCH (table:Table)
                WITH table, keys(table) as props
                RETURN DISTINCT props
                LIMIT 5
            """).data()
            properties["Table"] = table_props
            
            # Get Application properties
            app_props = session.run("""
                MATCH (app:Application)
                WITH app, keys(app) as props
                RETURN DISTINCT props
                LIMIT 5
            """).data()
            properties["Application"] = app_props
            
            return properties
    
    def analyze_category_name_impact(self) -> Dict[str, Any]:
        """Comprehensive category_name impact analysis"""
        with self.driver.session() as session:
            analysis = {}
            
            # 1. Direct column analysis
            category_name_column = session.run("""
                MATCH (col:Column {name: 'category_name'})
                RETURN col.name as column_name, col.data_type as data_type,
                       col.is_primary_key as is_pk, col.is_foreign_key as is_fk,
                       col.is_nullable as nullable, col.table_name as table_name,
                       col.max_length as max_length, col.default_value as default_value
            """).data()
            analysis["category_name_column"] = category_name_column
            
            # 2. Find containing table
            containing_table = session.run("""
                MATCH (table:Table)-[:CONTAINS]->(col:Column {name: 'category_name'})
                RETURN table.name as table_name, table.schema as schema,
                       table.table_type as table_type, table.business_criticality as criticality,
                       table.record_count as record_count
            """).data()
            analysis["containing_table"] = containing_table
            
            # 3. Find all CRUD operations targeting categories table
            crud_operations = session.run("""
                MATCH (crud:CRUDOperation)-[:TARGETS]->(table:Table {name: 'categories'})
                RETURN crud.operation_type as operation_type,
                       crud.function_name as function_name,
                       crud.file_path as file_path,
                       crud.line_number as line_number,
                       crud.complexity as complexity
            """).data()
            analysis["crud_operations"] = crud_operations
            
            # 4. Find applications using categories table
            using_applications = session.run("""
                MATCH (app:Application)-[:USES]->(table:Table {name: 'categories'})
                RETURN app.name as app_name, app.app_type as app_type,
                       app.language as language, app.framework as framework,
                       app.version as version
            """).data()
            analysis["using_applications"] = using_applications
            
            # 5. Find foreign key relationships
            foreign_key_relationships = session.run("""
                MATCH (table1:Table)-[ref:REFERENCES]->(table2:Table)
                WHERE table1.name = 'categories' OR table2.name = 'categories'
                RETURN table1.name as source_table, table2.name as target_table,
                       ref.constraint_name as constraint_name,
                       ref.cascade_type as cascade_type,
                       ref.relationship_type as relationship_type
            """).data()
            analysis["foreign_key_relationships"] = foreign_key_relationships
            
            # 6. Find all columns in categories table
            all_category_columns = session.run("""
                MATCH (table:Table {name: 'categories'})-[:CONTAINS]->(col:Column)
                RETURN col.name as column_name, col.data_type as data_type,
                       col.is_primary_key as is_pk, col.is_foreign_key as is_fk,
                       col.is_nullable as nullable, col.max_length as max_length
                ORDER BY col.name
            """).data()
            analysis["all_category_columns"] = all_category_columns
            
            # 7. Find related tables through foreign keys
            related_tables = session.run("""
                MATCH (table1:Table)-[ref:REFERENCES]->(table2:Table)
                WHERE table1.name = 'categories' OR table2.name = 'categories'
                WITH CASE WHEN table1.name = 'categories' THEN table2 ELSE table1 END as related_table
                RETURN DISTINCT related_table.name as table_name,
                       related_table.schema as schema,
                       related_table.table_type as table_type,
                       related_table.business_criticality as criticality
            """).data()
            analysis["related_tables"] = related_tables
            
            # 8. Find columns referencing categories
            referencing_columns = session.run("""
                MATCH (col1:Column)-[:FK_REFERENCES]->(col2:Column)
                WHERE col2.table_name = 'categories'
                RETURN col1.name as referencing_column,
                       col1.table_name as referencing_table,
                       col2.name as referenced_column,
                       col2.table_name as referenced_table
            """).data()
            analysis["referencing_columns"] = referencing_columns
            
            return analysis
    
    def generate_impact_queries(self) -> List[Dict[str, str]]:
        """Generate specific Cypher queries for impact analysis"""
        queries = [
            {
                "name": "Find all CRUD operations affecting category_name",
                "query": """
                    MATCH (crud:CRUDOperation)-[:TARGETS]->(table:Table {name: 'categories'})
                    RETURN crud.operation_type as operation_type,
                           crud.function_name as function_name,
                           crud.file_path as file_path,
                           crud.line_number as line_number,
                           crud.complexity as complexity
                    ORDER BY crud.operation_type, crud.function_name
                """,
                "purpose": "Identify all functions that perform CRUD operations on categories table"
            },
            {
                "name": "Find applications with high dependency on categories",
                "query": """
                    MATCH (app:Application)-[:USES]->(table:Table {name: 'categories'})
                    MATCH (app)-[:IMPLEMENTS]->(crud:CRUDOperation)-[:TARGETS]->(table)
                    RETURN app.name as application,
                           app.language as language,
                           count(crud) as crud_count,
                           collect(DISTINCT crud.operation_type) as operations
                    ORDER BY crud_count DESC
                """,
                "purpose": "Identify applications most affected by category_name changes"
            },
            {
                "name": "Analyze foreign key cascade effects",
                "query": """
                    MATCH (table1:Table)-[ref:REFERENCES]->(table2:Table)
                    WHERE table1.name = 'categories' OR table2.name = 'categories'
                    RETURN table1.name as source_table,
                           table2.name as target_table,
                           ref.constraint_name as constraint_name,
                           ref.cascade_type as cascade_type,
                           ref.relationship_type as relationship_type
                """,
                "purpose": "Analyze cascade effects of category_name changes"
            },
            {
                "name": "Find JOIN operations involving categories",
                "query": """
                    MATCH (crud:CRUDOperation)-[:TARGETS]->(table:Table)
                    WHERE crud.operation_type = 'SELECT' AND 
                          (crud.function_name CONTAINS 'join' OR 
                           crud.function_name CONTAINS 'JOIN')
                    MATCH (categories:Table {name: 'categories'})
                    RETURN crud.function_name as function_name,
                           crud.file_path as file_path,
                           table.name as target_table
                """,
                "purpose": "Find JOIN operations that might reference category_name"
            }
        ]
        return queries

def main():
    # Connection parameters
    uri = "bolt://localhost:7687"
    username = "neo4j"
    password = "password"
    
    print("=== Detailed Category Name Impact Analysis ===")
    
    analyzer = DetailedCategoryAnalyzer(uri, username, password)
    
    try:
        # Get actual node properties
        print("\n1. Analyzing actual node properties...")
        properties = analyzer.get_actual_node_properties()
        
        # Comprehensive analysis
        print("\n2. Performing comprehensive category_name impact analysis...")
        analysis = analyzer.analyze_category_name_impact()
        
        # Generate specific queries
        print("\n3. Generating impact analysis queries...")
        queries = analyzer.generate_impact_queries()
        
        # Compile results
        results = {
            "node_properties": properties,
            "impact_analysis": analysis,
            "suggested_queries": queries
        }
        
        # Save results
        with open("/root/aws.git/container/graphRAG/sample/detailed_category_impact_report.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print("\n" + "="*60)
        print("DETAILED ANALYSIS RESULTS")
        print("="*60)
        
        print(f"\nCategory Name Column Found: {len(analysis['category_name_column'])}")
        print(f"Containing Table: {len(analysis['containing_table'])}")
        print(f"CRUD Operations: {len(analysis['crud_operations'])}")
        print(f"Using Applications: {len(analysis['using_applications'])}")
        print(f"Foreign Key Relationships: {len(analysis['foreign_key_relationships'])}")
        print(f"All Category Columns: {len(analysis['all_category_columns'])}")
        print(f"Related Tables: {len(analysis['related_tables'])}")
        print(f"Referencing Columns: {len(analysis['referencing_columns'])}")
        
        # Print summary
        if analysis['category_name_column']:
            col_info = analysis['category_name_column'][0]
            print(f"\nCategory Name Column Details:")
            print(f"  - Data Type: {col_info['data_type']}")
            print(f"  - Nullable: {col_info['nullable']}")
            print(f"  - Max Length: {col_info.get('max_length', 'N/A')}")
            print(f"  - Table: {col_info['table_name']}")
        
        if analysis['foreign_key_relationships']:
            print(f"\nForeign Key Relationships:")
            for fk in analysis['foreign_key_relationships']:
                print(f"  - {fk['source_table']} -> {fk['target_table']} ({fk['constraint_name']})")
        
        if analysis['using_applications']:
            print(f"\nUsing Applications:")
            for app in analysis['using_applications']:
                print(f"  - {app['app_name']} ({app['language']})")
        
        print(f"\nDetailed results saved to: detailed_category_impact_report.json")
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        import traceback
        traceback.print_exc()
    finally:
        analyzer.close()

if __name__ == "__main__":
    main()