import os
import uuid
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, Header, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, EmailStr

from backend.auth import initialize, register, login, get_user

from backend.memory import (
    initialize_memory,
    save_message,
    get_history,
    clear_history
)

from backend.ai_engine import ask_ai, generate_code

from backend.apk_engine import analyze_apk, rebuild_apk

from backend.dex_engine import analyze_dex

from backend.image_engine import edit_image


app = FastAPI(title="FLAXXI AI")

BASE = Path(__file__).resolve().parent.parent

DATA = Path(os.getenv("DATA_DIR",str(BASE/"data")))

UPLOADS = DATA/"uploads"

OUTPUTS = DATA/"outputs"

FRONTEND = BASE/"frontend"

for folder in [DATA,UPLOADS,OUTPUTS]:
    folder.mkdir(parents=True,exist_ok=True)

initialize()
initialize_memory()


class Account(BaseModel):
    email: EmailStr
    password: str


class Chat(BaseModel):
    message: str


class Code(BaseModel):
    prompt: str
    language: str


def current_user(authorization):

    if not authorization:
        raise HTTPException(401,"Login required")

    token = authorization.replace("Bearer ","")

    user = get_user(token)

    if not user:
        raise HTTPException(401,"Invalid session")

    return user


async def upload_data(file,limit=50*1024*1024):

    data = await file.read(limit+1)

    if len(data)>limit:
        raise HTTPException(413,"File too large")

    return data


@app.get("/api/diagnostics")
def diagnostics():

    return {
        "name":"FLAXXI AI",
        "status":"online"
    }


@app.post("/api/register")
def create_account(data:Account):

    if not register(data.email,data.password):
        raise HTTPException(400,"Registration failed")

    return {"message":"Account created"}


@app.post("/api/login")
def login_account(data:Account):

    token = login(data.email,data.password)

    if not token:
        raise HTTPException(401,"Invalid credentials")

    return {"token":token}


@app.post("/api/chat")
def chat(data:Chat,authorization:str=Header(None)):

    user = current_user(authorization)

    if not data.message.strip():
        raise HTTPException(400,"Message required")

    history = get_history(user)

    save_message(user,"user",data.message)

    try:

        answer = ask_ai(data.message,history)

        save_message(user,"assistant",answer)

        return {"answer":answer}

    except Exception:

        raise HTTPException(503,"AI unavailable")


@app.post("/api/generate-code")
def code(data:Code,authorization:str=Header(None)):

    current_user(authorization)

    try:

        return {
            "language":data.language,
            "code":generate_code(data.prompt,data.language)
        }

    except Exception:

        raise HTTPException(503,"Code generation unavailable")


@app.get("/api/history")
def history(authorization:str=Header(None)):

    user = current_user(authorization)

    rows = get_history(user,100)

    return {
        "history":[
            {
                "role":item["role"],
                "message":item["content"]
            }
            for item in rows
        ]
    }


@app.delete("/api/history")
def delete_history(authorization:str=Header(None)):

    user = current_user(authorization)

    clear_history(user)

    return {"message":"History deleted"}


@app.post("/api/analyze-apk")
async def apk_analysis(
    file:UploadFile=File(...),
    authorization:str=Header(None)
):

    current_user(authorization)

    if not file.filename.lower().endswith(".apk"):
        raise HTTPException(400,"APK required")

    data = await upload_data(file)

    try:

        return analyze_apk(data)

    except Exception:

        raise HTTPException(400,"APK analysis failed")


@app.post("/api/rebuild-apk")
async def apk_rebuild(
    file:UploadFile=File(...),
    authorization:str=Header(None)
):

    current_user(authorization)

    if not file.filename.lower().endswith(".apk"):
        raise HTTPException(400,"APK required")

    data = await upload_data(file)

    try:

        result = rebuild_apk(data)

    except Exception:

        raise HTTPException(400,"APK rebuilding failed")

    filename = uuid.uuid4().hex+".apk"

    (OUTPUTS/filename).write_bytes(result)

    return {
        "download_url":"/api/download/"+filename
    }


@app.post("/api/analyze-dex")
async def dex_analysis(
    file:UploadFile=File(...),
    authorization:str=Header(None)
):

    current_user(authorization)

    if not file.filename.lower().endswith(".dex"):
        raise HTTPException(400,"DEX required")

    data = await upload_data(file)

    try:

        return analyze_dex(data)

    except Exception:

        raise HTTPException(400,"DEX analysis failed")


@app.post("/api/edit-image")
async def image_edit(
    image:UploadFile=File(...),
    mask:UploadFile=File(...),
    prompt:str="",
    authorization:str=Header(None)
):

    current_user(authorization)

    image_data = await upload_data(image)

    mask_data = await upload_data(mask)

    image_id = uuid.uuid4().hex

    original = UPLOADS/(image_id+".png")

    mask_path = UPLOADS/(image_id+"_mask.png")

    output = OUTPUTS/(image_id+"_edited.png")

    original.write_bytes(image_data)

    mask_path.write_bytes(mask_data)

    try:

        edit_image(
            str(original),
            str(mask_path),
            prompt,
            str(output)
        )

    except Exception:

        raise HTTPException(503,"Image model unavailable")

    return {
        "image_url":"/api/download/"+output.name
    }


@app.get("/api/download/{filename}")
def download(filename:str,authorization:str=Header(None)):

    current_user(authorization)

    if Path(filename).name != filename:
        raise HTTPException(400,"Invalid filename")

    path = OUTPUTS/filename

    if not path.is_file():
        raise HTTPException(404,"File not found")

    return FileResponse(path,filename=filename)


app.mount(
    "/",
    StaticFiles(directory=str(FRONTEND),html=True),
    name="frontend"
)
