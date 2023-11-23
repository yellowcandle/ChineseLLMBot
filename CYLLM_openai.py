import os
from litellm import completion
from dotenv import load_dotenv

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
user_input = input("Please enter your comment: ")

# openai call
response = completion(
    model="gpt-3.5-turbo",
    messages=[
        {
            "content": "使用瓊瑤的寫作風格回應，限制在 140 字元以內",
            "role": "system"},
        {"content": user_input, "role": "user"}
    ]
)


def response_output(response):
    print(response['choices'][0]['message']['content'])


response_output(response)
