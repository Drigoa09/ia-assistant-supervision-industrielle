from flask import Flask, request, jsonify, url_for # url_for might not be needed for test_chat
from flask_cors import CORS
from dotenv import load_dotenv
# from Agents.index import chat_with_human_graph # Commented out
# from Agents.OrderState import OrderState # Commented out
# from langchain_core.messages import HumanMessage, AIMessage # Commented out

load_dotenv()

app = Flask(__name__)
CORS(app) # Use simple global CORS for now
# CORS(app, resources={r"/chat": {"origins": "*", "methods": ["POST", "OPTIONS"], "allow_headers": ["Content-Type"]}}) # Commented out specific CORS

@app.errorhandler(Exception)
def handle_global_exception(e):
    import traceback
    app.logger.error('Unhandled Exception: %s', str(e))
    app.logger.error(traceback.format_exc())
    return jsonify({'type': 'error', 'content': 'An unexpected error occurred on the server. Please check server logs.'}), 500

# @app.route('/chat', methods=['POST', 'OPTIONS']) # Original chat route commented out
# def chat():
#     print("FLASK: /chat endpoint entered, request method:", request.method)
#     try:
#         data = request.json
#         client_history = data.get('history', [])
#         user_input = data.get('newMessage')

#         langchain_messages = []

#         if client_history:
#             for msg in client_history:
#                 content = msg.get('content', '')
#                 if msg.get('sender') == 'user':
#                     langchain_messages.append(HumanMessage(content=content))
#                 elif msg.get('sender') == 'assistant':
#                     langchain_messages.append(AIMessage(content=content))

#         if user_input is not None:
#             langchain_messages.append(HumanMessage(content=user_input))
#             print(f"Received newMessage: {user_input}")
#         else:
#             print("Initial call detected (newMessage is null)")

#         if not langchain_messages and user_input is None:
#              print("Effectively an initial call for welcome message, messages list is empty.")

#         print(f"Reconstructed langchain_messages: {langchain_messages}")
#         print(f"Received client_history: {client_history}")

#         current_state = OrderState(
#             messages=langchain_messages,
#             order=[],
#             question=[],
#             tools_to_answer=[],
#             finished=False,
#             Trois=False,
#             ui=None
#         )

#         config = {"recursion_limit": 100}
#         output_state_dict = chat_with_human_graph.invoke(dict(current_state), config)

#         ui_response = None
#         if output_state_dict.get('ui') and isinstance(output_state_dict['ui'], dict) and 'type' in output_state_dict['ui']:
#             ui_response = output_state_dict['ui']
#             if ui_response['type'] == 'image' and not ui_response['content'].startswith(('http://', 'https://', '/static/')):
#                  ui_response['content'] = url_for('static', filename=f'images/{ui_response["content"]}', _external=True)
#         else:
#             last_graph_message = output_state_dict['messages'][-1] if output_state_dict['messages'] else None
#             if last_graph_message and isinstance(last_graph_message, AIMessage):
#                 ui_response = {'type': 'text', 'content': last_graph_message.content}
#             else:
#                 ui_response = {'type': 'error', 'content': "Sorry, I couldn't process that or no UI response found."}

#         print(f"Sending UI Response: {ui_response}")

#         updated_client_history = []
#         current_ui_content_for_matching = None
#         current_ui_type = 'text'

#         if isinstance(ui_response, dict):
#             current_ui_type = ui_response.get('type', 'text')
#             if current_ui_type == 'text':
#                  current_ui_content_for_matching = ui_response.get('content')
#             elif ui_response.get('content'):
#                  current_ui_content_for_matching = ui_response.get('content')

#         for msg_idx, msg in enumerate(output_state_dict.get('messages', [])):
#             is_last_message = (msg_idx == len(output_state_dict.get('messages', [])) - 1)

#             if isinstance(msg, HumanMessage):
#                 updated_client_history.append({
#                     'sender': 'user',
#                     'content': msg.content,
#                     'type': 'text'
#                 })
#             elif isinstance(msg, AIMessage):
#                 msg_render_type = 'text'
#                 if is_last_message and msg.content == current_ui_content_for_matching:
#                     msg_render_type = current_ui_type
#                 elif is_last_message and ui_response and ui_response.get('type') != 'text' and isinstance(ui_response.get('content'), str) and msg.content == ui_response.get('content'):
#                     msg_render_type = ui_response.get('type')
#                 elif is_last_message and not current_ui_content_for_matching and ui_response:
#                      msg_render_type = current_ui_type

#                 updated_client_history.append({
#                     'sender': 'assistant',
#                     'content': msg.content,
#                     'type': msg_render_type
#                 })
#                 if is_last_message and msg_render_type != 'text' and updated_client_history[-1]['content'] != current_ui_content_for_matching :
#                     if current_ui_content_for_matching :
#                         updated_client_history[-1]['content'] = current_ui_content_for_matching

#         return jsonify({
#             'ui_response': ui_response,
#             'updated_history': updated_client_history
#         })

#     except Exception as e:
#         import traceback
#         app.logger.error('Chat Endpoint Exception: %s', str(e))
#         app.logger.error(traceback.format_exc())
#         return jsonify({'type': 'error', 'content': f'An error occurred while processing your request: {str(e)}'}), 500

@app.route('/test_chat', methods=['POST', 'OPTIONS']) # Keep OPTIONS for route matching
def test_chat():
    # Flask-CORS with CORS(app) should handle the OPTIONS preflight.
    print(f"FLASK: /test_chat endpoint entered, request method: {request.method}")

    if request.method == 'POST':
        try:
            data = request.json
            if data is None: # Handle case where JSON is not sent or malformed
                print("FLASK: /test_chat received no JSON data or malformed JSON.")
                return jsonify({"type": "error", "content": "Request body must be JSON."}), 400

            print("FLASK: /test_chat received data:", data)
            # Modified to expect 'newMessage' instead of 'message' to align with script.js payload
            user_message = data.get("newMessage", "No newMessage provided in JSON")

            response_data = {
                "reply": "TestData: Hello from Flask (test_chat)", # Added TestData: prefix
                "received_message": user_message
            }
            return jsonify(response_data), 200
        except Exception as e:
            print(f"FLASK: Error in /test_chat: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({"type": "error", "content": str(e)}), 500

    # If it's an OPTIONS request that somehow got past Flask-CORS to the function body
    if request.method == 'OPTIONS':
        response = app.make_default_options_response()
        return response

    # Fallback for any other case (should not happen with methods specified)
    return jsonify({"error": "This part should ideally not be reached."}), 405


if __name__ == '__main__':
    # For example, to see app.logger.error output:
    # import logging
    # logging.basicConfig(level=logging.DEBUG)
    app.run(host='0.0.0.0', port=5000, debug=True)
