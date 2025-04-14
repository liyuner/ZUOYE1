from py2neo import Graph, Node, Relationship
import pandas as pd

# 连接Neo4j数据库
graph = Graph("bolt://localhost:7687", auth=("neo4j", "18687127516Ly"))
graph.delete_all()  # 清空现有数据库

# 读取Excel文件
df = pd.read_excel('total.xlsx', sheet_name='Sheet1', header=0)  # 确保使用第一行作为列名

# 检查列名并打印出来，用于调试
print("DataFrame列名:", df.columns.tolist())

# 重命名列名为A,B,C以便后续处理
df.columns = ['A', 'B', 'C']

# 初始化变量
current_entity = None
current_relation = None

# 遍历数据行
for _, row in df.iterrows():
    # 获取当前行的数据
    entity = str(row['A']).strip() if pd.notna(row['A']) else None
    relation = str(row['B']).strip() if pd.notna(row['B']) else None
    attribute = str(row['C']).strip() if pd.notna(row['C']) else None

    # 更新当前实体和关系
    if entity and entity != "nan":
        current_entity = entity
    if relation and relation != "nan":
        current_relation = relation

    # 如果存在属性/子实体，则创建节点和关系
    if attribute and attribute != "nan" and current_entity:
        # 创建或获取主实体节点
        main_node = Node('Entity', name=current_entity)
        graph.merge(main_node, 'Entity', 'name')

        # 检查属性是否是子实体（包含"-"或"："等符号）
        if any(char in attribute for char in ['-', '：', '(', ')']):
            # 处理为子实体
            sub_entity = attribute.split('(')[0].split('：')[-1].strip()
            sub_node = Node('SubEntity', name=sub_entity, description=attribute)
            graph.merge(sub_node, 'SubEntity', 'name')

            # 创建关系
            if current_relation:
                rel = Relationship(main_node, current_relation, sub_node)
                graph.create(rel)
            else:
                rel = Relationship(main_node, '包含', sub_node)
                graph.create(rel)
        else:
            # 处理为属性
            if current_relation:
                # 创建属性节点
                attr_node = Node('Attribute', name=attribute)
                graph.merge(attr_node, 'Attribute', 'name')

                # 创建关系
                rel = Relationship(main_node, current_relation, attr_node)
                graph.create(rel)
            else:
                # 直接作为属性添加到主节点
                main_node['attribute'] = attribute
                graph.push(main_node)

print("知识图谱构建完成！")