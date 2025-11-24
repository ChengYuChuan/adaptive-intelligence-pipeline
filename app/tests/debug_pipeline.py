#!/usr/bin/env python3
"""
Debug version with verbose output
"""
import sys
import time

# Force unbuffered output
sys.stdout.reconfigure(line_buffering=True)

print("Starting script...", flush=True)
time.sleep(0.5)

try:
    print("Importing libraries...", flush=True)
    import requests
    import json
    from datetime import datetime
    print("✓ Libraries imported successfully", flush=True)
    
except Exception as e:
    print(f"✗ Error importing libraries: {e}", flush=True)
    sys.exit(1)

print("\n" + "="*60, flush=True)
print("Pipeline Debug Script", flush=True)
print("="*60 + "\n", flush=True)

# Check if server is running
print("Step 1: Checking server status...", flush=True)
try:
    response = requests.get("http://localhost:8000/health", timeout=5)
    print(f"✓ Server is running (status code: {response.status_code})", flush=True)
    data = response.json()
    print(f"  Server status: {data.get('status')}", flush=True)
except requests.exceptions.ConnectionError:
    print("✗ ERROR: Cannot connect to server", flush=True)
    print("  Please start the server first:", flush=True)
    print("  uvicorn app.main:app --reload", flush=True)
    input("\nPress Enter to exit...")
    sys.exit(1)
except Exception as e:
    print(f"✗ Unexpected error: {e}", flush=True)
    input("\nPress Enter to exit...")
    sys.exit(1)

# Prepare request
print("\nStep 2: Preparing request...", flush=True)
url = "http://localhost:8000/pipeline/run"
payload = {
    "query": "machine learning",
    "template": "academic",
    "max_results": 2,
    "date_range": "last_week"
}
print(f"  URL: {url}", flush=True)
print(f"  Query: {payload['query']}", flush=True)
print(f"  Template: {payload['template']}", flush=True)

# Send request
print("\nStep 3: Sending request...", flush=True)
print("  (This may take 10-30 seconds)", flush=True)

try:
    start_time = time.time()
    response = requests.post(url, json=payload, timeout=120)
    elapsed = time.time() - start_time
    
    print(f"✓ Response received in {elapsed:.1f} seconds", flush=True)
    print(f"  Status code: {response.status_code}", flush=True)
    
    if response.status_code == 200:
        result = response.json()
        
        print("\nStep 4: Processing response...", flush=True)
        print("="*60, flush=True)
        print("RESULTS", flush=True)
        print("="*60, flush=True)
        print(f"Status: {result.get('status')}", flush=True)
        print(f"Data fetched: {result.get('data_fetched')}", flush=True)
        print(f"Duration: {result.get('duration_seconds', 0):.2f}s", flush=True)
        
        if result.get('providers'):
            print("\nProviders used:", flush=True)
            for key, value in result['providers'].items():
                print(f"  {key}: {value}", flush=True)
        
        # Save results
        print("\nStep 5: Saving results...", flush=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save JSON
        json_file = f"pipeline_result_{timestamp}.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"✓ JSON saved: {json_file}", flush=True)
        
        # Save report
        if result.get('report'):
            txt_file = f"report_{timestamp}.txt"
            with open(txt_file, "w", encoding="utf-8") as f:
                f.write(result['report'])
            print(f"✓ Report saved: {txt_file}", flush=True)
            
            # Show preview
            print("\nReport preview:", flush=True)
            print("-"*60, flush=True)
            preview = result['report'][:500]
            print(preview, flush=True)
            if len(result['report']) > 500:
                print("...", flush=True)
            print("-"*60, flush=True)
        
        print("\n✓ SUCCESS! All results saved.", flush=True)
        
    else:
        print(f"✗ Unexpected status code: {response.status_code}", flush=True)
        print(f"Response: {response.text[:500]}", flush=True)
        
except requests.exceptions.Timeout:
    print("✗ Request timeout (>120 seconds)", flush=True)
except Exception as e:
    print(f"✗ Error: {e}", flush=True)
    import traceback
    traceback.print_exc()

print("\n" + "="*60, flush=True)
print("Script completed", flush=True)
print("="*60, flush=True)

input("\nPress Enter to exit...")