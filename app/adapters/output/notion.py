from typing import Dict, Any
from datetime import datetime
from app.adapters.output.base import BaseOutputAdapter
from app.config import settings
import httpx


class NotionAdapter(BaseOutputAdapter):
    """
    輸出到 Notion Database
    適合：個人知識管理、團隊共享
    
    需要在 Notion 中：
    1. 建立一個 Database
    2. 建立 Integration 並取得 API key
    3. 把 Integration 加到 Database
    """
    
    def __init__(self):
        self.api_key = settings.NOTION_API_KEY
        self.database_id = settings.NOTION_DATABASE_ID
        self.base_url = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
    
    async def send(self, content: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        在 Notion Database 中建立新頁面
        
        metadata 可包含：
        - title: 頁面標題
        - tags: 標籤列表
        - date: 日期
        """
        
        if not self.api_key or not self.database_id:
            return {
                "status": "failed",
                "message": "Notion API key 或 Database ID 未設定",
                "url": None,
                "timestamp": datetime.now().isoformat()
            }
        
        metadata = metadata or {}
        title = metadata.get("title", f"報告 - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        tags = metadata.get("tags", [])
        
        # 建立 Notion 頁面
        page_data = {
            "parent": {"database_id": self.database_id},
            "properties": {
                "Name": {  # 標題屬性（大部分 Database 都有）
                    "title": [
                        {
                            "text": {
                                "content": title
                            }
                        }
                    ]
                }
            },
            "children": [
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": content[:2000]  # Notion 單一 block 限制
                                }
                            }
                        ]
                    }
                }
            ]
        }
        
        # 如果有標籤（需要 Database 有 Tags 屬性）
        if tags:
            page_data["properties"]["Tags"] = {
                "multi_select": [{"name": tag} for tag in tags]
            }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/pages",
                    headers=self.headers,
                    json=page_data,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "status": "success",
                        "message": "成功建立 Notion 頁面",
                        "url": data.get("url"),
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    return {
                        "status": "failed",
                        "message": f"Notion API 錯誤: {response.status_code} - {response.text}",
                        "url": None,
                        "timestamp": datetime.now().isoformat()
                    }
        
        except Exception as e:
            return {
                "status": "failed",
                "message": f"發送到 Notion 失敗: {str(e)}",
                "url": None,
                "timestamp": datetime.now().isoformat()
            }
    
    def get_output_name(self) -> str:
        return "Notion"
