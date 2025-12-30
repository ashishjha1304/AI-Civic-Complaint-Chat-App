from langgraph_flow import router_node, road_issue_node, create_graph
from database import reset_session

# Test step by step
reset_session('step_test')

# Initial state
state = {
    'messages': [{'role': 'user', 'content': 'I have a pothole on the road'}],
    'issue_type': None,
    'location': None,
    'citizen_name': None,
    'complaint_description': None,
    'last_asked_field': None
}

print(f"Initial state messages: {len(state['messages'])} - {state['messages']}")

print("Step 1: Router node")
router_result = router_node(state.copy())
print(f"Router input state messages: {len(state['messages'])}")
print(f"  issue_type set to: {router_result.get('issue_type')}")
print(f"  messages: {len(router_result['messages'])}")

print("\nStep 2: Road issue node (simulating routing)")
if router_result.get('issue_type') == 'road_issue':
    road_result = road_issue_node(router_result.copy())
    print(f"  messages after road_issue_node: {len(road_result['messages'])}")
    print(f"  router messages: {len(router_result['messages'])}")
    print(f"  road messages: {len(road_result['messages'])}")
    if len(road_result['messages']) > len(router_result['messages']):
        print(f"  New message added: {road_result['messages'][-1]}")
        print("  SUCCESS!")
    else:
        print("  No new message added - checking messages:")
        print(f"    Router messages: {router_result['messages']}")
        print(f"    Road messages: {road_result['messages']}")
else:
    print("  Router didn't classify as road_issue")

print("\nStep 3: Check graph compilation")
try:
    graph = create_graph()
    print("  Graph created successfully")
    print(f"  Graph has {len(graph.nodes)} nodes")
except Exception as e:
    print(f"  Graph creation failed: {e}")