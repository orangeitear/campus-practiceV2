import os
import re
import time
import requests
from pathlib import Path
from bs4 import BeautifulSoup

# ============================================================
# 配置区（请根据实际情况修改）
# ============================================================
BASE_URL = "https://www.hhu.edu.cn"  # 替换为您的学校官网
OUTPUT_DIR = Path("../knowledge-base")
DELAY = 1  # 爬取间隔（秒）

# 栏目配置：URL路径 → 分类目录
CATEGORIES = {
    "/xxjj_23318": "01_学校概况",
    "/zzjg_23323": "02_组织机构",
    "/jxky": "03_教育教学",
    "/zsjy": "04_招生就业",
    # 根据实际网站结构添加更多
}

# ============================================================
# 爬虫核心函数
# ============================================================
def clean_text(text):
    """清洗文本，去除多余空白"""
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_content(soup):
    """提取页面正文内容"""
    # 尝试常见的内容容器
    selectors = [
        'div.content',
        'div.article',
        'div.main',
        'div.entry-content',
        'article',
        '.v_news_content',
    ]
    
    for selector in selectors:
        content = soup.select_one(selector)
        if content:
            return content.get_text(separator='\n')
    
    # 兜底：直接取 body 文本
    return soup.get_text(separator='\n')

def scrape_page(url, category, title=None):
    """爬取单个页面并保存"""
    try:
        print(f"  爬取: {url}")
        resp = requests.get(url, timeout=15)
        resp.encoding = 'utf-8'
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # 如果未指定标题，从页面提取
        if not title:
            title_tag = soup.find('title')
            if title_tag:
                title = title_tag.text.strip()
            else:
                title = url.split('/')[-1] or "未命名"
        
        # 提取正文
        body = extract_content(soup)
        body = clean_text(body)
        
        if len(body) < 50:
            print(f"      ⚠️ 内容过短，可能提取失败")
            return False
        
        # 生成文件名（去除特殊字符）
        safe_title = re.sub(r'[^\w\s\u4e00-\u9fff-]', '', title).strip()
        safe_title = safe_title[:50]  # 限制长度
        
        file_path = OUTPUT_DIR / category / f"{safe_title}.md"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 写入文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"""---
title: {title}
source_url: {url}
category: {category}
---

{body}
""")
        print(f"      ✅ 已保存: {file_path.relative_to(OUTPUT_DIR)}")
        return True
        
    except Exception as e:
        print(f"      ❌ 失败: {e}")
        return False

def discover_links(category_url):
    """发现栏目下的所有页面链接"""
    try:
        resp = requests.get(category_url, timeout=15)
        resp.encoding = 'utf-8'
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            text = a.text.strip()
            
            # 过滤有效链接
            if href.startswith('/') and len(href) > 1:
                full_url = BASE_URL + href
                if full_url not in links:
                    links.append((full_url, text))
        
        return links
    except Exception as e:
        print(f"   ❌ 发现链接失败: {e}")
        return []

# ============================================================
# 主程序
# ============================================================
def main():
    print("=" * 50)
    print("知识库爬虫")
    print("=" * 50)
    print(f"📂 输出目录: {OUTPUT_DIR}")
    print(f"🔗 目标网站: {BASE_URL}")
    print()
    
    total = 0
    for path, category in CATEGORIES.items():
        url = BASE_URL + path
        print(f"\n📂 分类: {category}")
        print(f"   URL: {url}")
        
        # 发现页面链接
        links = discover_links(url)
        print(f"   发现 {len(links)} 个页面")
        
        # 逐个爬取
        for page_url, title in links:
            if scrape_page(page_url, category, title):
                total += 1
                time.sleep(DELAY)
    
    print(f"\n{'='*50}")
    print(f"✅ 爬取完成！共生成 {total} 个文档")
    print(f"📁 保存位置: {OUTPUT_DIR}")
    print("="*50)

if __name__ == "__main__":
    main()
EOF