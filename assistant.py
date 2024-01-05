from openai import OpenAI
import time, json
from datetime import datetime
import assistant_functions

# define assistant prompt running

def add_date_tag(form: str = "%Y-%m-%d") -> str:
    '''
    Function returns the current date and time as a prefix to a prompt message.
    '''
    date_string = datetime.today().strftime(form)
    
    return "Message sent at " + date_string + ": \n\n"

def run_thread(client, thread, assistant_id):
    '''
    Runs the OpenAI thread and handles actions
    '''

    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id
    )

    while run.status != 'completed':
        if run.status == 'requires_action':
            run = handle_action(client, run, thread.id)

        elif run.status == 'queued' or run.status == 'in_progress':
            print("run is: " + run.status)
            time.sleep(2)
            run = client.beta.threads.runs.retrieve(
                thread_id=thread.id, 
                run_id=run.id
            )
        else:
            print("Run status is: " + run.status)
            break

    # get most recent message and return
    message = client.beta.threads.messages.list(thread_id=thread.id).data[0]
    return message


def handle_action(client, run, thread_id):
    '''
    Handles the actions required by a thread run
    Returns a new thread run
    '''
    # get calls from run object and run functions locally
    outputs = []
    print("handling action")
    for tool_call in run.required_action.submit_tool_outputs.tool_calls:
        function_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        print("running function: " + function_name + "\nwith arguments: \n" + str(arguments))

        try:
            function_to_call = getattr(assistant_functions, function_name)
        
        except Exception as e:
            print("Error getting function: \n" + e)
            break
        
        print("calling function")
        output = function_to_call(**arguments)
        print("received output of: \n" + output)

        outputs.append({"tool_call_id": tool_call.id, 
                        "output": output
                        })
    
    # submit outputs
    run = client.beta.threads.runs.submit_tool_outputs(
        thread_id=thread_id,
        run_id=run.id,
        tool_outputs=outputs
        )
    
    return run

def run_prompt(client, assistant_id, thread, prompt):
    '''
    Runs a thread with a new promp, returns the newest message generate from the assistant
    '''

    prompt = add_date_tag() + prompt

    # add message to thread
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=prompt
        )
    
    message = run_thread(client, thread, assistant_id)

    return message

    





