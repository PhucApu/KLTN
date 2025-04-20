import re

def is_theory(text):
    definition_patterns = [
        r"\b(\w+)\s+là\s+(?!là)\w+",  # Tránh "là là"
        r"\b(\w+)\s+được gọi là\s+\w+",
        r"\b(\w+)\s+còn gọi là\s+\w+",
        r"\b(\w+)\s+được định nghĩa là\s+\w+",
        r"\b(\w+)\s+có nghĩa là\s+\w+"
    ]
    
    for pattern in definition_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
        elif text == '':
            return False
    return False