

import argparse
import json
import sys
sys.path.append('/mnt/bn/chenguoqing-lf/code/survey_agent/src')

from survey_agent.survey import generate_survey
from survey_agent.utils import load_papers_from_jsonl
import os

# 导入环境配置
from survey_agent import env

# 或者手动设置（如果需要的话）
# os.environ["https_proxy"] = "http://127.0.0.1:7890"
# os.environ["http_proxy"] = "http://127.0.0.1:7890"


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='生成研究综述')
    
    # 论文来源参数（互斥）
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument('--terms', nargs='+', help='搜索关键词列表（单组）')
    source_group.add_argument('--multi_terms', nargs='+', action='append', help='多组搜索关键词，每组用--multi_terms分隔，组内OR，组间AND')
    source_group.add_argument('--titles', nargs='+', help='论文标题列表')
    source_group.add_argument('--papers', help='预处理的论文JSONL文件路径')
    source_group.add_argument('--bib_file', help='BIB文件路径')
    
    # 其他参数
    parser.add_argument('--max_results', type=int, default=100, help='最大搜索结果数量')
    parser.add_argument('--output_file', default='survey_result.md', help='输出文件路径')
    parser.add_argument('--llm_provider', default='openai', help='LLM提供商, 默认使用openai')
    parser.add_argument('--model_name', help='模型名称')
    parser.add_argument('--custom_prompt', help='自定义提示模板')
    parser.add_argument('--pdf_dir', help='PDF保存目录')
    parser.add_argument('--logic', choices=['AND', 'OR'], default='AND', help='关键词匹配逻辑: AND(必须同时满足所有关键词) 或 OR(满足任一关键词即可)')
    parser.add_argument('--date', help='查询指定日期发布的论文，格式: YYYY-MM-DD (例如: 2025-09-21)')
    parser.add_argument('--date_range', nargs=2, metavar=('START_DATE', 'END_DATE'), help='查询日期范围内的论文，格式: YYYY-MM-DD YYYY-MM-DD (例如: 2025-09-01 2025-09-30)')
    
    return parser.parse_args()


def main():
    """
    支持命令行参数的研究综述生成脚本
    """
    args = parse_arguments()
    
    # 准备参数
    kwargs = {
        'max_results': args.max_results,
        'output_file': args.output_file,
        'llm_provider': args.llm_provider,
        'model_name': args.model_name,
        'custom_prompt': args.custom_prompt,
        'pdf_dir': args.pdf_dir,
        'logic': args.logic,
        'date': args.date,
        'date_range': args.date_range,
    }

    
    # 根据不同的论文来源设置相应参数
    if args.terms:
        print(f"🔍 从搜索关键词生成综述: {args.terms}")
        kwargs['terms'] = args.terms
    elif args.multi_terms:
        print(f"🔍 从多组搜索关键词生成综述: {args.multi_terms}")
        kwargs['multi_terms'] = args.multi_terms
    elif args.titles:
        print(f"🔍 从论文标题生成综述: {args.titles}")
        kwargs['titles'] = args.titles
    elif args.papers:
        print(f"📄 从预处理论文文件生成综述: {args.papers}")
        papers = load_papers_from_jsonl(args.papers)
        kwargs['papers'] = papers
    elif args.bib_file:
        print(f"📚 从BIB文件生成综述: {args.bib_file}")
        kwargs['bib_file'] = args.bib_file
    
    # 生成综述
    print("✨ 开始生成综述...")
    try:
        result = generate_survey(**kwargs)
        print(f"✅ 综述生成完成！输出文件: {result}")
    except Exception as e:
        print(f"❌ 生成综述时出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
