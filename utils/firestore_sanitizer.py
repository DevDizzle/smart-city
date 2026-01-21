from typing import Any, Dict, List

def sanitize_for_firestore(data: Any) -> Any:
    """
    Sanitizes data to be compatible with Firestore restrictions.
    - Converts lists of lists to string representations (Firestore doesn't support nested arrays).
    - Recursively handles dicts and lists.
    """
    if isinstance(data, dict):
        return {k: sanitize_for_firestore(v) for k, v in data.items()}
    
    if isinstance(data, list):
        # Check if any element is a list
        if any(isinstance(item, list) for item in data):
            # Found nested list! Convert entire list to string to be safe and simple
            return str(data)
        
        # Otherwise, process items normally
        return [sanitize_for_firestore(item) for item in data]
    
    return data
