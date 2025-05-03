from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from openai import OpenAI
from pydantic import BaseModel
import httpx
import json

app = FastAPI()
client = OpenAI()

# Simulated GPT function
def gpt_function(prompt: str) -> str:

    response = client.responses.create(
        model="gpt-4.1-nano",
        instructions="""You are an outfit designer. You are given constraints on which you must base your outfit.
        From the given constraints you must deduce gender, and a top and bottom clothing items.
        If all the necessary data is present, you return a json object containing two fields: a "top" field with
        which contains three words, "man"/"woman", the top clothing piece type and its color. The second field is "bottom" and
        aslo contains three words: "man"/"woman", the bottom clothing piece type and its color.
        If no gender is specified, return a json object containing an error field with "gender".""",
        input=prompt,
    )
    return response.output_text

# Pydantic model for input validation
class ConversationRequest(BaseModel):
    uid: str
    time: str
    message: str

@app.post("/process")
async def process_conversation(data: ConversationRequest):
    try:
        # Step 1: Join conversation into one string
        full_prompt = " ".join(data.conversation)
        #print(full_prompt)

        # Step 2: Send to GPT function
        gpt_response = gpt_function(full_prompt)

        gpt_json = json.loads(gpt_response)
        if "error" in gpt_json:
            if gpt_json["error"] == "gender" : 
                # envia "Falta gender" a wasap
                return JSONResponse(status_code=200)
            #Comprovacio d'error i envia missatge a whatsapp

        # Step 4: Send JSON to second system (mock URL for now)
        async with httpx.AsyncClient() as client:
            response = await client.post("http://localhost:8001/second", json=gpt_json)

        if response.status_code != 200:
            pass
            #Enviar missatge a whats de l'error i despres marxar
            return
            # NO FA FALTAAAAAAAAAraise HTTPException(status_code=500, detail="Second system failed")

        second_json = response.json()
        
        #enviar un missatge a whats amb second_json com a contingut formatejat.
        return JSONResponse(status_code=200)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Run with: uvicorn main:app --reload
# Input: La conversacio --> La conversacio va cap a la funcio de Joan
# Joan en retorna un json en format de text. El que hem de fer es comprovar que te l'estrtuctura de json, comprovar que te tot el que necessitem
# Peticio post get prediction (Dins del post haurem de ficar la convo del json de whats)
# Retornem: Un json de les peces comprimides (cami blanca) al Arnau
