#!/bin/bash

# 在字节的merlin的开发机下不使用代理即可
export HTTP_PROXY=http://sys-proxy-rd-relay.byted.org:8118
export http_proxy=http://sys-proxy-rd-relay.byted.org:8118
export https_proxy=http://sys-proxy-rd-relay.byted.org:8118
export no_proxy="localhost,.byted.org,byted.org,.bytedance.net,bytedance.net,.byteintl.net,.tiktok-row.net,.tiktok-row.org,127.0.0.1,127.0.0.0/8,169.254.0.0/16,100.64.0.0/10,172.16.0.0/12,192.168.0.0/16,10.0.0.0/8,::1,fe80::/10,fd00::/8,arxiv.org,.arxiv.org"

TITLES_FILE="/mnt/bn/chenguoqing-lf/code/survey_agent/asserts/test.txt"

# 定义模型名称（可以根据需要修改）
# MODEL_NAME="ep-20250911141136-q5shc" # Kimi-K2
MODEL_NAME="ep-20250911120040-8dh4j" # Doubao-Seed-1.6

# 定义输出文件和PDF目录
TIMESTAMP=$(date +"%Y%m%d_%H%M")
BASE_DIR="/mnt/bn/chenguoqing-lf/code/survey_agent/output/titles"
OUTPUT_FILE="${BASE_DIR}/survey_titles_${TIMESTAMP}.md"
PDF_DIR="${BASE_DIR}/pdfs/"
LOG_FILE="${BASE_DIR}/logs/survey_titles_${TIMESTAMP}_log.txt"

# 创建必要的目录
mkdir -p "$(dirname "$LOG_FILE")"
mkdir -p "$PDF_DIR"

# 读取论文标题并转换为数组
echo "📖 读取论文标题文件: $TITLES_FILE"
TITLES=()
while IFS= read -r line; do
    # 跳过空行和注释行（以#开头的行）
    if [[ -n "$line" && ! "$line" =~ ^[[:space:]]*# ]]; then
        # 去掉论文标题中的 { 和 } 字符
        cleaned_line=$(echo "$line" | sed 's/[{}]//g')
        TITLES+=("$cleaned_line")
    fi
done < "$TITLES_FILE"

# 检查是否读取到标题
if [ ${#TITLES[@]} -eq 0 ]; then
    echo "❌ 错误: 文件中没有找到有效的论文标题"
    exit 1
fi

echo "✅ 成功读取 ${#TITLES[@]} 个论文标题:"
for i in "${!TITLES[@]}"; do
    echo "  $((i+1)). ${TITLES[$i]}"
done

echo ""
echo "🚀 开始生成综述..."
echo "📁 输出文件: $OUTPUT_FILE"
echo "📁 PDF目录: $PDF_DIR"
echo "📁 日志文件: $LOG_FILE"
echo ""

# 调用Python脚本生成综述
python3 /mnt/bn/chenguoqing-lf/code/survey_agent/examples/generate_survey_v2.py \
    --titles "${TITLES[@]}" \
    --output_file "$OUTPUT_FILE" \
    --llm_provider "openai" \
    --model_name "$MODEL_NAME" \
    --pdf_dir "$PDF_DIR" \
    2>&1 | tee -a "$LOG_FILE"

# 检查执行结果
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo ""
    echo "✅ 综述生成完成！"
    echo "📄 输出文件: $OUTPUT_FILE"
    echo "📁 PDF文件保存在: $PDF_DIR"
    echo "📋 详细日志: $LOG_FILE"
else
    echo ""
    echo "❌ 综述生成失败，请检查日志文件: $LOG_FILE"
    exit 1
fi