#!/usr/bin/env python3
"""
Run pipeline and save results with correct encoding
Fixed version with proper output flushing
"""
import requests
import json
from datetime import datetime
import sys

# Force unbuffered output
sys.stdout.reconfigure(line_buffering=True)


def run_pipeline_and_save(
    query="machine learning",
    template="academic", 
    max_results=2,
    date_range="last_week"
):
    """Run pipeline and save results"""
    
    print("="*60, flush=True)
    print("執行 Pipeline 並保存結果", flush=True)
    print("="*60, flush=True)
    print(flush=True)
    
    # Request payload
    payload = {
        "query": query,
        "template": template,
        "max_results": max_results,
        "date_range": date_range
    }
    
    print(f"查詢: {payload['query']}", flush=True)
    print(f"模板: {payload['template']}", flush=True)
    print(f"最大結果數: {payload['max_results']}", flush=True)
    print(f"日期範圍: {payload['date_range']}", flush=True)
    print(flush=True)
    print("發送請求中... (這可能需要 10-30 秒)", flush=True)
    print(flush=True)
    
    try:
        # Send request
        url = "http://localhost:8000/pipeline/run"
        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()
        
        # Parse response
        result = response.json()
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save full JSON
        json_filename = f"pipeline_result_{timestamp}.json"
        with open(json_filename, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print("✓ Pipeline 執行成功！", flush=True)
        print(flush=True)
        print("="*60, flush=True)
        print("執行摘要", flush=True)
        print("="*60, flush=True)
        print(f"狀態: {result['status']}", flush=True)
        print(f"獲取資料數: {result['data_fetched']} 篇", flush=True)
        print(f"執行時間: {result['duration_seconds']:.2f} 秒", flush=True)
        print(flush=True)
        
        if result.get('providers'):
            print("使用的服務:", flush=True)
            for key, value in result['providers'].items():
                print(f"  {key}: {value}", flush=True)
            print(flush=True)
        
        # Save report to text file
        if result.get('report'):
            txt_filename = f"report_{timestamp}.txt"
            with open(txt_filename, "w", encoding="utf-8") as f:
                f.write(result['report'])
            
            print(f"✓ 完整 JSON 已保存: {json_filename}", flush=True)
            print(f"✓ 報告內容已保存: {txt_filename}", flush=True)
            print(flush=True)
            
            # Display preview
            print("="*60, flush=True)
            print("報告預覽（前 800 字元）", flush=True)
            print("="*60, flush=True)
            report = result['report']
            preview = report[:800] + "..." if len(report) > 800 else report
            print(preview, flush=True)
            print(flush=True)
            print("="*60, flush=True)
            print(f"完整報告請查看: {txt_filename}", flush=True)
            print("="*60, flush=True)
        
        print(flush=True)
        print("✓ 所有結果已成功保存！", flush=True)
        print(f"  - JSON 檔案: {json_filename}", flush=True)
        if result.get('report'):
            print(f"  - 報告文字: {txt_filename}", flush=True)
        
        return True
        
    except requests.exceptions.Timeout:
        print("✗ 錯誤: 請求超時 (>120 秒)", flush=True)
        return False
        
    except requests.exceptions.ConnectionError:
        print("✗ 錯誤: 無法連接到伺服器", flush=True)
        print("  請確保伺服器正在運行: uvicorn app.main:app --reload", flush=True)
        return False
        
    except requests.exceptions.HTTPError as e:
        print(f"✗ HTTP 錯誤: {e}", flush=True)
        try:
            error_detail = response.json()
            print(f"  詳情: {error_detail.get('detail', '無詳細資訊')}", flush=True)
        except:
            print(f"  回應: {response.text[:500]}", flush=True)
        return False
        
    except Exception as e:
        print(f"✗ 未預期的錯誤: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function"""
    print(flush=True)
    print("="*60, flush=True)
    print("Adaptive Intelligence Pipeline", flush=True)
    print("Pipeline 執行與結果保存工具", flush=True)
    print("="*60, flush=True)
    print(flush=True)
    
    # Check if server is running
    print("檢查伺服器狀態...", flush=True)
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        response.raise_for_status()
        print("✓ 伺服器正在運行", flush=True)
        print(flush=True)
    except:
        print("✗ 無法連接到伺服器", flush=True)
        print("  請先啟動伺服器: uvicorn app.main:app --reload", flush=True)
        print(flush=True)
        input("按 Enter 鍵退出...")
        return 1
    
    # Get user input if arguments provided
    if len(sys.argv) > 1:
        query = sys.argv[1]
        template = sys.argv[2] if len(sys.argv) > 2 else "academic"
        max_results = int(sys.argv[3]) if len(sys.argv) > 3 else 2
        date_range = sys.argv[4] if len(sys.argv) > 4 else "last_week"
    else:
        query = "machine learning"
        template = "academic"
        max_results = 2
        date_range = "last_week"
    
    success = run_pipeline_and_save(query, template, max_results, date_range)
    
    print(flush=True)
    
    if success:
        print("="*60, flush=True)
        print("✓ 完成！", flush=True)
        print("="*60, flush=True)
    else:
        print("="*60, flush=True)
        print("✗ 執行失敗", flush=True)
        print("="*60, flush=True)
    
    print(flush=True)
    input("按 Enter 鍵退出...")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())