from openai import OpenAI
from dotenv import load_dotenv
import os

print("Step 1")

load_dotenv()

print("Step 2")

client = OpenAI()

print("Step 3")

response = client.responses.create(
    model="gpt-5",
    input="Say hello in one sentence."
)

print("Step 4")

print(response.output_text)
