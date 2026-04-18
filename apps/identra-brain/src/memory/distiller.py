import asyncio
import logging
from src.memory.engine import MemoryEngine
from src.llm.client import OllamaClient

logger = logging.getLogger("brain.distiller")

class MemoryDistiller:
    def __init__(self, memory_engine: MemoryEngine, llm_client: OllamaClient):
        self.memory_engine = memory_engine
        self.llm_client = llm_client
        self.running = False
        self.history_buffer = []

    def record_interaction(self, user_prompt: str, assistant_response: str):
        self.history_buffer.append(f"User: {user_prompt}\nAgent: {assistant_response}")

    async def start(self):
        self.running = True
        logger.info("Memory Distiller started in background")
        while self.running:
            await asyncio.sleep(60) # Run every 60 seconds
            if len(self.history_buffer) >= 3:
                await self.distill_memories()

    async def stop(self):
        self.running = False
        if self.history_buffer:
            await self.distill_memories()
        logger.info("Memory Distiller stopped")

    async def distill_memories(self):
        if not self.history_buffer:
            return

        chat_history = "\n\n".join(self.history_buffer)
        self.history_buffer.clear()
        
        prompt = f"""
        Analyze the following conversation and extract 1 to 3 core, permanent facts about the user.
        Format them as concise bullet points. 
        Only extract facts that are actually useful to remember long term (e.g. preferences, project details, opinions).
        If there is nothing worth remembering, reply with EXACTLY "NONE".
        
        Conversation:
        {chat_history}
        """
        
        logger.info("Distilling recent chat history into core memories...")
        
        # We use a non-streaming call here for simplicity, but we can simulate it with our stream client
        full_response = ""
        async for chunk in self.llm_client.stream_chat(prompt, system_prompt="You are an expert at extracting facts."):
            if "data: " in chunk:
                import json
                try:
                    data = json.loads(chunk.replace("data: ", ""))
                    if "content" in data:
                        full_response += data["content"]
                except json.JSONDecodeError:
                    pass

        full_response = full_response.strip()
        
        if full_response != "NONE" and full_response != "":
            for line in full_response.split('\n'):
                fact = line.strip().lstrip('-').lstrip('*').strip()
                if fact:
                    self.memory_engine.add_memory(fact, source="distillation")
                    logger.info(f"Distilled new memory: {fact}")
