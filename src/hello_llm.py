import os, sys
from dotenv import load_dotenv
from openai import OpenAI

# Load OPENAI_API_KEY from the environment — never hard-code keys
load_dotenv()

# Initialize the client with a custom base URL
client = OpenAI(
    base_url="https://openai.vocareum.com/v1" # Replace with your API base URL
)

def ask(question: str) ->str:

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are concise."},
            {"role": "user", "content": question},
        ],
        temperature=0.3,
    )
    return resp.choices[0].message.content

if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) or 'Say hello in one sentence'
    print(ask(q))
