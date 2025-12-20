#!/usr/bin/env python3
"""
将LunaTV-config.json转换为指定格式
"""

import json
import requests
from datetime import datetime

def fetch_original_data():
    """从GitHub获取原始数据"""
    url = "https://raw.githubusercontent.com/hafrey1/LunaTV-config/refs/heads/main/LunaTV-config.json"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def convert_format(original_data):
    """将原始数据转换为目标格式"""
    sites = []
    
    for item in original_data:
        # 确保有必要的字段
        if not all(k in item for k in ['name', 'url']):
            continue
            
        # 创建唯一key：使用小写字母，移除特殊字符
        key = item['name'].lower()
        key = ''.join(c for c in key if c.isalnum() or c == '_')
        
        # 处理URL，确保以JSON结尾
        api_url = item['url']
        if not api_url.endswith('.json'):
            # 如果是视频主页，转换为API地址
            if 'video' in api_url or 'vod' in api_url:
                # 移除末尾的.html或.php等
                api_url = api_url.split('.html')[0].split('.php')[0]
                if not api_url.endswith('/'):
                    api_url += '/'
                api_url += 'api.php/provide/vod/at/json'
        
        site = {
            "key": f"site_{key[:20]}",  # 限制长度
            "name": item['name'],
            "api": api_url,
            "active": True
        }
        
        sites.append(site)
    
    # 确保key唯一
    seen_keys = set()
    for i, site in enumerate(sites):
        base_key = site['key']
        counter = 1
        while site['key'] in seen_keys:
            site['key'] = f"{base_key}_{counter}"
            counter += 1
        seen_keys.add(site['key'])
    
    return {"sites": sites}

def save_output(data, filename="converted_data.json"):
    """保存转换后的数据"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"数据已保存到 {filename}")
    print(f"共转换了 {len(data['sites'])} 个站点")

def main():
    try:
        print("开始获取原始数据...")
        original_data = fetch_original_data()
        print(f"获取到 {len(original_data)} 条原始数据")
        
        print("开始转换格式...")
        converted_data = convert_format(original_data)
        
        print("保存转换后的数据...")
        save_output(converted_data)
        
        # 同时保存一个带时间戳的版本
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_filename = f"data/archive/converted_data_{timestamp}.json"
        save_output(converted_data, archive_filename)
        
        return True
        
    except Exception as e:
        print(f"处理过程中出现错误: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
