# ADR-0001: Capstone Framing — Open_Source_Documentation
- **Status:** Draft v1
- **Date:** 2026-07-16
- **Author:** Deeksha Bestta
## Context
what problem is this capstone trying to solve?
Developers, Students and Researchers spend significant time searching through open source documentation such as Langchain to find relevant information.This project uses RAG and Agentic AI to provide accurate answers from the documentation ,thereby reducing search time and improving efficiency.

Who is this for?
The solution is intended for 
-AI Engineers
-Software Developers
-Technical Researchers

why now?
The rapid growth of Generative AI has led to an explosion of frameworks such as LangChain, LlamaIndex, FastAPI, OpenAI, CrewAI, AutoGen, and many others. Their documentation is extensive and evolves frequently, making it increasingly difficult for developers to stay up to date.

Reference from :
OpenAI. (2026). ChatGPT(GPT-5.5)[Large language model]. https://chat.openai.com/

## Decision — Solution Framing Canvas
| Box | Your answer |
|-----|-------------|
| **Inputs** | Natural language Text, Uploaded documentation (example:PDF) |
| **Outputs** | The system produces — a text answer|
| **Tools** | Python,OpenAI LLM,Langchain,Vector DB,LangGraph,FastAPI |
| **Memory** | Short term memory conversation only for the current session to maintain context |
| **Autonomy level** | The system independently retrieves relevant documents, selects tools, reasons over retrieved context, and generates responses, but it only answers user queries and does not execute external actions.|
| **Decision boundaries** | The agent can retrieve documentation, choose retrieval strategies, and generate answers based only on indexed documentation. It cannot fabricate information, modify documentation, access external systems without permission, or perform actions on behalf of the user.|
## Consequences
- **Positive:** 
    -Provides fast, accurate, and context-aware answers from open-source documentation.

    -Reduces the time developers spend manually searching through documentation.

    -Generates grounded responses with citations, improving trust and reliability.
- **Negative / risks:** 
    -Response quality depends on the quality and freshness of the indexed documentation.

    -Maintaining the vector database requires periodic re-indexing as documentation changes.
- **Things we'll re-visit:** 
    -Evaluate support for additional documentation sources (e.g., GitHub repositories, Stack Overflow, API references).

    -Assess the need for long-term conversational memory and more advanced agent workflows (e.g., multi-agent collaboration or autonomous task execution).

Reference from :
OpenAI. (2026). ChatGPT(GPT-5.5)[Large language model]. https://chat.openai.com/