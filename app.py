from flask import Flask, request, jsonify, url_for
from flask_cors import CORS
from dotenv import load_dotenv
from Agents.index import chat_with_human_graph # Import the compiled graph
from OrderState import OrderState # Assuming OrderState.py is in the root
from langchain_core.messages import HumanMessage, AIMessage

load_dotenv()

app = Flask(__name__)
CORS(app)
# app = Flask(__name__, static_folder='your_static_folder_name', static_url_path='/your_static_url_path')

@app.errorhandler(Exception)
def handle_global_exception(e):
    import traceback
    app.logger.error('Unhandled Exception: %s', str(e))
    app.logger.error(traceback.format_exc())
    return jsonify({'type': 'error', 'content': 'An unexpected error occurred on the server. Please check server logs.'}), 500

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        client_history = data.get('history', [])
        user_input = data.get('newMessage') # This can be null for initial load

        # State Reconstruction
        langchain_messages = []

        # Only process history if it exists and is not empty
        if client_history:
            for msg in client_history:
                content = msg.get('content', '')
                if msg.get('sender') == 'user':
                    langchain_messages.append(HumanMessage(content=content))
                elif msg.get('sender') == 'assistant':
                    langchain_messages.append(AIMessage(content=content))

        # Add the new user input if it's not None (i.e., not an initial call)
        if user_input is not None:
            langchain_messages.append(HumanMessage(content=user_input))
            print(f"Received newMessage: {user_input}")
        else:
            # This is an initial call (newMessage is null)
            print("Initial call detected (newMessage is null)")

        if not langchain_messages and user_input is None: # Should only happen if client sends newMessage:null AND empty history
             print("Effectively an initial call for welcome message, messages list is empty.")

        print(f"Reconstructed langchain_messages: {langchain_messages}")
        print(f"Received client_history: {client_history}")


        # Construct the initial state for the graph
        current_state = OrderState(
            messages=langchain_messages,
            order=[],
            question=[],
            tools_to_answer=[],
            finished=False,
            Trois=False,
            ui=None # Initialize ui field, the graph should populate this
        )

        # Graph Invocation
        config = {"recursion_limit": 100}
        # Ensure chat_with_human_graph.invoke expects a dictionary that matches OrderState structure
        output_state_dict = chat_with_human_graph.invoke(dict(current_state), config)

        # Response Extraction
        ui_response = None
        # Check if 'ui' field is set by the graph and is a dictionary with 'type'
        if output_state_dict.get('ui') and isinstance(output_state_dict['ui'], dict) and 'type' in output_state_dict['ui']:
            ui_response = output_state_dict['ui']
            # If type is image, ensure URL is correctly formed if 'content' is just a filename
            if ui_response['type'] == 'image' and not ui_response['content'].startswith(('http://', 'https://', '/static/')):
                 # This assumes 'content' from ui is a filename like 'image.png'
                 ui_response['content'] = url_for('static', filename=f'images/{ui_response["content"]}', _external=True)

        else:
            # Fallback: Inspect the last AIMessage in the output state's messages
            last_graph_message = output_state_dict['messages'][-1] if output_state_dict['messages'] else None
            if last_graph_message and isinstance(last_graph_message, AIMessage):
                ui_response = {'type': 'text', 'content': last_graph_message.content}
            else:
                ui_response = {'type': 'error', 'content': "Sorry, I couldn't process that or no UI response found."}

        print(f"Sending UI Response: {ui_response}")

        # Prepare Client History for Response
        updated_client_history = []
        for msg in output_state_dict.get('messages', []):
            msg_type = 'text' # Default type for history messages
            msg_content = ''
            sender = ''

            if isinstance(msg, HumanMessage):
                sender = 'user'
                msg_content = msg.content
            elif isinstance(msg, AIMessage):
                sender = 'assistant'
                msg_content = msg.content # For history, we'll simplify AIMessage to its text content.
                                          # The rich 'ui_response' is for the current turn's display.
                                          # If AIMessage contains structured content (e.g. in additional_kwargs)
                                          # that needs to be preserved differently in history, this logic would need expansion.

            if sender and msg_content: # Only add if valid sender and content
                 updated_client_history.append({'sender': sender, 'content': msg_content, 'type': msg_type})

        return jsonify({
            'ui_response': ui_response,
            'updated_history': updated_client_history
        })

    except Exception as e:
        import traceback
        app.logger.error('Chat Endpoint Exception: %s', str(e))
        app.logger.error(traceback.format_exc())
        return jsonify({'type': 'error', 'content': f'An error occurred while processing your request: {str(e)}'}), 500

if __name__ == '__main__':
    # For example, to see app.logger.error output:
    # import logging
    # logging.basicConfig(level=logging.DEBUG)
    app.run(host='0.0.0.0', port=5000, debug=True)
