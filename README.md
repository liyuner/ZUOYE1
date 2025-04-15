# triplet_extraction

三元组抽取（实体-关系-实体，实体-属性-属性值）-- 模型训练&预测

功能，可用于非结构化文本抽取三元组，在构建知识图谱三元组数据时可提供帮助作用

# 使用方式
## ·训练

​    调用train模块下的model_train.py文件

```shell
 python train/model_train.py
```



## ·预测

​	调用主工程目录下的model_predict.py文件
注意， 预测时优于json load 的原因，i2p_dict的键将变成str，但'p'类型是int。你需要将它的类型转换为str

```shell
 python train/model_train.py
```

# 将三元组存入图数据库
```shell
 python database.py
```
# 抽取的实体关系存入total.xlsx中

