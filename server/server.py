from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import openai
import base64

openai.api_key = "YOUR_API_KEY"  # کلید API خودتو اینجا بذار

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def encode_file(file: UploadFile):
    content = file.file.read()
    return base64.b64encode(content).decode("utf-8"), file.content_type

@app.post("/chat")
async def chat(message: str = Form(...), file: UploadFile = File(None)):
    file_info = ""
    if file:
        encoded_data, content_type = encode_file(file)
        file_info = {
            "type": "image_url" if "image" in content_type else "file",
            "image_url": {
                "url": f"data:{content_type};base64,{encoded_data}"
            } if "image" in content_type else {}
        }

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": message}
    ]

    if file_info and file_info["type"] == "image_url":
        messages.append({
            "role": "user",
            "content": {
                "type": "image_url",
                "image_url": file_info["image_url"]
            }
        })

    response = openai.ChatCompletion.create(
        model="gpt-4-vision-preview" if file_info else "gpt-4",
        messages=messages,
        max_tokens=1000
    )

    return {"reply": response.choices[0].message['content']}
