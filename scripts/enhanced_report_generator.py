#!/usr/bin/env python3
"""
Enhanced HTML report generator with detailed explanations and trace links.
"""

import os
from datetime import datetime
from typing import List, Dict

def generate_enhanced_report(page_analysis: Dict, results: List[Dict]) -> str:
    """
    Generate comprehensive HTML report with:
    - Links to Nova Act trace files
    - Detailed explanations of each test
    - Easy dive-in points
    """
    
    # Calculate summary stats
    total_tests = len(results)
    successful = sum(1 for r in results if r['success'])
    failed = total_tests - successful
    success_rate = (successful / total_tests * 100) if total_tests > 0 else 0
    
    # Group by persona
    persona_results = {}
    for result in results:
        persona = result['persona']
        if persona not in persona_results:
            persona_results[persona] = []
        persona_results[persona].append(result)
    
    # Build HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nova Act Usability Test Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            border-radius: 8px;
        }}
        
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 15px;
            margin-bottom: 30px;
            font-size: 2.5em;
        }}
        
        h2 {{
            color: #34495e;
            margin-top: 40px;
            margin-bottom: 20px;
            font-size: 1.8em;
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 10px;
        }}
        
        h3 {{
            color: #2c3e50;
            margin-top: 25px;
            margin-bottom: 15px;
            font-size: 1.3em;
        }}
        
        .page-analysis {{
            background: #e8f4f8;
            padding: 25px;
            border-radius: 6px;
            margin: 20px 0;
            border-left: 4px solid #3498db;
        }}
        
        .page-analysis h3 {{
            margin-top: 0;
            color: #2980b9;
        }}
        
        .page-analysis ul {{
            margin: 10px 0;
            padding-left: 25px;
        }}
        
        .executive-summary {{
            background: #ecf0f1;
            padding: 25px;
            border-radius: 6px;
            margin: 20px 0;
            border-left: 4px solid #3498db;
        }}
        
        .executive-summary p {{
            margin: 10px 0;
            font-size: 1.1em;
        }}
        
        .executive-summary strong {{
            color: #2c3e50;
        }}
        
        .persona-section {{
            background: #fff;
            border: 2px solid #ddd;
            border-radius: 8px;
            padding: 25px;
            margin: 25px 0;
            box-shadow: 0 2px 5px rgba(0,0,0,0.08);
        }}
        
        .persona-section h3 {{
            color: #3498db;
            margin-top: 0;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .test-case {{
            background: #f8f9fa;
            border-left: 4px solid #95a5a6;
            padding: 20px;
            margin: 20px 0;
            border-radius: 4px;
        }}
        
        .test-case.success {{
            border-left-color: #2ecc71;
            background: #eafaf1;
        }}
        
        .test-case.failure {{
            border-left-color: #e74c3c;
            background: #fadbd8;
        }}
        
        .test-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }}
        
        .test-title {{
            font-size: 1.1em;
            font-weight: 600;
            color: #2c3e50;
        }}
        
        .test-status {{
            display: inline-block;
            padding: 6px 12px;
            border-radius: 4px;
            font-weight: bold;
            font-size: 0.9em;
        }}
        
        .test-status.success {{
            background: #2ecc71;
            color: white;
        }}
        
        .test-status.failure {{
            background: #e74c3c;
            color: white;
        }}
        
        .observation {{
            background: white;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 15px;
            margin: 10px 0;
        }}
        
        .observation-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }}
        
        .step-name {{
            font-weight: 600;
            color: #34495e;
        }}
        
        .step-result {{
            padding: 4px 8px;
            border-radius: 3px;
            font-size: 0.85em;
            font-weight: 600;
        }}
        
        .step-result.success {{
            background: #d5f4e6;
            color: #27ae60;
        }}
        
        .step-result.failure {{
            background: #fadbd8;
            color: #c0392b;
        }}
        
        .observation-action {{
            color: #555;
            font-style: italic;
            margin: 5px 0;
        }}
        
        .observation-notes {{
            background: #f8f9fa;
            padding: 10px;
            border-radius: 3px;
            margin-top: 8px;
            color: #555;
        }}
        
        .observation-notes.issue {{
            background: #fff3cd;
            border-left: 3px solid #ffc107;
        }}
        
        .trace-link {{
            display: inline-block;
            margin-top: 10px;
            padding: 8px 12px;
            background: #3498db;
            color: white;
            text-decoration: none;
            border-radius: 4px;
            font-size: 0.9em;
        }}
        
        .trace-link:hover {{
            background: #2980b9;
        }}
        
        .insights {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 20px;
            margin: 20px 0;
            border-radius: 4px;
        }}
        
        .insights h3 {{
            margin-top: 0;
            color: #f39c12;
        }}
        
        .insight-item {{
            margin: 10px 0;
            padding-left: 20px;
            position: relative;
        }}
        
        .insight-item:before {{
            content: "💡";
            position: absolute;
            left: 0;
        }}
        
        .footer {{
            margin-top: 50px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            text-align: center;
            color: #7f8c8d;
            font-size: 0.9em;
        }}
        
        .metric {{
            display: inline-block;
            margin: 0 15px;
            font-size: 1.1em;
        }}
        
        .metric-value {{
            font-weight: bold;
            color: #3498db;
            font-size: 1.3em;
        }}
        
        details {{
            margin: 15px 0;
        }}
        
        summary {{
            cursor: pointer;
            font-weight: 600;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 4px;
            user-select: none;
        }}
        
        summary:hover {{
            background: #e9ecef;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🦅 Nova Act Usability Test Report</h1>
        
        <div class="page-analysis">
            <h3>📄 Page Analysis: {page_analysis.get('title', 'Unknown')}</h3>
            <p><strong>URL:</strong> https://nova.amazon.com/act</p>
            <p><strong>Purpose:</strong> {page_analysis.get('purpose', 'Not analyzed')}</p>
            <p><strong>Navigation:</strong> {', '.join(page_analysis.get('navigation', ['None found']))}</p>
            <p><strong>Key Elements:</strong></p>
            <ul>
                <li>Documentation: {'✅ Available' if page_analysis.get('key_elements', {}).get('documentation') else '❌ Not found'}</li>
                <li>Interactive Demo: {'✅ Available' if page_analysis.get('key_elements', {}).get('demo') else '❌ Not found'}</li>
                <li>Pricing: {'✅ Available' if page_analysis.get('key_elements', {}).get('pricing') else '❌ Not found'}</li>
            </ul>
        </div>
        
        <div class="executive-summary">
            <h2>Executive Summary</h2>
            <p><strong>Test Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>Tests Conducted:</strong> {total_tests}</p>
            <p>
                <span class="metric">
                    <span class="metric-value">{successful}</span> Passed
                </span>
                <span class="metric">
                    <span class="metric-value">{failed}</span> Failed
                </span>
                <span class="metric">
                    <span class="metric-value">{success_rate:.1f}%</span> Success Rate
                </span>
            </p>
            <p><strong>Personas Tested:</strong> {len(persona_results)}</p>
        </div>
"""
    
    # Per-persona detailed results
    html += "<h2>Detailed Test Results</h2>\n"
    
    for persona_name, persona_tests in persona_results.items():
        persona_success = sum(1 for t in persona_tests if t['success'])
        persona_total = len(persona_tests)
        persona_rate = (persona_success / persona_total * 100) if persona_total > 0 else 0
        
        archetype = persona_tests[0]['persona_archetype']
        tech_level = persona_tests[0]['tech_proficiency']
        
        html += f"""
        <div class="persona-section">
            <h3>
                <span>{persona_name}</span>
                <span style="font-size: 0.8em; color: #7f8c8d;">({archetype} - {tech_level} proficiency)</span>
            </h3>
            <p><strong>Success Rate:</strong> {persona_success}/{persona_total} ({persona_rate:.1f}%)</p>
        """
        
        for test in persona_tests:
            test_class = "success" if test['success'] else "failure"
            status_text = "✅ PASSED" if test['success'] else "❌ FAILED"
            
            html += f"""
            <div class="test-case {test_class}">
                <div class="test-header">
                    <div class="test-title">{test['test_case']}</div>
                    <div class="test-status {test_class}">{status_text}</div>
                </div>
                <p><strong>Duration:</strong> {test['duration_seconds']}s</p>
                
                <details open>
                    <summary>Step-by-Step Observations ({len(test['observations'])} steps)</summary>
            """
            
            # Detailed observations
            for i, obs in enumerate(test['observations'], 1):
                obs_success = obs.get('success')
                if obs_success is True:
                    result_class = "success"
                    result_text = "✓"
                elif obs_success is False:
                    result_class = "failure"
                    result_text = "✗"
                else:
                    result_class = ""
                    result_text = "•"
                
                notes = obs.get('notes', '')
                is_issue = any(word in notes.upper() for word in ['ISSUE', 'FRICTION', 'PROBLEM', 'CRITICAL', 'MAJOR'])
                notes_class = "issue" if is_issue else ""
                
                html += f"""
                <div class="observation">
                    <div class="observation-header">
                        <span class="step-name">Step {i}: {obs.get('step', 'Unknown').replace('_', ' ').title()}</span>
                        {f'<span class="step-result {result_class}">{result_text} {obs.get("success", "N/A")}</span>' if result_class else ''}
                    </div>
                    <div class="observation-action">Action: {obs.get('action', 'No action recorded')}</div>
                    <div class="observation-notes {notes_class}">
                        <strong>{"⚠️ " if is_issue else ""}Observation:</strong> {notes}
                    </div>
                </div>
                """
            
            html += """
                </details>
                
            """
            
            # Add Nova Act trace file links
            trace_files = test.get('trace_files', [])
            if trace_files:
                html += f"""
                <div style="margin-top: 15px; padding: 15px; background: #e3f2fd; border-radius: 4px;">
                    <strong>🔍 Nova Act Session Recordings ({len(trace_files)}):</strong>
                    <div style="margin-top: 10px;">
                """
                for i, trace_file in enumerate(trace_files, 1):
                    # Make path relative to current working directory
                    try:
                        relative_path = os.path.relpath(trace_file, os.getcwd())
                    except ValueError:
                        # If on different drives (Windows), use absolute path
                        relative_path = trace_file
                    
                    html += f"""
                        <div style="margin: 5px 0;">
                            <a href="{relative_path}" class="trace-link" target="_blank">
                                📹 Recording {i}: {os.path.basename(trace_file)}
                            </a>
                            <span style="font-size: 0.85em; color: #666; margin-left: 10px;">
                                ({relative_path})
                            </span>
                        </div>
                    """
                html += """
                    </div>
                    <p style="margin-top: 10px; font-size: 0.9em; color: #555;">
                        <em>Click to view detailed Nova Act trace showing every action, screenshot, and AI decision</em>
                    </p>
                </div>
                """
            
            html += "</div>\n"
        
        html += "</div>\n"
    
    # Key insights
    html += """
        <div class="insights">
            <h3>🔍 Key Insights</h3>
    """
    
    # Generate insights
    all_notes = []
    for test in results:
        for obs in test.get('observations', []):
            notes = obs.get('notes', '')
            if any(word in notes.upper() for word in ['ISSUE', 'FRICTION', 'CRITICAL', 'MAJOR', 'PROBLEM']):
                all_notes.append(notes)
    
    if all_notes:
        html += "<h4>UX Issues Discovered:</h4>\n"
        for note in set(all_notes):  # Unique issues
            html += f'<div class="insight-item">{note}</div>\n'
    
    # Success patterns
    successes = [t for t in results if t['success']]
    if successes:
        html += "<h4>What Worked Well:</h4>\n"
        for test in successes[:3]:  # Top 3
            html += f'<div class="insight-item">{test["test_case"]} - Completed successfully in {test["duration_seconds"]}s</div>\n'
    
    html += "</div>\n"
    
    # Footer
    html += f"""
        <div class="footer">
            <p>Generated by Nova Act Usability Testing Suite | Powered by OpenClaw</p>
            <p>Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
</body>
</html>
"""
    
    # Write report to current working directory
    report_path = os.path.join(os.getcwd(), "nova_act_usability_report.html")
    with open(report_path, 'w') as f:
        f.write(html)
    
    return report_path
