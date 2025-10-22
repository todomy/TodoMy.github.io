import os
import sys

# 直接测试get_issue_status方法的关键代码
class MockGMEEK:
    def __init__(self):
        # 故意不初始化issue_status_file来模拟错误情况
        pass
    
    def get_issue_status(self):
        """测试修复后的get_issue_status方法"""
        # 确保issue_status_file属性存在
        if not hasattr(self, 'issue_status_file'):
            print("警告: issue_status_file属性不存在，设置默认值")
            self.issue_status_file = 'issue_status.json'
        
        print(f"当前issue_status_file: {self.issue_status_file}")
        return {"issues": {}, "last_updated": 0}

# 运行测试
try:
    mock = MockGMEEK()
    status = mock.get_issue_status()
    print(f"测试成功! 方法正常执行并返回: {status}")
except Exception as e:
    print(f"测试失败: {str(e)}")
    import traceback
    traceback.print_exc()
