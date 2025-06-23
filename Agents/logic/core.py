from index import chat_with_human_graph
from langchain_core.messages import HumanMessage
def process_user_input(history, user_text):
    messages = list(history) + [HumanMessage(content=user_text)]
    state = {
        "messages": messages,
        "order": [],
        "question": user_text,
        "tools_to_answer": [],
        "finished": False,
        "Trois": False
    }
    print(">> input to agent:", messages)

    result = chat_with_human_graph.invoke(state, config={"recursion_limit": 100})

    # On prépare le résultat final
    updated_state = result

    # 🔍 Ajout de la requête d'origine si elle a été extraite
    if "request_call" not in result:
        print("⚠️ Aucune 'request_call' trouvée dans le résultat.")
    else:
        print("✅ 'request_call' détecté.")

    return {
        "messages": result["messages"],
        "state": updated_state
    }
