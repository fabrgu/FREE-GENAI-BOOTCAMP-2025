import os
import gradio as gr
from groq import Groq


client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),  # This is the default and can be omitted
)
prompt = """ 
Generate a structured json output for Portuguese vocabulary with this format:
  {
    "portuguese": "ler",
    "english": "to read"
  }
Do not repeat words. Do not use the same words in the example.
Generate at least 5 vocabulary items and only return the json in a list
"""

def generate_vocab_json():
    chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": prompt,
        }
    ])
    print(chat_completion.choices[0].message.content)
    return chat_completion.choices[0].message.content

with gr.Blocks() as demo:
    gr.Markdown("# Vocabulary Language Importer")
    output = gr.Textbox(label="Output Box")
    generate_btn = gr.Button("Generate Vocabulary JSON")

    generate_btn.click(generate_vocab_json, output)

demo.launch()