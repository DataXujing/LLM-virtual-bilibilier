import asyncio
import edge_tts

from fastapi import FastAPI
from fastapi.responses import FileResponse

app = FastAPI()
 
TEXT = "大家好，欢迎关注语音之家，语音之家是一个助理AI语音开发者的社区。这样的话，就可以捕获，然后按照自己定义的方式响应json格式。"
VOICE = "zh-CN-XiaoxiaoNeural"
OUTPUT_FILE = "test.mp3"
 
 
@app.get("/tts/{input}")
async def amain(input: str) -> None:
    """Main function"""
    print(input)
    communicate = edge_tts.Communicate(input, VOICE)
    await communicate.save(OUTPUT_FILE)
    # return {"a":1}
    return FileResponse(OUTPUT_FILE, media_type="audio/mpeg")
    # return FileResponse(OUTPUT_FILE, file_name="test.mp3")

 
 
if __name__ == "__main__":
    # loop = asyncio.get_event_loop_policy().get_event_loop()
    # try:
    #     loop.run_until_complete(amain())
    # finally:
    #     loop.close()
    import uvicorn
    uvicorn.run(app='fast_api_tts:app', host="0.0.0.0", port=8087, reload=True)
