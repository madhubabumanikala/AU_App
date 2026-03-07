"""
Mobile Device Detection Utility
"""
import re
from flask import request

class MobileDetector:
    """Utility class to detect mobile devices and serve appropriate templates"""
    
    # Mobile user agents regex pattern
    MOBILE_AGENTS = re.compile(r'Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini|Mobile|mobile|CriOS', re.IGNORECASE)
    
    # Tablet user agents (treated as mobile for our PWA)
    TABLET_AGENTS = re.compile(r'iPad|tablet|Tablet', re.IGNORECASE)
    
    @classmethod
    def is_mobile(cls):
        """
        Detect if current request is from a mobile device
        Returns True for mobile devices, False for desktop
        """
        user_agent = request.headers.get('User-Agent', '')
        
        # Check for mobile patterns in user agent
        if cls.MOBILE_AGENTS.search(user_agent):
            return True
            
        # Check for tablet patterns
        if cls.TABLET_AGENTS.search(user_agent):
            return True
            
        # Check for small screen size hint (if provided)
        if 'Mobile' in request.headers.get('User-Agent', ''):
            return True
            
        return False
    
    @classmethod
    def get_template_name(cls, base_template, mobile_template=None):
        """
        Get appropriate template name based on device type
        
        Args:
            base_template: Desktop template name (e.g., 'auth/login.html')
            mobile_template: Mobile template name (e.g., 'auth/mobile_login.html')
                           If None, will auto-generate mobile template name
        
        Returns:
            Template name to use
        """
        if not cls.is_mobile():
            return base_template
            
        # If mobile template is explicitly provided, use it
        if mobile_template:
            return mobile_template
            
        # Auto-generate mobile template name
        template_parts = base_template.split('/')
        if len(template_parts) > 1:
            # For templates like 'auth/login.html', convert to 'auth/mobile_login.html'
            folder = template_parts[0]
            filename = template_parts[1]
            
            # Remove .html extension, add mobile_ prefix, add extension back
            name_without_ext = filename.replace('.html', '')
            mobile_filename = f'mobile_{name_without_ext}.html'
            
            return f'{folder}/{mobile_filename}'
        else:
            # For templates like 'index.html', convert to 'mobile_index.html'
            name_without_ext = base_template.replace('.html', '')
            return f'mobile_{name_without_ext}.html'
    
    @classmethod
    def get_device_type(cls):
        """
        Get device type string
        Returns: 'mobile', 'tablet', or 'desktop'
        """
        user_agent = request.headers.get('User-Agent', '')
        
        if cls.TABLET_AGENTS.search(user_agent):
            return 'tablet'
        elif cls.MOBILE_AGENTS.search(user_agent):
            return 'mobile'
        else:
            return 'desktop'
    
    @classmethod
    def should_use_mobile_layout(cls):
        """
        Determine if mobile layout should be used
        Returns True for mobile and tablet devices
        """
        return cls.is_mobile()
    
    @classmethod
    def get_viewport_meta(cls):
        """
        Get appropriate viewport meta tag content
        """
        if cls.is_mobile():
            return "width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no"
        else:
            return "width=device-width, initial-scale=1.0"
    
    @classmethod
    def get_css_classes(cls):
        """
        Get CSS classes to apply to body based on device type
        """
        device_type = cls.get_device_type()
        classes = [f'device-{device_type}']
        
        if cls.is_mobile():
            classes.append('mobile-device')
        else:
            classes.append('desktop-device')
            
        return ' '.join(classes)

# Template helper function
def mobile_template(template_name, mobile_template=None):
    """
    Template helper function to get appropriate template
    Usage in routes:
        return render_template(mobile_template('auth/login.html'))
    """
    return MobileDetector.get_template_name(template_name, mobile_template)

# Context processor to make mobile detection available in templates
def mobile_context_processor():
    """
    Context processor to add mobile detection variables to all templates
    """
    return {
        'is_mobile_device': MobileDetector.is_mobile(),
        'device_type': MobileDetector.get_device_type(),
        'mobile_css_classes': MobileDetector.get_css_classes(),
        'viewport_meta': MobileDetector.get_viewport_meta()
    }
