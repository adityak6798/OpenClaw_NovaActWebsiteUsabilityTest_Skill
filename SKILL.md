---
name: nova-act-usability
description: AI-orchestrated usability testing using Amazon Nova Act. Dynamically generates test plans, simulates realistic user interactions with digital twin personas, observes and analyzes each interaction step-by-step, and produces comprehensive HTML usability reports with links to detailed session recordings. Use when asked to "test website usability", "run usability test", "generate usability report", "evaluate user experience", or "analyze website UX" for any web application.
---

# Nova Act Usability Testing

**AI-orchestrated** usability testing with digital twin personas powered by Amazon Nova Act.

## User Invocation

Users can trigger this skill by saying:
- "Test the usability of [website URL]"
- "Run a usability test on [website URL]"
- "Generate a usability report for [website URL]"
- "Evaluate the UX of [website URL]"
- "Analyze [website URL] for usability issues"

**The AI will automatically:**
1. Analyze the page to understand it
2. Generate contextual personas
3. Create realistic test cases
4. Run adaptive, iterative tests with Nova Act
5. Generate comprehensive HTML report with trace links
6. Provide viewing instructions

## How This Works

**You (the AI) are the orchestrator.** This skill provides:
1. **Nova Act cookbook** (`references/nova-act-cookbook.md`) - Best practices for using Nova Act
2. **Adaptive test orchestrator** (`run_adaptive_test.py`) - Main execution script
3. **Session management** (`scripts/nova_session.py`) - Nova Act wrapper
4. **Report generator** (`enhanced_report_generator.py`) - Auto-generated HTML reports

**Execution Flow:**

When a user asks for usability testing:

```python
# 1. Run the adaptive test script
cd /home/adity/.openclaw/workspace
export NOVA_ACT_SKIP_PLAYWRIGHT_INSTALL=1
python3.14 run_adaptive_test.py

# This will:
# - Analyze the target page
# - Generate contextual personas  
# - Create realistic test cases
# - Execute iterative Nova Act tests
# - Capture trace files
# - Auto-generate HTML report
# - Print viewing instructions
```

The script handles everything automatically. You just need to:
1. Extract the website URL from the user's request
2. Update `WEBSITE_URL` in the script (or pass as argument)
3. Run the script
4. Share the report viewing instructions with the user

## Quick Start

**When user requests usability testing:**

```python
# 1. Update the target URL in run_adaptive_test.py
# Edit: WEBSITE_URL = "https://example.com"

# 2. Run the adaptive test
exec_command = """
cd /home/adity/.openclaw/workspace && \
export NOVA_ACT_SKIP_PLAYWRIGHT_INSTALL=1 && \
python3.14 run_adaptive_test.py 2>&1
"""

# 3. The script will:
# - Analyze the page
# - Generate personas
# - Run 9 adaptive tests (3 personas × 3 tasks)
# - Auto-generate HTML report
# - Print viewing instructions

# 4. Share the viewing instructions with user
```

## Detailed Workflow (Internal)

The adaptive test script (`run_adaptive_test.py`) handles:

### Step 1: Page Analysis
- Loads the page with Nova Act
- Extracts title, navigation, purpose
- Identifies key elements (docs, demo, pricing)

### Step 2: Contextual Persona Generation
- Creates personas based on what the page offers
- Developer persona if API/code focused
- Business persona for evaluation
- Beginner persona if demo available

### Step 3: Realistic Test Case Generation
- Top 3 use cases per persona
- Based on actual page content
- Matched to persona goals

### Step 4: Iterative Test Execution

For each persona + task combination:

```python
from scripts.nova_session import nova_session
from nova_act import BOOL_SCHEMA
import time

observations = []

with nova_session(website_url) as nova:
    start_time = time.time()
    
    # Initial navigation
    observations.append({
        "step": "navigate",
        "action": f"Loaded {website_url}",
        "success": True,
        "notes": "Initial page load"
    })
    
    # Execute task step-by-step (AI-orchestrated)
    # Break into small act() calls based on cookbook guidance
    
    # Example: "Find pricing information" task
    
    # Step 1: Look for pricing link
    nova.act("Look for a link or button for pricing, plans, or subscription")
    found = nova.act_get(
        "Is there a visible pricing or plans link?",
        schema=BOOL_SCHEMA
    )
    
    observations.append({
        "step": "find_pricing_link",
        "action": "Search for pricing navigation",
        "success": found.parsed_response,
        "notes": "Easy to find" if found.parsed_response else "Not immediately visible - UX friction"
    })
    
    if found.parsed_response:
        # Step 2: Navigate to pricing
        nova.act("Click on the pricing or plans link")
        
        # Step 3: Analyze pricing page
        is_clear = nova.act_get(
            "Is the pricing information clearly displayed with prices and features?",
            schema=BOOL_SCHEMA
        )
        
        observations.append({
            "step": "view_pricing",
            "action": "Accessed pricing page",
            "success": is_clear.parsed_response,
            "notes": "Clear pricing display" if is_clear.parsed_response else "Pricing unclear or confusing"
        })
    else:
        # Alternative path - try search
        nova.act("Look for a search function")
        # ... continue orchestrating
    
    duration = time.time() - start_time
    
    # Document overall task result
    task_success = all(obs["success"] for obs in observations if obs["success"] is not None)
    
    results.append({
        "persona": persona_name,
        "task": task_description,
        "success": task_success,
        "duration": duration,
        "observations": observations,
        "friction_points": [obs for obs in observations if not obs.get("success")]
    })
```

### Step 4: Pool and Analyze Results

After all tests:
1. Identify common friction points across personas
2. Note accessibility issues for low-tech personas
3. Flag efficiency problems (too many steps)
4. Document task failures (major UX issues)

### Step 5: Generate Report

```python
import json
from scripts.generate_report import generate_html_report

# Save results
with open("test_results.json", "w") as f:
    json.dump(results, f, indent=2)

# Generate HTML report
generate_html_report(
    results=results,
    analysis=analyze_results(results),
    template_path="assets/report-template.html",
    output_path="usability_report.html"
)
```

## Key Principles

### Dynamic Task Decomposition

The AI should decide how to break down each task based on:
- Website complexity
- Persona's technical level
- Task nature (navigation vs data entry vs search)

**Low-tech persona example:**
```python
# More explicit, step-by-step
nova.act("Look for a button labeled 'Contact' or 'Contact Us'")
nova.act("Click on the Contact button")
result = nova.act_get("Is there a phone number or email address visible?")
```

**High-tech persona example:**
```python
# Test efficiency features
nova.act("Look for keyboard shortcuts or quick access features")
nova.act("Try to use search (Ctrl+K or Cmd+K)")
```

### Real-Time Observation

After EVERY `act()` call, analyze:
- Did it succeed?
- Was the UI element easy to find?
- Was the label clear?
- How many attempts needed?
- Any error messages?

Document friction immediately in observations.

### Persona-Aware Prompting

Adapt `act()` prompts to persona characteristics:
- **Elderly/low-tech:** Look for obvious, labeled buttons; read everything
- **Power users:** Try keyboard shortcuts, advanced features
- **Mobile users:** Test mobile responsiveness, touch targets
- **Screen reader users:** Test keyboard navigation, ARIA labels

## Resources

### `references/nova-act-cookbook.md`
**MUST READ before starting any test.** Contains best practices for:
- Effective act() prompting
- Task decomposition strategies
- Data extraction patterns
- Error handling
- Persona adaptation

### `references/persona-examples.md`
Template personas with detailed profiles:
- Tech-savvy millennial
- Elderly first-timer
- Busy professional
- Student/budget-conscious
- Accessibility-focused
- International/non-native speaker

### `scripts/nova_session.py`
Thin wrapper providing Nova Act session primitive:
```python
with nova_session(url, headless=True) as nova:
    nova.act("action")
    result = nova.act_get("query", schema=Schema)
```

### `scripts/generate_report.py`
Compiles observations into HTML usability report.

### `assets/report-template.html`
Professional HTML template for usability reports.

## Prerequisites

### Nova Act Configuration

API key stored in `~/.openclaw/config/nova-act.json`:
```json
{
  "apiKey": "your-key-here",
  "region": "us-east-1"
}
```

### Nova Act SDK

```bash
pip install nova-act
```

## Example: AI-Orchestrated Test

**User request:** "Test example.com for elderly users"

**AI orchestration:**

1. Read `references/nova-act-cookbook.md`
2. Read `references/persona-examples.md`
3. Generate elderly persona (Dorothy, 72, low tech proficiency)
4. Generate tasks:
   - "Find contact information"
   - "Read about services"
   - "Navigate to FAQ"
5. For each task, dynamically orchestrate Nova Act:
   - Start session
   - Execute small act() steps
   - Observe and analyze each result
   - Take notes on friction (small text, unclear labels, etc.)
   - Continue or adapt based on observations
6. Pool observations
7. Generate HTML report with findings and recommendations

**The AI decides every step.** The skill just provides tools and guidance.
