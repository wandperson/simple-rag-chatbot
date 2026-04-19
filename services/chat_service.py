# LLM
from openai import OpenAI

# Custom modules
from database import DatabaseOperations


OPENAI_KEY = ""


class ChatService:
    def __init__(self):
        self.database = DatabaseOperations()
        self.openai_client = OpenAI(api_key=OPENAI_KEY) if OPENAI_KEY else None

        self.embedding_model_name = "text-embedding-3-small"
        self.embedding_dimensions = 512
        self.llm_model_name = "gpt-4o-mini"

    def get_answer(self, question: str, include_history: bool) -> dict[str, str]:
        # Save user question to DB
        user_msg_row = {"role": "user", "content": question}
        self.database.insert_message(user_msg_row)

        # Return fake answer if OpenAI client is not initialized
        if not self.openai_client:
            return self._fallback_answer()

        prompt_messages = []

        # Generate system instruction for LLM
        for instruction in self.database.select_llm_instructions():
            prompt_messages.append({"role": "system", "content": instruction})

        # Retrieve relevant context and provide for LLM as system insruction
        if context := self._get_context(question):
            prompt_messages.append(
                {"role": "system", "content": f"""<CONTEXT>\n{context}\n</CONTEXT>"""}
            )

        # Get chat user history and add to chat
        if include_history:
            history = self.database.select_history()
            prompt_messages.extend(history)

        # Add user meessage to prompt
        prompt_messages.append(user_msg_row)

        # Send to LLM for proceed messages
        answer = self._get_completion(prompt_messages)
        llm_msg_row = {"role": "assistant", "content": answer}
        self.database.insert_message(llm_msg_row)

        return llm_msg_row

    def _fallback_answer(self) -> dict:
        context = self.database.retrieve_context()
        answer = (
            f"<b>Assistant would answered your question with CONTEXT:</b><br>{context}"
        )
        result = {"role": "assistant", "content": answer}
        self.database.insert_message(result)
        return result

    def _get_context(self, text: str) -> str:
        response = self.openai_client.embeddings.create(
            model=self.embedding_model_name,
            dimensions=self.embedding_dimensions,
            input=text,
        )
        embedding = response["data"][0]["embedding"]

        context = self.database.retrieve_context(embedding)

        return context

    def _get_completion(self, messages: list[dict]) -> str:
        completion = self.openai_client.chat.completions.create(
            model=self.llm_model_name,
            messages=messages,
            temperature=0.05,
            max_tokens=512,
        )
        content = completion.choices[0].message.content

        return content

    def get_user_history(self) -> list[dict]:
        return self.database.select_history()
