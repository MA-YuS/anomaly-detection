'''
    程序说明：
            这一版本还是需要
            手动筛选每次要计算的车站名字
            手动改写当日数据文件的文件夹路径

            下一版本需优化改进上述两个问题

            这一版本解决了上述两个问题
            但还是需要每天改 middle_path
            若想实现所有车站全部的批量计算，就需要生成所有车站的设备配置文件
'''
import shutil
import os

import pandas as pd


def read_filenames(station_names, ):
    for i in range(len(station_names)):
        filename = station_names[i]
        names_folder = fr'D:\Energy consumption calculation\data\0各站设备文件名称\{filename}.txt'

        filenames = []  # 声明一个空列表，来保存文本文件数据
        file = open(names_folder, 'r')  # 打开文本文件
        # 遍历文本文件的每一行，strip可以移除字符串头尾指定的字符（默认为空格或换行符）或字符序列
        for line in file.readlines():
            line = line.strip()
            filename = line.split(' ')[0]  # 将每一行以空格为分隔符转换成列表
            filenames.append(filename)
        file.close()  # 依旧是关闭文件
        print(filenames)
    return filenames

def batch_copy_files(filenames, origin_folder, destination_folder):
    # 检查文件夹是否存在
    if not os.path.exists(destination_folder):
        # 不存在则创建文件夹
        os.makedirs(destination_folder)
        print("文件夹已成功创建！")
    else:
        print("文件夹已存在！")

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
    data_date = '20230815'
    real_date = '0814'
    data_message = pd.read_excel(r'D:\Energy consumption calculation\data\典型站车站数据信息.xlsx')
    for i in range(len(data_message)):
        metro_lines = data_message['线路编号'][i]
        station_name = data_message['车站名称'][i]
        filename = f'{metro_lines}_{station_name}'
        station_ip = data_message['综合监控服务器IP1'][i]
        middle_path = data_message['路径中间名'][i]

        print('-----------------------------------------------------------------------------------')
        print(f'----------------------------{filename}----------------------------------')
        filenames = []  # 声明一个空列表，来保存文本文件数据
        names_folder = fr'D:\Energy consumption calculation\data\1能耗计算配置文件\重命名\{filename}.txt'
        file = open(names_folder, 'r')  # 打开文本文件
        # 遍历文本文件的每一行，strip可以移除字符串头尾指定的字符（默认为空格或换行符）或字符序列
        for line in file.readlines():
            line = line.strip()
            name = line.split(',')[0]  # 将每一行以空格为分隔符转换成列表
            filenames.append(name)
        file.close()  # 依旧是关闭文件

        origin_folder = fr'D:\sql-data\每日数据\{data_date}\{middle_path}\export_data_{data_date}00\{station_ip}_{data_date}00\exported_data_{data_date}00'
        destination_folder = fr"D:\Energy consumption calculation\data\{filename}\{real_date}"
        batch_copy_files(filenames, origin_folder, destination_folder)





