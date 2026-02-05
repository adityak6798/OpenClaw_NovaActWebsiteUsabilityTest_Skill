#!/usr/bin/env python3
"""
Adaptive AI-orchestrated usability testing.
Explores the page, generates contextual personas, and iteratively tests.
"""

import sys
import os
import time
import json
from datetime import datetime
from pydantic import BaseModel
from typing import List, Dict, Optional

# Dynamic path resolution - works from any installation location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)
WORKSPACE_DIR = os.getcwd()

# Add skill scripts to path
sys.path.insert(0, SCRIPT_DIR)

from nova_session import nova_session
from enhanced_report_generator import generate_enhanced_report
from trace_finder import get_session_traces

WEBSITE_URL = "https://nova.amazon.com/act"  # Default - override via argument or edit
RESULTS_FILE = os.path.join(WORKSPACE_DIR, "test_results_adaptive.json")
LOGS_DIR = os.path.join(WORKSPACE_DIR, "nova_act_logs")

# Pydantic schemas for structured extraction
class NavigationLinks(BaseModel):
    links: List[str]

class PageAnalysis(BaseModel):
    main_purpose: str
    key_features: List[str]
    target_audience: str

def analyze_page(url: str) -> Dict:
    """
    Step 1: Analyze the page to understand what it offers.
    Uses Nova Act + vision to understand the page before testing.
    """
    print(f"\n🔍 ANALYZING PAGE: {url}")
    print("="*60)
    
    analysis = {}
    
    with nova_session(url, headless=True, logs_dir=LOGS_DIR) as nova:
        # Get basic page info
        print("→ Reading page title and main heading...")
        title = nova.act_get(
            "What is the main title or headline on this page?",
            schema={"type": "object", "properties": {"title": {"type": "string"}}, "required": ["title"]}
        )
        analysis['title'] = title.parsed_response.get('title', 'Unknown')
        print(f"  Title: {analysis['title']}")
        
        # Get navigation structure
        print("→ Analyzing navigation...")
        nav_links = nova.act_get(
            "List all the navigation links you see at the top of the page (just the text of each link, separated by commas)",
            schema={"type": "object", "properties": {"links": {"type": "string"}}, "required": ["links"]}
        )
        nav_text = nav_links.parsed_response.get('links', '')
        analysis['navigation'] = [link.strip() for link in nav_text.split(',') if link.strip()]
        print(f"  Navigation: {analysis['navigation']}")
        
        # Understand page purpose
        print("→ Understanding page purpose...")
        purpose = nova.act_get(
            "In one sentence, what does this page help users do?",
            schema={"type": "object", "properties": {"purpose": {"type": "string"}}, "required": ["purpose"]}
        )
        analysis['purpose'] = purpose.parsed_response.get('purpose', 'Unknown purpose')
        print(f"  Purpose: {analysis['purpose']}")
        
        # Check for key elements
        print("→ Checking for key elements...")
        has_pricing = nova.act_get("Is there any mention of pricing, cost, or plans on this page?", schema={"type": "boolean"})
        has_docs = nova.act_get("Is there any mention of documentation, API, or developer resources?", schema={"type": "boolean"})
        has_demo = nova.act_get("Is there an interactive demo or playground on this page?", schema={"type": "boolean"})
        
        analysis['key_elements'] = {
            'pricing': has_pricing.parsed_response,
            'documentation': has_docs.parsed_response,
            'demo': has_demo.parsed_response
        }
        print(f"  Key elements: {analysis['key_elements']}")
    
    return analysis

def generate_personas(page_analysis: Dict) -> List[Dict]:
    """
    Step 2: Generate contextual personas based on what the page actually offers.
    """
    print(f"\n👥 GENERATING PERSONAS")
    print("="*60)
    
    # Based on page analysis, create relevant personas
    purpose = page_analysis.get('purpose', '').lower()
    
    personas = []
    
    # Always include these archetypes, but customize to the page
    if 'developer' in purpose or 'api' in purpose or 'code' in purpose:
        personas.append({
            "name": "Alex Chen",
            "archetype": "developer",
            "age": 28,
            "tech_proficiency": "high",
            "goals": ["Integrate API", "Find technical docs", "See code examples"],
            "description": "Software developer looking to integrate this tool"
        })
    else:
        personas.append({
            "name": "Alex Chen",
            "archetype": "tech_savvy_user",
            "age": 28,
            "tech_proficiency": "high",
            "goals": ["Explore advanced features", "Try the tool", "Understand capabilities"],
            "description": "Tech-savvy early adopter"
        })
    
    # Business user
    personas.append({
        "name": "Marcus Johnson",
        "archetype": "business_professional",
        "age": 42,
        "tech_proficiency": "medium",
        "goals": ["Understand ROI", "Check pricing", "Evaluate ease of use"],
        "description": "Business professional evaluating tools"
    })
    
    # Only add beginner persona if the page seems accessible
    if page_analysis['key_elements'].get('demo') or 'simple' in purpose:
        personas.append({
            "name": "Sarah Williams",
            "archetype": "beginner",
            "age": 35,
            "tech_proficiency": "low",
            "goals": ["Understand what it does", "Try simple example", "Get help if stuck"],
            "description": "First-time user with basic tech skills"
        })
    
    for p in personas:
        print(f"→ {p['name']} ({p['archetype']}): {p['description']}")
    
    return personas

def generate_test_cases(persona: Dict, page_analysis: Dict) -> List[str]:
    """
    Step 3: Generate top 3 realistic test cases for this persona on THIS page.
    """
    archetype = persona['archetype']
    nav = page_analysis.get('navigation', [])
    has_pricing = page_analysis['key_elements'].get('pricing', False)
    has_docs = page_analysis['key_elements'].get('documentation', False)
    has_demo = page_analysis['key_elements'].get('demo', False)
    
    test_cases = []
    
    if archetype == "developer" or archetype == "tech_savvy_user":
        # Top use cases for tech users
        if has_docs:
            test_cases.append("Find and access technical documentation")
        if has_demo:
            test_cases.append("Try the interactive demo or playground")
        test_cases.append("Understand the core capabilities and features")
        
    elif archetype == "business_professional":
        # Top use cases for business users
        test_cases.append("Quickly understand the value proposition")
        if has_pricing:
            test_cases.append("Find pricing information to evaluate cost")
        else:
            test_cases.append("Determine if pricing is available or how to get it")
        test_cases.append("Find getting started resources or contact sales")
        
    elif archetype == "beginner":
        # Top use cases for beginners
        test_cases.append("Understand what this tool does in simple terms")
        if has_demo:
            test_cases.append("Try a simple example or tutorial")
        test_cases.append("Find help or support if confused")
    
    return test_cases[:3]  # Top 3

def iterative_test(persona: Dict, test_case: str, page_analysis: Dict) -> Dict:
    """
    Step 4: Iteratively test a hypothesis, adapting based on findings.
    Don't give up after one prompt - explore multiple approaches.
    """
    print(f"\n{'='*60}")
    print(f"PERSONA: {persona['name']} ({persona['archetype']})")
    print(f"TEST CASE: {test_case}")
    print(f"{'='*60}\n")
    
    observations = []
    start_time = time.time()
    success = False
    trace_files = []  # Collect Nova Act trace file paths
    
    try:
        from nova_act import BOOL_SCHEMA
        
        with nova_session(WEBSITE_URL, headless=True, logs_dir=LOGS_DIR) as nova:
            # Initial observation
            observations.append({
                "step": "navigate",
                "action": f"Loaded {WEBSITE_URL}",
                "success": True,
                "notes": "Page loaded successfully",
                "timestamp": datetime.now().isoformat()
            })
            
            # ITERATIVE EXPLORATION based on test case
            
            if "documentation" in test_case.lower():
                print("→ Exploring: Finding documentation...")
                
                # Approach 1: Check for exact match
                print("  Attempt 1: Look for 'Documentation' link")
                has_docs_exact = nova.act_get(
                    "Do you see a link with the exact word 'Documentation'?",
                    schema=BOOL_SCHEMA
                )
                
                if has_docs_exact.parsed_response:
                    observations.append({
                        "step": "find_docs_exact",
                        "action": "Check for 'Documentation' link",
                        "success": True,
                        "notes": "Found exact 'Documentation' link",
                        "timestamp": datetime.now().isoformat()
                    })
                    success = True
                else:
                    observations.append({
                        "step": "find_docs_exact",
                        "action": "Check for 'Documentation' link",
                        "success": False,
                        "notes": "No exact 'Documentation' link found",
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    # Approach 2: Try variations
                    print("  Attempt 2: Try variations (Docs, API, etc.)")
                    has_docs_variant = nova.act_get(
                        "Do you see a link containing 'Docs' or 'API' or 'Developer' or 'Guide'?",
                        schema=BOOL_SCHEMA
                    )
                    
                    if has_docs_variant.parsed_response:
                        observations.append({
                            "step": "find_docs_variant",
                            "action": "Check for documentation variations",
                            "success": True,
                            "notes": "Found documentation link with different wording",
                            "timestamp": datetime.now().isoformat()
                        })
                        success = True
                    else:
                        observations.append({
                            "step": "find_docs_variant",
                            "action": "Check for documentation variations",
                            "success": False,
                            "notes": "UX ISSUE: No documentation links found with any common variation",
                            "timestamp": datetime.now().isoformat()
                        })
            
            elif "demo" in test_case.lower() or "playground" in test_case.lower():
                print("→ Exploring: Finding interactive demo...")
                
                # Approach 1: Check for interactive element
                print("  Attempt 1: Look for input/prompt box")
                has_input = nova.act_get(
                    "Is there an input box, text field, or prompt where you can type?",
                    schema=BOOL_SCHEMA
                )
                
                observations.append({
                    "step": "find_interactive",
                    "action": "Check for interactive input element",
                    "success": has_input.parsed_response,
                    "notes": "Interactive element found" if has_input.parsed_response else "No interactive element visible",
                    "timestamp": datetime.now().isoformat()
                })
                
                if has_input.parsed_response:
                    success = True
                else:
                    # Approach 2: Look for demo/playground links
                    print("  Attempt 2: Look for 'Demo' or 'Playground' link")
                    has_demo_link = nova.act_get(
                        "Is there a link or button with 'Demo', 'Try', 'Playground', or 'Test'?",
                        schema=BOOL_SCHEMA
                    )
                    
                    observations.append({
                        "step": "find_demo_link",
                        "action": "Check for demo/playground link",
                        "success": has_demo_link.parsed_response,
                        "notes": "Demo link found" if has_demo_link.parsed_response else "No demo/playground access found",
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    success = has_demo_link.parsed_response
            
            elif "pricing" in test_case.lower():
                print("→ Exploring: Finding pricing...")
                
                # Approach 1: Check navigation
                print("  Attempt 1: Check navigation for 'Pricing'")
                nav_pricing = nova.act_get(
                    "Is there a navigation link with 'Pricing'?",
                    schema=BOOL_SCHEMA
                )
                
                if nav_pricing.parsed_response:
                    observations.append({
                        "step": "find_pricing_nav",
                        "action": "Check navigation for pricing",
                        "success": True,
                        "notes": "Pricing link in navigation",
                        "timestamp": datetime.now().isoformat()
                    })
                    success = True
                else:
                    observations.append({
                        "step": "find_pricing_nav",
                        "action": "Check navigation for pricing",
                        "success": False,
                        "notes": "No pricing in navigation",
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    # Approach 2: Check page body
                    print("  Attempt 2: Scroll and look for pricing in content")
                    nova.act("Scroll down to see more content")
                    time.sleep(2)
                    
                    has_pricing_body = nova.act_get(
                        "Do you see any text about pricing, cost, plans, or subscription?",
                        schema=BOOL_SCHEMA
                    )
                    
                    observations.append({
                        "step": "find_pricing_body",
                        "action": "Scroll and check for pricing in body",
                        "success": has_pricing_body.parsed_response,
                        "notes": "Pricing found in body" if has_pricing_body.parsed_response else "TRANSPARENCY ISSUE: No pricing information visible",
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    success = has_pricing_body.parsed_response
            
            elif "value proposition" in test_case.lower() or "understand" in test_case.lower():
                print("→ Exploring: Understanding value proposition...")
                
                # Check if purpose is clearly stated
                has_tagline = nova.act_get(
                    "Is there a sentence near the top that explains what this tool does or what problem it solves?",
                    schema=BOOL_SCHEMA
                )
                
                observations.append({
                    "step": "find_value_prop",
                    "action": "Check for clear value proposition",
                    "success": has_tagline.parsed_response,
                    "notes": "Value prop visible" if has_tagline.parsed_response else "UX ISSUE: No clear value proposition",
                    "timestamp": datetime.now().isoformat()
                })
                
                success = has_tagline.parsed_response
            
            elif "help" in test_case.lower() or "support" in test_case.lower():
                print("→ Exploring: Finding help/support...")
                
                # Approach 1: Header
                has_help_header = nova.act_get(
                    "Is there a 'Help', 'Support', or 'Contact' link in the header?",
                    schema=BOOL_SCHEMA
                )
                
                if has_help_header.parsed_response:
                    observations.append({
                        "step": "find_help_header",
                        "action": "Check header for help",
                        "success": True,
                        "notes": "Help link in header",
                        "timestamp": datetime.now().isoformat()
                    })
                    success = True
                else:
                    observations.append({
                        "step": "find_help_header",
                        "action": "Check header for help",
                        "success": False,
                        "notes": "No help in header",
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    # Approach 2: Footer
                    print("  Attempt 2: Check footer")
                    nova.act("Scroll to the bottom of the page")
                    time.sleep(2)
                    
                    has_help_footer = nova.act_get(
                        "Is there a 'Help', 'Support', 'Contact', or 'FAQ' link in the footer?",
                        schema=BOOL_SCHEMA
                    )
                    
                    observations.append({
                        "step": "find_help_footer",
                        "action": "Check footer for help",
                        "success": has_help_footer.parsed_response,
                        "notes": "Help in footer" if has_help_footer.parsed_response else "MAJOR ISSUE: No help/support access",
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    success = has_help_footer.parsed_response
            
            else:
                # Generic exploration for other test cases
                print(f"→ Generic exploration for: {test_case}")
                observations.append({
                    "step": "generic_test",
                    "action": f"Test: {test_case}",
                    "success": False,
                    "notes": "Test case not yet implemented with specific exploration logic",
                    "timestamp": datetime.now().isoformat()
                })
    
    except Exception as e:
        observations.append({
            "step": "error",
            "action": "Exception occurred",
            "success": False,
            "notes": f"Error: {str(e)}",
            "timestamp": datetime.now().isoformat()
        })
    
    # Capture Nova Act trace files for this session
    trace_files = get_session_traces(LOGS_DIR)
    print(f"  → Captured {len(trace_files)} Nova Act trace files")
    
    duration = time.time() - start_time
    
    return {
        "persona": persona['name'],
        "persona_archetype": persona['archetype'],
        "tech_proficiency": persona['tech_proficiency'],
        "test_case": test_case,
        "success": success,
        "duration_seconds": round(duration, 2),
        "observations": observations,
        "trace_files": trace_files,
        "timestamp": datetime.now().isoformat()
    }

def main():
    # Support URL as command line argument
    global WEBSITE_URL
    if len(sys.argv) > 1:
        WEBSITE_URL = sys.argv[1]
    
    print(f"\n🦅 ADAPTIVE NOVA ACT USABILITY TEST")
    print(f"Website: {WEBSITE_URL}")
    print(f"Workspace: {WORKSPACE_DIR}")
    print(f"="*60)
    
    # Step 1: Analyze the page
    page_analysis = analyze_page(WEBSITE_URL)
    
    # Step 2: Generate contextual personas
    personas = generate_personas(page_analysis)
    
    # Step 3 & 4: Generate test cases and run iterative tests
    all_results = []
    
    for persona in personas:
        print(f"\n\n{'#'*60}")
        print(f"# TESTING AS: {persona['name']}")
        print(f"{'#'*60}")
        
        test_cases = generate_test_cases(persona, page_analysis)
        print(f"\nTest cases for {persona['name']}:")
        for i, tc in enumerate(test_cases, 1):
            print(f"  {i}. {tc}")
        
        for test_case in test_cases:
            result = iterative_test(persona, test_case, page_analysis)
            all_results.append(result)
            
            status = "✅" if result['success'] else "❌"
            print(f"\n{status} Result: {test_case} ({result['duration_seconds']}s)")
    
    # Save results
    with open(RESULTS_FILE, 'w') as f:
        json.dump({
            "page_analysis": page_analysis,
            "test_results": all_results
        }, f, indent=2)
    
    # Summary
    success_count = sum(1 for r in all_results if r['success'])
    total = len(all_results)
    
    print(f"\n\n{'='*60}")
    print(f"✅ ADAPTIVE TEST COMPLETE")
    print(f"Success Rate: {success_count}/{total} ({success_count/total*100:.1f}%)")
    print(f"Results: {RESULTS_FILE}")
    print(f"{'='*60}")
    
    # Auto-generate HTML report
    print(f"\n📊 Generating HTML report...")
    report_path = generate_enhanced_report(page_analysis, all_results)
    
    print(f"\n{'='*60}")
    print(f"📄 HTML REPORT GENERATED")
    print(f"{'='*60}")
    print(f"\n🦅 Usability Report: {report_path}")
    print(f"\nView the report in your browser:")
    print(f"  file://{report_path}")
    print(f"\n{'='*60}\n")

if __name__ == "__main__":
    main()
