import requests
import json
import random
from tqdm import tqdm

url = 'http://81.70.187.238:30001/message'

headers = {
    'Content-Type': 'application/json',
}

payload = {
    "model_name": "szk_test_model_9b:earth_raw_prompt:earth:earth_256",
    "context": [
        {
            "role": "user",
            "content": "你是谁",
            "name": "用户"
        }
    ],
    "prompt": "",
    "is_stream": False,
    "decoding_params": {
        "num_beams": None,
        "top_p": 0.5,
        "top_k": None,
        "length_penalty": None,
        "temperature": 0.5,
        "no_repeat_ngram_size": None,
        "repetition_penalty": None,
        "seq_length": None,
        "out_seq_length": None
    }
}

# response = requests.post(url, headers=headers, json=data)

# print(response.status_code)    # 请求状态码，200成功，500失败

# # print(response.text)  # 开stream了用这个
# print(response.json()['response'])  # 没开stream用这个

payload['prompt'] = """你是一个擅长评价对话回复质量的助手。\n请你以公正的评判者的身份，评估一个AI助手与我对话时的回复质量。你需要从下面的几个维度对回复进行评估:
对话流畅性、回复帮助性、安慰的效果、语言自然度
我会给你提供完整的对话的上下文，当你开始评估时，你需要遵守以下的流程：
- 1. 指出AI助手的回复有哪些不足，并进一步解释。
- 2. 从不同维度对AI助手的回复进行评价，在每个维度的评价之后，给每一个维度一个1～10的分数。
- 3. 最后，综合每个维度的评估，对AI助手的回答给出一个1～10的综合分数。
- 4. 你的打分需要尽可能严格，并且要遵守下面的评分规则：总的来说，AI助手在各个评分维度的表现越高，则分数越高。其中，突出回复帮助性和安慰的效果这两个维度是最重要的，这两个维度的分数主导了最后的综合分数。
- 当AI助手的回复存有本质性的事实错误，或生成了有害内容时，总分必须是1到2分；
- 当AI助手的回复没有严重错误而且基本无害，但是安慰性较差，不像一个专业的心理咨询师所说的话，总分为3到4分；
- 当AI助手的回复基本符合专业心理咨询师的回复风格，但是在帮助性和流畅性上表现较差，质量中等，总分为5到6分；
- 当AI助手的回复在所有维度上表现良好，但是没有涉及到比较专业的心理咨询知识或心理治疗方法时，总分得7到8分；
- 只有当AI助手的回复质量十分好，充分地运用了专业的心理咨询知识和心理治疗方法，并且在所有维度上都接近满分的情况下，才能得9到10分。
请记住，你必须在你打分前进行评价和解释。在你对每个维度的解释之后，需要加上对该维度的打分。之后，在你回答的末尾，按照以下字典格式（包括括号）返回你所有的打分结果，并确保你的打分结果是整数：
{"维度一": 分数, "维度二": 分数, ..., "综合得分": 分数}，例如：{"对话流畅性": 9, "回复帮助性": 6, "安慰的效果": 7, "语言自然度": 6, "综合得分": 7}"""


payload['context'][0]['content'] = f"""
<|对话上下文-开始|>
用户：你好，我最近很难过
助手：你好，很高兴你能来聊聊。虽然现在感觉很难过，但你能意识到这一点并愿意分享，这已经是迈向好转的第一步了。我们一起来看看，有什么小事情是你现在能做到的，哪怕只是让自己稍微感觉好一点的呢？
用户：我女朋友生气了，我觉得她无理取闹
助手：你好，听起来你现在感到有些困惑和沮丧。虽然现在的情况可能让你觉得难以理解，但你能主动来谈论这个问题，这已经是很好的第一步了。或许我们可以换个角度来看待这个情况：有没有什么小事情是你能做的，来改善你们之间的沟通呢？比如，试着用平和的语气问问她，是什么让她感到不开心？这样不仅能让她感受到你的关心，也能帮助你们更好地理解彼此。你觉得这样尝试一下如何？
用户：我不想这样，我也很生气
助手：你好，我能理解你现在的心情，生气是很自然的反应。虽然你现在可能不想主动去沟通，但我们可以先从一个小小的行动开始，比如深呼吸几次，让自己稍微平静下来。然后，也许你可以试着想象一下，如果你们都能冷静下来，会有什么样的对话能让你们双方都感觉更好呢？哪怕只是一个小小的想法，也可能会帮助你们找到解决问题的方法。你觉得这样尝试一下如何？
用户：好吧，你说的有道理
助手：你好，很高兴听到你觉得有道理。既然我们已经找到了一个共同认可的小步骤，那不妨从这里开始。你可以先试着深呼吸几次，让自己平静下来。然后，想象一下，如果你们都能冷静下来，会有什么样的对话能让你们双方都感觉更好呢？哪怕只是一个小小的想法，也可能会帮助你们找到解决问题的方法。你觉得这样尝试一下如何？
<|对话上下文-结束|>
请用字典格式直接输出你的打分结果，不要添加任何解释信息：
"""
filepath = '/home/ckqsudo/code2024/Psy-Agent/experiment/convert/rag_unstructure_type2.json'
with open(filepath, 'r', encoding='utf-8') as f:
    raw_data = json.load(f)
    
final_result = []
for session in raw_data:
    dialog = session['content']
    user_prompt = f"""
<|对话上下文-开始|>
{dialog}
<|对话上下文-结束|>
请用字典格式直接输出你的打分结果，不要添加任何解释信息：""".strip()
    payload['context'][0]['content'] = user_prompt
    response = requests.post(url, headers=headers, json=payload)
    result = response.json()['response']
    print(response.json()['response'])
    try:
        score = json.loads(result)
        session['score'] = score
        final_result.append(session)
    except Exception as e:
        print(f'error:{e} {result}')
        
with open('/home/ckqsudo/code2024/Psy-Agent/experiment/results/rag_unstructure_type2_result.json', 'w', encoding='utf-8') as f:
    json.dump(final_result, f, ensure_ascii=False, indent=4)