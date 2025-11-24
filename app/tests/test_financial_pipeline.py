#!/usr/bin/env python3
"""
Test complete financial analysis pipeline with Week 2 features
"""
import requests
import json
from datetime import datetime

def test_financial_pipeline():
    print("="*60)
    print("Financial Analysis Pipeline - Full Test")
    print("="*60)
    
    # Test 1: NewsAPI + Claude + Console
    print("\n1. Testing NewsAPI → Claude → Console")
    test_config_1 = {
        "query": "TSMC OR NVIDIA OR semiconductor",
        "template": "financial",
        "max_results": 5,
        "date_range": "last_week",
        "output_title": "Semiconductor Industry Weekly Analysis"
    }
    
    # Update .env before running
    print("   Before running, ensure .env has:")
    print("   SOURCE_PROVIDER=newsapi")
    print("   LLM_PROVIDER=claude")
    print("   OUTPUT_PROVIDER=console")
    input("\n   Press Enter when ready...")
    
    response = requests.post(
        "http://localhost:8000/pipeline/run",
        json=test_config_1,
        timeout=120
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n   ✓ Pipeline Status: {result['status']}")
        print(f"   ✓ Articles Fetched: {result['data_fetched']}")
        print(f"   ✓ Duration: {result['duration_seconds']:.2f}s")
        
        # Save result
        with open('financial_report_console.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"\n   ✓ Report saved to: financial_report_console.json")
    else:
        print(f"\n   ✗ Failed with status code: {response.status_code}")
        return False
    
    # Test 2: NewsAPI + Bedrock + Email (if configured)
    print("\n2. Testing NewsAPI → Bedrock → Email")
    print("   This requires AWS Bedrock access and Email configuration")
    
    choice = input("   Do you want to test this? (y/n): ")
    if choice.lower() == 'y':
        print("\n   Update .env to:")
        print("   SOURCE_PROVIDER=newsapi")
        print("   LLM_PROVIDER=bedrock")
        print("   OUTPUT_PROVIDER=email")
        input("\n   Press Enter when ready...")
        
        response = requests.post(
            "http://localhost:8000/pipeline/run",
            json=test_config_1,
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n   ✓ Pipeline Status: {result['status']}")
            print(f"   ✓ Report sent to: {result.get('output_url', 'Email sent')}")
        else:
            print(f"\n   ✗ Failed with status code: {response.status_code}")
    
    print("\n" + "="*60)
    print("Test completed!")
    print("="*60)
    return True

if __name__ == "__main__":
    test_financial_pipeline()