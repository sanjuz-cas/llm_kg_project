import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import GraphCypherQAChain
from langchain_community.graphs import Neo4jGraph
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Ensure you have your GOOGLE_API_KEY set up in your .env file
llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0)

# This uses the older Neo4jGraph class that the chain expects
graph = Neo4jGraph(
    url=os.getenv("NEO4J_URI"),
    username=os.getenv("NEO4J_USERNAME"),
    password=os.getenv("NEO4J_PASSWORD")
)

# The GraphCypherQAChain will now initialize without the validation error
chain = GraphCypherQAChain.from_llm(
    llm=llm,
    graph=graph,
    verbose=True,
    # ✨ FINAL FIX HERE: Acknowledge the security warning
    allow_dangerous_requests=True
)

def ask_question(question):
    """
    Takes a user's question, sends it to the LLM chain, and prints the result.
    """
    try:
        result = chain.invoke({"query": question})
        print(f"\n> Question: {question}")
        print(f"\n> Answer: {result['result']}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    print("Knowledge Graph Q&A")
    print("Ask a question about the antibiotic resistance data. Type 'exit' to quit.")

    while True:
        user_question = input("\nYour question: ")
        if user_question.lower() == 'exit':
            break
        ask_question(user_question)