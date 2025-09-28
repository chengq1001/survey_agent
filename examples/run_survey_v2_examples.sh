#!/bin/bash

# 使用命令行参数运行generate_survey_v2.py的示例

echo "=== 模式1: 指定数量，按照关键字查询 ==="
echo "查询包含指定关键词的论文，按数量限制结果"
python examples/generate_survey_v2.py \
    --terms "LLM" "large language model" \
    --max_results 10 \
    --output_file "output/llm_survey.md" \
    --llm_provider "openai" \
    --model_name "ep-20250911120040-8dh4j" \
    --logic "OR"

echo -e "\n=== 模式2: 指定日期，查找这个日期内的所有关键字的文章 ==="
echo "查询指定日期发布的所有相关论文（不限制数量）"
python examples/generate_survey_v2.py \
    --terms "VLM" "vision language model" \
    --max_results 1000 \
    --output_file "output/vlm_date_survey.md" \
    --llm_provider "openai" \
    --model_name "ep-20250911120040-8dh4j" \
    --logic "OR" \
    --date "2025-09-21"

echo -e "\n=== 模式2变体: 查询日期范围内的所有相关文章 ==="
echo "查询指定日期范围内发布的所有相关论文"
python examples/generate_survey_v2.py \
    --terms "MLLM" "Multimodal" \
    --max_results 1000 \
    --output_file "output/mllm_range_survey.md" \
    --llm_provider "openai" \
    --model_name "ep-20250911120040-8dh4j" \
    --logic "OR" \
    --date_range "2025-09-01" "2025-09-30"

echo -e "\n=== 其他模式: 从论文标题生成综述 ==="
python examples/generate_survey_v2.py \
    --titles "Attention Is All You Need" "BERT: Pre-training of Deep Bidirectional Transformers" \
    --max_results 5 \
    --output_file "output/transformer_survey.md" \
    --llm_provider "openai"

echo -e "\n=== 其他模式: 从预处理论文JSONL文件生成综述 ==="
python examples/generate_survey_v2.py \
    --papers "vlm_games_papers.jsonl" \
    --output_file "output/vlm_games_survey_from_jsonl.md" \
    --llm_provider "openai"

echo -e "\n=== 其他模式: 从BIB文件生成综述 ==="
python examples/generate_survey_v2.py \
    --bib_file "papers.bib" \
    --output_file "output/survey_from_bib.md" \
    --llm_provider "openai" \
    --pdf_dir "pdfs/"

echo -e "\n=== 查看帮助信息 ==="
python examples/generate_survey_v2.py --help
