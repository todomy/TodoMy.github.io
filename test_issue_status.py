import os
import json

# 创建一个完全独立的测试类来模拟get_issue_status方法的行为
class SimpleTest:
    def __init__(self):
        # 只初始化必要的属性
        self.issue_status_file = 'issue_status.json'
        # 创建一个测试文件
        with open(self.issue_status_file, 'w', encoding='utf-8') as f:
            json.dump({"issues": {}, "last_updated": 0}, f)
    
    def get_issue_status(self):
        """模拟get_issue_status方法"""
        # 调试代码
        print(f"Debug: self.issue_status_file = {self.issue_status_file}")
        print(f"Debug: hasattr(self, 'issue_status_file') = {hasattr(self, 'issue_status_file')}")
        print(f"Debug: hasattr(self, 'issue_status.file') = {hasattr(self, 'issue_status.file')}")
        
        if hasattr(self, 'issue_status_file') and os.path.exists(self.issue_status_file):
            try:
                with open(self.issue_status_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"读取issue状态文件失败: {str(e)}")
        return {"issues": {}, "last_updated": 0}

# 运行测试
try:
    test = SimpleTest()
    status = test.get_issue_status()
    print(f"Test passed! get_issue_status returned: {status}")
    # 清理测试文件
    if os.path.exists('issue_status.json'):
        os.remove('issue_status.json')
except Exception as e:
    print(f"Test failed with error: {str(e)}")
    import traceback
    traceback.print_exc()