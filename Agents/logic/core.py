from index import chat_with_human_graph

def process_user_input(history, user_text):
    messages = list(history) + [user_text]
    state = {
        "messages": messages,
        "order": [],
        "question": [],
        "tools_to_answer": [],
        "finished": False,
        "Trois": False
    }
    result = chat_with_human_graph.invoke(state, config={"recursion_limit": 100})
    return result["messages"]
