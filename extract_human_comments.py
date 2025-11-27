
# -*- coding: utf-8 -*-
"""
提取模型日志文件中的人类评语
人类评语格式：
# 人类评语
```
评语内容
```
"""

import re

def extract_human_comments(file_path):
    """提取指定文件中的人类评语"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # 使用正则表达式匹配人类评语格式
        # 模式：# 人类评语\n```\n评语内容\n```
        pattern = r'# 人类评语\s*```\s*(.*?)\s*```'
        matches = re.findall(pattern, content, re.DOTALL)
        
        # 输出提取结果
        print(f"文件: {file_path}")
        print("=" * 50)
        
        if matches:
            print(f"找到 {len(matches)} 个人类评语:")
            print("-" * 30)
            
            for i, comment in enumerate(matches, 1):
                # 清理评语内容
                cleaned_comment = comment.strip()
                print(f"评语 {i}:")
                print(f"  {cleaned_comment}")
                print("-" * 30)
        else:
            print("未找到人类评语")
        
        return matches
        
    except FileNotFoundError:
        print(f"错误: 文件 {file_path} 不存在")
        return []
    except Exception as e:
        print(f"错误: 读取文件时发生异常 - {e}")
        return []

def extract_all_human_comments():
    """提取所有模型日志文件中的人类评语"""
    # 定义要处理的文件列表
    files_to_process = [
        r"c:\D\04_trae\第三轮\seed_01\docker_file_generation\1_model_log_第一轮对话.md",
        r"c:\D\04_trae\第三轮\seed_01\docker_file_generation\2_model_log_第二轮对话.md",
        r"c:\D\04_trae\第三轮\seed_01\docker_file_generation\3_model_log_第三轮对话.md",
        r"c:\D\04_trae\第三轮\seed_01\docker_file_generation\3_model_log_第三轮对话 copy.md"
    ]
    
    all_comments = []
    
    print("开始提取人类评语...")
    print("=" * 50)
    
    for file_path in files_to_process:
        comments = extract_human_comments(file_path)
        all_comments.extend([(file_path, comment) for comment in comments])
        print()  # 空行分隔不同文件的结果
    
    # 输出汇总结果
    print("=" * 50)
    print("汇总结果:")
    print(f"总共找到 {len(all_comments)} 个人类评语")
    
    if all_comments:
        print("所有评语内容:")
        print("-" * 30)
        for i, (file_path, comment) in enumerate(all_comments, 1):
            print(f"{i}. 文件: {file_path.split('/')[-1]}")
            print(f"   评语: {comment}")
            print()
    
    return all_comments

def main():
    """主函数"""
    all_comments = extract_all_human_comments()
    
    # 保存提取结果到文件
    if all_comments:
        output_file = r"c:\D\04_trae\第三轮\seed_01\docker_file_generation\extracted_human_comments.txt"
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("提取的人类评语汇总\n")
                f.write("=" * 50 + "\n\n")
                
                for i, (file_path, comment) in enumerate(all_comments, 1):
                    f.write(f"{i}. 来源文件: {file_path}\n")
                    f.write(f"   评语内容: {comment}\n\n")
                
                f.write(f"总共提取了 {len(all_comments)} 个人类评语\n")
            
            print(f"\n评语已保存到: {output_file}")
        except Exception as e:
            print(f"保存文件时出错: {e}")

if __name__ == "__main__":
    main()