# Nova Act Cookbook

Best practices for using Amazon Nova Act effectively in usability testing.

## Core Principles

### 0. Nova Act Matching Behavior

**CRITICAL:** Nova Act has two matching modes:

**Exact Matching (with quotes):**
- `"Documentation"` → Only matches the exact word "Documentation"
- `"API Documentation"` → Only matches that exact phrase
- Use for precise element identification

**Loose Matching (without quotes):**
- `Documentation` → Can match "Documentation", "Docs", "API Documentation", etc.
- More flexible, fuzzy matching
- Use for broader searches

❌ **WRONG:** Using quotes when you want flexible matching
```python
# This is too strict - will miss "API Docs", "Developer Docs", etc.
nova.act_get('Is there a link labeled "Documentation"?')
```

✅ **RIGHT:** Use quotes strategically
```python
# Loose matching - finds variations
nova.act_get('Is there a link with Documentation in it?')

# Exact matching - when you know the precise text
nova.act_get('Click the link that says "Sign Up"')
```

**Best Practice:** When searching for elements:
1. Start broad (no quotes): "What links do you see in the navigation?"
2. Use loose matching first: "Is there a link with Documentation?"
3. If you need precision: Use quotes for exact text matching
4. Try variations if first attempt fails

### 1. Break Tasks into Small Steps

Nova Act works most reliably when tasks can be accomplished in **fewer than 30 steps**.

❌ DON'T: Single large act() call
```python
nova.act("book me a hotel that costs less than $100 with highest rating then find car rental and book lunch")
```

✅ DO: Multiple small act() calls
```python
hotel = nova.act_get("book a hotel for $100 or less, return the address")
nova.act(f"book restaurant near {hotel.response} at 12:30pm")
nova.act(f"rent a car near {hotel.response}")
```

### 2. Be Direct and Specific

Make prompts clear about exactly what should happen.

❌ DON'T: Vague instructions
```python
nova.act("Let's see what routes are available")
```

✅ DO: Direct instructions  
```python
nova.act("Navigate to the routes tab")
```

### 3. Extract Information with Schemas

Use `act_get()` with Pydantic schemas for structured data extraction.

```python
from pydantic import BaseModel

class PricingInfo(BaseModel):
    price: float
    currency: str
    features: list[str]

result = nova.act_get(
    "Find the pricing information on this page",
    schema=PricingInfo.model_json_schema()
)

pricing = PricingInfo.model_validate(result.parsed_response)
```

### 4. Observe and Analyze Each Step

After each `act()` call, analyze the result before deciding the next action.

```python
# Navigate to page
nova.act("Go to the pricing page")

# Check if successful
is_found = nova.act_get(
    "Is there a pricing table visible on this page?",
    schema=BOOL_SCHEMA
)

if is_found.parsed_response:
    # Extract pricing
    pricing = nova.act_get("Extract all pricing tiers", schema=PricingSchema)
else:
    # Try alternative path
    nova.act("Look for a 'Plans' or 'Subscribe' link")
```

### 5. Use Playwright for Fine Control

For sensitive data or precise actions, use Playwright APIs directly:

```python
# Focus on field with act(), then type with Playwright
nova.act("click on the password field")
nova.page.keyboard.type(password)  # Doesn't send over network
nova.act("click sign in")
```

## Common Patterns

### Navigation Testing
```python
# Check if navigation is clear
nova.act("Navigate to the main menu")
is_clear = nova.act_get(
    "Are the menu items clearly labeled and easy to understand?",
    schema=BOOL_SCHEMA
)
```

### Form Filling
```python
# Fill forms step by step
nova.act("Click on the signup form")
nova.act("Enter email address test@example.com")
nova.act("Enter name 'John Doe'")
result = nova.act_get("Is there a clear submit button visible?")
```

### Search Testing
```python
# Test search functionality
nova.act("search for 'pricing'. press enter to initiate search")
results = nova.act_get(
    "Are search results relevant to 'pricing'?",
    schema=BOOL_SCHEMA
)
```

### Information Architecture
```python
# Test if information is findable
time_to_find = measure_time()
nova.act("Find the contact information")
duration = time_to_find()

# Note: If it took >30 steps or multiple attempts, that's a UX issue
```

## Persona Adaptation

Adjust act() prompts based on persona tech proficiency:

**Low proficiency (elderly user):**
```python
# More explicit, step-by-step
nova.act("Look for a button that says 'Contact' or 'Contact Us'")
nova.act("Click on the Contact button")
```

**High proficiency (power user):**
```python
# Test efficiency paths
nova.act("Find keyboard shortcut for search")
nova.act("Use keyboard shortcut to open search")
```

## Error Handling

```python
try:
    result = nova.act("Complete checkout")
except ActAgentError as e:
    # Agent couldn't complete - this is a UX issue!
    note_friction_point(
        "Checkout flow failed - agent couldn't figure it out",
        error=str(e)
    )
```

## Iterative Exploration Pattern

For usability testing, use an **explore-adapt-verify** approach:

**Step 1: Broad Discovery**
```python
# Don't assume - ask what's there
nav_items = nova.act_get("What navigation links do you see at the top?", schema=StringArraySchema)
```

**Step 2: Adapt Based on Findings**
```python
# If you found "API Documentation", now search for it specifically
if "API" in nav_items:
    nova.act("Click on the link containing 'API'")
```

**Step 3: Verify Hypothesis Multiple Ways**
```python
# Hypothesis: "Users can't find pricing"
# Approach 1: Check nav
has_nav_pricing = nova.act_get("Is 'Pricing' in the navigation?", schema=BOOL_SCHEMA)

# Approach 2: Check page body
if not has_nav_pricing:
    nova.act("Scroll down")
    has_body_pricing = nova.act_get("Do you see pricing or cost information?", schema=BOOL_SCHEMA)

# Approach 3: Check variations
if not has_body_pricing:
    has_plans = nova.act_get("Do you see 'Plans' or 'Subscribe'?", schema=BOOL_SCHEMA)
```

## Nova Act Trace Files

**Nova Act automatically generates detailed HTML trace files** for every session!

These trace files contain:
- Screenshots at each step
- AI reasoning and decisions
- Actions taken and their results
- Full timeline of the session

**Where to find them:**
- Set `logs_directory` when creating NovaAct instance
- Files are named: `act_<uuid>_output.html`
- Each test captures these files
- **Linked automatically in the HTML report**

```python
with NovaAct(
    starting_page=url,
    logs_directory="/path/to/logs"  # Set custom directory
) as nova:
    nova.act("Navigate somewhere")
    # Trace file automatically created
```

## Usability Observations

Document friction points as you observe them:

- **Task failed after multiple approaches** = Major UX issue
- **Found after 2+ attempts** = Moderate UX issue (discoverability)
- **Found but unclear label** = Minor UX issue
- **Small text, poor contrast** = Accessibility issue
- **>20 steps for simple task** = Efficiency issue
