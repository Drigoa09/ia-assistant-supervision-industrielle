from flask import Flask, request, jsonify, url_for
from flask_cors import CORS # Added import
from Agents.Graph_Agents.generateurReponse import generer_reponse
# HumanMessage is needed to construct the input state for generer_reponse
from langchain_core.messages import HumanMessage
# AIMessage and SystemMessage are not directly used here anymore as generer_reponse's output is simplified.
# AGENT_GENERATION_SYSINT and WELCOME_MSG are also handled within generer_reponse.

app = Flask(__name__)
CORS(app) # Added CORS initialization
# Ensure the static folder is configured. By default, Flask uses a 'static' folder in the same directory as the app.
# If a different static folder name or path were used, it would need to be specified:
# app = Flask(__name__, static_folder='your_static_folder_name', static_url_path='/your_static_url_path')

# Global error handler for unhandled exceptions
@app.errorhandler(Exception)
def handle_global_exception(e):
    # Log the exception with traceback for server-side debugging
    import traceback
    app.logger.error('Unhandled Exception: %s', str(e))
    app.logger.error(traceback.format_exc())
    # Return a standardized JSON error response to the client
    return jsonify({'type': 'error', 'content': 'An unexpected error occurred on the server. Please check server logs.'}), 500

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message_text = data.get('message')

        if user_message_text is None:
            return jsonify({'type': 'error', 'content': 'No message provided'}), 400

        print(f"Received message: {user_message_text}")

        # Construct the initial state for generer_reponse
        current_messages = [HumanMessage(content=user_message_text)]
        initial_state = {
            "messages": current_messages,
            # Other OrderState fields, initialized to default/empty if not directly used for this interaction
            "order": [],
            "question": [],
            "tools_to_answer": [],
            "finished": False,
            "Trois": False
        }

        # Call the assistant logic. It now returns a dict: {'type': ..., 'data': ...}
        assistant_output = generer_reponse(initial_state)

        response_type = assistant_output.get("type")
        response_data = assistant_output.get("data")

        if response_type == "text":
            return jsonify({'type': 'text', 'content': response_data})
        elif response_type == "image":
            # response_data is the filename, e.g., "simulated_graph.png"
            # IMPORTANT: This assumes 'static/images/' directory exists and contains the image.
            # Directory creation failed earlier, so this URL will be generated but might not resolve to a viewable image.
            image_url = url_for('static', filename=f'images/{response_data}', _external=True)
            return jsonify({'type': 'image', 'content': image_url})
        elif response_type == "list":
            return jsonify({'type': 'list', 'content': response_data})
        else:
            print(f"Unknown response type from assistant: {response_type}")
            return jsonify({'type': 'error', 'content': 'Received unknown response type from assistant.'}), 500

    except Exception as e:
        print(f"Error in /chat endpoint specific to this route: {e}") # Differentiate from global handler log
        # Log the full traceback for debugging on the server
        import traceback
        app.logger.error('Chat Endpoint Exception: %s', str(e)) # Use app.logger for consistency
        app.logger.error(traceback.format_exc())
        return jsonify({'type': 'error', 'content': f'An error occurred while processing your request: {str(e)}'}), 500

if __name__ == '__main__':
    # Configure logging for the app if not already configured elsewhere
    # For example, to see app.logger.error output:
    # import logging
    # logging.basicConfig(level=logging.DEBUG)
    app.run(host='0.0.0.0', port=5000, debug=True)
