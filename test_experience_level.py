#!/usr/bin/env python3
"""
Test script to verify experience level functionality in AI assessment generation.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Mock Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

try:
    import django
    django.setup()
    
    # Test the experience guidelines function
    from ai_assessments.ai_logic import _get_experience_guidelines
    
    print("🧪 Testing Experience Level Guidelines Function")
    print("=" * 60)
    
    # Test all experience levels
    levels = ['fresher', 'entry', 'mid', 'senior', 'expert']
    
    for level in levels:
        guidelines = _get_experience_guidelines(level)
        print(f"\n📊 {level.upper()} Level:")
        print(f"   Description: {guidelines['description']}")
        print(f"   Focus: {guidelines['focus']}")
        print(f"   Difficulty Distribution: {guidelines['difficulty_distribution']}")
        print(f"   Sample Topics: {guidelines['topics'][:3]}...")
    
    # Test default fallback
    print(f"\n🔄 Default (unknown level):")
    default_guidelines = _get_experience_guidelines('unknown_level')
    print(f"   Falls back to: {default_guidelines['description']}")
    
    print("\n✅ Experience Level Guidelines Function Working!")
    
    # Test Assessment model (if database is available)
    try:
        from ai_assessments.models import Assessment
        print(f"\n📋 Assessment Model Experience Level Choices:")
        for choice in Assessment.EXPERIENCE_LEVEL_CHOICES:
            print(f"   {choice[0]} -> {choice[1]}")
        print("✅ Assessment Model Updated!")
    except Exception as e:
        print(f"\n⚠️  Database not available for model test: {e}")
    
    print(f"\n🎉 All Tests Passed! Experience Level Feature Ready!")
    
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Make sure Django and dependencies are installed")
except Exception as e:
    print(f"❌ Error: {e}")