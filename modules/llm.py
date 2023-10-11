from enum import Enum
import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import requests

class ModelTypes(Enum):
    OpenAI = "OpenAI"
    OpenAI4 = "OpenAI4"
    Mistral = "Mistral"
    StableBeluga7B = "StableBeluga7B"

class LLM:
    def __init__(self, model_type):
        self.ClearModel(model_type)

    def ClearModel(self, model_type):
        self.model = ModelTypes(model_type)
        self.modelObj = None
        self.tokenizerObj = None

    def SetupModel(self):
        if self.model == ModelTypes.Mistral:
            return self._setup_mistral()
        elif self.model == ModelTypes.StableBeluga7B:
            return self._setup_beluga_7b()

    def ask(self, system_prompt, user_prompt, model_type=None):
        return self._ask(system_prompt, user_prompt, model_type)

    def _ask(self, system_prompt, user_prompt, model_type = None):
        if model_type is None:
            model_type = self.model
        elif model_type is not self.model:
                self.ClearModel(model_type)

        if model_type == ModelTypes.OpenAI:
            return self._ask_openai(system_prompt, user_prompt)
        elif model_type == ModelTypes.OpenAI4:
            return self._ask_openai(system_prompt, user_prompt, model="gpt-4", max_tokens=8190)
        elif model_type == ModelTypes.Mistral:
            return self._ask_mistral(system_prompt, user_prompt)
        elif model_type == ModelTypes.StableBeluga7B:
            return self._ask_stable_beluga_7b(system_prompt, user_prompt)

    def _ask_openai(self, system_prompt, user_prompt, model = "gpt-3.5-turbo", max_tokens=4096):
        # Placeholder for actual OpenAI API request
        # Uncomment and complete the following code in your local environment
        api_key = os.environ.get("OPENAI_API_KEY", "your-default-openai-api-key-here")
        api_url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }
        data ={
            "model" : model,
            "messages" :  [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ]
        }
        
        response = requests.post(api_url, headers=headers, json=data)
        
        
        if response.status_code == 200:
             response_data = response.json()
             print(response_data)
             return response_data["choices"][0]["message"]["content"]
        else:
             return f"Error: {response.status_code}"

    def _ask_mistral(self, system_prompt, user_prompt):
        if self.tokenizerObj is None or self.modelObj is None:
            self._setup_mistral()
        prompt = f"<s>[INST] {system_prompt} {user_prompt} [/INST]"
        inputs = self.tokenizerObj(prompt, return_tensors="pt")
        outputs = self.modelObj.generate(**inputs, max_new_tokens=4096)
        decoded = self.tokenizerObj.decode(outputs[0], skip_special_tokens=True)
        return decoded
    
    def _setup_mistral(self):
        if self.modelObj is None or self.tokenizerObj is None:
            self.modelObj = AutoModelForCausalLM.from_pretrained("mistralai/Mistral-7B-Instruct-v0.1")
            self.tokenizerObj = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-Instruct-v0.1")

    def _setup_beluga_7b(self):
        if self.modelObj is None or self.tokenizerObj is None:
            self.modelObj = AutoModelForCausalLM.from_pretrained("stabilityai/StableBeluga-7B", torch_dtype=torch.float16, low_cpu_mem_usage=True, device_map="auto")
            self.tokenizerObj = AutoTokenizer.from_pretrained("stabilityai/StableBeluga-7B", use_fast=False)

    def _ask_stable_beluga_7b(self, system_prompt, user_prompt):
        if self.tokenizerObj is None or self.modelObj is None:
            self._setup_beluga_7b()
        prompt = f"### System: {system_prompt}\\n\\n### User: {user_prompt}\\n\\n### Assistant:\\n"
        inputs = self.tokenizerObj(prompt, return_tensors="pt").to("cuda")
        output = self.modelObj.generate(**inputs, do_sample=True, top_p=0.95, top_k=0, max_new_tokens=4096)
        return self.tokenizerObj.decode(output[0], skip_special_tokens=True)


    def __repr__(self):
        return f"LLMBase(model={self.model})"
