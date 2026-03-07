#!/usr/bin/env python3
"""
Debug Mobile Detection
Quick test script to check mobile detection functionality
"""

def test_mobile_detection():
    print("Testing Mobile Detection Logic...")
    
    # Simulate different user agents
    test_cases = [
        {
            'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
            'expected': True,
            'device': 'iPhone'
        },
        {
            'user_agent': 'Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Mobile Safari/537.36',
            'expected': True,
            'device': 'Android Phone'
        },
        {
            'user_agent': 'Mozilla/5.0 (iPad; CPU OS 13_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/80.0.3987.95 Mobile/15E148 Safari/604.1',
            'expected': True,
            'device': 'iPad'
        },
        {
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'expected': False,
            'device': 'Desktop Chrome'
        },
        {
            'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'expected': False,
            'device': 'Desktop Mac'
        }
    ]
    
    import re
    MOBILE_AGENTS = re.compile(r'Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini|Mobile|mobile|CriOS', re.IGNORECASE)
    TABLET_AGENTS = re.compile(r'iPad|tablet|Tablet', re.IGNORECASE)
    
    def is_mobile_simulation(user_agent):
        if MOBILE_AGENTS.search(user_agent):
            return True
        if TABLET_AGENTS.search(user_agent):
            return True
        if 'Mobile' in user_agent:
            return True
        return False
    
    print("\n=== Mobile Detection Test Results ===")
    for case in test_cases:
        result = is_mobile_simulation(case['user_agent'])
        status = "✅ PASS" if result == case['expected'] else "❌ FAIL"
        print(f"{status} {case['device']}: Expected {case['expected']}, Got {result}")
        if result != case['expected']:
            print(f"   User Agent: {case['user_agent'][:100]}...")
    
    print("\n=== Template Name Generation Test ===")
    def get_template_name_simulation(base_template, is_mobile_device):
        if not is_mobile_device:
            return base_template
        
        template_parts = base_template.split('/')
        if len(template_parts) > 1:
            folder = template_parts[0]
            filename = template_parts[1]
            name_without_ext = filename.replace('.html', '')
            mobile_filename = f'mobile_{name_without_ext}.html'
            return f'{folder}/{mobile_filename}'
        else:
            name_without_ext = base_template.replace('.html', '')
            return f'mobile_{name_without_ext}.html'
    
    template_tests = [
        'main/dashboard_complete.html',
        'auth/login.html',
        'social/feed.html',
        'index.html'
    ]
    
    for template in template_tests:
        mobile_template = get_template_name_simulation(template, True)
        desktop_template = get_template_name_simulation(template, False)
        print(f"Desktop: {desktop_template}")
        print(f"Mobile:  {mobile_template}")
        print()

if __name__ == '__main__':
    test_mobile_detection()
