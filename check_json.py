import json
import sys

try:
    with open('blogBase.json', 'r') as f:
        data = json.load(f)
    print('JSON格式有效')
except json.JSONDecodeError as e:
    print('JSON格式无效:', e)
    sys.exit(1)
except Exception as e:
    print('其他错误:', e)
    sys.exit(1)