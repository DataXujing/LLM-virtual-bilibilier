# 编写Gradio调用函数
# import mdtex2html
from service.config import LangChainCFG
from langchain_chatglm3 import *

from fastapi import FastAPI

config = LangChainCFG()
application = LangChainApplication(config)
# 加载知识库
application.knowledge_service.init_knowledge_base()


app = FastAPI()

@app.get("/llm/{input}")
async def get_llm(input: str):
    result = application.get_knowledeg_based_answer(input)
    return { "llm_response":result["result"] }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app='fast_api_app:app', host="0.0.0.0", port=8066, reload=False)


