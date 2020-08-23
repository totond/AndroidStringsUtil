###
## 实现了输入文案列表的excel，输出对应的json：
# {
# 	"region_name": [{
# 		"id": "trade_test_1",
# 		"chi": "\u6d4b\u8bd51",
# 		"tra": "\u6e2c\u8a661",
# 		"eng": "Test1",
# 		"region": "test_strings"
# 	},
# 	...],
#   "region_name_2":[...]
# }
#
## todo
## 1.中文乱码问题
## 2.错误情况兼容,定义错误码和脚本处理：
# a.输入了空的id，目前是跳过不处理
# b.输入了空的region，目前放到空的key里面
# c.输入了空的文案，目前无处理
###

import pandas as pd
import os
import argparse
from json import JSONEncoder
import json


source_path = os.path.abspath(os.path.dirname(__file__)) + "\\strings_input.xlsx"
sheet_name = "Sheet1"
regionMap = {}


class MyEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__


class StringData(object):
    def __init__(self, id, chi, tra, eng, region):
        self.id = id
        self.chi = chi
        self.tra = tra
        self.eng = eng
        self.region = region


def parseParams(args):
    path = args.path

    global sheet_name
    global source_path

    if pd.isnull(path) or path == "":
        pass
    else:
        source_path = path

    sheet = args.sheet
    if pd.isnull(sheet) or sheet == "":
        pass
    else:
        sheet_name = sheet


def initParser():
    parser = argparse.ArgumentParser(description='用于把excel中的神策埋点数据转化为实际代码的工具')
    parser.add_argument('--path', '-p', help='path 属性，代表输入数据的excel。非必要参数,默认值是当前目录下的strings_input')
    parser.add_argument('--sheet', '-s', help='sheet 属性，Excel表格中装载数据的Sheet名，默认为Sheet1')
    return parser


def readDataSource():
    d = pd.read_excel(source_path, sheet_name=sheet_name, na_values='blank', encoding="utf-8")

    parseData(d)


def parseData(source):
    def addMap(data: StringData):
        list = regionMap.get(data.region, None)
        if list is None:
            list = []

        list.append(data)

        regionMap[data.region] = list

    hang = source.shape[0]
    allStrings = []

    for i in range(hang):
        sid = source.iloc[i, 0]
        chi = source.iloc[i, 1]
        tra = source.iloc[i, 2]
        eng = source.iloc[i, 3]
        region = source.iloc[i, 4]

        if pd.isnull(sid):
            continue

        if pd.isnull(region):
            region = ""

        string = StringData(sid, chi, tra, eng, region)
        addMap(string)
        allStrings.append(string)

    return


if __name__ == '__main__':
    parser = initParser()
    parseParams(parser.parse_args())
    readDataSource()
    print(json.dumps(regionMap, cls=MyEncoder))
