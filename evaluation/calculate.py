import numpy as np
import json

filepath = '/home/ckqsudo/code2024/Psy-Agent/experiment/results/rag_unstructure_type2_result.json'
with open(filepath, 'r', encoding='utf-8') as f:
    data = json.load(f)
    
scores = {
    "对话流畅性": [],
    "回复帮助性": [],
    "安慰的效果": [],
    "语言自然度": [],
    "综合得分": []
}

for item in data:
    scores["对话流畅性"].append(item['score']["对话流畅性"])
    scores["回复帮助性"].append(item['score']["回复帮助性"])
    scores["安慰的效果"].append(item['score']["安慰的效果"])
    scores["语言自然度"].append(item['score']["语言自然度"])
    scores["综合得分"].append(item['score']["综合得分"])
    
print("均值")
print(f"对话流畅性：{np.mean(scores['对话流畅性'])}")
print(f"回复帮助性：{np.mean(scores['回复帮助性'])}")
print(f"安慰的效果：{np.mean(scores['安慰的效果'])}")
print(f"语言自然度：{np.mean(scores['语言自然度'])}")
print(f"综合得分：{np.mean(scores['综合得分'])}")