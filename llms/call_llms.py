import base64
import requests
from config import config
from dashscope import MultiModalConversation,Generation
class CallQwenVL:
    def __init__(self, model_name = "qwen-vl-max-latest"):
        self.model_name = model_name

    def infer(self,image_path,prompt):
        return self.infer_from_api(image_path,prompt,self.model_name)

    def infer_from_api(self,image_path,prompt,model_name):
        if image_path:
            #  base 64 编码格式
            def encode_image(image_path):
                with open(image_path, "rb") as image_file:
                    return base64.b64encode(image_file.read()).decode("utf-8")
            response = MultiModalConversation.call(
                api_key=config.dash_scope_api_key,
                model=model_name,
                messages=[
                    {
                        "role": "system",
                        "content": [{"type": "text", "text": "You are a helpful assistant."}],
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "image":image_path
                            },
                            {"text":prompt},
                        ],
                    },
                ],
                vl_high_resolution_images = True)
            return response["output"]["choices"][0]["message"].content[0]["text"]