import matplotlib.pyplot as plt
import numpy as np
import csv

Time_Unit = 1 #ns
Sim_Time = 300 #s
output_dir = "./output/QoS_viz/"
Delay_dir = "../test_data/end_to_end/run/logs_ns3/burst_0_qos/burst_0_delay.csv"
Jitter_dir = "../test_data/end_to_end/run/logs_ns3/burst_0_qos/burst_0_delayJitter.csv"
PacketLoss_dir = "../test_data/end_to_end/run/logs_ns3/burst_0_qos/burst_0_packetLoss.csv"
def read_path_file():
    """
    read end-to-end path from specific  csv file
    return time array and path array
    """
    delayData = [list() for i in range(2)]
    jitterData = [list() for i in range(2)]
    packetLossData = [[0],[0]]
    with open(Delay_dir) as csvFile:
        csv_reader = csv.reader(csvFile)  # 使用csv.reader读取csvfile中的文件
        for row in csv_reader:            # 将csv 文件中的数据保存到data中
            # print(row[1])
            delayData[0].append(eval(row[1])*Time_Unit/1000000000)
            delayData[1].append(eval(row[2])*Time_Unit/1000000)
    
    with open(Jitter_dir) as csvFile:
        csv_reader = csv.reader(csvFile)  # 使用csv.reader读取csvfile中的文件
        for row in csv_reader:            # 将csv 文件中的数据保存到data中
            # print(row[1])
            jitterData[0].append(eval(row[1])*Time_Unit/1000000000)
            jitterData[1].append(eval(row[2])*Time_Unit/1000000)
    
    with open(PacketLoss_dir) as csvFile:
        csv_reader = csv.reader(csvFile)  # 使用csv.reader读取csvfile中的文件
        for row in csv_reader:            # 将csv 文件中的数据保存到data中
            # print(row[1])
            packetLossData[0].append(eval(row[2])*Time_Unit/1000000000)
            packetLossData[1].append(packetLossData[1][-1]+1)
    
    return delayData, jitterData, packetLossData

        
#画图 
delayData, jitterData, packetLossData = read_path_file()
plt.figure()
plt.plot(delayData[0], delayData[1], 'b*--', alpha=0.5, linewidth=1, label='Path Delay')#'
plt.xlabel('time/s')
plt.ylabel('time/ms')
xMax = int(max(delayData[0])*1.2)
yMax = int(int(max(delayData[1])*1.2))
x = range(xMax)
y = range(yMax)
plt.xticks(x[::int(xMax/10)])
plt.yticks(y[::int(yMax/10)])
plt.title('Delay of path from Shanghai to LosAngeles')
plt.savefig(output_dir+"fig1_Delay of path from Shanghai to LosAngeles", dpi=200)

plt.figure()
plt.plot(packetLossData[0], packetLossData[1], 'rs--', alpha=0.5, linewidth=1, label='Packet Loss')
plt.xlabel('time/s')
plt.ylabel('packets')
xMax = int(max(delayData[0])*1.2)
x = range(xMax)
plt.xticks(x[::50])
plt.title('Packet loss of traffic from Shanghai to LosAngeles')
plt.savefig(output_dir+"fig2_Packet loss of traffic from Shanghai to LosAngeles", dpi=200)

plt.figure()
plt.plot(jitterData[0], jitterData[1], 'go--', alpha=0.5, linewidth=1, label='Path Delay Jitter')
plt.xlabel('time/s')
plt.ylabel('time/ms')
yMax = int(max(delayData[1])*1.2)
y = range(yMax)
# plt.ylim(-20000,+10000)
plt.title('Delay jitter of path from Shanghai to LosAngeles')
plt.savefig(output_dir+"fig3_Delay jitter of path from Shanghai to LosAngeles", dpi=200)

 
#plt.ylim(-1,1)#仅设置y轴坐标范围
plt.show()
