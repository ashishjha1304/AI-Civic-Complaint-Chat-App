from langgraph_flow import graph, get_session_state
from database import reset_session

# Test with fresh session
reset_session('final_test')

state = get_session_state('final_test')
state['messages'] = [{'role': 'user', 'content': 'I have a pothole on the road'}]

print('Testing graph.stream to see execution steps:')
print(f'Input messages: {len(state["messages"])}')

# Use stream to see what happens at each step
step_count = 0
for step in graph.stream(state, stream_mode="updates"):
    step_count += 1
    print(f'\nStep {step_count}:')
    for node_name, node_state in step.items():
        print(f'  Node: {node_name}')
        messages = node_state.get('messages', [])
        print(f'  Messages: {len(messages)}')
        for i, msg in enumerate(messages):
            print(f'    {i}: {type(msg).__name__} - {getattr(msg, "content", "no content")[:50]}...')
        print(f'  issue_type: {node_state.get("issue_type")}')
        print(f'  location: {node_state.get("location")}')

print(f'\nTotal steps: {step_count}')

# Also try invoke
print('\nTesting graph.invoke:')
result = graph.invoke(state)
print(f'Result messages: {len(result["messages"])}')

# Check all messages in detail
print('\nDetailed message analysis:')
for i, msg in enumerate(result['messages']):
    print(f'Message {i}:')
    print(f'  Type: {type(msg).__name__}')
    if isinstance(msg, dict):
        print(f'  Dict content: {msg}')
        if msg.get('role') == 'assistant':
            print(f'  *** FOUND ASSISTANT MESSAGE: {msg.get("content")}')
    else:
        print(f'  Object type: {getattr(msg, "type", "no type")}')
        print(f'  Content: {getattr(msg, "content", "no content")[:100]}...')
        if hasattr(msg, 'role'):
            print(f'  Role: {msg.role}')
        if hasattr(msg, 'type') and msg.type == 'assistant':
            print(f'  *** FOUND ASSISTANT MESSAGE (type): {msg.content}')
