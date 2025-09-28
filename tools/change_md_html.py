#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markdown 转 HTML 工具
将 Markdown 文件转换为 HTML 文件
"""

import os
import sys
import re
from pathlib import Path

try:
    import markdown
    from markdown.extensions import codehilite, fenced_code, tables, toc
except ImportError:
    print("错误: 需要安装 markdown 库")
    print("请运行: pip install markdown")
    sys.exit(1)


def parse_md_structure(md_content):
    """
    解析 Markdown 文件结构，分离 Paper List 和 TLDR/Notes 部分
    
    Args:
        md_content (str): Markdown 文件内容
    
    Returns:
        tuple: (paper_list_content, papers_dict)
    """
    # 按一级标题分割内容
    sections = re.split(r'^# ', md_content, flags=re.MULTILINE)
    
    paper_list_content = ""
    papers_dict = {}
    
    for section in sections:
        if not section.strip():
            continue
            
        lines = section.split('\n')
        title = lines[0].strip()
        content = '\n'.join(lines[1:]).strip()
        
        if title == "Paper List":
            paper_list_content = content
        elif title == "TLDR/Notes":
            # 解析二级标题（论文）
            paper_sections = re.split(r'^## ', content, flags=re.MULTILINE)
            
            for paper_section in paper_sections:
                if not paper_section.strip():
                    continue
                    
                paper_lines = paper_section.split('\n')
                paper_title = paper_lines[0].strip()
                paper_content = '\n'.join(paper_lines[1:]).strip()
                
                if paper_title:
                    papers_dict[paper_title] = paper_content
    
    return paper_list_content, papers_dict


def convert_md_to_html(md_file_path, output_path=None):
    """
    将 Markdown 文件转换为 HTML 文件
    
    Args:
        md_file_path (str): Markdown 文件路径
        output_path (str, optional): 输出 HTML 文件路径，默认为同目录同名文件
    """
    # 检查输入文件是否存在
    if not os.path.exists(md_file_path):
        print(f"错误: 文件 '{md_file_path}' 不存在")
        return False
    
    # 设置输出路径
    if output_path is None:
        md_path = Path(md_file_path)
        output_path = md_path.with_suffix('.html')
    
    try:
        # 读取 Markdown 文件
        with open(md_file_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # 解析文件结构
        paper_list_content, papers_dict = parse_md_structure(md_content)
        
        # 配置 Markdown 扩展
        extensions = [
            'codehilite',
            'fenced_code',
            'tables',
            'toc',
            'nl2br',
            'attr_list'
        ]
        
        # 创建 Markdown 实例
        md = markdown.Markdown(extensions=extensions)
        
        # 生成分页 HTML 文档
        full_html = generate_paginated_html(paper_list_content, papers_dict, md)
        
        # 写入 HTML 文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_html)
        
        print(f"成功转换: {md_file_path} -> {output_path}")
        return True
        
    except Exception as e:
        print(f"转换失败: {e}")
        return False


def generate_paginated_html(paper_list_content, papers_dict, md):
    """
    生成分页的 HTML 文档
    
    Args:
        paper_list_content (str): Paper List 部分的内容
        papers_dict (dict): 论文标题和内容的字典
        md: Markdown 实例
    
    Returns:
        str: 完整的 HTML 文档
    """
    # 生成 Paper List 页面的 HTML
    paper_list_html = md.convert(paper_list_content)
    
    # 为 Paper List 中的链接添加锚点
    paper_list_html = add_links_to_papers(paper_list_html, papers_dict, paper_list_content)
    
    # 生成论文页面
    paper_pages = []
    for i, (paper_title, paper_content) in enumerate(papers_dict.items(), 1):
        paper_html = md.convert(f"## {paper_title}\n\n{paper_content}")
        paper_pages.append(paper_html)
    
    # 生成完整的分页 HTML
    return generate_full_paginated_html(paper_list_html, paper_pages, papers_dict)


def extract_paper_info_from_content(content, paper_title):
    """
    从内容中提取论文信息和链接
    
    Args:
        content (str): 包含论文信息的Markdown内容
        paper_title (str): 论文标题（锚点格式）
    
    Returns:
        tuple: (真实论文标题, 论文链接HTML)
    """
    # 查找包含该论文标题的行
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if paper_title in line:
            # 查找前一行是否有真实标题（**标题**格式）
            real_title = paper_title
            paper_link_html = '<span class="no-link">无链接</span>'
            
            # 检查当前行和前一行
            for check_line in [lines[i-1] if i > 0 else '', line]:
                # 提取真实论文标题（**标题**格式）
                title_match = re.search(r'\*\*(.*?)\*\*', check_line)
                if title_match:
                    real_title = title_match.group(1)
                
                # 查找 [[Paper](url)] 格式的链接
                paper_link_match = re.search(r'\[\[Paper\]\(([^)]+)\)\]', check_line)
                if paper_link_match:
                    paper_url = paper_link_match.group(1)
                    paper_link_html = f'<a href="{paper_url}" target="_blank" class="paper-external-link">Paper</a>'
            
            return real_title, paper_link_html
    
    return paper_title, '<span class="no-link">无链接</span>'


def add_links_to_papers(paper_list_html, papers_dict, paper_list_content):
    """
    为 Paper List 中的论文标题添加编号和链接，并以表格形式显示
    
    Args:
        paper_list_html (str): Paper List 的 HTML 内容
        papers_dict (dict): 论文标题和内容的字典
        paper_list_content (str): 原始 Paper List 的 Markdown 内容
    
    Returns:
        str: 添加了编号和链接的 HTML 内容
    """
    # 生成表格HTML
    table_html = '''
    <div class="paper-list-container">
        <table class="paper-list-table">
            <thead>
                <tr>
                    <th class="col-number">ID</th>
                    <th class="col-title">论文名称</th>
                    <th class="col-paper-link">论文链接</th>
                    <th class="col-notes-link">笔记链接</th>
                </tr>
            </thead>
            <tbody>
    '''
    
    # 为每个论文添加表格行
    for i, paper_title in enumerate(papers_dict.keys(), 1):
        # 创建安全的 ID（移除特殊字符）
        safe_id = re.sub(r'[^\w\s-]', '', paper_title).strip()
        safe_id = re.sub(r'[-\s]+', '-', safe_id).lower()
        
        # 提取真实论文标题和链接
        real_title, paper_link = extract_paper_info_from_content(paper_list_content, paper_title)
        
        # 显示完整标题，允许换行
        display_title = real_title
        
        table_html += f'''
                <tr class="paper-row">
                    <td class="paper-number">{i}</td>
                    <td class="paper-title" title="{real_title}">
                        {display_title}
                    </td>
                    <td class="paper-actions">
                        {paper_link}
                    </td>
                    <td class="paper-actions">
                        <a href="#paper-{safe_id}" class="notes-link">查看笔记</a>
                    </td>
                </tr>
        '''
    
    table_html += '''
            </tbody>
        </table>
    </div>
    '''
    
    # 检查原内容中是否包含论文标题
    found_papers = False
    print(f"Debug: papers_dict has {len(papers_dict)} papers")
    for paper_title in papers_dict.keys():
        print(f"Debug: checking paper title: {paper_title[:50]}...")
        # 匹配各种可能的格式：**标题**、*标题*、标题等
        patterns = [
            rf'\*\*{re.escape(paper_title)}\*\*',
            rf'\*{re.escape(paper_title)}\*',
            rf'`{re.escape(paper_title)}`',
            re.escape(paper_title)
        ]
        
        for pattern in patterns:
            if re.search(pattern, paper_list_html, flags=re.IGNORECASE):
                print(f"Debug: found paper in HTML: {paper_title[:50]}...")
                found_papers = True
                break
        if found_papers:
            break
    
    # 如果检测到有论文内容，直接替换整个Paper List内容为表格
    if found_papers:
        print("Debug: replacing entire Paper List content with table")
        # 直接替换整个内容为表格
        paper_list_html = table_html
    else:
        print("Debug: no papers found, adding table at end")
        # 如果没有找到论文标题，直接在内容末尾添加表格
        paper_list_html += table_html
    
    return paper_list_html


def generate_full_paginated_html(paper_list_html, paper_pages, papers_dict=None):
    """
    生成完整的分页 HTML 文档
    
    Args:
        paper_list_html (str): Paper List 页面的 HTML
        paper_pages (list): 论文页面的 HTML 列表
    
    Returns:
        str: 完整的 HTML 文档
    """
    # 获取 CSS 样式
    css = get_css_style()
    
    # 生成导航
    navigation = generate_navigation(len(paper_pages), papers_dict)
    
    # 生成所有页面内容
    pages_content = []
    
    # 第一页：Paper List
    pages_content.append(f'''
    <div class="page" id="page-0">
        <h1>Paper List</h1>
        {paper_list_html}
    </div>
    ''')
    
    # 后续页面：每篇论文
    for i, paper_html in enumerate(paper_pages, 1):
        # 从论文 HTML 中提取标题
        title_match = re.search(r'<h2[^>]*>(.*?)</h2>', paper_html, re.DOTALL)
        if title_match:
            paper_title = title_match.group(1).strip()
            safe_id = re.sub(r'[^\w\s-]', '', paper_title).strip()
            safe_id = re.sub(r'[-\s]+', '-', safe_id).lower()
        else:
            safe_id = f"paper-{i}"
        
        pages_content.append(f'''
        <div class="page" id="page-{i}" data-paper-id="paper-{safe_id}">
            {paper_html}
        </div>
        ''')
    
    # 生成完整 HTML
    html_template = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>论文调研报告</title>
    {css}
</head>
<body>
    {navigation}
    <div class="container">
        {''.join(pages_content)}
    </div>
    
    <!-- 分页导航按钮 -->
    <div class="page-navigation">
        <button id="prevBtn" class="nav-btn prev-btn" onclick="previousPage()" disabled>
            <span>← 上一页</span>
        </button>
        <button id="nextBtn" class="nav-btn next-btn" onclick="nextPage()">
            <span>下一页 →</span>
        </button>
    </div>
    <script>
        
        // 处理锚点链接
        document.addEventListener('click', function(e) {{
            if (e.target.classList.contains('paper-link') || e.target.classList.contains('notes-link')) {{
                e.preventDefault();
                const href = e.target.getAttribute('href');
                const paperId = href.replace('#', '');
                const targetPage = document.querySelector(`[data-paper-id="${{paperId}}"]`);
                if (targetPage) {{
                    const pageIndex = Array.from(document.querySelectorAll('.page')).indexOf(targetPage);
                    showPage(pageIndex);
                }}
            }}
        }});
        
        // 分页导航功能
        let currentPage = 0;
        const totalPages = document.querySelectorAll('.page').length;
        
        function updateNavigationButtons() {{
            const prevBtn = document.getElementById('prevBtn');
            const nextBtn = document.getElementById('nextBtn');
            
            prevBtn.disabled = currentPage === 0;
            nextBtn.disabled = currentPage === totalPages - 1;
        }}
        
        function previousPage() {{
            if (currentPage > 0) {{
                currentPage--;
                showPage(currentPage);
                updateNavigationButtons();
            }}
        }}
        
        function nextPage() {{
            if (currentPage < totalPages - 1) {{
                currentPage++;
                showPage(currentPage);
                updateNavigationButtons();
            }}
        }}
        
        // 修改showPage函数以更新当前页面
        function showPage(pageIndex) {{
            currentPage = pageIndex;
            const pages = document.querySelectorAll('.page');
            pages.forEach((page, index) => {{
                page.style.display = index === pageIndex ? 'block' : 'none';
            }});
            
            // 更新导航状态
            const navItems = document.querySelectorAll('.nav-item');
            navItems.forEach((item, index) => {{
                item.classList.toggle('active', index === pageIndex);
            }});
            
            // 滚动导航栏到当前激活的项
            const activeNavItem = navItems[pageIndex];
            if (activeNavItem) {{
                activeNavItem.scrollIntoView({{ 
                    behavior: 'smooth', 
                    block: 'nearest', 
                    inline: 'center' 
                }});
            }}
            
            updateNavigationButtons();
            
            // 滚动到页面顶部
            window.scrollTo({{ top: 0, behavior: 'smooth' }});
        }}
        
        // 初始化显示第一页
        showPage(0);
    </script>
</body>
</html>"""
    
    return html_template


def generate_navigation(total_pages, papers_dict=None):
    """
    生成导航栏
    
    Args:
        total_pages (int): 总页数
        papers_dict (dict, optional): 论文标题和内容的字典
    
    Returns:
        str: 导航栏 HTML
    """
    nav_items = ['<a href="#" class="nav-item" onclick="showPage(0)">Paper List</a>']
    
    if papers_dict:
        # 使用论文标题作为导航项
        for i, paper_title in enumerate(papers_dict.keys(), 1):
            # 截断过长的标题
            display_title = paper_title[:20] + "..." if len(paper_title) > 20 else paper_title
            nav_items.append(f'<a href="#" class="nav-item" onclick="showPage({i})" title="{paper_title}">论文 {i}</a>')
    else:
        # 回退到原来的编号方式
        for i in range(1, total_pages + 1):
            nav_items.append(f'<a href="#" class="nav-item" onclick="showPage({i})">论文 {i}</a>')
    
    return f'''
    <nav class="navigation">
        <div class="nav-container">
            {''.join(nav_items)}
        </div>
    </nav>
    '''


def get_css_style():
    """
    获取 CSS 样式
    
    Returns:
        str: CSS 样式字符串
    """
    # 分页样式
    paginated_css = """
    <style>
    body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;
        line-height: 1.6;
        color: #24292e;
        margin: 0;
        padding: 0;
        background-color: #f8f9fa;
    }
    
    /* 导航栏样式 */
    .navigation {
        background-color: #fff;
        border-bottom: 1px solid #e1e4e8;
        padding: 0;
        position: sticky;
        top: 0;
        z-index: 100;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        height: 60px; /* 固定高度，约为页面的1/5 */
        overflow: hidden;
    }
    
    .nav-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 20px;
        display: flex;
        gap: 0;
        overflow-x: auto;
        overflow-y: hidden;
        height: 100%;
        align-items: center;
        scrollbar-width: thin;
        scrollbar-color: #c1c1c1 #f1f1f1;
    }
    
    .nav-container::-webkit-scrollbar {
        height: 6px;
    }
    
    .nav-container::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 3px;
    }
    
    .nav-container::-webkit-scrollbar-thumb {
        background: #c1c1c1;
        border-radius: 3px;
    }
    
    .nav-container::-webkit-scrollbar-thumb:hover {
        background: #a8a8a8;
    }
    
    .nav-item {
        display: inline-block;
        padding: 8px 12px;
        color: #586069;
        text-decoration: none;
        border-bottom: 2px solid transparent;
        transition: all 0.2s ease;
        font-weight: 500;
        white-space: nowrap;
        flex-shrink: 0;
        font-size: 14px;
    }
    
    .nav-item:hover {
        color: #0366d6;
        background-color: #f6f8fa;
    }
    
    .nav-item.active {
        color: #0366d6;
        border-bottom-color: #0366d6;
        background-color: #f6f8fa;
    }
    
    /* 容器样式 */
    .container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 20px;
    }
    
    /* 页面样式 */
    .page {
        background-color: #fff;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        padding: 40px;
        margin-bottom: 20px;
        min-height: calc(100vh - 120px); /* 调整高度计算，考虑导航栏高度 */
    }
    
    .page:not(:first-child) {
        display: none;
    }
    
    /* 标题样式 */
    h1, h2, h3, h4, h5, h6 {
        color: #24292e;
        margin-top: 24px;
        margin-bottom: 16px;
        font-weight: 600;
    }
    
    h1 { 
        font-size: 2.5em; 
        border-bottom: 2px solid #e1e4e8; 
        padding-bottom: 16px;
        margin-top: 0;
    }
    
    h2 { 
        font-size: 1.8em; 
        border-bottom: 1px solid #e1e4e8; 
        padding-bottom: 12px;
        margin-top: 32px;
    }
    
    h3 { font-size: 1.4em; }
    h4 { font-size: 1.2em; }
    h5 { font-size: 1.1em; }
    h6 { font-size: 1em; color: #6a737d; }
    
    /* 代码样式 */
    code {
        background-color: rgba(27,31,35,0.05);
        padding: 0.2em 0.4em;
        border-radius: 3px;
        font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
        font-size: 85%;
    }
    
    pre {
        background-color: #f6f8fa;
        padding: 16px;
        border-radius: 6px;
        overflow-x: auto;
        font-size: 85%;
        line-height: 1.45;
        border: 1px solid #e1e4e8;
    }
    
    pre code {
        background-color: transparent;
        padding: 0;
        font-size: 100%;
    }
    
    /* 引用样式 */
    blockquote {
        border-left: 4px solid #dfe2e5;
        padding-left: 16px;
        color: #6a737d;
        margin: 16px 0;
        font-style: italic;
    }
    
    /* 表格样式 */
    table {
        border-collapse: collapse;
        width: 100%;
        margin: 16px 0;
        border: 1px solid #e1e4e8;
        border-radius: 6px;
        overflow: hidden;
    }
    
    th, td {
        border: 1px solid #e1e4e8;
        padding: 12px 16px;
        text-align: left;
    }
    
    th {
        background-color: #f6f8fa;
        font-weight: 600;
    }
    
    /* 确保论文列表表格的表头颜色正确 */
    .paper-list-table thead th {
        background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%) !important;
        color: white !important;
    }
    
    tr:nth-child(even) {
        background-color: #f6f8fa;
    }
    
    /* 链接样式 */
    a {
        color: #0366d6;
        text-decoration: none;
    }
    
    a:hover {
        text-decoration: underline;
    }
    
    .paper-link {
        color: #0366d6;
        font-weight: 500;
        padding: 2px 4px;
        border-radius: 3px;
        transition: background-color 0.2s ease;
    }
    
    .paper-link:hover {
        background-color: #e3f2fd;
        text-decoration: none;
    }
    
    /* 论文项目样式 */
    .paper-item {
        display: block;
        margin: 12px 0;
        padding: 8px 0;
        border-bottom: 1px solid #f0f0f0;
    }
    
    .paper-number {
        font-weight: 600;
        color: #0366d6;
        margin-right: 8px;
    }
    
    .notes-link {
        color: #28a745;
        font-size: 0.9em;
        margin-left: 8px;
        padding: 2px 6px;
        border-radius: 3px;
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        transition: all 0.2s ease;
    }
    
    .notes-link:hover {
        background-color: #28a745;
        color: white;
        text-decoration: none;
    }
    
    /* 论文列表表格样式 */
    .paper-list-container {
        margin: 24px 0;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        max-height: 70vh;
        overflow-y: auto;
    }
    
    .paper-list-table {
        width: 100%;
        border-collapse: collapse;
        background-color: #fff;
        font-size: 14px;
        position: relative;
    }
    
    .paper-list-table thead {
        background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
        color: white;
        position: sticky;
        top: 0;
        z-index: 10;
    }
    
    .paper-list-table th {
        padding: 16px 12px;
        text-align: left;
        font-weight: 600;
        font-size: 15px;
        border: none;
    }
    
    .paper-list-table .col-number {
        width: 60px;
        text-align: center;
    }
    
    .paper-list-table .col-title {
        width: auto;
    }
    
    .paper-list-table .col-paper-link {
        width: 100px;
        text-align: center;
    }
    
    .paper-list-table .col-notes-link {
        width: 100px;
        text-align: center;
    }
    
    .paper-list-table tbody tr {
        border-bottom: 1px solid #f0f0f0;
        transition: background-color 0.2s ease;
    }
    
    .paper-list-table tbody tr:hover {
        background-color: #f8f9fa;
    }
    
    .paper-list-table tbody tr:last-child {
        border-bottom: none;
    }
    
    .paper-list-table td {
        padding: 16px 12px;
        vertical-align: middle;
        border: none;
    }
    
    .paper-list-table .paper-number {
        text-align: center;
        font-weight: 600;
        color: #0366d6;
        font-size: 16px;
    }
    
    .paper-list-table .paper-title {
        word-wrap: break-word;
        word-break: break-word;
        white-space: normal;
        line-height: 1.4;
        max-width: 400px; /* 设置最大宽度，超出时换行 */
    }
    
    .paper-list-table .paper-title .paper-link {
        color: #24292e;
        font-weight: 500;
        text-decoration: none;
        line-height: 1.4;
    }
    
    .paper-list-table .paper-title .paper-link:hover {
        color: #0366d6;
        text-decoration: underline;
    }
    
    .paper-list-table .paper-actions {
        text-align: center;
    }
    
    .paper-list-table .notes-link {
        display: inline-block;
        padding: 6px 12px;
        background-color: #28a745;
        color: white;
        text-decoration: none;
        border-radius: 4px;
        font-size: 12px;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    .paper-list-table .notes-link:hover {
        background-color: #218838;
        transform: translateY(-1px);
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    .paper-external-link {
        display: inline-block;
        padding: 6px 12px;
        background-color: #0366d6;
        color: white;
        text-decoration: none;
        border-radius: 4px;
        font-size: 12px;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    .paper-external-link:hover {
        background-color: #0256cc;
        transform: translateY(-1px);
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        text-decoration: none;
    }
    
    .no-link {
        color: #6a737d;
        font-style: italic;
        font-size: 12px;
    }
    
    /* 分页导航按钮样式 */
    .page-navigation {
        position: fixed;
        bottom: 30px;
        left: 0;
        right: 0;
        display: flex;
        justify-content: space-between;
        padding: 0 30px;
        pointer-events: none;
        z-index: 1000;
    }
    
    .nav-btn {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 12px 20px;
        border-radius: 25px;
        font-size: 14px;
        font-weight: 600;
        cursor: pointer;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
        pointer-events: auto;
        min-width: 120px;
    }
    
    .nav-btn:hover:not(:disabled) {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
    }
    
    .nav-btn:disabled {
        background: #ccc;
        cursor: not-allowed;
        opacity: 0.6;
    }
    
    .prev-btn {
        margin-right: auto;
    }
    
    .next-btn {
        margin-left: auto;
    }
    
    /* 列表样式 */
    ul, ol {
        padding-left: 2em;
    }
    
    li {
        margin: 0.5em 0;
    }
    
    /* 段落样式 */
    p {
        margin: 16px 0;
    }
    
    /* 响应式设计 */
    @media (max-width: 768px) {
        .container {
            padding: 10px;
        }
        
        .page {
            padding: 20px;
        }
        
        .nav-container {
            padding: 0 10px;
        }
        
        .nav-item {
            padding: 6px 10px;
            font-size: 13px;
        }
        
        .navigation {
            height: 50px; /* 移动端更小的高度 */
        }
        
        h1 {
            font-size: 2em;
        }
        
        h2 {
            font-size: 1.5em;
        }
        
        /* 移动端表格样式 */
        .paper-list-table {
            font-size: 12px;
        }
        
        .paper-list-table th,
        .paper-list-table td {
            padding: 8px 6px;
        }
        
        .paper-list-table .col-paper-link,
        .paper-list-table .col-notes-link {
            width: 80px;
        }
        
        .paper-list-table .notes-link {
            padding: 4px 8px;
            font-size: 11px;
        }
    }
    </style>
    """
    
    return paginated_css


def main():
    """主函数"""
    # 在这里直接指定要转换的文件路径
    input_file = "/mnt/bn/chenguoqing-lf/code/survey_agent/output/titles/survey_titles_20250927_1915.md"
    output_file = None       # 留空则自动生成同名 HTML 文件
    
    # 转换文件
    success = convert_md_to_html(input_file, output_file)
    
    if success:
        print("转换完成!")
    else:
        print("转换失败!")
        sys.exit(1)


if __name__ == '__main__':
    main()
