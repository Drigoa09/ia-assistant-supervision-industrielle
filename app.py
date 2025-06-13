from flask import Flask, request, jsonify, url_for
from flask_cors import CORS
from dotenv import load_dotenv
from Agents.index import chat_with_human_graph # Import the compiled graph
from Agents.OrderState import OrderState # Corrected import path
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
        # Safely get content and type from ui_response, defaulting if not present
        # current_ui_content is used to identify the AIMessage that corresponds to the current turn's ui_response
        current_ui_content_for_matching = None
        current_ui_type = 'text' # Default type

        if isinstance(ui_response, dict):
            # For image or list types, ui_response['content'] might be a URL or array/object.
            # For text type, it's the direct string.
            # The AIMessage.content from the graph should match this text content if it's a text response.
            # If ui_response was derived from state['ui'] directly, its 'content' might be different
            # from any single AIMessage's content (e.g. a graph producing a final image directly to state['ui']).
            # We use AIMessage.content matching primarily for text, or if image/list content in ui_response is the same as an AIMessage content.
            current_ui_type = ui_response.get('type', 'text')
            if current_ui_type == 'text':
                 current_ui_content_for_matching = ui_response.get('content')
            # If image/list, and if its content was derived from an AIMessage, that AIMessage's content might be the URL/data itself.
            # This matching logic is simplified; a unique ID would be better.
            elif ui_response.get('content'): # Could be URL for image, or data for list
                 current_ui_content_for_matching = ui_response.get('content')


        for msg_idx, msg in enumerate(output_state_dict.get('messages', [])):
            is_last_message = (msg_idx == len(output_state_dict.get('messages', [])) - 1)

            if isinstance(msg, HumanMessage):
                updated_client_history.append({
                    'sender': 'user',
                    'content': msg.content,
                    'type': 'text'
                })
            elif isinstance(msg, AIMessage):
                # Determine the type for this specific AIMessage
                # If this is the last AI message in the list AND its content matches what ui_response was based on, use ui_response's type.
                # This handles cases where ui_response might be text, image, or list from the latest turn.
                # This also assumes that ui_response.content (for text) or the URL (for image) matches msg.content.
                # Or, if ui_response was from state.ui directly, this AIMessage might just be a textual summary.

                msg_render_type = 'text' # Default for older AI messages or if no match
                if is_last_message and msg.content == current_ui_content_for_matching:
                    msg_render_type = current_ui_type
                elif is_last_message and ui_response and ui_response.get('type') != 'text' and isinstance(ui_response.get('content'), str) and msg.content == ui_response.get('content'):
                    # Catch-all for when ui_response content (like URL) matches message content for non-text last message
                    msg_render_type = ui_response.get('type')
                elif is_last_message and not current_ui_content_for_matching and ui_response: # ui_response from state.ui, not matching any specific AIMessage content
                     msg_render_type = current_ui_type # Trust ui_response for the last message type

                updated_client_history.append({
                    'sender': 'assistant',
                    'content': msg.content, # For images/lists, this content might be a placeholder if current_ui_type was used
                                           # but the actual rich content (URL/data) is in current_ui_content.
                                           # If msg_render_type implies rich content, use current_ui_content.
                    'type': msg_render_type
                })
                # If this is the last message and it's meant to be rich (image/list), ensure its content field is the rich content
                if is_last_message and msg_render_type != 'text' and updated_client_history[-1]['content'] != current_ui_content_for_matching :
                    if current_ui_content_for_matching : # current_ui_content_for_matching would be the URL or list data
                        updated_client_history[-1]['content'] = current_ui_content_for_matching


        return jsonify({
            'ui_response': ui_response, # ui_response is still sent for potential direct use by client if needed, though history should be primary
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
