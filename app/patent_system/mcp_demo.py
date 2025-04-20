#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MCP Patent Applicant Analyzer Demo

This script demonstrates how to use the MCP Patent Applicant Analyzer tools
to analyze patent applicant data for patent examiners.

The demo shows:
1. How to get summary information about an applicant
2. How to generate a visual report with charts
3. How to analyze specific aspects (assessment ratios, technical fields)
4. How to compare applicants with competitors
5. How to access reference resources

Note: This is a simulated MCP client. In a real environment, these tools
would be called by an LLM like Claude through the MCP protocol.
"""

import json
import time
import sys
from importlib import import_module

# Load the MCP server module
try:
    mcp_server_module = import_module("app.patent_system.mcp_patent_server")
    print("Successfully imported MCP server module")
except ImportError:
    print("Failed to import MCP server module. Make sure you're running from the project root.")
    sys.exit(1)

# Separator for output
def print_separator(title=None):
    print("\n" + "=" * 80)
    if title:
        print(f"  {title}")
        print("-" * 80)
    print()

# Simulate MCP call format
def simulate_mcp_call(tool_name, arguments=None, resource_uri=None):
    """
    Simulate an MCP call to demonstrate tool usage
    
    Args:
        tool_name (str): Name of the tool to call
        arguments (dict, optional): Arguments for the tool
        resource_uri (str, optional): URI for resource access
        
    Returns:
        dict: Tool response
    """
    print_separator(f"MCP CALL: {tool_name or resource_uri}")
    
    if tool_name:
        print(f"TOOL: {tool_name}")
        if arguments:
            print(f"ARGS: {json.dumps(arguments, indent=2, ensure_ascii=False)}")
        
        # Format as an example LLM prompt
        print("\nExample LLM Prompt:")
        print("""
<use_mcp_tool>
<server_name>patent-applicant-analyzer</server_name>
<tool_name>{tool}</tool_name>
<arguments>
{args}
</arguments>
</use_mcp_tool>
""".format(
            tool=tool_name,
            args=json.dumps(arguments, indent=2, ensure_ascii=False) if arguments else "{}"
        ))
        
        # Call the actual tool
        start_time = time.time()
        result = mcp_server_module.execute_tool(tool_name, arguments or {})
        elapsed_time = time.time() - start_time
        
    else:  # Resource access
        print(f"RESOURCE: {resource_uri}")
        
        # Format as an example LLM prompt
        print("\nExample LLM Prompt:")
        print("""
<access_mcp_resource>
<server_name>patent-applicant-analyzer</server_name>
<uri>{uri}</uri>
</access_mcp_resource>
""".format(uri=resource_uri))
        
        # Access the resource
        start_time = time.time()
        result = mcp_server_module.access_resource(resource_uri)
        elapsed_time = time.time() - start_time
    
    print(f"\nRESPONSE TIME: {elapsed_time:.2f} seconds")
    print(f"RESULT TYPE: {type(result).__name__}")
    
    # For markdown reports, just show a preview
    if tool_name == "generate_visual_report" and "markdown_report" in result:
        print("RESULT PREVIEW (markdown report):")
        lines = result["markdown_report"].split("\n")
        preview_lines = lines[:10] + ["..."] + lines[-5:] if len(lines) > 15 else lines
        print("\n".join(preview_lines))
    # For image data, indicate it contains embedded images
    elif isinstance(result, dict) and any(key.endswith("_chart") for key in result.keys()):
        print("RESULT SUMMARY (contains embedded images):")
        result_summary = {k: "[Base64 image data]" if k.endswith("_chart") else v for k, v in result.items()}
        print(json.dumps(result_summary, indent=2, ensure_ascii=False))
    else:
        print("RESULT:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    return result

def demo_available_tools_and_resources():
    """Demonstrate listing available tools and resources"""
    print_separator("AVAILABLE TOOLS")
    tools = mcp_server_module.get_tools()
    for tool in tools:
        print(f"- {tool['name']}: {tool['description']}")
    
    print_separator("AVAILABLE RESOURCES")
    resources = mcp_server_module.get_resources()
    for resource in resources:
        print(f"- {resource['uri']}: {resource['description']}")

def demo_applicant_summary():
    """Demonstrate getting a summary for an applicant"""
    print_separator("APPLICANT SUMMARY DEMO")
    print("This demonstrates getting a comprehensive summary for a patent applicant.")
    
    # Example 1: Get summary for a specific applicant
    simulate_mcp_call("get_applicant_summary", {"applicant_name": "テック株式会社"})

def demo_visual_report():
    """Demonstrate generating a visual report"""
    print_separator("VISUAL REPORT DEMO")
    print("This demonstrates generating a visual report with embedded charts.")
    
    # Generate a visual report
    simulate_mcp_call("generate_visual_report", {"applicant_name": "イノベーション製造"})
    
    print("\nNote: The actual report contains embedded charts in Markdown format.")
    print("An LLM like Claude can display these charts when responding to a user.")

def demo_assessment_analysis():
    """Demonstrate assessment ratio analysis"""
    print_separator("ASSESSMENT RATIO ANALYSIS DEMO")
    print("This demonstrates analyzing the assessment ratios for a patent applicant.")
    
    # Analyze assessment ratios
    simulate_mcp_call("analyze_assessment_ratios", {"applicant_name": "AIソリューションズ"})

def demo_technical_field_analysis():
    """Demonstrate technical field analysis"""
    print_separator("TECHNICAL FIELD ANALYSIS DEMO")
    print("This demonstrates analyzing the technical fields for a patent applicant.")
    
    # Analyze technical fields
    simulate_mcp_call("analyze_technical_fields", {"applicant_name": "データシステムズ"})

def demo_competitor_comparison():
    """Demonstrate competitor comparison"""
    print_separator("COMPETITOR COMPARISON DEMO")
    print("This demonstrates comparing a patent applicant with competitors.")
    
    # Compare with competitors
    simulate_mcp_call("compare_with_competitors", {
        "applicant_name": "未来技研", 
        "num_competitors": 2
    })

def demo_resource_access():
    """Demonstrate accessing resources"""
    print_separator("RESOURCE ACCESS DEMO")
    print("This demonstrates accessing reference resources.")
    
    # Access patent status descriptions
    simulate_mcp_call(None, resource_uri="patent_status_descriptions")
    
    # Access IPC code reference
    simulate_mcp_call(None, resource_uri="ipc_code_reference")
    
    # Access top applicants list
    simulate_mcp_call(None, resource_uri="top_applicants")

def demo_examiner_usage_examples():
    """Show examples of how a patent examiner might use these tools through an LLM"""
    print_separator("PATENT EXAMINER USAGE EXAMPLES")
    print("""
Here are examples of how a patent examiner might use these tools through an LLM like Claude:

1. **Basic applicant research**
   "請求項1に記載のAI画像認識技術について、テック株式会社の過去の出願状況を教えてください。"
   
   The LLM would use the get_applicant_summary tool to retrieve information about テック株式会社.

2. **Visual analysis for reporting**
   "AIソリューションズの特許審査レポートを作成したいです。査定率と技術分野の分布に関する図表を含めてください。"
   
   The LLM would use the generate_visual_report tool to create a comprehensive report 
   with embedded charts showing assessment ratios and technical field distribution.

3. **Comparative examination**
   "データシステムズとその競合他社の査定率を比較し、技術分野ごとの差異を分析してください。"
   
   The LLM would use the compare_with_competitors tool to generate comparative charts 
   and provide insights on the differences in assessment rates and technical focus.

4. **Technical field focus analysis**
   "未来技研のG06Nに関する特許はどのくらいあり、どのような傾向がありますか？"
   
   The LLM would use the analyze_technical_fields tool to provide details about 
   the applicant's patents in the G06N classification.

5. **Office action preparation assistance**
   "イノベーション製造の過去の出願において、拒絶される傾向がある特定のパターンはありますか？"
   
   The LLM would analyze the assessment statistics and examiner insights from 
   the get_applicant_summary tool to identify patterns in rejected applications.
""")

def main():
    """Main demo function"""
    print("\n特許出願人分析MCP サーバーデモ\n")
    print("このデモでは、特許審査官向けに開発されたMCPツールの使用方法を紹介します。")
    print("実際の環境では、これらのツールはClaudeなどのLLMからMCPプロトコルを通じて呼び出されます。")
    
    # Run all demos
    try:
        demo_available_tools_and_resources()
        demo_applicant_summary()
        demo_visual_report()
        demo_assessment_analysis()
        demo_technical_field_analysis()
        demo_competitor_comparison()
        demo_resource_access()
        demo_examiner_usage_examples()
        
        print_separator("デモ完了")
        print("これらのツールを使用することで、特許審査官は出願人の詳細な分析を行い、")
        print("査定の傾向や技術分野の分布などの洞察を得ることができます。")
        
    except Exception as e:
        print(f"デモの実行中にエラーが発生しました: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
