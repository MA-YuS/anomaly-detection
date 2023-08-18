'''
程序说明：
        该程序通过各车站的点类表文件，即
        ‘cfg_view_device.csv’ 和 ‘cfg_view_point_protocol.csv’ 两个文件
        结合能耗计算设备文件，即：‘3_洪园站_energy.xlsx’ 该文件主要为了获取设备名称

        生成 设备名称 与 运行数据文件名称 一一对应的配置文件
        配置文件为字典形式，保存为 .txt文件类型

        这一版本是依靠车站单独的点类表运行的，后续与综合监控人员对接后，
        可能须迭代为依据全线路的点类表生成所有车站的配置文件
'''
import os
import shutil
import pandas as pd
import numpy as np

'根据点类表生成设备名称与数据文件名称一一对应的配置文件'
def extract(name_path, device_path, protocol_path):
    name_file = pd.read_excel(name_path, )  # 读取设备能耗文件
    device_file = pd.read_csv(device_path, )  # 读取设备点类表
    protocol_file = pd.read_csv(protocol_path, )  # 读取设备点类表

    device_name = name_file['风机']
    filename_dict = {}
    for i in range(len(device_name)):
        name = device_name[i]
        # 使用numpy的where函数查找设备在点类表中的索引
        indices = np.where(device_file['Label'] == name)[0]  # ['Label']设备名称列的索引

        if len(indices) > 0:
            print(f"The element {name} is at index {indices[0]}")  # indices[0]即设备名称的行索引
            file_slice = np.array(device_file['DeviceId'])
            file_slice = file_slice[indices[0]]  # ‘file_slice’即文件名切片,字符串格式
            parts = file_slice.split("_")  # 使用split()方法按下划线分割file_slice字符串
            file_slice_parts0 = parts[0]
            file_slice_parts1 = parts[1]
            file_slice_parts2 = parts[2]
            file_slice_parts3 = int(parts[3])
            condition1 = (protocol_file['StationName'] == file_slice_parts0)
            condition2 = (protocol_file['SubSystemName'] == file_slice_parts1)
            condition3 = (protocol_file['DeviceTypeName'] == file_slice_parts2)
            condition4 = (protocol_file['DeviceNo'] == file_slice_parts3)
            combined_condition = condition1 & condition2 & condition3 & condition4
            protocol_slice = protocol_file[combined_condition]
            point_name = protocol_slice['PointName']

            if 'PLFK' in point_name.values:
                filename = 'state_history_' + file_slice.lower() + '_plfk.csv'
                key = filename
                value = name
                filename_dict[key] = value
            elif 'SSGL' in point_name.values:
                filename = 'state_history_' + file_slice.lower() + '_ssgl.csv'
                key = filename
                value = name
                filename_dict[key] = value
            elif 'YGGL' in point_name.values:
                filename = 'state_history_' + file_slice.lower() + '_yggl.csv'
                key = filename
                value = name
                filename_dict[key] = value
            elif 'GL' in point_name.values:
                filename = 'state_history_' + file_slice.lower() + '_gl.csv'
                key = filename
                value = name
                filename_dict[key] = value
            else:
                print(f"The element exists in not the column point_name")

        else:
            print(f"The element {name} was not found in the DataFrame")
    return filename_dict

'将上述生成的字典保存为 .txt 文件'
def save_filename_dict(filename_dict_path, filename_dict):
    # 打开文件并写入字典内容
    with open(filename_dict_path, 'w') as file:
        # 遍历字典的键值对并换行打印
        for key, value in filename_dict.items():
            line = f"{key}, {value}\n"
            file.write(line)

'将 .txt 重新读成字典'
def read_dict(filename_dict_path):
    dict = {} # 声明一个空字典，来保存文本文件数据
    file = open(filename_dict_path,'r') # 打开文本文件
    # 遍历文本文件的每一行，strip可以移除字符串头尾指定的字符（默认为空格或换行符）或字符序列
    for line in file.readlines():
        line = line.strip()
        k = line.split(' ')[0] #将每一行以空格为分隔符转换成列表
        v = line.split(' ')[1]
        dict[k] = v
    file.close() # 依旧是关闭文件
    return dict

'根据生成的字典(配置文件)，在每日新增的运行数据中筛选设备能耗计算所需的文件'
def get_data(origin_folder, destination_folder, filename_dict):
    filenames = []
    for key, value in filename_dict.items():
        filenames.append(key)
    for filename in filenames:
        # 拼接源文件路径
        source_file = os.path.join(origin_folder, filename)
        # 拼接目标文件路径
        destination_file = os.path.join(destination_folder, filename)
        try:
            # 复制文件
            shutil.copy2(source_file, destination_file)
            print(f"成功复制文件: {filename}")
        except FileNotFoundError:
            print(f"找不到文件: {filename}")
        except shutil.SameFileError:
            print(f"源文件和目标文件相同: {filename}")
        except Exception as e:
            print(f"复制文件时出错: {filename}，错误信息: {str(e)}")


if __name__ == '__main__':
    '注意：须统一车站点类表的格式'
    station_names = [
        '3_洪园站', '3_星桥站', '4_明石路', '6_公望街站', '6_昙花庵站', '8_仓北村站', '9_江河汇站',
    ]

    for i in range(len(station_names)):
        filename = station_names[i]
        name_path = fr'D:\Energy consumption calculation\energy file\{filename}_energy.xlsx'  # 设备名称文件
        device_path = fr'D:\Energy consumption calculation\data\2点类表\{filename}\cfg_view_device.csv'  # 点类表
        protocol_path = fr'D:\Energy consumption calculation\data\2点类表\{filename}\cfg_view_point_protocol.csv'  # 点类表
        filename_dict = extract(name_path, device_path, protocol_path)
        print(filename_dict)

        # 指定文件路径和文件名
        filename_dict_path = fr"D:\Energy consumption calculation\data\1能耗计算配置文件\{filename}.txt"
        save_filename_dict(filename_dict_path,  filename_dict)
    # dict = read_dict(filename_dict_path)
    # print(dict)

    # 原文件夹路径
    # origin_folder = r"D:\sql-data\每日数据\20230810\4号线\2_节能历史趋势文件\明石路\10.37.19.1_2023081000\exported_data_2023081000"
    # 目标文件夹路径
    # destination_folder = r"D:\Energy consumption calculation\data\明石路\0809"
    # get_data(origin_folder, destination_folder, filename_dict)
