import anthropic
from typing import List, Dict, Any
from app.adapters.llm.base import BaseLLMAdapter
from app.config import settings
import json


class ClaudeAPIAdapter(BaseLLMAdapter):
    """
    使用 Anthropic Claude API 的 Adapter
    適合：開發階段、Demo、快速原型
    """
    
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = settings.CLAUDE_MODEL
        self.max_tokens = 2048
    
    async def _call_claude(self, system_prompt: str, user_message: str) -> str:
        """內部方法：呼叫 Claude API"""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=system_prompt,
            messages=[{
                "role": "user",
                "content": user_message
            }]
        )
        return response.content[0].text
    
    async def summarize(self, text: str, max_length: int = 300) -> str:
        system_prompt = f"""你是一個專業的摘要助手。
請用繁體中文提供清晰、精確的摘要，不超過 {max_length} 字。
摘要應該保留最重要的資訊和關鍵細節。"""
        
        user_message = f"請摘要以下內容：\n\n{text}"
        
        return await self._call_claude(system_prompt, user_message)
    
    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        system_prompt = """你是情緒分析專家。
分析文本的情緒傾向，並以 JSON 格式回覆：
{
  "sentiment": "positive" | "negative" | "neutral",
  "confidence": 0.0-1.0,
  "reasoning": "簡短解釋為何是這個情緒"
}

只回覆 JSON，不要有其他文字。"""
        
        user_message = f"請分析以下文本的情緒：\n\n{text}"
        
        response = await self._call_claude(system_prompt, user_message)
        
        # 解析 JSON 回應
        try:
            # 移除可能的 markdown 標記
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            
            return json.loads(response.strip())
        except json.JSONDecodeError:
            # 如果解析失敗，返回預設結構
            return {
                "sentiment": "neutral",
                "confidence": 0.5,
                "reasoning": "無法解析回應"
            }
    
    async def extract_key_points(self, text: str, num_points: int = 5) -> List[str]:
        system_prompt = f"""你是內容分析專家。
從文本中提取 {num_points} 個最重要的關鍵要點。
每個要點用一句話表達，用繁體中文。
請以列表形式回覆，每行一個要點，開頭用 "- "。"""
        
        user_message = f"請從以下內容提取關鍵要點：\n\n{text}"
        
        response = await self._call_claude(system_prompt, user_message)
        
        # 解析列表
        points = [
            line.strip("- ").strip() 
            for line in response.split("\n") 
            if line.strip().startswith("-")
        ]
        
        return points[:num_points]
    
    async def generate_report(
        self, 
        data: Dict[str, Any], 
        template: str,
        language: str = "zh-TW"
    ) -> str:
        # 根據模板選擇不同的 system prompt
        if template == "academic":
            system_prompt = """你是學術論文分析專家。
請生成一份專業的學術文獻彙整報告，包含：
1. 整體趨勢摘要
2. 重點論文列表（標題、作者、核心貢獻）
3. 關鍵發現
4. 推薦閱讀

使用繁體中文，保持學術專業的語氣。"""
        
        elif template == "financial":
            system_prompt = """你是金融分析師。
請生成一份投資分析報告，包含：
1. 市場動態摘要
2. 關鍵新聞及影響
3. 情緒分析（利多/利空）
4. 相關公司動態
5. 建議關注事項

使用繁體中文，保持專業客觀的語氣。"""
        
        else:
            system_prompt = "你是專業分析師，請根據提供的資料生成一份完整報告。使用繁體中文。"
        
        # 將資料轉換為 JSON 字串
        data_str = json.dumps(data, ensure_ascii=False, indent=2)
        user_message = f"請根據以下資料生成報告：\n\n{data_str}"
        
        return await self._call_claude(system_prompt, user_message)
    
    async def answer_question(self, question: str, context: str) -> str:
        system_prompt = """你是專業的問答助手。
根據提供的上下文回答問題，保持客觀準確。
如果上下文中沒有足夠資訊，請明確指出。
使用繁體中文回答。"""
        
        user_message = f"""上下文：
{context}

問題：{question}"""
        
        return await self._call_claude(system_prompt, user_message)
