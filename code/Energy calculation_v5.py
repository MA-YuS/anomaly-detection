import os
import glob
import numpy as np
import pandas as pd

#%%
def read_path_plfk(path, ):
    file = glob.glob(os.path.join(path, "*.csv"))  # 文件列表
    file.sort()
    return file
#%%
def err_function(x):
    if x==0:
        err_formula = 0
    elif x < 30:
        err_formula = 1.18
    elif x >= 30 and x <= 45:
        err_formula = 1.1
    else:
        err_formula = 1
    return err_formula

#%%
def cal_plfk(dic, name_path):
    energy_file = pd.read_excel(name_path, index_col=0) #读取设备能耗文件
    names = []  #设备名称
    energyss = [] #设备能耗
    timess = [] #设备运行时间
    rated_powers = [] #设备额定功率
    r_power_energys = [] #设备额定功率能耗

    for file in file_plfk:
        print(file)
        key = os.path.basename(file)#只读文件名称，即配置文件的key
        print(key)
        print(type(key))
        name = dic[key]#读取设备名称，即配置文件的values

        name_prefix = os.path.splitext(key)[0][-4:]
        if name_prefix == 'plfk':
            sbcs = energy_file.loc[name]#读取该设备列的参数，如25hz系数等
            rated_power = sbcs['额定功率']
            hz_25 = sbcs['25Hz系数']
            hz_30 = sbcs['30Hz系数']
            hz_40 = sbcs['40Hz系数']
            hz_50 = sbcs['50Hz系数']
            x = np.array([25, 30, 40, 50]) #以频率为x
            y_hz = np.array([hz_25, hz_30, hz_40, hz_50]) #以频率系数为y_hz
            hz_formula = np.polyfit(x, y_hz, 3) # 拟合出的频率系数公式

            data = pd.read_csv(file, parse_dates=['ts']) # 待转换为**datetime64[ns]**格式的列→col1
            value = data.iloc[:, 1:2].values
            energys = 0
            times = 0
            for i in range(len(value)):
                if i < len(value)-1:
                    starttime = data.iloc[i, 0]
                    endtime = data.iloc[i+1, 0]
                    time_interval = (endtime - starttime).total_seconds()
                    hz_num_i = hz_formula[0] * value[i] ** 3 + hz_formula[1] * value[i] ** 2 + hz_formula[2] * value[i] + hz_formula[3]
                    hz_num_i1 = hz_formula[0] * value[i+1] ** 3 + hz_formula[1] * value[i+1] ** 2 + hz_formula[2] * value[i+1] + hz_formula[3]
                    err_num_i = err_function(value[i])
                    err_num_i1 = err_function(value[i + 1])
                    value_i = rated_power * hz_num_i * err_num_i #功率预估
                    value_i1 = rated_power * hz_num_i1 * err_num_i1 #功率预估
                    energy = time_interval / 3600 * (value_i + value_i1) /2
                    energys = energys + energy
                    if (value[i] !=0) & (value[i+1] !=0):
                        times = times+time_interval / 3600

                elif i == len(value):
                    starttime = data.iloc[i-1, 0]
                    endtime = data.iloc[i, 0]
                    time_interval = (endtime - starttime).total_seconds()
                    hz_num_i = hz_formula[0] * value[i-1] ** 3 + hz_formula[1] * value[i-1] ** 2 + hz_formula[2] * value[i-1] + hz_formula[3]
                    hz_num_i1 = hz_formula[0] * value[i] ** 3 + hz_formula[1] * value[i] ** 2 + hz_formula[2] * value[i] + hz_formula[3]
                    err_num_i = err_function(value[i-1])
                    err_num_i1 = err_function(value[i])
                    value_i = rated_power * hz_num_i * err_num_i  # 功率预估
                    value_i1 = rated_power * hz_num_i1 * err_num_i1  # 功率预估
                    energy = time_interval / 3600 * (value_i + value_i1) / 2
                    energys = energys + energy
            # r_power_energy = rated_power * times
        else:
            sbcs = energy_file.loc[name]#读取该设备列的参数，如25hz系数等
            rated_power = sbcs['额定功率']
            data = pd.read_csv(file, parse_dates=['ts'])  # 待转换为**datetime64[ns]**格式的列→col1
            value = data.iloc[:, 1:2].values
            energys = 0
            times = 0
            for i in range(len(value)):
                if i < len(value) - 1:
                    starttime = data.iloc[i, 0]
                    endtime = data.iloc[i + 1, 0]
                    time_interval = (endtime - starttime).total_seconds()
                    value_i = value[i]  # 实时功率
                    value_i1 = value[i+1]  # 实时功率
                    energy = time_interval / 3600 * (value_i + value_i1) / 2
                    energys = energys + energy
                    if (value[i] != 0) & (value[i + 1] != 0):
                        times = times + time_interval / 3600

                elif i == len(value):
                    starttime = data.iloc[i - 1, 0]
                    endtime = data.iloc[i, 0]
                    time_interval = (endtime - starttime).total_seconds()
                    value_i = value[i-1]  # 实时功率
                    value_i1 = value[i]  # 实时功率
                    energy = time_interval / 3600 * (value_i + value_i1) / 2
                    energys = energys + energy
        r_power_energy = rated_power * times

        energyss.extend(energys)
        names.append(name)
        timess.append(times)
        rated_powers.append(rated_power)
        r_power_energys.append(r_power_energy)
        print(' %s 运行时间 %.2f 小时' %(name, times))

    return names,energyss, timess, rated_powers, r_power_energys


'将 .txt 重新读成字典'
def read_dict(filename_dict_path):
    dict = {} # 声明一个空字典，来保存文本文件数据
    file = open(filename_dict_path,'r') # 打开文本文件
    # 遍历文本文件的每一行，strip可以移除字符串头尾指定的字符（默认为空格或换行符）或字符序列
    for line in file.readlines():
        line = line.strip()
        k = line.split(',')[0] #将每一行以空格为分隔符转换成列表
        v = line.split(' ')[1]
        dict[k] = v
    file.close() # 依旧是关闭文件
    return dict


def output_file(names, energyss, timess, rated_powers, r_power_energys, filename, date):
    names = pd.DataFrame(names, columns=['设备名称'])
    energyss = pd.DataFrame(energyss, columns=['设备能耗'])
    timess = pd.DataFrame(timess, columns=['设备运行时间'])
    rated_powers = pd.DataFrame(rated_powers, columns=['额定功率'])
    r_power_energys = pd.DataFrame(r_power_energys, columns=['额定功率能耗'])
    energy_file = pd.concat([names, energyss, timess, rated_powers, r_power_energys], axis=1)
    print(energy_file)
    energy_file.to_excel(fr'D:\Energy consumption calculation\energy calculation\{filename}\{filename}设备能耗{date}.xlsx', index = False,)


if __name__ == '__main__':
    '注意：车站名称的顺序 和 数据文件路径的顺序 必须严格一致 一一对应'
    date = '0810'
    station_names = [
        '3_洪园站', '3_星桥站', '4_明石路', '6_公望街站', '6_昙花庵站', '8_仓北村站', '9_江河汇站',
    ]

    for i in range(len(station_names)):
        filename = station_names[i]
        path_plfk = fr'D:\Energy consumption calculation\data\{filename}\{date}'  # 各设备频率文件
        file_plfk = read_path_plfk(path_plfk)

        filename_dict_path = fr'D:\Energy consumption calculation\data\1能耗计算配置文件\{filename}.txt'
        dic = read_dict(filename_dict_path)

        name_path = fr'D:\Energy consumption calculation\energy file\{filename}_energy.xlsx'  # 设备名称文件
        names, energys, times, rated_powers, r_power_energys = cal_plfk(dic, name_path)

        output_file(names, energys, times, rated_powers, r_power_energys, filename, date)
        print(times)
