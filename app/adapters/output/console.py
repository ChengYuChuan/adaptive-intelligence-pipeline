from typing import Dict, Any
from datetime import datetime
from app.adapters.output.base import BaseOutputAdapter


class ConsoleOutputAdapter(BaseOutputAdapter):
    """
    Output to Console (standard output)
    Suitable for: Development testing, quick verification
    """
    
    async def send(self, content: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Print directly to console"""
        
        print("\n" + "="*80)
        print("📊 Report Generated")
        print("="*80)
        
        if metadata:
            print("\n📋 Metadata:")
            for key, value in metadata.items():
                print(f"  {key}: {value}")
        
        print("\n📄 Content:")
        print("-"*80)
        print(content)
        print("-"*80)
        print("\n")
        
        return {
            "status": "success",
            "message": "Successfully output to console",
            "url": None,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_output_name(self) -> str:
        return "Console"