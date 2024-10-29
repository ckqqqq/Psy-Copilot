import json

# 读取txt文件
def read_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    return content

# 将对话分隔开
def split_dialogues(content):
    dialogues = content.split('\n\n')
    return dialogues

# 处理每一段对话
def process_cn_dialogue(dialogue):
    lines = dialogue.split('\n')
    final_str = ""
    for i, line in enumerate(lines):
        if i % 2 == 0:
            final_str += f"用户: {line}\n"
        else:
            final_str += f"助手: {line}\n"
    return {"content":final_str.strip()}

def process_en_dialogue(dialogue):
    lines = dialogue.split('\n')
    final_str = ""
    for i, line in enumerate(lines):
        if i % 2 == 0:
            final_str += f"user: {line}\n"
        else:
            final_str += f"assistant: {line}\n"
    return {"content":final_str.strip()}

# 将处理后的对话保存到json文件
def save_to_json(dialogues, output_file):
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(dialogues, file, ensure_ascii=False, indent=4)

# 主函数
def main(input_file, output_file):
    content = read_txt(input_file)
    dialogues = split_dialogues(content)
    processed_dialogues = [process_cn_dialogue(dialogue) for dialogue in dialogues[:5]]
    processed_dialogues += [process_en_dialogue(dialogue) for dialogue in dialogues[5:]]
    
    save_to_json(processed_dialogues, output_file)

# 调用主函数
if __name__ == "__main__":
    input_file = '/home/ckqsudo/code2024/Psy-Agent/experiment/raw_text/rag_unstructure_type2.txt'  # 输入的txt文件路径
    output_file = '/home/ckqsudo/code2024/Psy-Agent/experiment/convert/rag_unstructure_type2.json'  # 输出的json文件路径
    main(input_file, output_file)
