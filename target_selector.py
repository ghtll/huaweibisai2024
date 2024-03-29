from model import *
import numpy as np
from globaldatas import *
import sys
#全局变量robot状态表。good坐标：()，berth坐标：(),状态：0闲置，1需要搜索good，2在去good路上，3需要搜索berth，4去berth路上
# berth id, good value
#target_table = np.zeros((10,8),dtype=int)

#新全局变量。(1-2)good坐标(x,y)(3)berth id
#(4)状态：0闲置，1需要搜索good，2在去good路上，3需要搜索berth，4去berth路上
#(5)good_value(6)初始位最开始是0表示用粗略估计，1表示正常（7）上次目标货物港口
target_table = np.zeros((10,7),dtype=int)
target_table[:,6] = -1

'''
0 空闲需要找目标
1 找到goods目标
2 去good目标的路上
3 到了good,需要搜索berth
4 前往berth
'''
# paths[2][(a,b)]
def robot2goods(goods,robots,berths,paths,now_frame,robot_to_init_goods,boat_capacity,berth_final):
    global target_table
    index_good_choosen = []
    if len(goods.available_goods) == 0:
        return []
    available_goods = np.array(goods.available_goods)
    #第一步计算出船厂与所有good的距离
    berth2good = np.zeros((10,len(goods.available_goods)),dtype=int)
    for index_berth,berth in enumerate(berths):
        for index_good in range(len(goods.available_goods)):
            berth2good[index_berth][index_good] = paths[index_berth][(goods.available_goods[index_good][0],goods.available_goods[index_good][1])]
    #当船厂号在最终不可达船厂号，设置为无限大
    
    
    ber2good_final = berth2good.copy()
    for i in range(10):
        if i in berth_final:
            ber2good_final[i,:] = 99999
    
    # if  now_frame>=13120 and  now_frame<=13128:
    #     print(berth_final,file=sys.stderr)  
    #     with open("debug.txt", "a") as file:  # 打开文件以追加模式写入
    #             file.write(f"ber2good_final:\n{ber2good_final}")
        # print("ber2good_final",ber2good_final,file=sys.stderr)


    #获得所有物品的死亡帧
    death_good = np.array(available_goods[:,3]) + 1000
    #获取所有物品价值
    good_value = np.array(available_goods[:,2])
    #获得good到其最近船厂的距离和对应船厂id
    good2berth_id = np.argmin(ber2good_final,axis=0)#1*n
    # print(good2berth_id,file=sys.stderr)
    good2berth_value = np.amin(ber2good_final,axis=0)#1*n

    # if  now_frame>=13120 and  now_frame<=13128:
    #     print("good2berth_value",good2berth_value,file=sys.stderr)  


    for index_robot,robot in enumerate(robots):
        #判断是否为初始机器人
        if target_table[index_robot][5] == 1:
            if target_table[index_robot][3] == 0 and robot.live and np.any(good2berth_value < 99999):
                #获取机器人所在的berth号

                berth_id = target_table[index_robot][2]
                robot2good = berth2good[berth_id]
                #确定机器人是否能拿到货物,不能拿到货的r2g距离设置成99999
                RobotArriveTime = robot2good + now_frame + 10
                CanNotReach = RobotArriveTime > death_good
                robot2good[CanNotReach] = 99999
                all_path_len = robot2good + good2berth_value 

                #当最后一轮时要考虑船厂死亡帧
                if now_frame > 12500:
                    for ind in range(10):
                        list_berths = np.where(good2berth_id == ind)[0]
                        if len(list_berths) > 0:
                            need_to_op = all_path_len[list_berths] + now_frame + 5
                            CanNotReach = need_to_op > berth_death[ind]
                            cannot = list_berths[CanNotReach]
                            all_path_len[cannot] = 99999

                m = np.divide(good_value, all_path_len)
                Choose_good_id = np.argmax(m)
                Choose_berth_id = good2berth_id[Choose_good_id]
                #如果选择的还是大，那么不选
                if robot2good[Choose_good_id]>=99999 or all_path_len[Choose_good_id]>=99999:
                    continue
                index_good_choosen.append(Choose_good_id)
                good2berth_value[Choose_good_id] = 99999
                target_table[index_robot][0] = available_goods[Choose_good_id][0]
                target_table[index_robot][1] = available_goods[Choose_good_id][1]
                target_table[index_robot][2] = Choose_berth_id
                target_table[index_robot][3] = 1
                target_table[index_robot][4] = available_goods[Choose_good_id][2]
                target_table[index_robot][6] = berth_id
        else:
            if target_table[index_robot][3] == 0 and robot.live and np.any(good2berth_value < 99999):
                
                # r_x = robot.x
                # r_y = robot.y
                # second_goods_x = available_goods[:,0]
                # second_goods_y = available_goods[:,1]
                # second_goods2robot = (abs(second_goods_x - r_x) + abs(second_goods_y - r_y))

                second_goods2robot=robot_to_init_goods[index_robot]
                # RobotArriveTime = second_goods2robot + now_frame + 10
                # CanNotReach = RobotArriveTime > death_good
                # second_goods2robot[CanNotReach] = 99999
                # print(second_goods2robot.shape,good2berth_value,file=sys.stderr)
                all_path_len = second_goods2robot + good2berth_value
                m = np.divide(good_value, all_path_len)
                Choose_good_id = np.argmax(m)

                #如果选择的还是大，那么不选
                if second_goods2robot[Choose_good_id]>=99999 or all_path_len[Choose_good_id]>=99999:
                    continue
                Choose_berth_id = good2berth_id[Choose_good_id]
                index_good_choosen.append(Choose_good_id)
                good2berth_value[Choose_good_id] = 99999
                target_table[index_robot][0] = available_goods[Choose_good_id][0]
                target_table[index_robot][1] = available_goods[Choose_good_id][1]
                target_table[index_robot][2] = Choose_berth_id
                target_table[index_robot][3] = 1
                target_table[index_robot][4] = available_goods[Choose_good_id][2]

    return index_good_choosen



# def robot2goods(goods,robots,berths,paths):#goods是物品全局变量，b2g是上面算出的船厂到物品的距离
#     global target_table
#     if len(goods.available_goods)==0:
#         return []
#     goods_npy = np.array(goods.available_goods)
#     #berth 到 物品的距离最后是一个5*10
#     b2g = []
#     index_good_choosen = []
#     goods_x = goods_npy[:,0]
#     goods_y = goods_npy[:,1]
#     for berth in berths:
#         x_t = goods_x-berth.x
#         y_t = goods_y-berth.y
#         b2g.append(abs(x_t)+abs(y_t))
#     b2g = np.vstack(b2g)
#     goods_value = goods_npy[:,2]
#     for index, robot in enumerate(robots):
#         if target_table[index][4] == 0 and np.any(b2g[0] != 80000):
#             x_t = goods_x-robot.x
#             y_t = goods_y-robot.y
#             r2g_dis = abs(x_t) + abs(y_t)
#             #获得good到berth的最小值
#             min_values = np.amin(b2g, axis=0)
#             # 找到每一列的最小值的索引,物品到其最小的船厂的index
#             min_indices_g2b = np.argmin(b2g, axis=0)
#             #这个其实就是robot到good和good到其最小berth的和
#             r2b_dis = r2g_dis + min_values
#             # 存储选择值value/dis
#             r2b = np.divide(goods_value,r2b_dis)
#             good_index = np.argmax(r2b)
#             berth_index = min_indices_g2b[good_index]
#             # 将选取过的物品到船厂距离设成无穷大
#             b2g[:,good_index] = 80000
#             index_good_choosen.append(good_index) # 这里需要给good
#             # 修改目标表
#             target_table[index][0] = goods_x[good_index]
#             target_table[index][1] = goods_y[good_index]
#             target_table[index][2] = berths[berth_index].x
#             target_table[index][3] = berths[berth_index].y
#             target_table[index][4] = 1
#             target_table[index][5] = berth_index
#             target_table[index][6] = goods.available_goods[good_index][2]
            
#     return index_good_choosen #每次计算完一次路径，调用allgoods类里的reset_av方法重新设置可选物品队列