import os

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import numpy as np
import tritonclient.grpc as grpcclient

TRITON_URL = os.getenv("TRITON_URL", "localhost:8001")

client = grpcclient.InferenceServerClient(url=TRITON_URL)
app = FastAPI()

class EmbeddingRequest(BaseModel):
    input: List[str]
    model: str

@app.post("/v1/embeddings")
async def create_embedding(req: EmbeddingRequest):
    # Use STRING instead of BYTES
    text_input = grpcclient.InferInput("text", [len(req.input)], "STRING")
    text_input.set_data_from_numpy(np.array(req.input, dtype=object))
    print(text_input)

    output_req = grpcclient.InferRequestedOutput("embeddings")
    response = client.infer(
        model_name=req.model,
        inputs=[text_input],
        outputs=[output_req]
    )

    embeddings = response.as_numpy("embeddings").tolist()
    return {
        "object": "list",
        "data": [
            {"object": "embedding", "embedding": emb, "index": idx}
            for idx, emb in enumerate(embeddings)
        ],
        "model": req.model,
        "usage": {"prompt_tokens": 0, "total_tokens": 0}
    }
