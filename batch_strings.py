###
## 实现了输入文案列表的excel，输出对应的json：
# {
#   "error_code": 0,
#   "error_msg": "",
# 	"data": [
# 	{"region_name": "test_strings",
# 	"strings": [{"id": "trade_test_1", "chi": "测试1", "tra": "測試1", "eng": "Test1", "region": "test_strings"}
# 	},
# 	...],
# }
#
###

import pandas as pd
import os
import argparse
from json import JSONEncoder
import json

ERROR_CODE = "error_code"
ERROR_MSG = "error_msg"

OPEN_FILE_ERROR = 1
OPEN_FILE_ERROR_MSG = "打开Excel异常，请确认路径和Sheet名是否正确"
DATA_NULL_ERROR = 2
DATA_NULL_ERROR_MSG = "输入为空，请检查输入"

SUCCESS = 0

REGION_NULL_WARNING = -1
REGION_NULL_WARNING_MSG = "检查到输入有空的region，已正常加入到strings。如非本意，请检查输入"
ID_NULL_WARNING = -2
ID_NULL_WARNING_MSG = "检查到输入有空的id，已跳过处理，请检查输入"
STRING_NULL_WARNING = -3
STRING_NULL_WARNING_MSG = "检查到输入有空的文案string，已正常加入到strings。如非本意，请检查输入"

source_path = os.path.abspath(os.path.dirname(__file__)) + "\\strings_input.xlsx"
sheet_name = "Sheet1"
regionMap = {}
regions = []
result = {ERROR_CODE: 0, ERROR_MSG: ""}


class MyEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__


class RegionData(object):
    def __init__(self, region, strings):
        self.region_name = region
        self.strings = strings


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
    parser = argparse.ArgumentParser(description='用于把excel中的文案提炼成json的工具')
    parser.add_argument('--path', '-p', help='path 属性，代表输入数据的excel。非必要参数,默认值是当前目录下的strings_input')
    parser.add_argument('--sheet', '-s', help='sheet 属性，Excel表格中装载数据的Sheet名，默认为Sheet1')
    return parser



def readDataSource():
    try:
        d = pd.read_excel(source_path, sheet_name=sheet_name, na_values='blank', encoding="utf-8")
    except BaseException:
        result[ERROR_CODE] = OPEN_FILE_ERROR
        result[ERROR_MSG] = OPEN_FILE_ERROR_MSG
        return False

    parseData(d)

    for key, values in regionMap.items():
        regions.append(RegionData(key, values))

    return True


def parseData(source):
    def checkStrNull(str):

        if pd.isnull(str):
            result[ERROR_CODE] = STRING_NULL_WARNING
            result[ERROR_MSG] = STRING_NULL_WARNING_MSG
            return ""
        else:
            return str

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
            result[ERROR_CODE] = ID_NULL_WARNING
            result[ERROR_MSG] = ID_NULL_WARNING_MSG
            continue

        if pd.isnull(region):
            result[ERROR_CODE] = REGION_NULL_WARNING
            result[ERROR_MSG] = REGION_NULL_WARNING_MSG
            region = ""

        string = StringData(sid, checkStrNull(chi), checkStrNull(tra), checkStrNull(eng), region)
        addMap(string)
        allStrings.append(string)

    if len(allStrings) == 0:
        result[ERROR_CODE] = DATA_NULL_ERROR
        result[ERROR_MSG] = DATA_NULL_ERROR_MSG

    return


if __name__ == '__main__':
    parser = initParser()
    parseParams(parser.parse_args())
    readDataSource()
    result["data"] = regions
    print(json.dumps(result, cls=MyEncoder, ensure_ascii=False))
