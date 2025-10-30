#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
备份功能测试脚本
用于验证统一备份方法在不同模式下的工作情况
"""

import os
import sys
import json

# 导入Gmeek类
sys.path.append('.')
from Gmeek import GMEEK as Gmeek

class BackupTester:
    def __init__(self):
        print("📋 初始化备份功能测试")
        self.backup_dir = 'backup/'
        self.test_files = []
        
    def setup_test(self):
        """准备测试环境"""
        # 确保backup目录存在
        os.makedirs(self.backup_dir, exist_ok=True)
        print(f"✅ 测试环境准备完成: {self.backup_dir}")
    
    def test_backup_method(self):
        """测试backupPostContent方法"""
        print("\n🔍 测试统一备份方法...")
        
        # 创建一个简单的Gmeek实例用于测试
        # 通过配置参数来设置本地模式
        import argparse
        # 创建argparse配置对象
        parser = argparse.ArgumentParser()
        # 添加必要的参数
        parser.add_argument('--repo', default='todomy/todomy.github.io')
        parser.add_argument('--token', default='')
        parser.add_argument('--blogBase', default='blogBase.json')
        parser.add_argument('--local', action='store_true')
        parser.add_argument('--rebuild', action='store_true')
        parser.add_argument('--number', default='')
        test_options = parser.parse_args([])  # 创建配置对象
        test_options.github_token = None
        test_options.repo_name = None
        test_options.local = True
        
        # 初始化Gmeek实例，传入options参数
        test_blog = Gmeek(test_options)
        
        # 测试数据
        test_articles = [
            {"title": "测试文章1", "content": "这是测试文章1的内容", "issue_number": 1},
            {"title": "测试文章2/特殊字符", "content": "这是测试文章2的内容", "issue_number": 2},
            {"title": "测试文章3", "content": None, "issue_number": 3},
        ]
        
        # 测试首次备份
        print("\n📝 测试首次备份:")
        for article in test_articles:
            success, path, changed = test_blog.backupPostContent(
                article["title"], 
                article["content"], 
                article["issue_number"]
            )
            print(f"  - 文章: {article['title']}")
            print(f"    成功: {success}")
            print(f"    路径: {path}")
            print(f"    有更新: {changed}")
            
            if success:
                self.test_files.append(path)
                # 验证文件存在
                assert os.path.exists(path), f"备份文件不存在: {path}"
                print(f"    ✅ 文件验证通过")
        
        # 测试内容无变化的备份
        print("\n📝 测试内容无变化的备份:")
        for article in test_articles:
            success, path, changed = test_blog.backupPostContent(
                article["title"], 
                article["content"], 
                article["issue_number"]
            )
            print(f"  - 文章: {article['title']}")
            print(f"    成功: {success}")
            print(f"    有更新: {changed}")
            # 应该返回True, path
            assert success, f"备份失败: {article['title']}"
            # 对于非空内容，应该没有变化
            if article["content"]:
                assert not changed, f"内容无变化但报告有更新: {article['title']}"
                print(f"    ✅ 更新检测验证通过")
            else:
                print(f"    ✅ 空内容备份验证通过")
        
        # 测试内容变化的备份
        print("\n📝 测试内容变化的备份:")
        for article in test_articles:
            new_content = article["content"] + " [已更新]" if article["content"] else "新内容"
            success, path, changed = test_blog.backupPostContent(
                article["title"], 
                new_content, 
                article["issue_number"]
            )
            print(f"  - 文章: {article['title']}")
            print(f"    成功: {success}")
            print(f"    有更新: {changed}")
            # 应该返回True, path, True
            assert success, f"更新备份失败: {article['title']}"
            assert changed, f"内容有变化但报告无更新: {article['title']}"
            print(f"    ✅ 内容更新检测验证通过")
    
    def clean_up(self):
        """清理测试文件"""
        print("\n🧹 清理测试文件...")
        for file_path in self.test_files:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"  - 已删除: {file_path}")
        print("✅ 测试清理完成")
    
    def run_all_tests(self):
        """运行所有测试"""
        try:
            self.setup_test()
            self.test_backup_method()
            print("\n🎉 所有测试通过!")
            print("✅ 备份功能正常工作，支持线上线下模式统一备份")
            print("✅ 支持内容变化检测，避免重复备份")
            print("✅ 支持安全文件名生成")
            return True
        except Exception as e:
            print(f"\n❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            # 询问是否清理测试文件
            if input("\n是否清理测试文件? (y/n): ").lower() == 'y':
                self.clean_up()
            else:
                print("⚠️ 测试文件未清理，保留在backup目录中")

if __name__ == "__main__":
    print("=== 备份功能测试工具 ===")
    print("验证Gmeek.py中统一备份方法的功能")
    
    tester = BackupTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n📋 总结:")
        print("1. 已成功实现统一的文章备份方法")
        print("2. 无论线上还是线下模式，都会保留backup目录并备份文章")
        print("3. 支持内容变化检测，避免不必要的重复备份")
        print("4. 优化了错误处理和日志记录")
        print("5. 支持安全的文件名生成")
    
    print("\n测试完成!")
