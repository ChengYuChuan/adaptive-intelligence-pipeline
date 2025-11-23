from typing import Dict, Any
from datetime import datetime
from app.adapters.output.base import BaseOutputAdapter


class ConsoleOutputAdapter(BaseOutputAdapter):
    """
    輸出到 Console（標準輸出）
    適合：開發測試、快速驗證
    """
    
    async def send(self, content: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """直接印到 console"""
        
        print("\n" + "="*80)
        print("📊 報告生成完成")
        print("="*80)
        
        if metadata:
            print("\n📋 元資料:")
            for key, value in metadata.items():
                print(f"  {key}: {value}")
        
        print("\n📄 內容:")
        print("-"*80)
        print(content)
        print("-"*80)
        print("\n")
        
        return {
            "status": "success",
            "message": "成功輸出到 console",
            "url": None,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_output_name(self) -> str:
        return "Console"
