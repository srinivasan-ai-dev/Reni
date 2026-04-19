import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.orchestration.graph import reni_app

test_path = os.path.join("backend", "uploads", "test.jpg")
if not os.path.exists(test_path):
    # Try touching it
    os.makedirs(os.path.dirname(test_path), exist_ok=True)
    with open(test_path, 'wb') as f:
        f.write(b'fake image data')

initial_state = {
    "doc_id": "TEST-001",
    "file_path": test_path,
    "iterations": 0,
}

import asyncio

async def test_pipeline():
    accumulated_state = {}
    for event in reni_app.stream(initial_state):
        node_name = list(event.keys())[0]
        accumulated_state.update(event[node_name])
    
    print("FUSION_RESULT:")
    print(accumulated_state.get('fusion_result'))
    print("ALL KEYS:")
    print(accumulated_state.keys())

# Since we don't have async calls inside stream, we can just run it synchronously
accumulated_state = {}
for event in reni_app.stream(initial_state):
    node_name = list(event.keys())[0]
    accumulated_state.update(event[node_name])
    print(f"Node {node_name} finished. Keys returned: {event[node_name].keys()}")

print("-------------")
print(accumulated_state.get("fusion_result"))
