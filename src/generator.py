import requests
import os
from dotenv import load_dotenv
from src.retriever import search

load_dotenv()


class GigaChatRAG:
    def __init__(self, collection):
        self.collection = collection
        self.token = self._get_token()
    
    def _get_token(self):
        auth_key = os.getenv("GIGACHAT_AUTH_KEY")
        if not auth_key:
            return None
        
        response = requests.post(
            "https://ngw.devices.sberbank.ru:9443/api/v2/oauth",
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json',
                'RqUID': 'd39534d0-150b-4aae-a7fd-ed3227e27d9c',
                'Authorization': f'Basic {auth_key}'
            },
            data={'scope': 'GIGACHAT_API_PERS'},
            verify=False
        )
        
        try:
            return response.json().get('access_token')
        except:
            return None
    
    def ask(self, question):
        contexts, metadatas = search(self.collection, question, top_k=4)
        context_text = "\n\n".join(contexts) if contexts else ""
        if context_text:
            prompt = (
                "Ты помощник по технической документации. "
                "Отвечай ТОЛЬКО на основе контекста ниже. "
                "Если ответа нет в контексте, так и скажи.\n\n"
                f"Контекст:\n{context_text}\n\n"
                f"Вопрос: {question}\n\nОтвет:"
            )
        else:
            prompt = f"Вопрос: {question}\n\nОтвет:"
        answer = self._call_gigachat(prompt) if self.token else "GigaChat не настроен. Проверьте ключи в .env файле."

        sources = list(set(m.get("source", "N/A") for m in metadatas))
        
        return {"answer": answer, "sources": sources, "contexts": contexts}
    
    def _call_gigachat(self, prompt):
        try:
            response = requests.post(
                "https://gigachat.devices.sberbank.ru/api/v1/chat/completions",
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.token}'
                },
                json={
                    "model": "GigaChat",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1,
                    "max_tokens": 500
                },
                verify=False
            )
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            return f"Ошибка GigaChat: {str(e)[:100]}"