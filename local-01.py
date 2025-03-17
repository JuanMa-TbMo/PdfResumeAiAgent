
import ollama

def create_agent(step_number):
    def agent(task):
        response = ollama.chat(
            model='llama3.2:3b',
            messages=[
                {
                    'role': 'system',
                    'content': f'You are an AI assistant agent{step_number} tasked with answering ONLY the step {step_number}. Ignore all other steps',
                },
                {
                    'role': 'user',
                    'content': f'Given this task:{task}\n Provide implementation for step {step_number} only',
                }
            ]
        )
        return response['message']['content']
    return agent


def Main_agent(user_input,is_final=False):
    system_prompt='You are O1, an AI focused on step-by-step reasoning. For any task, break it down into 4 smaller, logical steps, organize them in a clear sequence, solve each step thoroughly, and provide feedback with a summary of results and insights.' if not is_final else 'sumarize the following plan'
    
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


def process_task(user_input):
    inital_plan= Main_agent(user_input)

    agents = [create_agent(i) for i in range(1,5) ]
    implementatios=[agent(inital_plan) for agent in agents]

    final_input=f"Initial Plan:\n{inital_plan}\n\nImplementations:\n"+"\n".join(implementatios)
    final_sum= Main_agent(final_input,is_final=True) 
    with open("final_sum.txt",'w') as f:
        f.write(final_sum)
    return final_sum


question= "how should i use ai to make money"
final_res=process_task(question)

print(final_res)

