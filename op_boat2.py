import numpy as np
from globaldatas import *
import sys
from util import *
#（1）目的berth id （2）状态 ：0闲置，1确定好船厂还没执行，2为在去船厂路上，3正在取货，4已经可以离开还没执行,5代表在去虚拟点路上。
#（3)轮次（4）转折次数 
target_table_boat_berth = np.zeros((5,4),dtype=int)
target_table_boat_berth[:,0] = -1

#全新改版将轮次设置为1-6000帧，6000-9000，9000-12000，12000-15000.后三阶段和以前相同，第一阶段随意装，直到装满

def update_BoatStatus(boats,berths,capacity,now_frame):
    global target_table_boat_berth
    global berth_final
    global berth_death
    global berth_death_num
    for index_boat in range(5):
        #（共用）
        if target_table_boat_berth[index_boat][1] == 5 and boats[index_boat].update_status():
            target_table_boat_berth[index_boat][1] = 0
            target_table_boat_berth[index_boat][3] = 0
            #第五轮直接设置为转移过一次了，不会再转了
            # if target_table_boat_berth[index_boat][2] == 4:
            #     target_table_boat_berth[index_boat][3] = 1
            boats[index_boat].idle()
        #第一轮6000帧以内，涉及到它只回去一次，也可能回去两次。不管如何6000帧必须在虚拟点，并且前期就是要么装满走人，如果转移的话考虑船内装没装够0.9cap，装够的话去虚拟点卖就行。只有前两轮用这个
        if now_frame < 12000 :
            if target_table_boat_berth[index_boat][1] == 0:
                    #选取目标
                    berth_index = -1
                    #第一轮就正常选
                    if target_table_boat_berth[index_boat][2] == 0:
                        berth_index = select_first_two_first(berths,now_frame)
                    #只有能选的berth才会执行
                    if berth_index != -1:
                        target_table_boat_berth[index_boat][0] = berth_index
                        target_table_boat_berth[index_boat][1] = 1
                        berths[berth_index].choosen = 1
                    #如果没选到直接啥也不干轮次+1
                    # else:
                    #     target_table_boat_berth[index_boat][2] += 1
                #确定是否到船厂
            if target_table_boat_berth[index_boat][1] == 2 and boats[index_boat].update_status():
                target_table_boat_berth[index_boat][1] = 3
            #装货状态判断
            if target_table_boat_berth[index_boat][1] == 3:
                index_berth = target_table_boat_berth[index_boat][0]
                #判断是否可以继续装货
                if len(berths[index_berth].GoodsOfBerth) > 0 and boats[index_boat].inventory < capacity:
                    boats[index_boat].load(berths[index_berth].unload(capacity - boats[index_boat].inventory))
                #不能继续装货有两种情况，第一种是港口空了，第二种是船满了
                else:
                    #先解锁
                    berths[index_berth].choosen = 0
                    #如果是装满了就直接回去
                    if boats[index_boat].inventory >= capacity:
                        target_table_boat_berth[index_boat][1] = 4
                    #没装满。
                    else:
                        #如果装够0.9个cap直接走人就行了
                        if boats[index_boat].inventory >= 0.9 * capacity:
                            target_table_boat_berth[index_boat][1] = 4
                        #如果没装够0.9
                        else:
                            berth_index = select_first_two_second(berths,capacity - boats[index_boat].inventory,now_frame)
                            if berth_index != -1:
                                target_table_boat_berth[index_boat][0] = berth_index
                                target_table_boat_berth[index_boat][1] = 1
                                berths[berth_index].choosen = 1
                                target_table_boat_berth[index_boat][3] += 1 
                if (12000 - now_frame) <= berths[index_berth].transport_time:
                    target_table_boat_berth[index_boat][1] = 4
                    #进入阶段2  
        # elif 6000 <= now_frame < 12000 and target_table_boat_berth[index_boat][2] < 4:
        #     if target_table_boat_berth[index_boat][1] == 0:
        #             #选取目标
        #             berth_index = -1
        #             #第三轮就正常选
        #             if target_table_boat_berth[index_boat][2] == 2:
        #                 berth_index = select(berths,capacity)
        #             #如果是第四轮要用下面的选
        #             elif target_table_boat_berth[index_boat][2] == 3:
        #                 berth_index = select_first_two_first(berths,now_frame,1)
        #             #只有能选的berth才会执行
        #             if berth_index != -1:
        #                 target_table_boat_berth[index_boat][0] = berth_index
        #                 target_table_boat_berth[index_boat][1] = 1
        #                 berths[berth_index].choosen = 1
        #             #如果没选到直接啥也不干轮次+1
        #             else:
        #                 target_table_boat_berth[index_boat][2] += 1
        #         #确定是否到船厂
        #     if target_table_boat_berth[index_boat][1] == 2 and boats[index_boat].update_status():
        #         target_table_boat_berth[index_boat][1] = 3
        #     #装货状态判断
        #     if target_table_boat_berth[index_boat][1] == 3:
        #         index_berth = target_table_boat_berth[index_boat][0]
        #         #判断是否可以继续装货
        #         if len(berths[index_berth].GoodsOfBerth) > 0 and boats[index_boat].inventory < capacity:
        #             boats[index_boat].load(berths[index_berth].unload(capacity - boats[index_boat].inventory))
        #         #不能继续装货有两种情况，第一种是港口空了，第二种是船满了
        #         else:
        #             #先解锁
        #             berths[index_berth].choosen = 0
        #             #如果是装满了就直接回去
        #             if boats[index_boat].inventory >= capacity:
        #                 target_table_boat_berth[index_boat][1] = 4
        #             #没装满。考虑两种情况，第一种是第一轮能转2次，第二种是第二轮只能转一次
        #             else:
        #                 #如果是第三轮
        #                 if target_table_boat_berth[index_boat][2] == 2:
        #                     #第三轮能转2次
        #                     if target_table_boat_berth[index_boat][3] < 2:
        #                         # #如果是第一轮装够0.9个cap直接走人就行了
        #                         # if boats[index_boat].inventory >= 0.9 * capacity:
        #                         #     target_table_boat_berth[index_boat][1] = 4
        #                         # #如果没装够0.9且没转够两次
        #                         # else:
        #                         berth_index = select_first_one(berths,capacity - boats[index_boat].inventory)
        #                         target_table_boat_berth[index_boat][0] = berth_index
        #                         target_table_boat_berth[index_boat][1] = 1
        #                         berths[berth_index].choosen = 1
        #                         target_table_boat_berth[index_boat][3] += 1
        #                      #如果转移过两次了，直接走人
        #                     else: 
        #                         target_table_boat_berth[index_boat][1] = 4  
        #                 #如果是第四轮只能转1次
        #                 elif target_table_boat_berth[index_boat][2] == 3:
        #                     berth_index = select_first_two_second(berths,capacity - boats[index_boat].inventory,now_frame,1)
        #                     if target_table_boat_berth[index_boat][3] == 0 and berth_index != -1:
        #                         target_table_boat_berth[index_boat][0] = berth_index
        #                         target_table_boat_berth[index_boat][1] = 1
        #                         berths[berth_index].choosen = 1
        #                         target_table_boat_berth[index_boat][3] = 1 
        #                     #第二轮装货状态6000帧必须到虚拟点
        #                     else:
        #                         if (12000 - now_frame) <= berths[index_berth].transport_time:
        #                             target_table_boat_berth[index_boat][1] = 4
        else:
            #全新改版
            if 12000 <= now_frame <= 12005 :
                if target_table_boat_berth[index_boat][1] == 0:
                #只有最后一轮直接定
                        berth_index = select(berths,capacity)
                        target_table_boat_berth[index_boat][0] = berth_index
                        target_table_boat_berth[index_boat][1] = 1
                        berths[berth_index].choosen = 1
                        target_table_boat_berth[index_boat][2] = 4
                        #最后一轮直接加时间
                        if target_table_boat_berth[index_boat][2] == 4:
                            l_time = len(berths[berth_index].GoodsOfBerth) / berths[berth_index].loading_speed
                            #这样可以
                            berth_death[berth_index] = now_frame + berths[berth_index].transport_time + l_time + 5
                            berth_death_num += 1
            #确定是否到船厂(共用)
            if target_table_boat_berth[index_boat][1] == 2 and boats[index_boat].update_status():
                target_table_boat_berth[index_boat][1] = 3
            #装货状态
            if target_table_boat_berth[index_boat][1] == 3:
                index_berth = target_table_boat_berth[index_boat][0]
                #判断是否可以继续装货
                if len(berths[index_berth].GoodsOfBerth) > 0 and boats[index_boat].inventory < capacity:
                    boats[index_boat].load(berths[index_berth].unload(capacity - boats[index_boat].inventory))
                else:
                    #先解锁
                    berths[index_berth].choosen = 0
                    #如果是倒数第二轮最后走的时候不解锁
                    # if target_table_boat_berth[index_boat][2] == 3 and target_table_boat_berth[index_boat][3] == 1:
                    #     berths[index_berth].choosen = 1
                    #如果是装满了就直接回去（实际不会出现）
                    if boats[index_boat].inventory >= capacity:
                        target_table_boat_berth[index_boat][1] = 4
                        if target_table_boat_berth[index_boat][2] == 4:
                            if len(berth_final) == 9:
                                berth_final.clear()
                                berth_death[:] = 99999
                               # print('清空',file=sys.stderr)
                            #最多为4因此应该小于9，这样最后加完应该为9
                            if len(berth_final) < 9:
                                berth_final.append(target_table_boat_berth[index_boat][0])
                            # None
                    else:#没装满考虑怎么走
                    #如果没装满并且没有转移过，找下家
                        if target_table_boat_berth[index_boat][3] == 0:
                            if target_table_boat_berth[index_boat][2] == 4:
                                berth_final.append(target_table_boat_berth[index_boat][0])
                                #print(f'frame:{now_frame},boat_id:{index_boat},left:{boats[index_boat].inventory},boat_table:\n{target_table_boat_berth}',file=sys.stderr)
                            berth_index = select_two(berths,capacity - boats[index_boat].inventory,now_frame)
                            target_table_boat_berth[index_boat][0] = berth_index
                            target_table_boat_berth[index_boat][1] = 1
                            berths[berth_index].choosen = 1
                            target_table_boat_berth[index_boat][3] = 1 
                            if target_table_boat_berth[index_boat][2] == 4:
                                #记录船厂被锁时间
                                berth_death[berth_index] = 15000 - berths[berth_index].transport_time
                                berth_death_num += 1
                                #==========
                                # b_left = capacity - boats[index_boat].inventory
                                # berth_left = len(berths[target_table_boat_berth[index_boat][0]].GoodsOfBerth)
                                # if berth_left >= b_left - 3:
                                #     t = b_left / berths[target_table_boat_berth[index_boat][0]].loading_speed
                                #     if (now_frame + t + 500) <  berth_death[target_table_boat_berth[index_boat][0]]:
                                #         berth_death[target_table_boat_berth[index_boat][0]] = now_frame + t + 500
                                #     print(f'更新berth_death:{berth_death}',file=sys.stderr)
                                # print(f'最后一轮boat_table:{target_table_boat_berth}',file=sys.stderr)
                                # for i in range(5):
                                #     print("boatid:{},left_num:{}".format(i,boats[i].inventory),file=sys.stderr)
                                # for i in range(10):
                                #     print("id:{},left_num:{}".format(i,len(berths[i].GoodsOfBerth)),file=sys.stderr)
                                #================
                                if berth_death_num == 10:
                                    # 找到不是 999 的值的下标
                                    indices = np.where(berth_death != 99999)[0]
                                    # 通过下标获取对应的值
                                    values = berth_death[indices]
                                    # 找到最大值的下标
                                    max_index = np.argmax(values)
                                    # 在原始矩阵中找到最大值的位置
                                    max_value_index = indices[max_index]
                                    berth_death[max_value_index] = 99999
                                
                        #如果转移过只有呆满才能走
                        else: 
                            if (3000 - (now_frame % 3000)) <= berths[index_berth].transport_time:
                                target_table_boat_berth[index_boat][1] = 4  
                                if target_table_boat_berth[index_boat][2] == 4:
                                    if len(berth_final) == 9:
                                        berth_final.clear()
                                        berth_death[:] = 99999
                                        #print('清空',file=sys.stderr)
                                    #最多为4因此应该小于9，这样最后加完应该为9
                                    if len(berth_final) < 9:
                                        berth_final.append(target_table_boat_berth[index_boat][0])
                                    # None                   
    return berths,boats
#第二轮第一次要考虑来回能不能回来。
def select_first_two_first(berths,now_frame):
    global target_table_boat_berth
    end_frame = 12000
    metric = np.zeros(10)
    for i in range(10):
        if berths[i].choosen == 1:
            metric[i] = -1
        else:
            load_time = len(berths[i].GoodsOfBerth) / berths[i].loading_speed
            time_left = end_frame - 2 * berths[i].transport_time - now_frame - load_time
            if time_left < 0:
                metric[i] = -1
            else:
                value_goods = sum(berths[i].GoodsOfBerth)
                metric[i] = value_goods 
    choosen_berth = np.argmax(metric)
    if metric[choosen_berth] == -1:
        return -1
    return choosen_berth
#第2轮第二次需要考虑6000帧能不能回去
def select_first_two_second(berths,boat_v_left,now_frame):
    global target_table_boat_berth
    end_frame = 12000
    metric = np.zeros(10)
    for i in range(10):
        if berths[i].choosen == 1:
            metric[i] = -1
        else:
            time_of_you = end_frame - 500 - now_frame  - berths[i].transport_time
            if time_of_you <= 0:
                metric[i] = -1
            else:
                load_goods = time_of_you * berths[i].loading_speed
                len_goods = min(len(berths[i].GoodsOfBerth),load_goods,boat_v_left)
                value_goods = sum(berths[i].GoodsOfBerth[:len_goods])
                metric[i] = value_goods 
    choosen_berth = np.argmax(metric)
    if metric[choosen_berth] == -1:
        return -1
    return choosen_berth
#第1轮一直装，反正就是
def select_first_one(berths,boat_v_left):
    global target_table_boat_berth
    metric = np.zeros(10)
    for i in range(10):
        if berths[i].choosen == 1:
            metric[i] = -1
        else:
            len_goods = min(len(berths[i].GoodsOfBerth),boat_v_left)
            value_goods = sum(berths[i].GoodsOfBerth[:len_goods])
            metric[i] = value_goods 
    choosen_berth = np.argmax(metric)
    return choosen_berth

def select(berths,cap):
    global target_table_boat_berth
    metric = np.zeros(10)
    for i in range(10):
        if berths[i].choosen == 1:
            metric[i] = -1
        else:
            len_goods = min(len(berths[i].GoodsOfBerth),cap)
            value_goods = sum(berths[i].GoodsOfBerth[:len_goods])
            load_time = len_goods / berths[i].loading_speed
            metric[i] = value_goods / (load_time + berths[i].transport_time)
    choosen_berth = np.argmax(metric)
    return choosen_berth

# def select_two(berths,cap,boat_v,now_frame):
#     global target_table_boat_berth
#     metric = np.zeros(10)
#     for i in range(10):
#         if berths[i].choosen == 1:
#             metric[i] = -1
#         else:
#             len_goods = min(len(berths[i].GoodsOfBerth),cap-boat_v)
#             value_goods = sum(berths[i].GoodsOfBerth[:len_goods])
#             load_time = len_goods / berths[i].loading_speed
#             metric[i] = value_goods / (500 + load_time + berths[i].transport_time)
#     for i in range(10):
#         if berths[i].transport_time >= 2500 - (now_frame % 3000):
#             metric[i] = -1
#     choosen_berth = np.argmax(metric)
#     return choosen_berth\

#既然最后一定回去，那么第二轮选择就没必要考虑时间因素了
def select_two(berths,boat_v_left,now_frame):
    global target_table_boat_berth
    metric = np.zeros(10)
    for i in range(10):
        if berths[i].choosen == 1:
            metric[i] = -1
        else:
            time_of_you = 2500 - (now_frame % 3000) - berths[i].transport_time
            if time_of_you <= 0:
                metric[i] = -1
            else:
                load_goods = time_of_you * berths[i].loading_speed
                len_goods = min(len(berths[i].GoodsOfBerth),load_goods,boat_v_left)
                value_goods = sum(berths[i].GoodsOfBerth[:len_goods])
                metric[i] = value_goods 
    choosen_berth = np.argmax(metric)
    return choosen_berth

