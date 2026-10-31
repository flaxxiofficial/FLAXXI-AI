# FLAXXI AI

Your AI. Your Intelligence.

A multi-functional AI assistant.

## Features

- AI Chat
- Login/Register
- Persistent Memory
- Code Generation
- Image Editing
- APK Analysis
- APK Rebuilding
- DEX Analysis

## Installation

Install Python 3.11.

Install dependencies:

pip install -r requirements.txt

Configure environment variables:

SECRET_KEY=your-secret-key
OLLAMA_URL=http://localhost:11434
AI_MODEL=qwen2.5:3b

Install Ollama and pull model:

ollama pull qwen2.5:3b

Start backend:

uvicorn backend.server:app --reload

Open:

http://localhost:8000

## Deployment

Connect this GitHub repository to Render.

Configure environment variables and persistent storage.

## Project

FLAXXI AI
Your AI. Your Intelligence.
