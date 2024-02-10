import ray
from ray import serve

from fastapi import FastAPI
from transformers import pipeline

app = FastAPI()

serve_handle = None

@app.on_event("startup") # Code to be run when the server starts.
async def startup_event():
    ray.init(address="auto") # Connect to the running Ray cluster.
    client = serve.start() # Start the Ray Serve client.

    # Define a callable class to use for our Ray Serve backend.
    class GPT2:
        def __init__(self):
            self.nlp_model = pipeline("text-generation", model="gpt2")
        def __call__(self, request):
            return self.nlp_model(request.data, max_length=50)

    # Set up a backend with the desired number of replicas.
    backend_config = serve.BackendConfig(num_replicas=8)
    client.create_backend("gpt-2", GPT2, config=backend_config)
    client.create_endpoint("generate", backend="gpt-2")
    
    # Get a handle to our Ray Serve endpoint so we can query it in Python.
    global serve_handle
    serve_handle = client.get_handle("generate")

@app.get("/generate")
async def generate(query: str):
    return await serve_handle.remote(query)
