from typing import Dict, Any
from datetime import datetime
from app.adapters.output.base import BaseOutputAdapter
from app.config import settings
import httpx


class NotionAdapter(BaseOutputAdapter):
    """
    Output to Notion Database
    Suitable for: Personal knowledge management, team sharing
    
    Requirements in Notion:
    1. Create a Database
    2. Create an Integration and get API key
    3. Add the Integration to the Database
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
        Create a new page in Notion Database
        
        metadata can include:
        - title: Page title
        - tags: List of tags
        - date: Date
        """
        
        if not self.api_key or not self.database_id:
            return {
                "status": "failed",
                "message": "Notion API key or Database ID not configured",
                "url": None,
                "timestamp": datetime.now().isoformat()
            }
        
        metadata = metadata or {}
        title = metadata.get("title", f"Report - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        tags = metadata.get("tags", [])
        
        # Create Notion page
        page_data = {
            "parent": {"database_id": self.database_id},
            "properties": {
                "Name": {  # Title property (most databases have this)
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
                                    "content": content[:2000]  # Notion single block limit
                                }
                            }
                        ]
                    }
                }
            ]
        }
        
        # Add tags if present (requires Tags property in Database)
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
                        "message": "Successfully created Notion page",
                        "url": data.get("url"),
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    return {
                        "status": "failed",
                        "message": f"Notion API error: {response.status_code} - {response.text}",
                        "url": None,
                        "timestamp": datetime.now().isoformat()
                    }
        
        except Exception as e:
            return {
                "status": "failed",
                "message": f"Failed to send to Notion: {str(e)}",
                "url": None,
                "timestamp": datetime.now().isoformat()
            }
    
    def get_output_name(self) -> str:
        return "Notion"