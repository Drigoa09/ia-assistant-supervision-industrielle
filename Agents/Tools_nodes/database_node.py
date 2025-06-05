from langgraph.prebuilt import ToolNode
from model import model

from langchain_core.tools import tool

@tool
def get_element(a, b) -> int:
    '''Multiply a and b'''
    return a + b

tools = [get_element]
tool_node = ToolNode(tools)

llm_with_tools = model.bind_tools(tools)
