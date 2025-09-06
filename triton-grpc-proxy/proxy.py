import os

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import numpy as np
import tritonclient.grpc as grpcclient

TRITON_URL = os.getenv("TRITON_URL", "tritonserver:8001")

client = grpcclient.InferenceServerClient(url=TRITON_URL)
app = FastAPI()


@app.on_event("startup")
def debug_model_info():
    try:
        metadata = client.get_model_metadata(model_name="Qwen/Qwen3-Embedding-0.6B")
        config = client.get_model_config(model_name="Qwen/Qwen3-Embedding-0.6B")

        print("=== Model Metadata ===")
        print(metadata)

        print("=== Model Config ===")
        print(config)
    except Exception as e:
        print(f"Failed to fetch model info: {e}")


@app.get("/v1/model_info/{model}")
async def model_info(model: str):
    try:
        metadata = client.get_model_metadata(model_name=model)
        config = client.get_model_config(model_name=model)

        return {
            "metadata": grpcclient._get_error_grpc_message(metadata).decode()
            if hasattr(metadata, "ByteSize")
            else str(metadata),
            "config": str(config),
        }
    except Exception as e:
        return {"error": str(e)}


@app.post("/v1/debug/{model}")
async def debug_input(model: str, req: EmbeddingRequest):
    try:
        clean_inputs = [str(x) for x in req.input]
        arr = np.array(clean_inputs, dtype=np.object_)
        return {
            "model": model,
            "inputs": clean_inputs,
            "types": [str(type(x)) for x in clean_inputs],
            "numpy_dtype": str(arr.dtype),
            "numpy_shape": arr.shape,
            "numpy_repr": arr.tolist(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class EmbeddingRequest(BaseModel):
    input: List[str]
    model: str


@app.post("/v1/embeddings")
async def create_embedding(req: EmbeddingRequest):
	# Shape: [batch], dtype=object (for STRING in Triton)
    text_input = grpcclient.InferInput("text", [len(req.input)], "STRING")
    text_input.set_data_from_numpy(
        np.array(req.input, dtype=np.object_)
    )

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
