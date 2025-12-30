import asyncio
from langgraph_flow import process_message

async def test_full_flow():
    print('Testing full complaint submission flow...')

    # Simulate user messages that would trigger complaint creation
    messages = [
        'I have a pothole on the road',
        'Main Street near the park',
        'John Smith',
        'There is a large pothole that is very dangerous for vehicles',
        'john.smith@email.com',
        'urgent'
    ]

    session_id = 'full_test'

    for i, message in enumerate(messages, 1):
        print(f'\n--- Step {i}: User says \"{message}\" ---')
        response = await process_message(message, session_id)
        print(f'Bot response: {response}')

    print('\n--- Test completed ---')
    print('Check Supabase dashboard to verify complaint was saved!')

if __name__ == "__main__":
    asyncio.run(test_full_flow())
