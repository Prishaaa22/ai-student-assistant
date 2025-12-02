from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings
from openai import OpenAI
from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

def ask_agent(query):
    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
    db = Chroma(persist_directory="college_db", embedding_function=embeddings)

    results = db.similarity_search(query, k=3)
    context = "\n\n".join([r.page_content for r in results])

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful AI Student Support agent."},
            {"role": "user", "content": f"Context: {context}\n\nQuestion: {query}"}
        ]
    )

    return response.choices[0].message["content"]
