"""Prompt templates for Conversational RAG."""

from langchain_core.prompts import (
	ChatPromptTemplate,
	HumanMessagePromptTemplate,
	MessagesPlaceholder,
	SystemMessagePromptTemplate,
)

from chat.model.models import PromptType


# Rewrites the latest user input into a standalone question using chat history.
CONTEXTUALIZE_QUESTION_PROMPT = ChatPromptTemplate.from_messages(
	[
		SystemMessagePromptTemplate.from_template(
			"""
You are a helpful assistant. Given a chat history and the latest user question, rewrite the
question so it can be understood without the history. Do not answer the question. If the
question is already standalone, return it unchanged.
			"""
		),
		MessagesPlaceholder("chat_history"),
		HumanMessagePromptTemplate.from_template("{input}"),
	]
)


# Answers the user using retrieved context; avoid inventing facts.
CONTEXT_QA_PROMPT = ChatPromptTemplate.from_messages(
	[
		SystemMessagePromptTemplate.from_template(
			"""
You are a concise assistant for question answering. Use the provided context to answer the
question. If the answer is not in the context, say you don't know. Keep answers brief.

Context:
{context}
			"""
		),
		MessagesPlaceholder("chat_history"),
		HumanMessagePromptTemplate.from_template("Question: {input}"),
	]
)


PROMPT_REGISTRY = {
	PromptType.CONTEXTUALIZE_QUESTION.value: CONTEXTUALIZE_QUESTION_PROMPT,
	PromptType.CONTEXT_QA.value: CONTEXT_QA_PROMPT,
}
