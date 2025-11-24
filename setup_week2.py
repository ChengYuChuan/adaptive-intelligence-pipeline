#!/usr/bin/env python3
"""
Week 2 Quick Start Script
Helps you set up and test all Week 2 adapters
"""
import sys
import os
from pathlib import Path


class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.ENDC}\n")


def print_section(text):
    print(f"\n{Colors.BOLD}{Colors.GREEN}▶ {text}{Colors.ENDC}\n")


def print_warning(text):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.ENDC}")


def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.ENDC}")


def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.ENDC}")


def check_dependencies():
    """Check if all required dependencies are installed"""
    print_section("Checking Dependencies")
    
    missing = []
    
    # Check Python packages
    packages = {
        'newsapi': 'newsapi-python',
        'boto3': 'boto3',
        'aiosmtplib': 'aiosmtplib'
    }
    
    for module, package in packages.items():
        try:
            __import__(module)
            print_success(f"{package} installed")
        except ImportError:
            print_error(f"{package} not installed")
            missing.append(package)
    
    if missing:
        print_warning("\nInstall missing packages:")
        print(f"  pip install {' '.join(missing)}")
        return False
    
    return True


def check_env_file():
    """Check if .env file exists and has necessary variables"""
    print_section("Checking Environment Configuration")
    
    env_path = Path('.env')
    
    if not env_path.exists():
        print_error(".env file not found")
        print_warning("Copy .env.example to .env and fill in your API keys")
        return False
    
    print_success(".env file found")
    
    # Read .env and check for new Week 2 variables
    with open(env_path, 'r') as f:
        env_content = f.read()
    
    week2_vars = {
        'NEWSAPI_KEY': 'NewsAPI',
        'AWS_ACCESS_KEY_ID': 'AWS Bedrock (optional)',
        'AWS_SECRET_ACCESS_KEY': 'AWS Bedrock (optional)',
        'SMTP_HOST': 'Email',
        'SMTP_USERNAME': 'Email',
        'SMTP_PASSWORD': 'Email'
    }
    
    missing_vars = []
    for var, service in week2_vars.items():
        if var not in env_content or f"{var}=" in env_content:
            print_warning(f"{var} not configured ({service})")
            missing_vars.append(var)
        else:
            print_success(f"{var} configured")
    
    if missing_vars:
        print_warning(f"\n⚠ Some adapters won't work without proper configuration")
        return False
    
    return True


def deploy_adapters():
    """Copy adapter files to the correct locations"""
    print_section("Deploying Week 2 Adapters")
    
    # Define source and destination paths
    adapters = [
        ('newsapi_adapter.py', 'app/adapters/source/newsapi.py'),
        ('bedrock_adapter.py', 'app/adapters/llm/bedrock.py'),
        ('email_adapter.py', 'app/adapters/output/email.py')
    ]
    
    success_count = 0
    
    for source, dest in adapters:
        if not Path(source).exists():
            print_error(f"{source} not found")
            continue
        
        # Create destination directory if it doesn't exist
        dest_path = Path(dest)
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Copy file
        import shutil
        try:
            shutil.copy(source, dest)
            print_success(f"Deployed {dest}")
            success_count += 1
        except Exception as e:
            print_error(f"Failed to deploy {dest}: {e}")
    
    return success_count == len(adapters)


def update_factory_functions():
    """Update factory functions to include new adapters"""
    print_section("Updating Factory Functions")
    
    updates = [
        ('app/adapters/source/__init__.py', 'NewsAPI'),
        ('app/adapters/llm/__init__.py', 'Bedrock'),
        ('app/adapters/output/__init__.py', 'Email')
    ]
    
    for file_path, adapter_name in updates:
        path = Path(file_path)
        
        if not path.exists():
            print_error(f"{file_path} not found")
            continue
        
        with open(path, 'r') as f:
            content = f.read()
        
        # Check if adapter is already imported
        if adapter_name.lower() in content.lower():
            print_success(f"{adapter_name} already in {file_path}")
        else:
            print_warning(f"{adapter_name} not found in {file_path}")
            print(f"  Please manually update {file_path}")


def test_adapters():
    """Run basic tests on each adapter"""
    print_section("Testing Adapters")
    
    print("1. Testing NewsAPI Adapter...")
    try:
        from app.adapters.source.newsapi import NewsAPIAdapter
        adapter = NewsAPIAdapter()
        print_success("NewsAPI adapter initialized")
    except Exception as e:
        print_error(f"NewsAPI adapter failed: {e}")
    
    print("\n2. Testing Bedrock Adapter...")
    try:
        from app.adapters.llm.bedrock import AWSBedrockAdapter
        adapter = AWSBedrockAdapter()
        print_success("Bedrock adapter initialized")
    except Exception as e:
        print_warning(f"Bedrock adapter failed (may need AWS credentials): {e}")
    
    print("\n3. Testing Email Adapter...")
    try:
        from app.adapters.output.email import EmailAdapter
        adapter = EmailAdapter()
        print_success("Email adapter initialized")
    except Exception as e:
        print_error(f"Email adapter failed: {e}")


def show_next_steps():
    """Show next steps after setup"""
    print_section("Next Steps")
    
    print("1. Update Factory Functions")
    print("   Edit the following files to enable new adapters:")
    print("   - app/adapters/source/__init__.py")
    print("   - app/adapters/llm/__init__.py")
    print("   - app/adapters/output/__init__.py")
    print()
    
    print("2. Test Individual Adapters")
    print("   Run test scripts:")
    print("   - python test_newsapi.py")
    print("   - python test_bedrock.py")
    print("   - python test_email.py")
    print()
    
    print("3. Test Complete Pipeline")
    print("   Start the server:")
    print("   uvicorn app.main:app --reload")
    print()
    print("   Then test different combinations:")
    print("   - NewsAPI + Claude + Email")
    print("   - arXiv + Bedrock + Email")
    print("   - NewsAPI + Bedrock + Notion")
    print()
    
    print("4. Read Documentation")
    print("   - WEEK2_GUIDE.md - Complete setup guide")
    print("   - WEEK2_SUMMARY.md - Achievement summary")
    print()


def main():
    """Main setup function"""
    print_header("Week 2 Quick Start Setup")
    
    print(f"{Colors.YELLOW}This script will help you set up Week 2 adapters{Colors.ENDC}")
    print("Make sure you have:")
    print("  • NewsAPI API key")
    print("  • AWS credentials (optional)")
    print("  • Email SMTP credentials")
    print()
    
    input(f"{Colors.BOLD}Press Enter to continue...{Colors.ENDC}")
    
    # Step 1: Check dependencies
    if not check_dependencies():
        print_error("\n❌ Please install missing dependencies first")
        return 1
    
    # Step 2: Check environment configuration
    check_env_file()
    
    # Step 3: Deploy adapters
    if not deploy_adapters():
        print_warning("\n⚠ Some adapters failed to deploy")
    
    # Step 4: Update factory functions
    update_factory_functions()
    
    # Step 5: Test adapters
    print()
    test_input = input(f"\n{Colors.BOLD}Run adapter tests? (y/n): {Colors.ENDC}")
    if test_input.lower() == 'y':
        test_adapters()
    
    # Show next steps
    show_next_steps()
    
    print_header("Setup Complete!")
    print(f"{Colors.GREEN}Week 2 adapters are ready to use!{Colors.ENDC}")
    print(f"Check {Colors.BOLD}WEEK2_GUIDE.md{Colors.ENDC} for detailed instructions.\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())