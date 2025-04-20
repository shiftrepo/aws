#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MCP Patent Analysis Server 

This server provides specialized tools for patent examiners to analyze applicant data.
It exposes functionality from the ApplicantAnalyzer class through MCP tools.
"""

import json
from datetime import datetime
from .applicant_analyzer import ApplicantAnalyzer

# Schema definitions for MCP tools
SCHEMAS = {
    "get_applicant_summary": {
        "type": "object",
        "properties": {
            "applicant_name": {
                "type": "string",
                "description": "Name of the applicant to analyze"
            }
        },
        "required": ["applicant_name"]
    },
    "generate_visual_report": {
        "type": "object",
        "properties": {
            "applicant_name": {
                "type": "string",
                "description": "Name of the applicant to generate a visual report for"
            }
        },
        "required": ["applicant_name"]
    },
    "analyze_assessment_ratios": {
        "type": "object",
        "properties": {
            "applicant_name": {
                "type": "string",
                "description": "Name of the applicant to analyze assessment ratios for"
            }
        },
        "required": ["applicant_name"]
    },
    "analyze_technical_fields": {
        "type": "object",
        "properties": {
            "applicant_name": {
                "type": "string",
                "description": "Name of the applicant to analyze technical fields for"
            }
        },
        "required": ["applicant_name"]
    },
    "compare_with_competitors": {
        "type": "object",
        "properties": {
            "applicant_name": {
                "type": "string",
                "description": "Name of the applicant to compare"
            },
            "num_competitors": {
                "type": "integer",
                "description": "Number of competitors to compare with",
                "minimum": 1,
                "maximum": 5,
                "default": 3
            }
        },
        "required": ["applicant_name"]
    }
}

class PatentApplicantServer:
    """MCP Server for patent applicant analysis"""
    
    def __init__(self):
        """Initialize the server"""
        self.analyzer = ApplicantAnalyzer()
    
    def get_tools(self):
        """Return list of available tools"""
        return [
            {
                "name": "get_applicant_summary",
                "description": "Get a comprehensive summary of a patent applicant including assessment statistics, application history, technical distribution, and examiner insights.",
                "schema": SCHEMAS["get_applicant_summary"]
            },
            {
                "name": "generate_visual_report",
                "description": "Generate a visual report for a specified applicant with charts and markdown format.",
                "schema": SCHEMAS["generate_visual_report"]
            },
            {
                "name": "analyze_assessment_ratios",
                "description": "Analyze the assessment ratios (granted, rejected, etc.) for a specific applicant, including visual representation.",
                "schema": SCHEMAS["analyze_assessment_ratios"]
            },
            {
                "name": "analyze_technical_fields",
                "description": "Analyze the technical fields distribution for a specific applicant, including visualization and domain analysis.",
                "schema": SCHEMAS["analyze_technical_fields"]
            },
            {
                "name": "compare_with_competitors",
                "description": "Compare a patent applicant with their top competitors in terms of assessment statistics and technical distribution.",
                "schema": SCHEMAS["compare_with_competitors"]
            }
        ]
    
    def get_resources(self):
        """Return list of available resources"""
        return [
            {
                "uri": "current_date",
                "description": "Current date for reference in patent analysis"
            },
            {
                "uri": "patent_status_descriptions",
                "description": "Descriptions of patent statuses (granted, rejected, etc.)"
            },
            {
                "uri": "ipc_code_reference",
                "description": "Reference for International Patent Classification (IPC) codes"
            },
            {
                "uri": "top_applicants",
                "description": "List of top patent applicants in the database"
            }
        ]
    
    def execute_tool(self, tool_name, arguments):
        """Execute a specific tool with the given arguments"""
        if tool_name == "get_applicant_summary":
            return self._get_applicant_summary(arguments)
        elif tool_name == "generate_visual_report":
            return self._generate_visual_report(arguments)
        elif tool_name == "analyze_assessment_ratios":
            return self._analyze_assessment_ratios(arguments)
        elif tool_name == "analyze_technical_fields":
            return self._analyze_technical_fields(arguments)
        elif tool_name == "compare_with_competitors":
            return self._compare_with_competitors(arguments)
        else:
            return {"error": f"Unknown tool: {tool_name}"}
    
    def access_resource(self, uri):
        """Access a specific resource by URI"""
        if uri == "current_date":
            return {"date": datetime.now().strftime("%Y-%m-%d")}
        elif uri == "patent_status_descriptions":
            return self._get_patent_status_descriptions()
        elif uri == "ipc_code_reference":
            return self._get_ipc_code_reference()
        elif uri == "top_applicants":
            return self._get_top_applicants()
        else:
            return {"error": f"Unknown resource URI: {uri}"}
    
    def _get_applicant_summary(self, arguments):
        """
        Get a comprehensive summary of a patent applicant
        
        Args:
            arguments (dict): Arguments containing applicant_name
            
        Returns:
            dict: Comprehensive summary data
        """
        applicant_name = arguments["applicant_name"]
        
        # Get summary data
        result = self.analyzer.get_applicant_summary(applicant_name)
        
        # Format the response to be more readable in LLM output
        return {
            "applicant_name": applicant_name,
            "total_patents": result["applicant"]["total_patents"],
            "assessment_statistics": {
                "grant_rate": f"{result['assessment_statistics']['grant_rate']:.1%}",
                "rejection_rate": f"{result['assessment_statistics']['rejection_rate']:.1%}",
                "pending_rate": f"{result['assessment_statistics']['status_distribution']['pending'] / result['assessment_statistics']['total_patents']:.1%}",
                "average_processing_time": f"{result['assessment_statistics']['average_processing_time_days'] / 30:.1f} months",
                "average_office_actions": f"{result['assessment_statistics']['average_office_actions']:.1f}"
            },
            "technical_distribution": [
                {
                    "field": item["ipc_code"],
                    "description": item["description"],
                    "percentage": f"{item['percentage']:.1f}%",
                    "count": item["count"]
                } 
                for item in result["technical_distribution"][:5]  # Top 5 fields
            ],
            "examiner_insights": [
                {
                    "type": insight["type"],
                    "level": insight["level"],
                    "description": insight["description"],
                    "recommendation": insight["recommendation"]
                }
                for insight in result["examiner_insights"]
            ],
            "application_trend": [
                {
                    "year": item["year"],
                    "count": item["count"]
                }
                for item in result["application_history"]["yearly_data"][-5:]  # Last 5 years
            ]
        }
    
    def _generate_visual_report(self, arguments):
        """
        Generate a visual report for an applicant
        
        Args:
            arguments (dict): Arguments containing applicant_name
            
        Returns:
            dict: Report data with markdown report
        """
        applicant_name = arguments["applicant_name"]
        
        # Generate report
        result = self.analyzer.generate_visual_report(applicant_name)
        
        # Return the markdown report
        return {
            "applicant_name": applicant_name,
            "markdown_report": result["markdown_report"]
        }
    
    def _analyze_assessment_ratios(self, arguments):
        """
        Analyze assessment ratios for an applicant
        
        Args:
            arguments (dict): Arguments containing applicant_name
            
        Returns:
            dict: Assessment ratio data
        """
        applicant_name = arguments["applicant_name"]
        
        # Analyze assessment ratios
        result = self.analyzer.analyze_assessment_ratios(applicant_name)
        
        # Format the response
        return {
            "applicant_name": applicant_name,
            "total_patents": result["total_patents"],
            "assessment_data": {
                "grant_rate": f"{result['assessment_data']['grant_rate']:.1%}",
                "rejection_rate": f"{result['assessment_data']['rejection_rate']:.1%}",
                "status_distribution": {
                    status: count
                    for status, count in result["assessment_data"]["status_distribution"].items()
                },
                "average_processing_time": f"{result['assessment_data']['average_processing_time_days'] / 30:.1f} months",
                "average_office_actions": f"{result['assessment_data']['average_office_actions']:.1f}"
            },
            "chart": f"data:image/png;base64,{result['visualization']}" if "visualization" in result else None
        }
    
    def _analyze_technical_fields(self, arguments):
        """
        Analyze technical fields for an applicant
        
        Args:
            arguments (dict): Arguments containing applicant_name
            
        Returns:
            dict: Technical field data
        """
        applicant_name = arguments["applicant_name"]
        
        # Analyze technical fields
        result = self.analyzer.analyze_technical_fields(applicant_name)
        
        # Format the response
        return {
            "applicant_name": applicant_name,
            "total_patents": result["total_patents"],
            "technical_fields": [
                {
                    "field": item["ipc_code"],
                    "description": item["description"],
                    "percentage": f"{item['percentage']:.1f}%",
                    "count": item["count"]
                } 
                for item in result["technical_fields"]
            ],
            "domain_analysis": {
                "domains": [
                    {
                        "name": domain["name"],
                        "percentage": f"{domain['percentage']:.1f}%",
                        "count": domain["count"]
                    }
                    for domain in result["domain_analysis"]["domains"] if "domains" in result["domain_analysis"]
                ]
            },
            "chart": f"data:image/png;base64,{result['visualization']}" if "visualization" in result else None
        }
    
    def _compare_with_competitors(self, arguments):
        """
        Compare applicant with competitors
        
        Args:
            arguments (dict): Arguments containing applicant_name and optionally num_competitors
            
        Returns:
            dict: Comparison data
        """
        applicant_name = arguments["applicant_name"]
        num_competitors = arguments.get("num_competitors", 3)
        
        # Compare with competitors
        result = self.analyzer.compare_with_competitors(applicant_name, num_competitors)
        
        # Format the response
        return {
            "applicant_name": applicant_name,
            "total_patents": result["applicant"]["total_patents"],
            "competitors": [
                {
                    "name": comp["name"],
                    "total_patents": comp["total_patents"],
                    "grant_rate": f"{comp['assessment_stats']['grant_rate']:.1%}",
                    "top_fields": [
                        {
                            "field": item["ipc_code"],
                            "percentage": f"{item['percentage']:.1f}%"
                        }
                        for item in comp["tech_distribution"][:3]  # Top 3 fields
                    ]
                }
                for comp in result["competitors"]
            ],
            "assessment_comparison_chart": f"data:image/png;base64,{result['assessment_comparison']}" if "assessment_comparison" in result else None,
            "field_comparison_chart": f"data:image/png;base64,{result['field_comparison']}" if "field_comparison" in result else None
        }
    
    def _get_patent_status_descriptions(self):
        """Get descriptions of patent statuses"""
        return {
            "granted": "特許が付与され、法的保護が与えられた出願",
            "rejected": "審査の結果、特許として認められなかった出願",
            "pending": "現在審査中の出願",
            "withdrawn": "出願人によって取り下げられた出願",
            "appealed": "拒絶査定に対して審判請求されている出願"
        }
    
    def _get_ipc_code_reference(self):
        """Get reference for IPC codes"""
        return self.analyzer.base_analyzer.ipc_descriptions
    
    def _get_top_applicants(self):
        """Get list of top applicants"""
        return [
            {
                "name": applicant["name"],
                "total_patents": applicant["total_patents"]
            }
            for applicant in self.analyzer.base_analyzer.applicants
        ]

# Create singleton instance for use with the MCP server
patent_applicant_server = PatentApplicantServer()

# MCP server functions that will be called by the MCP framework

def get_tools():
    """Return the tools provided by this server"""
    return patent_applicant_server.get_tools()

def get_resources():
    """Return the resources provided by this server"""
    return patent_applicant_server.get_resources()

def execute_tool(tool_name, arguments):
    """Execute a tool with the given arguments"""
    arguments_dict = json.loads(arguments) if isinstance(arguments, str) else arguments
    return patent_applicant_server.execute_tool(tool_name, arguments_dict)

def access_resource(uri):
    """Access a resource by URI"""
    return patent_applicant_server.access_resource(uri)
