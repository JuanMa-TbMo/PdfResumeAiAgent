#summarize.py
import ollama


def Main_agent(user_input, info_input):
    system_prompt=f'You are an Ai focused in summarizing this Info: {info_input} . Based on this demands: {user_input}'
    
    response = ollama.chat(
        model='llama3.2:3b',
        messages=[
            {
                'role': 'system',
                'content': system_prompt
            },
            {
                'role': 'user',
                'content': user_input
            }
        ]
    )
    return response['message']['content']