#针对channel命名正确的tdms文件
import time
import os
import re
import struct 
import numpy as np
from nptdms import TdmsFile
import shutil

def process_tdms_files(input_path, output_path):
    # 获取当前文件夹下的所有TDMS文件
    #files = [f for f in os.listdir(input_path) if f.startswith("记录") and f.endswith(".tdms")]
    #files = [f for f in os.listdir(input_path) if f.endswith(".tdms")]
    #files = [f for f in os.listdir(input_path) if f.endswith(".tdms") and "112037" in f]
    #files = [f for f in os.listdir(input_path) if f.endswith(".tdms") and "170604" in f ] 
    #files = [f for f in os.listdir(input_path) if f.endswith(".tdms") and "12-08" in f ] 
    files = [f for f in os.listdir(input_path) if f.endswith(".tdms") and "04-2" in f ]

    for file in files:
        fname = os.path.join(input_path, file)
        #设置文件大小至少为1GB大小
        #if os.path.getsize(fname) < 0.8 * 1024 * 1024 * 1024 or os.path.getsize(fname) > 6 * 1024 * 1024 * 1024:  # 1GB = 1 * 1024^3 bytes
        #if os.path.getsize(fname) > 80 * 1024 * 1024 or os.path.getsize(fname) < 70 * 1024 * 1024:  # 1GB = 1 * 1024^3 bytes
        #if os.path.getsize(fname) > 80 * 1024 * 1024 or os.path.getsize(fname) < 70 * 1024 * 1024:  # 1GB = 1 * 1024^3 bytes
        if os.path.getsize(fname) < 2* 1024 * 1024 * 1024 :  # 1GB = 1 * 1024^3 bytes
            continue 

        # 读取TDMS文件
        print(f"Processing file: {fname}")
        start = time.process_time()
        tdms_file = TdmsFile.read(fname)
        end = time.process_time()
        print(f'Time to read the file: {end - start} Seconds')

        # 获取所有group并处理group[1]
        all_groups = tdms_file.groups()
        if len(all_groups) > 1:
            print("Original TDMS file from NI.")  # 输出错误消息
            group_name = all_groups[1].name
            all_group_channels = all_groups[1].channels()
        else:
            #raise ValueError("TDMS file contains less than 2 groups.")
            print("Converted TDMS file.")  # 输出错误消息
            #continue
            group_name = all_groups[0].name
            all_group_channels = all_groups[0].channels()

        
        # 在指定路径2下创建以group名字命名的文件夹
        #group_output_name =extract_and_format(fname) 
        #group_output_name = os.path.splitext(file)[0]
        #group_name = os.path.splitext(file)[0]
        group_output_name = f"{group_name}"
        group_output_dir = os.path.join(output_path, group_output_name)
        os.makedirs(group_output_dir, exist_ok=True)

        # 处理group[1]下的所有channel
        for channel in all_group_channels:
            channel_name = channel.name
            data = channel[:]
            
            # 创建新文件，使用channel名字命名
            channel_folder = os.path.join(group_output_dir, channel_name)
            os.makedirs(channel_folder, exist_ok=True)
            output_file_path = os.path.join(channel_folder, f"{channel_name}.bin")
            trans(output_file_path,data)

def trans(binfile,bindata):
	print(f"Creating file: {binfile}")
	with open(binfile, 'wb') as fileBIN2:
        #add header
        # 写入第一个 32 位整数 (0x00006C20
		fileBIN2.write(struct.pack('<I', 0x00006C20))
        # 写入第二个 32 位浮点数 (采样频率: 5000.0 Hz)
		fileBIN2.write(struct.pack('<f', 5000.0))
        # 写入第三个 32 位浮点数 (ADC 全范围: 20.0 V)
		fileBIN2.write(struct.pack('<f', 20.0))            
		tot_num = len(bindata) // 20000
		for num in range(tot_num):
			if num % 100 == 0:
				print(f"Processing chunk {100*num / tot_num:2f}%")
            # 转换为指定格式
            #converted_data = ((bindata[20000 * num:20000 * (num + 1)] + 10.0) * (2**15) / 5).astype(np.dtype('<u4'))
            #converted_data = ((bindata[20000 * num:20000 * (num + 1)] + 10.0) * (2**24) / 20).astype(np.dtype('<u4'))
			converted_data = ((bindata[20000 * num:20000 * (num + 1)] + 10.0) * (2**32-1) / 20.0).astype(np.dtype('<u4'))
			fileBIN2.write(converted_data.tobytes())
	print(f"Finished processing file: {binfile}")	


# 设置路径1和路径2
# 路径1，包含TDMS文件的目录（只在当前目录查找）
#input_path = "/mnt/d/RUNs/RUN2410/Background2410/NI Project Data"F
#input_path = "/mnt/d/RUNs/RUN2410/BKG_RUN2410_2_2/未命名项目/NI Project Data"
input_path = "/mnt/d/RUNs/RUN2504/TEST/未命名项目/NI Project Data"
#input_path = "/mnt/d/RUNs/RUN2410/LC2410_2_2/WP_selection/NI Project Data"
#input_path = "/mnt/e/RUNs_data_analysis/RUN2408/Converted_Data/tdms" 
#input_path = "/mnt/d/RUNs/RUN2408/bkgdata240820/bkg240820/Assets/NI Project Data"
# 路径2，生成文件所在的目录
#output_path = "/mnt/d/RUNs_data_analysis/Heater3"
output_path = "/mnt/d/RUNs_data_analysis/TEMP"
#output_path = './analysis/001'
#output_path = "/home/shihongfu/data/RUNs_data_analysis/RUN2410/Converted_Data"
#output_path = "/home/shihongfu/data/RUNs_data_analysis/RUN2408/Converted_Data"

# 调用函数处理TDMS文件
process_tdms_files(input_path, output_path)
