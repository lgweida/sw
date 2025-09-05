#!/usr/bin/env python3
"""
FIX Message Preview - Quick look at FIX message structure
"""

def preview_fix_message(message):
    """Quick preview of FIX message structure"""
    print("FIX Message Preview:")
    print("-" * 50)
    
    if '\x01' in message:
        fields = message.split('\x01')
    else:
        fields = re.split(r'[|=]', message)
    
    for field in fields:
        if '=' in field:
            tag, value = field.split('=', 1)
            print(f"Tag {tag:>3}: {value}")
    
    print("-" * 50)

# Example usage
sample_message = "8=FIX.4.2|35=D|54=1|38=100|55=AAPL|40=2|44=150.25|59=1"
preview_fix_message(sample_message)