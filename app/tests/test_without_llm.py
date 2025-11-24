#!/usr/bin/env python3
"""
Test Adaptive Intelligence Pipeline without requiring LLM API credits
This script tests the components that don't need Claude API
"""
import requests
import json
from datetime import datetime


class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.ENDC}\n")


def test_health():
    """Test health endpoint"""
    print_header("Test 1: Health Check")
    
    try:
        response = requests.get("http://localhost:8000/health", timeout=10)
        response.raise_for_status()
        
        data = response.json()
        print(f"{Colors.GREEN}✓ Status: {data.get('status')}{Colors.ENDC}")
        
        if 'providers' in data:
            print(f"\n  Current Providers:")
            for key, value in data['providers'].items():
                print(f"    {key}: {value}")
        
        return True
    except Exception as e:
        print(f"{Colors.RED}✗ Failed: {e}{Colors.ENDC}")
        return False


def test_config():
    """Test config endpoint"""
    print_header("Test 2: Configuration")
    
    try:
        response = requests.get("http://localhost:8000/config", timeout=10)
        response.raise_for_status()
        
        data = response.json()
        print(f"{Colors.GREEN}✓ Configuration loaded successfully{Colors.ENDC}")
        print(f"\n  Settings:")
        for key, value in data.items():
            print(f"    {key}: {value}")
        
        return True
    except Exception as e:
        print(f"{Colors.RED}✗ Failed: {e}{Colors.ENDC}")
        return False


def test_arxiv_source():
    """Test arXiv data source (no API key needed)"""
    print_header("Test 3: arXiv Data Source")
    
    print(f"{Colors.YELLOW}Testing direct arXiv adapter...{Colors.ENDC}\n")
    
    # We'll use Python to test the adapter directly
    try:
        import sys
        sys.path.insert(0, '.')
        
        from app.adapters.source.arxiv import ArXivAdapter
        import asyncio
        from datetime import datetime, timedelta
        
        adapter = ArXivAdapter()
        
        # Test fetch
        print("Fetching papers from arXiv...")
        papers = asyncio.run(adapter.fetch(
            query="machine learning",
            max_results=2,
            date_from=datetime.now() - timedelta(days=7),
            date_to=datetime.now()
        ))
        
        print(f"{Colors.GREEN}✓ Successfully fetched {len(papers)} papers{Colors.ENDC}\n")
        
        if papers:
            print("Sample paper:")
            paper = papers[0]
            print(f"  Title: {paper['title'][:60]}...")
            print(f"  Authors: {', '.join(paper['authors'][:3])}")
            print(f"  Published: {paper['published_date']}")
            print(f"  Categories: {', '.join(paper['metadata']['categories'])}")
        
        return True
        
    except Exception as e:
        print(f"{Colors.RED}✗ Failed: {e}{Colors.ENDC}")
        import traceback
        traceback.print_exc()
        return False


def test_console_output():
    """Test console output adapter (no API key needed)"""
    print_header("Test 4: Console Output")
    
    try:
        import sys
        sys.path.insert(0, '.')
        
        from app.adapters.output.console import ConsoleOutputAdapter
        import asyncio
        
        adapter = ConsoleOutputAdapter()
        
        # Test send
        print(f"{Colors.YELLOW}Testing console output...{Colors.ENDC}\n")
        
        result = asyncio.run(adapter.send(
            content="This is a test report generated without LLM.",
            metadata={
                "title": "Test Report",
                "tags": ["test", "no-llm"]
            }
        ))
        
        print(f"\n{Colors.GREEN}✓ Console output test successful{Colors.ENDC}")
        print(f"  Status: {result['status']}")
        
        return True
        
    except Exception as e:
        print(f"{Colors.RED}✗ Failed: {e}{Colors.ENDC}")
        import traceback
        traceback.print_exc()
        return False


def test_validation_only():
    """Test pipeline validation without executing"""
    print_header("Test 5: API Validation")
    
    try:
        # Test with invalid data
        response = requests.post(
            "http://localhost:8000/pipeline/run",
            json={"query": "test"},  # Missing required fields
            timeout=10
        )
        
        if response.status_code == 422:
            print(f"{Colors.GREEN}✓ Validation working correctly{Colors.ENDC}")
            print(f"  (Correctly rejected invalid request)")
            return True
        else:
            print(f"{Colors.YELLOW}⚠ Unexpected status code: {response.status_code}{Colors.ENDC}")
            return False
            
    except Exception as e:
        print(f"{Colors.RED}✗ Failed: {e}{Colors.ENDC}")
        return False


def show_summary(results):
    """Show test summary"""
    print_header("Test Summary")
    
    total = len(results)
    passed = sum(results.values())
    
    for test_name, passed in results.items():
        status = f"{Colors.GREEN}✓ PASSED{Colors.ENDC}" if passed else f"{Colors.RED}✗ FAILED{Colors.ENDC}"
        print(f"{test_name}: {status}")
    
    print(f"\n{Colors.BOLD}Results: {passed}/{total} tests passed{Colors.ENDC}")
    
    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 All tests passed!{Colors.ENDC}")
        print(f"\n{Colors.YELLOW}Note:{Colors.ENDC} LLM functionality requires API credits.")
        print("To test the complete pipeline with LLM:")
        print("  1. Add credits at: https://console.anthropic.com/settings/billing")
        print("  2. Then run: python week1_補充檔案/test_pipeline.py")
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}⚠ Some tests failed{Colors.ENDC}")
        print("Check the errors above for details.")
    
    print()


def main():
    """Main test function"""
    print(f"\n{Colors.BOLD}{'='*60}")
    print("Adaptive Intelligence Pipeline")
    print("Testing Without LLM API Credits")
    print(f"{'='*60}{Colors.ENDC}\n")
    
    print(f"{Colors.YELLOW}Note:{Colors.ENDC} These tests don't require Claude API credits.")
    print("They verify that your system architecture is working correctly.\n")
    
    results = {
        "Health Check": test_health(),
        "Configuration": test_config(),
        "arXiv Source": test_arxiv_source(),
        "Console Output": test_console_output(),
        "API Validation": test_validation_only(),
    }
    
    show_summary(results)
    
    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())