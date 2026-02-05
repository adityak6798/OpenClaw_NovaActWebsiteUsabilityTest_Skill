#!/usr/bin/env python3
"""
Adaptive AI-orchestrated usability testing - FULLY DYNAMIC VERSION.
Exploration strategy, prompts, and questions are all generated per test case.
"""

import sys
import os
import time
import json
from datetime import datetime
from pydantic import BaseModel
from typing import List, Dict, Optional

# Dynamic path resolution
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)
WORKSPACE_DIR = os.getcwd()

sys.path.insert(0, SCRIPT_DIR)

from nova_session import nova_session
from enhanced_report_generator import generate_enhanced_report
from trace_finder import get_session_traces
from safe_nova_wrapper import safe_act, safe_act_get, safe_scroll, is_session_healthy
from dynamic_exploration import generate_exploration_strategy, adapt_prompt_for_persona

WEBSITE_URL = "https://nova.amazon.com/act"  # Default
RESULTS_FILE = os.path.join(WORKSPACE_DIR, "test_results_adaptive.json")
LOGS_DIR = os.path.join(WORKSPACE_DIR, "nova_act_logs")

class NavigationLinks(BaseModel):
    links: List[str]

class PageAnalysis(BaseModel):
    main_purpose: str
    key_features: List[str]
    target_audience: str

def analyze_page(url: str) -> Dict:
    """
    Step 1: Analyze the page with graceful error handling.
    """
    print(f"\n🔍 ANALYZING PAGE: {url}")
    print("="*60)
    
    analysis = {
        'title': 'Unknown',
        'navigation': [],
        'purpose': 'Unknown purpose',
        'key_elements': {'pricing': False, 'documentation': False, 'demo': False}
    }
    
    try:
        with nova_session(url, headless=True, logs_dir=LOGS_DIR) as nova:
            print("→ Reading page title and main heading...")
            ok, response, error = safe_act_get(
                nova,
                "What is the main title or headline on this page?",
                schema={"type": "object", "properties": {"title": {"type": "string"}}, "required": ["title"]},
                timeout=20
            )
            if ok and response:
                analysis['title'] = response.get('title', 'Unknown')
                print(f"  Title: {analysis['title']}")
            else:
                print(f"  ⚠️ Could not extract title: {error}")
            
            if is_session_healthy(nova):
                print("→ Analyzing navigation...")
                ok, response, error = safe_act_get(
                    nova,
                    "List all the navigation links you see at the top of the page (just the text of each link, separated by commas)",
                    schema={"type": "object", "properties": {"links": {"type": "string"}}, "required": ["links"]},
                    timeout=20
                )
                if ok and response:
                    nav_text = response.get('links', '')
                    analysis['navigation'] = [link.strip() for link in nav_text.split(',') if link.strip()]
                    print(f"  Navigation: {analysis['navigation']}")
                else:
                    print(f"  ⚠️ Could not extract navigation: {error}")
            
            if is_session_healthy(nova):
                print("→ Understanding page purpose...")
                ok, response, error = safe_act_get(
                    nova,
                    "In one sentence, what does this page help users do?",
                    schema={"type": "object", "properties": {"purpose": {"type": "string"}}, "required": ["purpose"]},
                    timeout=20
                )
                if ok and response:
                    analysis['purpose'] = response.get('purpose', 'Unknown purpose')
                    print(f"  Purpose: {analysis['purpose']}")
                else:
                    print(f"  ⚠️ Could not extract purpose: {error}")
            
            if is_session_healthy(nova):
                print("→ Checking for key elements...")
                from nova_act import BOOL_SCHEMA
                
                ok1, pricing, _ = safe_act_get(nova, "Is there any mention of pricing, cost, or plans on this page?", schema=BOOL_SCHEMA, timeout=15)
                ok2, docs, _ = safe_act_get(nova, "Is there any mention of documentation, API, or developer resources?", schema=BOOL_SCHEMA, timeout=15)
                ok3, demo, _ = safe_act_get(nova, "Is there an interactive demo or playground on this page?", schema=BOOL_SCHEMA, timeout=15)
                
                if ok1:
                    analysis['key_elements']['pricing'] = pricing
                if ok2:
                    analysis['key_elements']['documentation'] = docs
                if ok3:
                    analysis['key_elements']['demo'] = demo
                    
                print(f"  Key elements: {analysis['key_elements']}")
    
    except Exception as e:
        print(f"⚠️ Page analysis encountered error: {str(e)}")
        print("   Continuing with default analysis...")
    
    return analysis

def generate_personas(page_analysis: Dict) -> List[Dict]:
    """Step 2: Generate contextual personas."""
    print(f"\n👥 GENERATING PERSONAS")
    print("="*60)
    
    purpose = page_analysis.get('purpose', '').lower()
    personas = []
    
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
    
    personas.append({
        "name": "Marcus Johnson",
        "archetype": "business_professional",
        "age": 42,
        "tech_proficiency": "medium",
        "goals": ["Understand ROI", "Check pricing", "Evaluate ease of use"],
        "description": "Business professional evaluating tools"
    })
    
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
    """Step 3: Generate realistic test cases."""
    archetype = persona['archetype']
    has_pricing = page_analysis['key_elements'].get('pricing', False)
    has_docs = page_analysis['key_elements'].get('documentation', False)
    has_demo = page_analysis['key_elements'].get('demo', False)
    
    test_cases = []
    
    if archetype == "developer" or archetype == "tech_savvy_user":
        if has_docs:
            test_cases.append("Find and access technical documentation")
        if has_demo:
            test_cases.append("Try the interactive demo or playground")
        test_cases.append("Understand the core capabilities and features")
        
    elif archetype == "business_professional":
        test_cases.append("Quickly understand the value proposition")
        if has_pricing:
            test_cases.append("Find pricing information to evaluate cost")
        else:
            test_cases.append("Determine if pricing is available or how to get it")
        test_cases.append("Find getting started resources or contact sales")
        
    elif archetype == "beginner":
        test_cases.append("Understand what this tool does in simple terms")
        if has_demo:
            test_cases.append("Try a simple example or tutorial")
        test_cases.append("Find help or support if confused")
    
    return test_cases[:3]

def execute_exploration_step(nova, step: Dict, persona: Dict) -> Dict:
    """
    Execute a single exploration step from the dynamic strategy.
    Returns observation dict for this step.
    """
    from nova_act import BOOL_SCHEMA
    
    step_name = step['step_name']
    action_type = step['action_type']
    base_prompt = step['prompt']
    fallback_prompts = step.get('fallback_prompts', [])
    
    # Adapt prompt for persona
    prompt = adapt_prompt_for_persona(base_prompt, persona)
    
    print(f"  → {step_name}: {action_type}")
    
    observation = {
        "step": step_name,
        "action": step.get('expected_outcome', 'Check page'),
        "success": False,
        "notes": "",
        "timestamp": datetime.now().isoformat()
    }
    
    # Execute based on action type
    if action_type == "query":
        ok, response, error = safe_act_get(nova, prompt, schema=BOOL_SCHEMA, timeout=15)
        
        if not ok:
            observation['notes'] = f"Nova Act error: {error}"
            observation['success'] = False
            return observation
        
        observation['success'] = response
        observation['notes'] = step.get('expected_outcome', 'Checked') if response else f"Not found - tried: {prompt[:80]}..."
        
        # Try fallbacks if failed
        if not response and fallback_prompts:
            for i, fallback in enumerate(fallback_prompts[:2], 1):  # Limit to 2 fallbacks
                if not is_session_healthy(nova):
                    break
                    
                print(f"    Fallback {i}: Trying alternative prompt...")
                ok_fb, response_fb, error_fb = safe_act_get(nova, fallback, schema=BOOL_SCHEMA, timeout=15)
                
                if ok_fb and response_fb:
                    observation['success'] = True
                    observation['notes'] = f"Found via fallback prompt (attempt {i})"
                    break
        
        return observation
    
    elif action_type == "scroll":
        direction = step.get('direction', 'down')
        scroll_ok, scroll_error = safe_scroll(nova, direction=direction, max_attempts=2)
        
        if not scroll_ok:
            observation['notes'] = f"Scroll failed: {scroll_error}"
            observation['success'] = False
            return observation
        
        time.sleep(1)  # Let page settle
        
        # After scroll, ask the follow-up question
        ok, response, error = safe_act_get(nova, prompt, schema=BOOL_SCHEMA, timeout=15)
        
        if not ok:
            observation['notes'] = f"Scrolled but query failed: {error}"
            observation['success'] = False
        else:
            observation['success'] = response
            observation['notes'] = step.get('expected_outcome', 'Scrolled and checked') if response else "Scrolled but element not found"
        
        return observation
    
    elif action_type == "navigate":
        ok, nav_error = safe_act(nova, prompt, timeout=15)
        
        observation['success'] = ok
        observation['notes'] = "Navigation successful" if ok else f"Navigation failed: {nav_error}"
        
        return observation
    
    else:
        observation['notes'] = f"Unknown action type: {action_type}"
        return observation

def iterative_test_dynamic(persona: Dict, test_case: str, page_analysis: Dict) -> Dict:
    """
    Step 4: FULLY DYNAMIC iterative testing.
    Exploration strategy generated per test - no hardcoded logic.
    """
    print(f"\n{'='*60}")
    print(f"PERSONA: {persona['name']} ({persona['archetype']})")
    print(f"TEST CASE: {test_case}")
    print(f"{'='*60}\n")
    
    observations = []
    start_time = time.time()
    success = False
    trace_files = []
    session_failed = False
    
    # GENERATE DYNAMIC EXPLORATION STRATEGY
    print(f"→ Generating exploration strategy for '{test_case}'...")
    exploration_strategy = generate_exploration_strategy(test_case, persona, page_analysis)
    print(f"  Generated {len(exploration_strategy)} exploration steps\n")
    
    try:
        with nova_session(WEBSITE_URL, headless=True, logs_dir=LOGS_DIR) as nova:
            # Initial observation
            observations.append({
                "step": "navigate",
                "action": f"Loaded {WEBSITE_URL}",
                "success": True,
                "notes": "Page loaded successfully",
                "timestamp": datetime.now().isoformat()
            })
            
            # EXECUTE DYNAMIC EXPLORATION STRATEGY
            for i, step in enumerate(exploration_strategy, 1):
                if session_failed:
                    observations.append({
                        "step": step['step_name'],
                        "action": "Skipped",
                        "success": False,
                        "notes": "Skipped - session failed earlier",
                        "timestamp": datetime.now().isoformat()
                    })
                    continue
                
                if not is_session_healthy(nova):
                    print(f"  ⚠️ Session unhealthy, skipping remaining steps")
                    session_failed = True
                    continue
                
                print(f"\n  Step {i}/{len(exploration_strategy)}")
                observation = execute_exploration_step(nova, step, persona)
                observations.append(observation)
                
                # If this step succeeded, mark overall test as success
                if observation['success']:
                    success = True
                
                # If step failed critically, mark session as failed
                if "error" in observation['notes'].lower() and "nova act" in observation['notes'].lower():
                    session_failed = True
                    print(f"    ❌ Critical error, stopping exploration")
                    break
                
                # Brief pause between steps
                time.sleep(0.5)
    
    except Exception as e:
        observations.append({
            "step": "error",
            "action": "Exception occurred",
            "success": False,
            "notes": f"Error: {str(e)}",
            "timestamp": datetime.now().isoformat()
        })
    
    # Capture Nova Act trace files
    trace_files = get_session_traces(LOGS_DIR)
    print(f"\n  → Captured {len(trace_files)} Nova Act trace files")
    
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
    global WEBSITE_URL
    if len(sys.argv) > 1:
        WEBSITE_URL = sys.argv[1]
    
    print(f"\n🦅 FULLY DYNAMIC NOVA ACT USABILITY TEST")
    print(f"Website: {WEBSITE_URL}")
    print(f"Workspace: {WORKSPACE_DIR}")
    print(f"="*60)
    
    # Step 1: Analyze
    page_analysis = analyze_page(WEBSITE_URL)
    
    # Step 2: Generate personas
    personas = generate_personas(page_analysis)
    
    # Step 3 & 4: Test
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
            try:
                result = iterative_test_dynamic(persona, test_case, page_analysis)
                all_results.append(result)
                
                status = "✅" if result['success'] else "❌"
                print(f"\n{status} Result: {test_case} ({result['duration_seconds']}s)")
            except Exception as e:
                print(f"\n❌ CRITICAL ERROR in test: {test_case}")
                print(f"   Error: {str(e)}")
                all_results.append({
                    "persona": persona['name'],
                    "persona_archetype": persona['archetype'],
                    "tech_proficiency": persona['tech_proficiency'],
                    "test_case": test_case,
                    "success": False,
                    "duration_seconds": 0,
                    "observations": [{
                        "step": "fatal_error",
                        "action": "Test execution",
                        "success": False,
                        "notes": f"Fatal error: {str(e)}",
                        "timestamp": datetime.now().isoformat()
                    }],
                    "trace_files": [],
                    "timestamp": datetime.now().isoformat()
                })
                continue
    
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
    print(f"✅ DYNAMIC TEST COMPLETE")
    print(f"Success Rate: {success_count}/{total} ({success_count/total*100:.1f}%)")
    print(f"Results: {RESULTS_FILE}")
    print(f"='*60}")
    
    # Generate report
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
