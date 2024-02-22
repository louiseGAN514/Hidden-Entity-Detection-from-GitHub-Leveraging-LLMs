import requests
import time
import urllib


class Answer:
    def __init__(self, answer, elapse):
        self.answer = answer
        self.elapse = elapse

def generate(prompt, temperature=0.01, max_length=1024):
    response = requests.post('http://localhost:8000',json={'prompt':prompt,
                             'temperature':temperature, 'max_length':max_length,
                            'context-type':'application/json'})
    if response.status_code != 200:
        return f"Error code {response.status_code}. Message {response.content}"
    else:
        return urllib.parse.unquote(response.text)

def run_prompt(prompt, temperature=0.01, max_length=1024):
    start_time = time.time()
    answer = generate(prompt, temperature=temperature, max_length=max_length)
    end_time = time.time()
    elapse = round(end_time - start_time)
    return Answer(answer, elapse)

def display_answer(answer:Answer):
    print(f"Time to generate: {answer.elapse} seconds")
    print(answer.answer)
