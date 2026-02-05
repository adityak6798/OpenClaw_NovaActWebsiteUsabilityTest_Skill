#!/usr/bin/env python3
"""
Dynamic exploration strategy generator.
Uses AI to generate contextual Nova Act prompts instead of hardcoded logic.
"""

from typing import Dict, List, Tuple
import json

def generate_exploration_strategy(
    test_case: str,
    persona: Dict,
    page_analysis: Dict
) -> List[Dict]:
    """
    Generate a dynamic exploration strategy for a given test case.
    
    Returns a list of exploration steps, each containing:
    - step_name: Human-readable step name
    - action_type: "query" or "navigate" or "scroll"
    - prompt: The actual Nova Act prompt to use
    - expected_outcome: What we're looking for
    - fallback_prompts: Alternative prompts if first fails
    
    This replaces hardcoded if/elif logic with contextual prompts.
    """
    
    # Extract context
    archetype = persona.get('archetype', 'user')
    tech_level = persona.get('tech_proficiency', 'medium')
    page_title = page_analysis.get('title', 'this page')
    navigation = page_analysis.get('navigation', [])
    key_elements = page_analysis.get('key_elements', {})
    
    strategy = []
    
    # Analyze the test case and generate appropriate exploration steps
    test_lower = test_case.lower()
    
    # ===== DOCUMENTATION / TECHNICAL RESOURCES =====
    if any(keyword in test_lower for keyword in ['documentation', 'docs', 'api', 'technical', 'developer']):
        # Step 1: Look in navigation first
        strategy.append({
            "step_name": "check_navigation_for_docs",
            "action_type": "query",
            "prompt": f"Is there a navigation link related to documentation, API, developer resources, or technical guides?",
            "expected_outcome": "Find docs link in nav",
            "fallback_prompts": [
                "Do you see any link with 'Docs', 'API', 'Developer', 'Guide', or 'Reference'?",
                "Is there a 'Resources' or 'Learn' section in the navigation?"
            ]
        })
        
        # Step 2: Check page content if nav fails
        strategy.append({
            "step_name": "check_page_for_docs",
            "action_type": "query",
            "prompt": f"Looking at the main content area, is there any mention of documentation, getting started guides, or technical resources?",
            "expected_outcome": "Find docs reference in content",
            "fallback_prompts": [
                "Are there any code snippets, API examples, or technical documentation visible?",
                f"Does {page_title} explain how developers can use or integrate this?"
            ]
        })
        
        # Tech-savvy users might look for specific things
        if tech_level == "high":
            strategy.append({
                "step_name": "check_advanced_docs",
                "action_type": "query",
                "prompt": "Are there links to GitHub, SDK downloads, or API reference documentation?",
                "expected_outcome": "Find advanced technical resources",
                "fallback_prompts": []
            })
    
    # ===== DEMO / INTERACTIVE FEATURES =====
    elif any(keyword in test_lower for keyword in ['demo', 'playground', 'try', 'interactive', 'example']):
        # Step 1: Look for interactive elements
        strategy.append({
            "step_name": "find_interactive_element",
            "action_type": "query",
            "prompt": "Is there an input field, text box, or interactive area where you can try something out?",
            "expected_outcome": "Find interactive element on page",
            "fallback_prompts": [
                "Do you see a 'Try it', 'Demo', or 'Playground' button or section?",
                "Is there anywhere you can type or interact with a live example?"
            ]
        })
        
        # Step 2: Check navigation
        strategy.append({
            "step_name": "check_nav_for_demo",
            "action_type": "query",
            "prompt": "Is there a navigation link for 'Demo', 'Playground', 'Try', or 'Examples'?",
            "expected_outcome": "Find demo link in navigation",
            "fallback_prompts": [
                "Do you see 'Get Started', 'Live Demo', or 'Interactive' in the menu?"
            ]
        })
        
        # Beginners need obvious calls-to-action
        if tech_level == "low":
            strategy.append({
                "step_name": "check_prominent_cta",
                "action_type": "query",
                "prompt": "Is there a large, obvious button near the top that invites you to try or start using the tool?",
                "expected_outcome": "Find beginner-friendly CTA",
                "fallback_prompts": []
            })
    
    # ===== PRICING / COST INFORMATION =====
    elif any(keyword in test_lower for keyword in ['pricing', 'price', 'cost', 'plan', 'subscription', 'fee']):
        # Step 1: Navigation check
        strategy.append({
            "step_name": "check_nav_for_pricing",
            "action_type": "query",
            "prompt": "Is there a 'Pricing', 'Plans', or 'Cost' link in the navigation menu?",
            "expected_outcome": "Find pricing in navigation",
            "fallback_prompts": [
                "Do you see 'Subscribe', 'Buy', or 'Get Started' with pricing info?",
                "Is there a 'Free' or 'Pro' tier mentioned in the navigation?"
            ]
        })
        
        # Step 2: Visible pricing on current page
        strategy.append({
            "step_name": "check_visible_pricing",
            "action_type": "query",
            "prompt": "Is there any pricing information, cost, or subscription tiers visible on the current page?",
            "expected_outcome": "Find pricing in content",
            "fallback_prompts": [
                "Do you see dollar amounts, price tags, or cost comparisons?",
                "Is there mention of 'free', 'premium', or different plan levels?"
            ]
        })
        
        # Step 3: Scroll for pricing
        strategy.append({
            "step_name": "scroll_for_pricing",
            "action_type": "scroll",
            "direction": "down",
            "prompt": "After scrolling, do you now see any pricing, cost, or subscription information?",
            "expected_outcome": "Find pricing after scroll",
            "fallback_prompts": []
        })
        
        # Business users care about transparency
        if archetype == "business_professional":
            strategy.append({
                "step_name": "check_transparent_pricing",
                "action_type": "query",
                "prompt": "If pricing is visible, are the actual dollar amounts clearly displayed, or is it 'contact us' / 'request quote'?",
                "expected_outcome": "Assess pricing transparency",
                "fallback_prompts": []
            })
    
    # ===== VALUE PROPOSITION / UNDERSTANDING =====
    elif any(keyword in test_lower for keyword in ['understand', 'value', 'what', 'purpose', 'does', 'benefit']):
        # Step 1: Check hero section
        strategy.append({
            "step_name": "check_hero_tagline",
            "action_type": "query",
            "prompt": "Near the top of the page, is there a clear headline or tagline that explains what this tool/product does or what problem it solves?",
            "expected_outcome": "Find clear value proposition",
            "fallback_prompts": [
                f"Does {page_title} have a sentence that tells you immediately what it's for?",
                "Is the main benefit or use case explained prominently?"
            ]
        })
        
        # Step 2: Supporting copy
        strategy.append({
            "step_name": "check_supporting_copy",
            "action_type": "query",
            "prompt": "Below the main headline, is there supporting text that elaborates on features, benefits, or how it works?",
            "expected_outcome": "Find detailed explanation",
            "fallback_prompts": [
                "Are there bullet points, feature lists, or use cases described?",
                "Can you quickly understand what makes this different or useful?"
            ]
        })
        
        # Beginners need simple language
        if tech_level == "low":
            strategy.append({
                "step_name": "check_simple_language",
                "action_type": "query",
                "prompt": "Is the description written in simple, non-technical language that anyone could understand?",
                "expected_outcome": "Assess language clarity",
                "fallback_prompts": [
                    "Are there lots of jargon, acronyms, or technical terms that might confuse a beginner?"
                ]
            })
    
    # ===== HELP / SUPPORT =====
    elif any(keyword in test_lower for keyword in ['help', 'support', 'contact', 'assistance', 'faq']):
        # Step 1: Header check
        strategy.append({
            "step_name": "check_header_for_help",
            "action_type": "query",
            "prompt": "In the top navigation or header area, is there a 'Help', 'Support', 'Contact', or 'FAQ' link?",
            "expected_outcome": "Find help in header",
            "fallback_prompts": [
                "Do you see 'Get Help', 'Contact Us', 'Support Center', or similar?",
                "Is there a question mark icon or help button visible?"
            ]
        })
        
        # Step 2: Footer check (scroll required)
        strategy.append({
            "step_name": "scroll_to_footer",
            "action_type": "scroll",
            "direction": "down",
            "prompt": "In the footer area, is there a 'Help', 'Support', 'Contact', or 'FAQ' link?",
            "expected_outcome": "Find help in footer",
            "fallback_prompts": [
                "Do you see contact email, phone number, or support links at the bottom?",
                "Is there a 'Help Center' or 'Resources' section in the footer?"
            ]
        })
        
        # Beginners might need more obvious help options
        if tech_level == "low":
            strategy.append({
                "step_name": "check_chat_widget",
                "action_type": "query",
                "prompt": "Is there a chat widget, chatbot, or live support button visible anywhere on the page?",
                "expected_outcome": "Find live help option",
                "fallback_prompts": []
            })
    
    # ===== GETTING STARTED / ONBOARDING =====
    elif any(keyword in test_lower for keyword in ['getting started', 'get started', 'onboard', 'begin', 'setup']):
        strategy.append({
            "step_name": "check_cta",
            "action_type": "query",
            "prompt": "Is there a prominent 'Get Started', 'Sign Up', 'Try Now', or 'Start Free' button or call-to-action?",
            "expected_outcome": "Find getting started CTA",
            "fallback_prompts": [
                "What's the main action button on this page?",
                "How would a new user begin using this product?"
            ]
        })
        
        strategy.append({
            "step_name": "check_onboarding_guide",
            "action_type": "query",
            "prompt": "Is there a 'Getting Started Guide', 'Quick Start', or step-by-step tutorial linked or visible?",
            "expected_outcome": "Find onboarding resources",
            "fallback_prompts": [
                "Are there numbered steps or a 'how to get started' section?",
                "Does the page explain the first steps clearly?"
            ]
        })
    
    # ===== GENERIC FALLBACK =====
    else:
        # If we don't recognize the test case, generate generic exploration
        strategy.append({
            "step_name": "understand_task",
            "action_type": "query",
            "prompt": f"As a {archetype} with {tech_level} technical skills, can you easily accomplish this task: '{test_case}'?",
            "expected_outcome": "Generic task assessment",
            "fallback_prompts": [
                f"Is it obvious how to {test_case} on this page?",
                f"Where would you look to {test_case}?"
            ]
        })
        
        strategy.append({
            "step_name": "check_navigation",
            "action_type": "query",
            "prompt": f"Looking at the navigation menu, is there any link that seems related to: {test_case}?",
            "expected_outcome": "Find relevant nav link",
            "fallback_prompts": []
        })
    
    return strategy


def adapt_prompt_for_persona(base_prompt: str, persona: Dict) -> str:
    """
    Adapt a prompt based on persona characteristics.
    
    E.g., for low-tech users, make prompts more explicit about looking for obvious elements.
    For high-tech users, look for efficiency and advanced features.
    """
    tech_level = persona.get('tech_proficiency', 'medium')
    archetype = persona.get('archetype', 'user')
    
    # Low-tech users: emphasize obvious, large, clearly labeled elements
    if tech_level == "low":
        if "link" in base_prompt.lower():
            return base_prompt.replace("link", "clearly labeled link or button")
        if "find" in base_prompt.lower():
            return base_prompt.replace("find", "easily find")
    
    # High-tech users: look for shortcuts and advanced features
    elif tech_level == "high":
        if "documentation" in base_prompt.lower():
            return base_prompt + " Also note if there are keyboard shortcuts or advanced search features."
    
    # Business users: emphasize clarity and trust signals
    if archetype == "business_professional":
        if "pricing" in base_prompt.lower():
            return base_prompt + " Note if there are enterprise options or 'contact sales' mentions."
    
    return base_prompt


def generate_fallback_questions(failed_step: Dict, context: Dict) -> List[str]:
    """
    If a step fails, generate contextual follow-up questions to try.
    
    This allows the test to adapt when the first approach doesn't work.
    """
    step_name = failed_step.get('step_name', '')
    
    fallbacks = []
    
    # If navigation check failed, try content area
    if 'navigation' in step_name or 'nav' in step_name:
        fallbacks.append("Ignoring the navigation menu, is the information visible anywhere in the main content area?")
        fallbacks.append("Is there a search box where you could search for this?")
    
    # If exact match failed, try fuzzy matching
    if 'exact' in step_name or 'specific' in step_name:
        fallbacks.append("Using different wording, is there anything similar or related visible?")
        fallbacks.append("What IS visible that might be related?")
    
    # If scroll didn't help, try other strategies
    if 'scroll' in step_name:
        fallbacks.append("Back at the top of the page, did we miss anything obvious?")
        fallbacks.append("Is there a sitemap, footer navigation, or breadcrumbs that might help?")
    
    return fallbacks
