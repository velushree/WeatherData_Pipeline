import os
import sys
sys.path.append("path_to_your_installed_packages")
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.vectorstores.faiss import FAISS
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

load_dotenv()

cities = [
    "New York", "London", "Tokyo", "Paris", "Los Angeles", "Chicago", "Beijing", "Mumbai", "Bangkok", "Dubai",
    "Singapore", "Toronto", "San Francisco", "Istanbul", "Seoul", "Mexico City", "Moscow", "Sydney", "Barcelona",
    "Rome", "Berlin", "Amsterdam", "Delhi", "Shanghai", "Cairo", "Jakarta", "Hong Kong", "Buenos Aires", "Lagos"
]

current_dir = os.path.dirname(os.path.abspath(__file__))
persistent_directory = "D:\\Projects\\WeatherData_Pipeline\\db\\faiss_index"

embedding_model = HuggingFaceEmbeddings(model_name="BAAI/bge-base-en-v1.5", model_kwargs={"device": "cpu"} )
db = FAISS.load_local(persistent_directory, embedding_model, allow_dangerous_deserialization=True)

retriever = db.as_retriever(
    search_type = "similarity",
    search_kwargs={'k': 1}
)

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")

# Contextualize prompt
contextualize_prompt = (
    "Reformulate the latest user question into a fully self-contained question "
    "that can be understood without any prior context. Ensure all necessary details "
    "from the chat history are included in the question itself. "
    "Do NOT answer the question, just return the reformulated version. "
    "If the question is already standalone, return it as is."
)

contextualize_prompt_template = ChatPromptTemplate.from_messages([
    ("system", contextualize_prompt),
    (MessagesPlaceholder("chat_history")),
    ("human", "{input}")
])

# History-aware retriever
History_aware_retriever = create_history_aware_retriever(llm, retriever, contextualize_prompt_template)

# answer prompt
answer_prompt = (    ""
    "You are an assistant for question-answering tasks. "
    "You CAN ASSIST and GREET the users."
    "Use the provided context to answer the question. "
    "Use three sentences maximum and keep the answer concise. "
    "By default, you have access only to the data available in your knowledge base. "
    "Based on the given weather data context try to predict the weather tomorrow."
    "If the user asks for information about a city or topic not found in the context, dont try try answer ur self' "
    "If any data is empty in the provided context DO NOT MENTION THAT DATA while answering"
    "Also include self-care tips in bullet points based on the weather data and conditions in new line."
    "\n\n"
    "{context}"
)

answer_prompt_template = ChatPromptTemplate.from_messages([
    ("system", answer_prompt),
    (MessagesPlaceholder("chat_history")),
    ("human", "{input}")
])

# document chain
question_answer_chain = create_stuff_documents_chain(llm=llm, prompt=answer_prompt_template)
rag_chain = create_retrieval_chain(History_aware_retriever, question_answer_chain)

def get_chatbot_response(user_input, chat_history):    
    result = rag_chain.invoke({"input": user_input, "chat_history": chat_history})
    return result["answer"]