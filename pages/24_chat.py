# main.py
import streamlit as st
from langchain.chat_models import ChatOpenAI
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from cached_data import get_defense_bot,get_tba_oprs_and_ranks_for_event,get_team_zscores,get_bot_matches  # your @tool-decorated function
import os

os.environ["OPENAI_API_KEY"] = st.secrets['openai']["OPEN_API_KEY"]

# main.py

#def build_agent():
#    llm = ChatOpenAI(model="gpt-4o", temperature=0)
#    tools = [get_defense_bot]
#    agent = create_openai_functions_agent(llm=llm, tools=tools)
#    return AgentExecutor(agent=agent, tools=tools, verbose=True)

def build_agent():
    llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0)
    tools = [get_defense_bot,get_tba_oprs_and_ranks_for_event,get_team_zscores,get_bot_matches]
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant that can answer questions about FRC robots."),
        MessagesPlaceholder(variable_name="messages"),
        ("human", "{input}"),
        ("ai", "{agent_scratchpad}")
    ])

    agent = create_openai_functions_agent(llm=llm, tools=tools,prompt=prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True)

st.set_page_config(page_title="FRC Defense Chatbot", layout="wide")
st.title("🤖 FRC Defense Assistant")

if "agent_exec" not in st.session_state:
    st.session_state.agent_exec = build_agent()
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if user_question := st.chat_input("Ask about defense performance..."):
    st.session_state.messages.append({"role": "user", "content": user_question})
    with st.chat_message("user"):
        st.markdown(user_question)
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            result = st.session_state.agent_exec.invoke({
                "messages": st.session_state.messages,
                "input": user_question})
            output = result.get("output") or str(result)
            st.markdown(output)
            st.session_state.messages.append({"role": "assistant", "content": output})
