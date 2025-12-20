#!/usr/bin/env python3
"""
将LunaTV-config.json转换为指定格式 - 修复版
"""

import json
import requests
import re
from datetime import datetime
from urllib.parse import urlparse

def fetch_original_data():
    """从GitHub获取原始数据"""
    url = "https://raw.githubusercontent.com/hafrey1/LunaTV-config/refs/heads/main/LunaTV-config.json"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def sanitize_key(name):
    """从站点名称生成安全的key"""
    if not name:
        return "unknown"
    
    # 移除特殊字符，只保留字母数字和下划线
    key = re.sub(r'[^\w\u4e00-\u9fff]', '_', str(name))
    
    # 如果是中文开头，添加前缀
    if re.match(r'^[\u4e00-\u9fff]', key):
        key = 'site_' + key
    
    # 确保只包含字母数字和下划线
    key = re.sub(r'[^a-zA-Z0-9_]', '', key)
    
    # 转换为小写
    key = key.lower()
    
    # 确保长度合适
    if len(key) > 30:
        key = key[:30]
    
    if not key:
        key = "site"
    
    return key

def extract_api_url(url):
    """从各种URL格式中提取或构造API地址"""
    if not url:
        return ""
    
    # 尝试几种常见的API格式
    
    # 1. 已经是API地址
    if 'api.php' in url:
        return url
    
    # 2. 尝试从视频站点URL构造API地址
    parsed = urlparse(url)
    
    # 移除路径末尾的文件名
    path = parsed.path
    if '.' in path.split('/')[-1]:
        path = '/'.join(path.split('/')[:-1]) + '/'
    
    # 常见Maccms API路径
    api_paths = [
        'api.php/provide/vod/at/json',
        'api.php/provide/vod/',
        'api.php/json',
        'api.php'
    ]
    
    base_url = f"{parsed.scheme}://{parsed.netloc}{path}"
    
    # 测试可能的API地址
    for api_path in api_paths:
        api_url = base_url + api_path
        # 在实际使用中，这里可以添加测试API是否可用的代码
        return api_url
    
    # 如果无法构造，返回原始URL
    return url

def convert_format(original_data):
    """将原始数据转换为目标格式"""
    sites = []
    
    # 处理各种可能的原始数据结构
    if isinstance(original_data, list):
        data_list = original_data
    elif isinstance(original_data, dict):
        # 如果原始数据是字典，尝试找到包含站点列表的键
        possible_keys = ['sites', 'list', 'data', 'items', 'video_sites']
        for key in possible_keys:
            if key in original_data and isinstance(original_data[key], list):
                data_list = original_data[key]
                break
        else:
            # 如果没有找到列表，尝试将整个字典视为一个站点
            data_list = [original_data]
    else:
        print(f"无法处理的数据类型: {type(original_data)}")
        return {"sites": []}
    
    print(f"开始处理 {len(data_list)} 个数据项...")
    
    for i, item in enumerate(data_list):
        try:
            # 尝试从不同的键名中获取名称
            name = None
            possible_name_keys = ['name', 'title', 'site_name', 'nm', '网站名']
            for key in possible_name_keys:
                if key in item:
                    name = item[key]
                    break
            
            # 尝试从不同的键名中获取URL
            url = None
            possible_url_keys = ['url', 'api', 'address', 'link', '网址', 'site_url']
            for key in possible_url_keys:
                if key in item:
                    url = item[key]
                    break
            
            if not name or not url:
                print(f"跳过第 {i+1} 项: 缺少名称或URL")
                print(f"  数据项: {item}")
                continue
            
            # 生成唯一key
            key_name = sanitize_key(name)
            base_key = key_name
            counter = 1
            final_key = base_key
            
            # 检查key是否重复
            while any(site['key'] == final_key for site in sites):
                final_key = f"{base_key}_{counter}"
                counter += 1
            
            # 处理API URL
            api_url = extract_api_url(url)
            
            site = {
                "key": final_key,
                "name": str(name),
                "api": api_url,
                "active": True
            }
            
            sites.append(site)
            print(f"添加站点: {name} -> {final_key}")
            
        except Exception as e:
            print(f"处理第 {i+1} 项时出错: {str(e)}")
            print(f"  数据项: {item}")
            continue
    
    return {"sites": sites}

def debug_original_data(original_data):
    """调试原始数据结构"""
    print("\n=== 原始数据调试信息 ===")
    print(f"数据类型: {type(original_data)}")
    
    if isinstance(original_data, list):
        print(f"列表长度: {len(original_data)}")
        if len(original_data) > 0:
            print("\n前3个元素:")
            for i in range(min(3, len(original_data))):
                print(f"\n元素 {i}:")
                print(f"  类型: {type(original_data[i])}")
                if isinstance(original_data[i], dict):
                    print(f"  键: {list(original_data[i].keys())}")
                    for k, v in original_data[i].items():
                        print(f"  {k}: {v}")
    
    elif isinstance(original_data, dict):
        print(f"字典键: {list(original_data.keys())}")
        for k, v in original_data.items():
            print(f"\n{k}:")
            print(f"  类型: {type(v)}")
            if isinstance(v, list) and len(v) > 0:
                print(f"  列表长度: {len(v)}")
                if len(v) > 0:
                    print(f"  第一个元素类型: {type(v[0])}")
                    if isinstance(v[0], dict):
                        print(f"  第一个元素的键: {list(v[0].keys())}")

def save_output(data, filename="converted_data.json"):
    """保存转换后的数据"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n数据已保存到 {filename}")
    print(f"共转换了 {len(data['sites'])} 个站点")
    
    # 打印前几个站点作为示例
    if len(data['sites']) > 0:
        print("\n前5个转换后的站点:")
        for i, site in enumerate(data['sites'][:5]):
            print(f"\n{i+1}. {site['name']}")
            print(f"   Key: {site['key']}")
            print(f"   API: {site['api']}")

def main():
    try:
        print("开始获取原始数据...")
        original_data = fetch_original_data()
        
        # 调试原始数据结构
        debug_original_data(original_data)
        
        print("\n开始转换格式...")
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
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
