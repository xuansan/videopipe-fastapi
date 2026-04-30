#!/usr/bin/env python3
"""
Milvus Schema导入脚本
根据JSON schema文件创建Milvus集合
"""

import json
import sys
from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility

def load_schema(json_file):
    """加载schema文件"""
    with open(json_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def convert_field_type(field_info):
    """转换字段类型到Milvus DataType"""
    field_type = field_info['type']
    
    type_mapping = {
        'INT64': DataType.INT64,
        'FLOAT_VECTOR': DataType.FLOAT_VECTOR,
        'VARCHAR': DataType.VARCHAR,
        'BOOL': DataType.BOOL,
        'INT32': DataType.INT32,
        'FLOAT': DataType.FLOAT,
        'DOUBLE': DataType.DOUBLE,
        'BINARY_VECTOR': DataType.BINARY_VECTOR
    }
    
    return type_mapping.get(field_type, DataType.VARCHAR)

def create_collection_from_schema(schema_data, host='localhost', port='19530'):
    """根据schema创建Milvus集合"""
    
    try:
        # 连接Milvus
        print(f"正在连接到Milvus: {host}:{port}")
        connections.connect("default", host=host, port=port)
        print("✅ 连接成功")
        
        # 提取集合信息
        collection_name = schema_data['collection_name']
        description = schema_data.get('description', '')
        fields_data = schema_data['fields']
        index_info = schema_data.get('index_info', {})
        consistency_level = schema_data.get('consistency_level', 'Bounded')
        db_name = schema_data.get('db_name', 'default')
        
        print(f"正在创建集合: {collection_name}")
        print(f"数据库: {db_name}")
        print(f"描述: {description}")
        
        # 检查集合是否已存在
        if utility.has_collection(collection_name):
            print(f"⚠️  集合 {collection_name} 已存在")
            choice = input("是否要删除现有集合并重新创建？(y/N): ")
            if choice.lower() == 'y':
                utility.drop_collection(collection_name)
                print(f"已删除现有集合: {collection_name}")
            else:
                print("取消创建操作")
                return
        
        # 构建字段schema
        fields = []
        for field_data in fields_data:
            field_name = field_data['name']
            field_type = convert_field_type(field_data)
            description = field_data.get('description', '')
            is_primary = field_data.get('is_primary', False)
            auto_id = field_data.get('auto_id', False)
            
            # 基础字段参数
            field_params = {
                'name': field_name,
                'dtype': field_type,
                'description': description,
                'is_primary': is_primary,
                'auto_id': auto_id
            }
            
            # 处理特殊类型参数
            if field_type == DataType.VARCHAR:
                max_length = field_data.get('max_length', 65535)
                field_params['max_length'] = max_length
            elif field_type == DataType.FLOAT_VECTOR:
                dim = field_data.get('dim', 128)
                field_params['dim'] = dim
            
            field_schema = FieldSchema(**field_params)
            fields.append(field_schema)
            
            print(f"  字段: {field_name} ({field_data['type']}) - {description}")
        
        # 创建集合schema
        schema = CollectionSchema(
            fields=fields,
            description=description,
            enable_dynamic_field=True
        )
        
        # 创建集合
        collection = Collection(
            name=collection_name,
            schema=schema,
            consistency_level=consistency_level
        )
        
        print(f"✅ 集合创建成功: {collection_name}")
        
        # 创建索引
        if index_info:
            print("正在创建索引...")
            for field_name, index_config in index_info.items():
                print(f"  为字段 {field_name} 创建索引")
                
                index_type = index_config.get('index_type', 'IVF_FLAT')
                metric_type = index_config.get('metric_type', 'L2')
                params = index_config.get('params', {})
                
                # 创建索引
                index_params = {
                    'index_type': index_type,
                    'metric_type': metric_type,
                    'params': params
                }
                
                collection.create_index(field_name, index_params)
                print(f"    ✅ 索引创建成功: {index_type} ({metric_type})")
        
        # 加载集合
        collection.load()
        print("✅ 集合加载成功")
        
        # 显示集合信息
        print(f"\n📊 集合信息:")
        print(f"  名称: {collection_name}")
        print(f"  描述: {description}")
        print(f"  一致性级别: {consistency_level}")
        print(f"  实体数量: {collection.num_entities}")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)
    finally:
        connections.disconnect("default")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Milvus Schema导入工具')
    parser.add_argument('schema_file', help='Schema JSON文件路径')
    parser.add_argument('--host', default='localhost', help='Milvus主机地址 (默认: localhost)')
    parser.add_argument('--port', default='19530', help='Milvus端口 (默认: 19530)')
    
    args = parser.parse_args()
    
    print("🚀 Milvus Schema导入工具")
    print("=" * 50)
    
    try:
        # 加载schema
        schema_data = load_schema(args.schema_file)
        print(f"✅ 加载schema文件: {args.schema_file}")
        
        # 创建集合
        create_collection_from_schema(schema_data, args.host, args.port)
        
        print("\n🎉 导入完成！")
        
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()