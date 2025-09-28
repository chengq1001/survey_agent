import requests
import os
from pathlib import Path

def download_pdf(url, output_dir):
    """
    下载PDF文件到指定目录，使用原始文件名
    
    Args:
        url (str): PDF文件的URL
        output_dir (str): 保存文件的目录路径
    """
    try:
        # 创建输出目录（如果不存在）
        os.makedirs(output_dir, exist_ok=True)
        
        # 发送HTTP请求下载文件
        print(f"正在下载文件: {url}")
        response = requests.get(url, stream=True)
        response.raise_for_status()  # 检查请求是否成功
        
        # 从URL中提取文件名
        filename = url.split('/')[-1]
        if not filename.endswith('.pdf'):
            filename += '.pdf'
        
        # 构建完整的文件路径
        output_path = os.path.join(output_dir, filename)
        
        # 获取文件大小
        total_size = int(response.headers.get('content-length', 0))
        
        # 写入文件
        with open(output_path, 'wb') as file:
            downloaded = 0
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        print(f"\r下载进度: {percent:.1f}%", end='', flush=True)
        
        print(f"\n文件下载完成: {output_path}")
        print(f"文件大小: {os.path.getsize(output_path)} 字节")
        
    except requests.exceptions.RequestException as e:
        print(f"下载失败: {e}")
    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    # PDF文件URL
    pdf_url = "https://arxiv.org/pdf/2509.12508v2"
    
    # 输出目录 - 保存到output目录
    output_dir = "/mnt/bn/chenguoqing-lf/code/survey_agent/output"
    
    # 下载文件
    download_pdf(pdf_url, output_dir)
