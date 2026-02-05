#!/usr/bin/env python3
"""
Robust wrapper for Nova Act calls with error handling and timeout protection.
"""

import time
import functools
from typing import Any, Callable, Optional

class NovaActTimeout(Exception):
    """Raised when a Nova Act operation times out."""
    pass

class NovaActError(Exception):
    """Raised when a Nova Act operation fails."""
    pass

def with_timeout(timeout_seconds: int = 30):
    """
    Decorator to add timeout protection to Nova Act calls.
    If the call takes longer than timeout_seconds, raise NovaActTimeout.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            import signal
            
            def timeout_handler(signum, frame):
                raise NovaActTimeout(f"Operation timed out after {timeout_seconds}s")
            
            # Set up timeout (Unix only)
            try:
                old_handler = signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(timeout_seconds)
                try:
                    result = func(*args, **kwargs)
                finally:
                    signal.alarm(0)
                    signal.signal(signal.SIGALRM, old_handler)
                return result
            except AttributeError:
                # Windows doesn't have SIGALRM, fall back to no timeout
                return func(*args, **kwargs)
        
        return wrapper
    return decorator

def safe_act(nova, action: str, timeout: int = 20, max_retries: int = 1) -> tuple[bool, Optional[str]]:
    """
    Safely execute a Nova Act action with error handling.
    
    Returns:
        (success: bool, error_message: Optional[str])
    """
    for attempt in range(max_retries):
        try:
            start = time.time()
            nova.act(action)
            duration = time.time() - start
            
            # Detect if it took suspiciously long (possible loop)
            if duration > 15:
                return False, f"Action took {duration:.1f}s (possible scroll loop or hang)"
            
            return True, None
            
        except Exception as e:
            error_msg = str(e)
            
            # Check for common Nova Act errors
            if "timeout" in error_msg.lower():
                return False, "Nova Act timeout - page may be unresponsive"
            elif "element not found" in error_msg.lower():
                return False, "Element not found on page"
            elif "scroll" in error_msg.lower() and "loop" in error_msg.lower():
                return False, "Scroll loop detected"
            elif attempt < max_retries - 1:
                time.sleep(2)  # Brief pause before retry
                continue
            else:
                return False, f"Nova Act error: {error_msg}"
    
    return False, "Max retries exceeded"

def safe_act_get(nova, query: str, schema: Any, timeout: int = 20, max_retries: int = 1) -> tuple[bool, Any, Optional[str]]:
    """
    Safely execute a Nova Act query with error handling.
    
    Returns:
        (success: bool, response: Any, error_message: Optional[str])
    """
    for attempt in range(max_retries):
        try:
            start = time.time()
            result = nova.act_get(query, schema=schema)
            duration = time.time() - start
            
            # Detect if it took suspiciously long
            if duration > 15:
                return False, None, f"Query took {duration:.1f}s (possible hang)"
            
            return True, result.parsed_response, None
            
        except Exception as e:
            error_msg = str(e)
            
            if "timeout" in error_msg.lower():
                return False, None, "Nova Act timeout"
            elif attempt < max_retries - 1:
                time.sleep(2)
                continue
            else:
                return False, None, f"Nova Act error: {error_msg}"
    
    return False, None, "Max retries exceeded"

def safe_scroll(nova, direction: str = "down", max_attempts: int = 3) -> tuple[bool, Optional[str]]:
    """
    Safely scroll with loop detection.
    
    Args:
        nova: Nova Act session
        direction: "down" or "up"
        max_attempts: Max scroll attempts before declaring loop
    
    Returns:
        (success: bool, error_message: Optional[str])
    """
    previous_positions = []
    
    for attempt in range(max_attempts):
        try:
            # Try to get current scroll position (if possible)
            start = time.time()
            
            if direction == "down":
                nova.act("Scroll down to see more content")
            else:
                nova.act("Scroll up")
            
            duration = time.time() - start
            
            # If scroll takes too long, probably stuck
            if duration > 10:
                return False, "Scroll operation taking too long (possible loop)"
            
            # Small delay to let page settle
            time.sleep(1)
            
            return True, None
            
        except Exception as e:
            error_msg = str(e)
            if "scroll" in error_msg.lower() and "loop" in error_msg.lower():
                return False, "Scroll loop detected by Nova Act"
            elif attempt < max_attempts - 1:
                time.sleep(2)
                continue
            else:
                return False, f"Scroll error: {error_msg}"
    
    return False, "Scroll stuck (max attempts)"

def is_session_healthy(nova) -> bool:
    """
    Quick health check to see if Nova Act session is still responsive.
    
    Returns:
        True if session is healthy, False otherwise
    """
    try:
        start = time.time()
        # Simple query that should always work
        result = nova.act_get(
            "Is there any text visible on the page?",
            schema={"type": "boolean"}
        )
        duration = time.time() - start
        
        # If it takes more than 10s for a simple check, session is degraded
        return duration < 10 and result.parsed_response is not None
        
    except:
        return False
