# Custom modules
from app.database import DatabaseOperations
from app.infrastructure.llm_provider import LLMProvider


class ChatService:
    def __init__(self, database: DatabaseOperations, provider: LLMProvider) -> None:
        self.db = database
        self.provider = provider

    def get_answer(self, question: str, include_history: bool) -> dict[str, str | None]:
        # Save user question to DB
        user_msg_row = {"role": "user", "content": question}
        self.db.insert_message(user_msg_row)

        prompt_messages = []

        # Generate system instruction for LLM
        for instruction in self.db.select_llm_instructions():
            prompt_messages.append({"role": "system", "content": instruction})

        # Retrieve relevant context and provide for LLM as system insruction
        embedding_result = self.provider.embed(question)
        if context := self.db.retrieve_context(embedding_result.vector):
            prompt_messages.append(
                {"role": "system", "content": f"""<CONTEXT>\n{context}\n</CONTEXT>"""}
            )

        if include_history:
            # Get chat user history and add to chat
            history = self.db.select_history()
            prompt_messages.extend(history)
        else:
            # Add current user message to prompt
            prompt_messages.append(user_msg_row)

        # Send to LLM for proceed messages
        answer = self.provider.get_completion(prompt_messages)
        llm_msg_row = {"role": "assistant", "content": answer}
        self.db.insert_message(llm_msg_row)

        return llm_msg_row

    def get_user_history(self) -> list[dict]:
        return self.db.select_history()
