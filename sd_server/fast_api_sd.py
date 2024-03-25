
import asyncio
from fastapi import FastAPI
# from fastapi.responses import FileResponse
# from fastapi.responses import FileResponse

# from starlette.responses import Response

from starlette.responses import FileResponse
import cv2
from PIL import  Image
from io import BytesIO

app = FastAPI()
 
from diffusers import DiffusionPipeline
# 可以在代码中快速关闭NSFW（Not safe for work）检测：https://borrowastep.net/p/-stablediffusion-nsfw--8avcvhpmu
# https://github.com/huggingface/diffusers/blob/main/src/diffusers/pipelines/stable_diffusion/safety_checker.py
# pipeline = DiffusionPipeline.from_pretrained("./taiyi-stablediffusion-1B/hf_out_5_19572")
pipeline = DiffusionPipeline.from_pretrained("./pretrain/Taiyi-Stable-Diffusion-1B-Chinese-v0.1")

pipeline = pipeline.to("cuda")

def generate(text, steps=50):
    image = pipeline(text,num_inference_steps=steps,guidance_scale=7.5).images[0]
    return image

def PIL2bytes(pil_img):
    '''Transform PIL image to bytes.
    Args: 
        pil_img: PIL object.
    '''
    bytesIO = BytesIO()
    pil_img.save(bytesIO, format="JPEG")
    return bytesIO.getvalue()

 
@app.get("/sd/{input}")
async def amain(input: str) -> None:
    """Main function"""
    image = generate(input, steps=20)
    # print(type(image))
    # cv2.imwrite("test.jpg",image)
    image.save("./test.jpg")
    # image = PIL2bytes(image)
    # image = image.tobytes()
    # file_like = open('./test.jpg', mode="rb")

    # with open("./test.jpg", "rb") as image_file:
    # 	file_like = image_file.read()

    # return {"a":1}
    # return FileResponse(file_like, media_type="image/jpg")

    return  FileResponse("test.jpg")


 
 
if __name__ == "__main__":

    import uvicorn
    uvicorn.run(app='fast_api_sd:app', host="0.0.0.0", port=8068, reload=True)

