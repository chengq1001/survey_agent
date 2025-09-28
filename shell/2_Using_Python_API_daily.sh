#!/bin/bash

# unset HTTP_PROXY; unset http_proxy; unset https_proxy

# # 设置代理
# export HTTP_PROXY=http://sys-proxy-rd-relay.byted.org:8118
# export http_proxy=http://sys-proxy-rd-relay.byted.org:8118
# export https_proxy=http://sys-proxy-rd-relay.byted.org:8118
# export no_proxy="localhost,.byted.org,byted.org,.bytedance.net,bytedance.net,.byteintl.net,.tiktok-row.net,.tiktok-row.org,127.0.0.1,127.0.0.0/8,169.254.0.0/16,100.64.0.0/10,172.16.0.0/12,192.168.0.0/16,10.0.0.0/8,::1,fe80::/10,fd00::/8"

date_str=2025-09-20
echo "date: $date_str"

# 定义搜索关键词组
TERM_GROUPS_1=(
    "LLM" 
    "Large Language Model" 
    "VLM" 
    "Vision Language Model" 
    "MLLM" 
    "Multimodal Large Language Models" 
    "LVLM" 
    "Large Vision-Language Models"
)

# 第二组：强化学习和推理相关
TERM_GROUPS_2=(
    "Reasoning" 
    "Hallucination"
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
MODEL_NAME="ep-20250911120040-8dh4j" # Kimi-K2

# 定义输出文件和PDF目录
TIMESTAMP=$(date +"%Y%m%d_%H%M")
BASE_DIR="/mnt/bn/chenguoqing-lf/code/survey_agent/output/daily_${date_str}"
OUTPUT_FILE="${BASE_DIR}/survey_${TIMESTAMP}.md"
PDF_DIR="${BASE_DIR}/pdfs/"

log_file=${BASE_DIR}/logs/survey_${TIMESTAMP}_log.txt

mkdir -p "$(dirname "$log_file")"


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

echo -e "\n=== 模式3: 动态生成排列组合循环调用 ==="
echo "为每组组合创建独立的输出文件并调用程序"

# 函数：将字符串转换为文件名安全的格式
to_filename() {
    echo "$1" | sed 's/[^a-zA-Z0-9]/_/g' | sed 's/__*/_/g' | sed 's/^_\|_$//g'
}

# 循环调用每组组合
for term1 in "${TERM_GROUPS_1[@]}"; do
    for term2 in "${TERM_GROUPS_2[@]}"; do
        # 动态创建组合名称
        term1_clean=$(to_filename "$term1")
        term2_clean=$(to_filename "$term2")
        combo_name="${term1_clean}_${term2_clean}"
        combo_output_file="${BASE_DIR}/${combo_name}/survey_${TIMESTAMP}.md"
        
        
        echo -e "\n--- 处理组合: $term1 + $term2 ---"
        echo "组合名称: $combo_name"
        echo "输出文件: $combo_output_file"
        echo "日志文件: $log_file"
        
        # 创建日志目录
        mkdir -p "$(dirname "$combo_output_file")"
        
        # 调用程序
        python3 /mnt/bn/chenguoqing-lf/code/survey_agent/examples/generate_survey_v2.py \
            --terms "$term1" "$term2" \
            --max_results 200 \
            --output_file "$combo_output_file" \
            --llm_provider "openai" \
            --model_name "$MODEL_NAME" \
            --pdf_dir "$PDF_DIR" \
            --logic "AND" \
            --date_range ${date_str} ${date_str} \
            2>&1 | tee -a "$log_file"
        
        echo "完成组合: $term1 + $term2"
    done
done

echo -e "\n=== 所有组合处理完成 ==="



