from numpy import *
import numpy as np
import csv
import matplotlib as mpl
import matplotlib.pyplot as plt
from sklearn.decomposition import NMF
from sklearn.cluster import KMeans
from mpl_toolkits.mplot3d import Axes3D
from geopy.distance import geodesic
import random
from math import *
from matplotlib import style

def load_data(path):
    data = []
    with open(path) as csvfile:
        csv_reader = csv.reader(csvfile)  # 使用csv.reader读取csvfile中的文件
        i = 0
        for row in csv_reader:  # 将csv 文件中的数据保存到data中
            data.append(row)
            # i += 1
            # if i == 10000:
            #     break

    data = [[int(x) for x in row] for row in data]  # 将数据从string形式转换为float形式

    data = np.array(data)  # 将list数组转化成array数组便于查看数据结构
    # data = data.transpose()
    print(data.shape)  # 利用.shape查看结构。

    return data

def initiate(data, r):
    row_num = data.shape[0]
    col_num = data.shape[1]
    W = mat(np.random.rand(row_num, r))
    H = mat(np.random.rand(r, col_num))
    # W = mat(ones((row_num, r)))
    # H = mat(ones((r, col_num)))
    return W, H

def iterate(V, W, H, r):
    row_num = V.shape[0]
    col_num = V.shape[1]
    first_numerator = W.transpose()*V
    first_denominator = W.transpose()*W*H
    for i in range(0, r):
        for j in range(0, col_num):
            H[i, j] = H[i, j] * first_numerator[i, j] / first_denominator[i, j]

    second_numerator = V*H.transpose()
    second_denominator=W*H*H.transpose()
    for i in range(0, row_num):
        for j in range(0, r):
            if second_denominator[i, j] != 0:
                W[i, j] = W[i, j] * second_numerator[i, j] / second_denominator[i, j]
            else:
                W[i, j] = W[i, j] * second_numerator[i, j] / 0.000000001
    return W, H

def judge(V,W,H, previous):
    Error = V - W * H
    MSE = 0
    row_num = V.shape[0]
    col_num = V.shape[1]
    for i in range(0, row_num):
        for j in range(0, col_num):
           MSE += pow(Error[i, j], 2)
    RMSE = sqrt(MSE)
    rate = (RMSE - previous) / previous
    print(RMSE, previous, rate)

    if rate < 0.001 and -0.001 < rate:
        return True, RMSE
    return False, RMSE

def read():
    W = np.load("20111128_W.npy")
    H = np.load("20111128_H.npy")
    return W, H

def print_file(W, H):
    np.save("20111128_W.npy", W)
    np.save("20111128_H.npy", H)

def graph(H, r):
    x = []
    i = 0
    while i < 24:
        x.append(i)
        i += 0.25
    i = 0
    # 循环写法
    # while i < r:
    #     y = []
    #     j = 0
    #     while j < 96:
    #         y.append(float(H[i, j]))
    #         j += 1
    #     plt.plot(x, y)
    #     plt.grid(True)  ##增加格点
    #     i += 1
    y1 = [float(H[0, j]) for j in range(0, 96)]
    y2 = [float(H[1, j]) for j in range(0, 96)]
    y3 = [float(H[2, j]) for j in range(0, 96)]
    plt.plot
    plt.plot(x, y1, color = "blue", label = "r1")
    plt.plot(x, y2, color = "red", label = "r2")
    plt.plot(x, y3, color = "green", label = "r3")
    plt.grid(True)

    plt.show()





def center_point(num, luduan, longi_lati):
    point_temp_1 = luduan[num][0]
    point_temp_2 = luduan[num][1]

    flag1 = 0
    flag2 = 0
    for i in longi_lati:
        if i[0] == point_temp_1:
            lon1 = i[1]
            lat1 = i[2]
            flag1 = 1
        elif i[0] == point_temp_2:
            lon2 = i[1]
            lat2 = i[2]
            flag2 = 1
        elif flag1 == 1 and flag2 == 1:
            break
    lon = (lon1+lon2) * math.pi / 360
    lat = (lat1+lat2) * math.pi / 360
    return lon, lat




def distance_physics(num1, num2, longi_lati, luduan):
    (lon1, lat1) = center_point(num1, luduan, longi_lati)
    (lon2, lat2) = center_point(num2, luduan, longi_lati)

    dis_phy = geodesic((lon1, lat1), (lon2, lat2)).km

    return dis_phy



def distance_logistics(num1, num2, W):
    # 对于9个的大W
    dis_log = 0
    for i in range(0, 9):
        temp = (W[num1][0]-W[num2][0])**2 + (W[num1][1]-W[num2][1])**2 + (W[num1][2]-W[num2][2])**2
        dis_log += temp
        num1 += 127049
        num2 += 127049
    dis_log = sqrt(dis_log)
    return dis_log


def distance(num1, num2, longi_lati, luduan, W, alpha = 0.1, tau = 1):
    dis_phy = distance_physics(num1, num2, longi_lati, luduan)
    dis_log = distance_logistics(num1, num2, W)
    dis = alpha * dis_phy + (1-alpha) * dis_log / tau

    return dis



def k_center(W, k):
    row_num = 127049
    center = []
    cluster = []
    for i in range(0, k):
        n = random.randint(0, row_num)
        center.append(n)
        cluster.append([n])

    times = 0
    while True:
        (center, old_cluster) = k_center_interate(W, k, center, cluster)
        if center == 0 or times == 200:
            break
        cluster = []
        for i in range(0, k):
            cluster.append([center[i]])
        times += 1
        print(times)
        print(cluster)


    result_y = [0 for i in W]
    for i in range(0, k):
        for j in range(0, len(old_cluster[i])):
            result_y[old_cluster[i][j]] = i

    result = np.array(result_y)
    np.save("k_center_cluster.npy")
    np.save("k_center_result_y.npy")


    return cluster, result_y




def k_center_interate(W, k, center, cluster):
    row_num = 127049
    new_dist = [0 for i in range(0, 127049)]
    longi_lati = np.load("longi_lati.npy")
    luduan = np.load("totoal_9_luduan.npy")

    for i in range(0, row_num):
        print(i)
        d = []
        if i not in center:
            for j in range(0, k):
                d.append(distance(i, center[j], longi_lati, luduan, W))

            num = d.index(min(d))
            # print(num)
            for g in cluster[num]:
                new_dist[g] += distance(i, g, longi_lati, luduan, W)
                new_dist[i] += distance(i, g, longi_lati, luduan, W)
            cluster[num].append(i)
            # print(cluster)
        else:
            continue

    new_center = []
    for i in range(0, k):
        min_dis = float("inf")
        pos = -1
        # print("第", i, "个簇")
        for j in cluster[i]:
            if new_dist[j] < min_dis:
                # print(new_dist[j])
                min_dis = new_dist[j]
                pos = j
        new_center.append(pos)

    for i in center:
        if i not in new_center:
            return new_center, cluster

    return 0, cluster


def paint_k_center(ypred, W):

    y_class = array(ypred)
    ax = plt.subplot(111, projection='3d')
    x_array = np.array(W, dtype=float)
    y_array = np.array(y_class, dtype=int)
    a = x_array[np.where(y_array == 0)]
    b = x_array[np.where(y_array == 1)]
    c = x_array[np.where(y_array == 2)]
    ax.scatter(a[:, 0], a[:, 1], a[:, 2], c='r', label='a')
    ax.scatter(b[:, 0], b[:, 1], b[:, 2], c='b', label='b')
    ax.scatter(c[:, 0], c[:, 1], c[:, 2], c='g', label='c')
    ax.set_zlabel('Z')  # 坐标轴
    ax.set_ylabel('Y')
    ax.set_xlabel('X')
    plt.legend(loc='upper left')
    ax.view_init(35, 300)
    plt.show()










if __name__ == '__main__':
    r = 3
    style.use('fivethirtyeight')

    # path = "data_csv/20111128_REAL.csv"
    # V = load_data(path)
    # i = 0
    # previous = 0.00001
    # (W, H) = initiate(V, r)
    # while True:
    #     (W, H) = iterate(V, W, H, r)
    #     (bool, previous) = judge(V, W, H, previous)
    #     i += 1
    #     print(i)
    #     if i == 1000 or bool:
    #         break
    # print("W___________")
    # print(W)
    # print("H____________")
    # print(H)
    # print_file(W, H)
    #
    #
    # (W, H) = read()

    # W = np.load("20111128_W.npy")
    # H = np.load("20111128_H.npy")

    W = np.load("totoal_9_data.npy")

    # graph(H, r)

    k = 3

    (cluster, result_y) = k_center(W, k)
    print(cluster)
    print(result_y)
    paint_k_center(result_y, W)



