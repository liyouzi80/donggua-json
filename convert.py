import requests
import json
import hashlib

def get_unique_key(url):
    # 生成唯一Key
    return "key_" + hashlib.md5(url.encode()).hexdigest()[:8]

def main():
    source_url = "https://raw.githubusercontent.com/hafrey1/LunaTV-config/refs/heads/main/LunaTV-config.json"
    
    try:
        response = requests.get(source_url, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        new_sites = []
        unique_urls = set() # 用于过滤重复的 API

        # --- 深度解析逻辑 ---
        # 1. 检查是否是 LunaTV 常用的字典格式，站点通常在 'lives' 或 'sites' 键下
        potential_keys = ['lives', 'sites', 'list']
        source_items = []

        if isinstance(data, list):
            source_items = data
        elif isinstance(data, dict):
            for k in potential_keys:
                if k in data and isinstance(data[k], list):
                    source_items.extend(data[k])
                    break
        
        # 2. 如果还是没找到，尝试遍历字典中所有的列表（兜底逻辑）
        if not source_items and isinstance(data, dict):
            for val in data.values():
                if isinstance(val, list):
                    source_items.extend(val)

        # 3. 提取并格式化
        for item in source_items:
            if not isinstance(item, dict):
                continue
                
            # 提取 API 地址：尝试多种常见的字段名 (api, url, ext)
            api_url = item.get('api') or item.get('url') or item.get('ext')
            name = item.get('name', '未命名站点')

            # 过滤无效数据和重复数据
            if api_url and isinstance(api_url, str) and api_url.startswith('http'):
                if api_url not in unique_urls:
                    new_sites.append({
                        "key": get_unique_key(api_url),
                        "name": name,
                        "api": api_url,
                        "active": True
                    })
                    unique_urls.add(api_url)
        
        # 构建最终输出
        output = {"sites": new_sites}
        
        with open('LunaTV-formatted.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
            
        print(f"解析完成！从源文件提取了 {len(new_sites)} 个有效站点。")
        
    except Exception as e:
        print(f"转换过程中出错: {e}")
        # 写入一个基础结构防止完全失效
        with open('LunaTV-formatted.json', 'w', encoding='utf-8') as f:
            json.dump({"sites": []}, f)
        exit(1)

if __name__ == "__main__":
    main()
