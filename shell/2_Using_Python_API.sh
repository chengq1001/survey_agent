#!/bin/bash

# 设置代理
# 在字节的merlin的开发机下不使用代理即可
# export HTTP_PROXY=http://sys-proxy-rd-relay.byted.org:8118
# export http_proxy=http://sys-proxy-rd-relay.byted.org:8118
# export https_proxy=http://sys-proxy-rd-relay.byted.org:8118
# export no_proxy="localhost,.byted.org,byted.org,.bytedance.net,bytedance.net,.byteintl.net,.tiktok-row.net,.tiktok-row.org,127.0.0.1,127.0.0.0/8,169.254.0.0/16,100.64.0.0/10,172.16.0.0/12,192.168.0.0/16,10.0.0.0/8,::1,fe80::/10,fd00::/8,arxiv.org,.arxiv.org"

# 定义搜索关键词和模型名称
TERMS=(
    "LLM" 
    "Large Language Model" 
    "VLM" 
    "Vision Language Model" 
    "MLLM" 
    "Multimodal Large Language Models" 
    "LVLM" 
    "Large Vision-Language Models"
    "RL" 
    "Reinforcement Learning" 
    "RLHF" 
    "Reasoning" 
    "Hallucination" 
    "Chain of Thought" 
    "COT" 
    "Agent" 
    "Multi-Agent"
)
MODEL_NAME="ep-20250911141136-q5shc" # Kimi-K2
MODEL_NAME="ep-20250911120040-8dh4j" # Doubao-Seed-1.6

# 定义输出文件和PDF目录
TIMESTAMP=$(date +"%Y%m%d_%H%M")
BASE_DIR="/mnt/bn/chenguoqing-lf/code/survey_agent/output/all"
OUTPUT_FILE="${BASE_DIR}/survey_${TIMESTAMP}.md"
PDF_DIR="${BASE_DIR}/pdfs/"

log_file=${BASE_DIR}/logs/survey_${TIMESTAMP}_log.txt

mkdir -p "$(dirname "$log_file")"
mkdir -p "$(dirname "$BASE_DIR")"


# echo -e "\n=== 查看帮助信息 ==="
# python3 /mnt/bn/chenguoqing-lf/code/survey_agent/examples/generate_survey_v2.py --help

# echo "=== 模式1: 指定数量，按照关键字查询 ==="
# echo "查询包含指定关键词的论文，按数量限制结果（关键词：OR逻辑）"
# python3 /mnt/bn/chenguoqing-lf/code/survey_agent/examples/generate_survey_v2.py \
#     --terms "${TERMS[@]}" \
#     --max_results 20 \
#     --output_file "$OUTPUT_FILE" \
#     --llm_provider "openai" \
#     --model_name "$MODEL_NAME" \
#     --pdf_dir "$PDF_DIR" \
#     --logic "OR"

# echo -e "\n=== 模式2: 指定日期，查找这个日期内的所有关键字的文章 ==="
# echo "查询指定日期发布的所有相关论文（关键词：OR逻辑）"
# DATE_OUTPUT_FILE="${BASE_DIR}/survey_date_${TIMESTAMP}.md"

# python3 /mnt/bn/chenguoqing-lf/code/survey_agent/examples/generate_survey_v2.py \
#     --terms "${TERMS[@]}" \
#     --max_results 1000 \
#     --output_file "$DATE_OUTPUT_FILE" \
#     --llm_provider "openai" \
#     --model_name "$MODEL_NAME" \
#     --pdf_dir "$PDF_DIR" \
#     --logic "OR" \
#     --date "2025-09-18"

echo -e "\n=== 模式2变体: 查询日期范围内的所有相关文章 ==="
echo "查询指定日期范围内发布的所有相关论文（关键词：OR逻辑）"
RANGE_OUTPUT_FILE="${BASE_DIR}/survey_range_${TIMESTAMP}.md"

python3 /mnt/bn/chenguoqing-lf/code/survey_agent/examples/generate_survey_v2.py \
    --terms "${TERMS[@]}" \
    --max_results 10 \
    --output_file "$RANGE_OUTPUT_FILE" \
    --llm_provider "openai" \
    --model_name "$MODEL_NAME" \
    --pdf_dir "$PDF_DIR" \
    --logic "OR" \
    --date_range "2025-09-18" "2025-09-20" \
    2>&1 | tee -a "${log_file}"



