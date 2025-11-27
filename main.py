# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "httpx",
#   "python-dotenv",
#   "fastapi",
#   "uvicorn"
# ]
# ///

import os
import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import httpx
from dotenv import load_dotenv
from fastapi import BackgroundTasks
import time
import subprocess

load_dotenv()  # loads .env file

AIPIPE_TOKEN = os.getenv("AIPIPE_TOKEN")
AIPIPE_URL = os.getenv("AIPIPE_API_URL")
SECRET_KEY = os.getenv("SECRET")


app = FastAPI()
# create a FastAPI that takes POST requests at /receive_request in this format 
"""{
  "email": "your email",
  "secret": "your secret",
  "url": "https://tds-llm-analysis.s-anand.net/demo"
}

"""

def process_request(data):
    # function to process the request data
    # import time to simulate a long running task

    print("processing request for:", data.get("email"))
  
    # post this JSON to "url": "https://tds-llm-analysis.s-anand.net/submit" // A unique task url 
    """{"email": "your email","secret": "your secret","url": "https://tds-llm-analysis.s-anand.net/submit","answer": "anything you want"}"""

    # visit the url that comes in data["url"] and it will be having a quiz, read the quiz and do whatever it ask to do, have llm
    # generate code from taking request(data) that came and still sending response to the submit url that's on page

    prompt_for_llm = f"""
    Generate a standalone Python script that performs the following tasks:
    1. Uses `httpx` to visit the URL: {data.get("url")}.
    2. Extracts the quiz question from the page.
    3. Here are some types of questions you can expect:
            Scraping a website (which may require JavaScript) for information
            Sourcing from an API (with API-specific headers provided where required)
            Cleansing text / data / PDF / … you retrieved
            Processing the data (e.g. data transformation, transcription, vision)
            Analysing by filtering, sorting, aggregating, reshaping, or applying statistical / ML models. Includes geo-spatial / network analysis
            Visualizing by generating charts (as images or interactive), narratives, slides
    4. Uses the AIPIPE API to generate the answer dynamically. 
       - API URL: {AIPIPE_URL}
       - API Token: {AIPIPE_TOKEN}
       - Use model: "gpt-4o-mini"
    5. Submits the answer to the submission endpoint: https://tds-llm-analysis.s-anand.net/submit
    
    The script must be fully functional, handle JSON formatting/headers correctly, 
    and NOT hardcode the answer. It must solve the quiz at runtime using the LLM API.
    Your job is to generate a whole single python script that will solve the quiz by scraping the website and using the AIPIPE API,
    and solve the question at runtime and submit the answer to the submission endpoint.
    """
    
    
    llm_response = httpx.post(
        AIPIPE_URL,
        headers={
            "accept":"*/*",
            "accept-language":"en-US,en;q=0.9",
            "Authorization": f"Bearer {AIPIPE_TOKEN}",
            "Content-Type": "application/json"
        },
        json={
            "model": "openai/gpt-4o-mini",
            "max_tokens": 1000,
            "messages": [
                {"role": "system","content": "You are a helpful assistant that generates python scripts."},
                {"role": "user","content": prompt_for_llm}
            ]
        }, timeout=60       
    )

    answer_script = llm_response.json()

    # use subprocess to run the generated script
    generated = answer_script.get('choices')[0]['message']['content'] 
    with open("generated_script.py", "w") as f:
        f.write(generated)
    completed = subprocess.run(["python", "generated_script.py"], capture_output=True, text=True, env=os.environ.copy())
    stdout = completed.stdout
    stderr = completed.stderr

    print("finished processing for:", data.get("email"))
    
    # print(stdout)
    # print(stderr)
    pass


@app.post("/receive_request")
async def receive_request(request: Request, background_tasks: BackgroundTasks):
    data = await request.json() 
    # validate the secret if it is correct then send 200 OK otherwise send 403
    if data.get("secret") != SECRET_KEY:
        return JSONResponse(content={"error": "Forbidden"}, status_code=403)
    else:
      # run the function to process the request in background using fastapi's background tasks
      background_tasks.add_task(process_request, data)
      return JSONResponse(content={"message": "Request received"}, status_code=200)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
