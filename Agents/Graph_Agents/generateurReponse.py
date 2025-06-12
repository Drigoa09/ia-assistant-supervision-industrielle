import os # For potential image path manipulation, though not fully used due to dir creation issues
from langchain_core.messages import AIMessage, HumanMessage # HumanMessage for inspecting user input
# OrderState is used for input structure, but output changes
from OrderState import OrderState
from model import model

WELCOME_MSG = (
    "Bonjour ! Je suis votre assistant, comment puis-je vous aider?"
)

AGENT_GENERATION_SYSINT = (
    '''Génère une réponse à partir du message qu'on te donne. La question est dans Human Message et la réponse est dans ToolMessage'''
)

# Path for simulated image saving.
# NOTE: Directory creation failed, so this is for logical structure only.
STATIC_IMAGES_PATH = "static/images/"

def generer_reponse(state: OrderState) -> dict:
    """
    Processes user input and generates a response which can be text, a path to an image, or a list.
    Returns a dictionary like: {'type': 'text'|'image'|'list', 'data': ...}
    """
    user_message_text = ""
    if state["messages"] and isinstance(state["messages"][-1], HumanMessage):
        user_message_text = state["messages"][-1].content.lower()

    # Simulation based on keywords
    if "image" in user_message_text:
        # Simulate image generation and saving
        # In a real scenario, the model or a tool would generate an image file here.
        # Due to tool limitations, we cannot create files/directories reliably.
        # We'll just return a placeholder filename.
        image_filename = "simulated_graph.png"
        # print(f"Simulating image generation: {image_filename} (would be saved to {STATIC_IMAGES_PATH})")
        return {"type": "image", "data": image_filename}

    elif "list" in user_message_text:
        # Simulate list generation
        sample_list = ["Élément 1 de la liste", "Élément 2", "Un autre élément"]
        # print("Simulating list generation")
        return {"type": "list", "data": sample_list}

    # Default to text generation if no keywords are met
    if state["messages"]:
        # Original text generation logic
        ai_message_obj = model.invoke([AGENT_GENERATION_SYSINT] + state["messages"])
        response_content = ai_message_obj.content
    else:
        # Welcome message
        response_content = WELCOME_MSG
        # We wrap it in an AIMessage-like structure if other parts of calling code expect that,
        # but here we just need the content for the dict.

    return {"type": "text", "data": response_content}
