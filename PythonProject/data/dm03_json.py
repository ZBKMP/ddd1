# json --一种特定格式的字符串 结构与字典类似,json的属性名必须是str，且使用双引号
#python 中支持字典与json相互转换
import json

stu_dict={
    'name':'zbk',
    'age':18,
    'score':88,


}
#dict->json
json_str = json.dumps(stu_dict,ensure_ascii=False)
print(json_str)

#list[dict] --->json
list_dict =[{
      'name':'zbck',
      'age':19,
      'score':89,
      'school':{'name':'北大','addr':'北京','years':100
              }

},
{      'name':'zbw',
    'age':22,
    'score':90,
    'school':{'name':'上交','addr':'上海','years':100
              }
}
]
json_str = json.dumps(list_dict,ensure_ascii=False)
print(json_str)

#json_str --> dict
stu_dict=json.loads(json_str)
print(stu_dict)
############################################################################

#json文件操作
#将字典/字典[列表] 写入json
with open (file='txt/stu.json',mode='w',encoding='utf-8') as f:
    json.dump(list_dict,f,ensure_ascii=False,indent=2)

# 读取json文件内容 转为dict/list[dict]
     # 结果可能是dict 或list[dict]
with open (file='txt/stu.json',mode='r',encoding='utf-8') as f:
    list_dict = json.load(f)
    for i in list_dict:
          print(i,type(i))



