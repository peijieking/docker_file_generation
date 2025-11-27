
# -*- coding: utf-8 -*-
"""
清理模型日志文件中的changes段落
移除changes段落及其包含的newStr和oldStr内容
"""

import re

def clean_changes_in_file(file_path):
    """清理文件中的changes段落"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # 使用正则表达式匹配并移除changes段落
        # 匹配从changes:开始到下一个toolName或#人类评语之间的内容
        pattern = r'(changes: \s*\n)(.*?)(?=\n\s*(toolName:|#人类评语))'
        
        cleaned_content = re.sub(pattern, '', content, flags=re.DOTALL)
        
        # 写入清理后的内容
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(cleaned_content)
        
        print(f"成功清理文件: {file_path}")
        return True
        
    except Exception as e:
        print(f"清理文件时出错: {e}")
        return False

def main():
    # 要清理的文件路径
    file_path = r"c:\D\04_trae\第三轮\seed_01\docker_file_generation\3_model_log_第三轮对话 copy.md"
    
    print("开始清理changes段落...")
    
    if clean_changes_in_file(file_path):
        print("清理完成！")
    else:
        print("清理失败！")

if __name__ == "__main__":
    main()