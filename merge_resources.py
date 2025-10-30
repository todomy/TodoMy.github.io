#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
资源合并和优化工具
用于合并JavaScript插件文件，减少HTTP请求数量
"""

import os
import re
import argparse
import datetime

def merge_js_files(plugins_dir, output_file):
    """合并指定目录下的JavaScript文件"""
    merged_content = f"""/*
 * 合并的JavaScript资源文件
 * 生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
 * 包含以下插件:
"""
    
    js_files = [f for f in os.listdir(plugins_dir) if f.endswith('.js') and not f.startswith('merged_')]
    
    for js_file in js_files:
        merged_content += f" * - {js_file}\n"
    
    merged_content += " */\n\n"
    
    # 读取并合并所有JavaScript文件
    for js_file in js_files:
        file_path = os.path.join(plugins_dir, js_file)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # 移除文件末尾的多余空白行
            content = content.rstrip('\n\r')
            merged_content += f"/* ----- {js_file} ----- */\n"
            merged_content += content
            merged_content += "\n\n"
    
    # 中级压缩：移除多余空白和注释，保留关键代码结构
    # 移除多余空行
    merged_content = re.sub(r'\n\s*\n', '\n\n', merged_content)
    # 压缩多行注释（保留文件标识注释）
    merged_content = re.sub(r'\/\*[^*]*\*\/(?!\n\/\*\s*-)', '', merged_content)
    # 移除行尾注释
    merged_content = re.sub(r'\s*\/\/[^\n]*\n', '\n', merged_content)
    # 移除多余的空格
    merged_content = re.sub(r'\s+', ' ', merged_content)
    # 恢复换行
    merged_content = re.sub(r';\s*', ';\n', merged_content)
    merged_content = re.sub(r'\{\s*', '{\n', merged_content)
    merged_content = re.sub(r'\}\s*', '\n}\n', merged_content)
    
    # 写入合并后的文件
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(merged_content)
        print(f"✅ 成功合并 {len(js_files)} 个JavaScript文件到 {output_file}")
        
        # 同时复制到docs目录
        docs_output_file = os.path.join('docs', os.path.basename(output_file))
        shutil.copy(output_file, docs_output_file)
        print(f"✅ 已复制到docs目录: {docs_output_file}")
        
        return output_file
    except Exception as e:
        print(f"❌ 写入文件时出错: {e}")
        return None

def update_config_for_merged_resources(config_file, merged_js_file):
    """更新配置文件，指向合并后的资源文件"""
    if not os.path.exists(config_file):
        print(f"配置文件 {config_file} 不存在")
        return False
    
    try:
        # 读取配置文件
        import json
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 添加合并后的脚本到配置
        if 'custom_script' not in config:
            config['custom_script'] = []
        
        # 添加合并后的JS文件路径
        merged_js_path = f"/plugins/{os.path.basename(merged_js_file)}"
        # 移除可能存在的旧合并文件引用
        config['custom_script'] = [script for script in config['custom_script'] 
                                 if not script.endswith('merged_plugins.js')]
        # 添加新的合并文件引用
        config['custom_script'].append(merged_js_path)
        
        # 写回配置文件
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        print(f"已更新配置文件 {config_file}，添加了合并后的资源引用")
        return True
    except Exception as e:
        print(f"更新配置文件时出错: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='合并JavaScript资源文件')
    parser.add_argument('--plugins-dir', default='plugins', help='插件目录路径')
    parser.add_argument('--output', default='plugins/merged_plugins.js', help='输出文件路径')
    parser.add_argument('--config', default='config.json', help='配置文件路径')
    parser.add_argument('--update-config', action='store_true', help='是否更新配置文件')
    
    args = parser.parse_args()
    
    # 确保插件目录存在
    plugins_dir = os.path.abspath(args.plugins_dir)
    if not os.path.isdir(plugins_dir):
        print(f"插件目录 {plugins_dir} 不存在")
        exit(1)
    
    # 确保输出目录存在
    output_dir = os.path.dirname(os.path.abspath(args.output))
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"✅ 创建输出目录: {output_dir}")
    
    # 执行合并
    output_file = merge_js_files(plugins_dir, args.output)
    
    # 可选：更新配置文件
    if args.update_config:
        update_config_for_merged_resources(args.config, args.output)
    
    # 可选：清理临时文件或执行其他操作
    print("✅ 资源合并完成!")

# 添加缺失的导入
import shutil
    
    # 合并JavaScript文件
    output_file = merge_js_files(plugins_dir, args.output)
    
    # 更新配置文件（如果指定）
    if args.update_config:
        update_config_for_merged_resources(args.config, output_file)
    
    print("资源合并完成!")
