import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.1,
    max_tokens=1000,
    api_key=os.getenv("GEMINI_API_KEY"),
)

template = (
    "You are tasked with extracting specific information from the following text content:\n\n"
    "{dom_content}\n\n"
    "Please follow these instructions:\n"
    "1. Extract only the following: {parse_description}.\n"
    "2. If not found, return an empty string ('').\n"
    "3. Do not include any extra commentary or explanations.\n"
    "4. Return only the exact information requested."
)

def parse_text(text):
    prompt = ChatPromptTemplate.from_template(template)
    chain =prompt | llm

    response = chain.invoke({
        "dom_content": text,
        "parse_description": "Professor's research interest, publications, current ongoing project, previous projects. If not found, return an empty string."
    })

    return response.content if response.content else ""




