import json
from gpt.brain import GptBrain

keys_path = '../data/keys.json'
constants_path = '../data/constants.json'
prompt_path = '../data/prompt.txt'

with open(keys_path, 'r', encoding='UTF8') as f:
    keys = json.load(f)
with open(constants_path, 'r', encoding='UTF8') as f:
    constants = json.load(f)
with open(prompt_path, 'r', encoding="UTF-8") as f:
    prompt = f.read()

gpt = GptBrain(
    token=keys['openaiKey'],
    assistant=keys['assistantId']
)

text = "지향성 마이크, DSLR 1, DSLR 2, 핸디 3, 미러리스 1, 삼각대 6, 삼각대 7, 삼각대 8, 삼각대 3, 플레이트 6, 플레이트 1, 플레이트 2, 플레이트 3, 플레이트 4, SD카드 1, SD카드 2, SD카드 3, SD카드 4, SD카드 5, SD카드 6, SD카드 7, SD카드 8, 무선마이크 2, 무선마이크 3, DSLR 배터리, 핸디 배터리, 미러리스 배터리, DSLR 충전기, 핸디 충전기, 미러리스 충전기"

tool_prompt, date_prompt = prompt.split("##\n")

tool_prompt = tool_prompt.replace("$TOOL_LIST$", ', '.join(constants['tools']))
print(tool_prompt)
res = gpt(text, tool_prompt)

print(res)
