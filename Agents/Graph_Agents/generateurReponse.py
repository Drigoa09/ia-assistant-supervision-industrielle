import os
from langchain_core.messages import AIMessage # HumanMessage removed as not used
from ..OrderState import OrderState # Changed to relative import
from ..model import model # Changed to relative import

WELCOME_MSG = (
    "Bonjour ! Je suis votre assistant, comment puis-je vous aider?"
)

AGENT_GENERATION_SYSINT = (
    '''Génère une réponse à partir du message qu'on te donne. La question est dans Human Message et la réponse est dans ToolMessage'''
)

# STATIC_IMAGES_PATH removed as this node now only handles text.

def generer_reponse(state: OrderState) -> dict: # This dict is a partial OrderState update
    # Get existing messages from the input state dictionary.
    # LangGraph passes the state as a dictionary.
    current_messages_from_state = state.get("messages", [])

    if not current_messages_from_state:
        # Welcome message scenario: state['messages'] was empty
        welcome_ai_msg = AIMessage(content=WELCOME_MSG)
        # The state update should include the new message list and the UI directive
        return {
            "messages": [welcome_ai_msg],
            "ui": {"type": "text", "content": WELCOME_MSG}
        }
    else:
        # Normal response generation
        # The 'messages' in the state for model invocation should be the actual list of HumanMessage/AIMessage objects
        ai_message_obj = model.invoke([AGENT_GENERATION_SYSINT] + current_messages_from_state)
        response_content = ai_message_obj.content
        new_ai_msg = AIMessage(content=response_content)

        # Append the new AI message to the existing list from the state
        updated_messages = current_messages_from_state + [new_ai_msg]

        return {
            "messages": updated_messages,
            "ui": {"type": "text", "content": response_content}
        }
