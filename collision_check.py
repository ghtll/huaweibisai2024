#问题简化成了对于两个相邻距离为1的机器人，如何防止两个机器人碰撞；
#继续简化，如果两个机器人第i步可能会发生冲突，如果对方的位置没有出现在第i+1步中，我认为可以让一个机器人等待，另一个机器人前往，这样用一个指令时间去等待；
#如果

# map1 24 178699 169445 171249 85536 122728
# map2 21 169120 168811 158088 153165 159051
# map3 23
# map4 17
# map5 25
# map6 29 31
# map7 25 26
# map8 25 26
import numpy as np
from model import *
from util import *
import random
import time
import itertools
direction = [[1,0],[0,1],[-1,0],[0,-1]]
direction_flag = [0] * 10


def detect_collision_1(paths , robots , track_index, connected_points , connected_locks):
    
    bot_num = 10
    collision_flag = True
    reback_status = [0] * 10
    now_position = set()
    robot_next_pos = [] # 存储机器人的位置信息
    robot_flag = [0] * 10 # 标记机器人下一个执行位置是否合法
    robot_next_pos_1 = set()
    waits = [[] for _ in range(10)]
    # nums = []

    #初始化robot_pos
    for index in range(bot_num):
        now_position.add(Node(robots[index].x , robots[index].y))
        if track_index[index] < len(paths[index]) and isinstance(paths[index][track_index[index]] , tuple) and len(paths[index][track_index[index]]) > 1:
            robot_flag[index] = 1
            robot_next_pos.append(Node(paths[index][track_index[index]][0],paths[index][track_index[index]][0]))
        else:
            robot_next_pos.append(Node(-1,-1))

    robot_next_pos_1 = set(robot_next_pos)
    if len(connected_locks) > 15:
        #进行单通道的解锁
        for index in range(len(connected_locks)):
            if connected_locks[index] != 0:
                pos = Node(robots[connected_locks[index]-1].x , robots[connected_locks[index]-1].y)
                if pos not in connected_points[index]:
                    connected_locks[index] = 0

        #进行单通道的上锁
        for index in range(bot_num):
            step = 0
            index_1 = max(0 , min(len(paths[index])-1 , track_index[index]+step))
            cancel_flag = True
            if index_1 < len(paths[index]) and isinstance(paths[index][index_1] , tuple) and len(paths[index][index_1]) > 1:
                pos = Node(paths[index][index_1][0] , paths[index][index_1][1])
                for i in range(len(connected_points)):
                    if pos in connected_points[i]:
                        cancel_flag = False
                        if connected_locks[i] == index+1:
                            continue
                        elif connected_locks[i] == 0:
                            connected_locks[i] = index+1
                        else:
                            # track_index[index] = max(0 , track_index[index]-1)
                            # 单通道门口执行左右移动
                            if direction_flag[index] == 0:
                                reback_status[index] = 2
                                left_right_flag = False # 判断其他两个方向有没有空地
                                wait_pos = [] #构建可选点，长度为1或者2
                                for dict in direction:
                                    pos = (robots[index].x+dict[0] , robots[index].y+dict[1])
                                    pos_1 = Node(robots[index].x+dict[0],robots[index].y+dict[1])
                                    if min(pos[0],pos[1]) >= 0 and max(pos[0] , pos[1]) <= 199 and pos != paths[index][track_index[index]] and pos_1 not in obstacles_set and pos_1 not in robot_next_pos_1 and pos_1 not in now_position: # 测试时修改为live_points_1，同时传入
                                        if track_index[index] >= 2 and pos == paths[index][track_index[index]-2]:
                                            continue
                                        wait_pos.append(pos)
                                        left_right_flag = True
                                if not left_right_flag: # 没有左右的执行回退
                                    track_index[index] = max(0 , track_index[index]-2)
                                    reback_status[index] = 3
                                else:
                                    pos = wait_pos[0]
                                    waits[index] = wait_pos
                                    paths[index].insert(track_index[index] , pos)
                                    paths[index].insert(track_index[index]+1 , (robots[index].x , robots[index].y))
                                    reback_status[index] = 2 # 发生过左右的情况
                                direction_flag[index] = 1
                            else:
                                reback_status[index] = 3
                                track_index[index] = max(0 , track_index[index]-2)
                        break
                if cancel_flag:
                    direction_flag[index] = 0
    

    while(collision_flag):
        collision_flag = False
        bots = list(itertools.combinations(robots, 2))
        random.shuffle(bots)

        for bot in bots:
            robot_1 = bot[0].id
            robot_2 = bot[1].id
            if len(paths[robot_1]) <= 1 or len(paths[robot_2]) <= 1 or track_index[robot_1] < 0 or track_index[robot_2] < 0 or track_index[robot_1] >= len(paths[robot_1]) or track_index[robot_2] >= len(paths[robot_2]):
                continue
            
            # 两种情况，直接冲突和交换冲突
            if (paths[robot_1][track_index[robot_1]][0] == paths[robot_2][track_index[robot_2]][0] and paths[robot_1][track_index[robot_1]][1] == paths[robot_2][track_index[robot_2]][1]) or ((robots[robot_1].x == paths[robot_2][track_index[robot_2]][0] and robots[robot_1].y == paths[robot_2][track_index[robot_2]][1]) and (robots[robot_2].x == paths[robot_1][track_index[robot_1]][0] and robots[robot_2].y == paths[robot_1][track_index[robot_1]][1])):
                
                # 选取对象机器人，优先选取不再运货的机器人
                # target_robot = robot_2
                # if reback_status[robot_1] < reback_status[robot_2]:
                #     target_robot = robot_1
                # 除此之外，计算周围的障碍物数量
                # ob_nums_1 = 0
                # ob_nums_2 = 0
                # for i in range(-1 , 2):
                #     for j in range(-1 , 2):
                #         if i == 0 and j == 0:
                #             continue
                #         node_1 = Node(robots[robot_1].x+i , robots[robot_1].y+j)
                #         node_2 = Node(robots[robot_2].x+i , robots[robot_2].y+j)
                #         if min(node_1.x , node_1.y) >= 0 and max(node_1.x , node_1.y) <= 199:
                #             if node_1 not in obstacles_set and node_1 not in robot_next_pos_1 and node_1 not in now_position:
                #                 continue
                #             else:
                #                 ob_nums_1 = ob_nums_1 + 1
                #         if min(node_2.x , node_2.y) >= 0 and max(node_2.x , node_2.y) <= 199:
                #             if node_2 not in obstacles_set and node_2 not in robot_next_pos_1 and node_2 not in now_position:
                #                 continue
                #             else:
                #                 ob_nums_2 = ob_nums_2 + 1
                # target_robot = robot_1 if ob_nums_1 < ob_nums_2 else robot_2
                # if ob_nums_1 == ob_nums_2:
                target_robot = robot_1 if reback_status[robot_1] < reback_status[robot_2] else robot_2

                #编号小的保持不变，编号大的进行处理，即robot_2，这里规定0代表未发生碰撞，1代表停止，2代表其他两个方向寻路，==3代表回退
                reback_status[target_robot] = reback_status[target_robot] + 1
                if reback_status[target_robot] >= 4:# 已经进行过所有避障操作
                    continue
                elif reback_status[target_robot] == 3: # 已经产生了左右退的现象，弹出插入的点执行回退
                    if len(waits[target_robot]) == 2: # 如果还有备选位置，执行另一个躲避位置
                        paths[target_robot][track_index[target_robot]] = waits[target_robot][1]
                        waits[target_robot] = []
                        reback_status[target_robot] = 2
                    else:
                        del paths[target_robot][track_index[target_robot]]
                        track_index[target_robot] = max(0 , track_index[target_robot]-1)
                elif reback_status[target_robot] == 1 and paths[robot_1][track_index[robot_1]] == paths[robot_2][track_index[robot_2]]: #产生相撞于一点
                    track_index[target_robot] = max(0 , track_index[target_robot]-1)
                elif (reback_status[target_robot] == 1 and ((robots[robot_1].x , robots[robot_1].y) == paths[robot_2][track_index[robot_2]] and (robots[robot_2].x , robots[robot_2].y) == paths[robot_1][track_index[robot_1]])):
                    left_right_flag = False # 判断其他两个方向有没有空地
                    wait_pos = [] #构建可选点，长度为1或者2
                    for dict in direction:
                        pos = (robots[target_robot].x+dict[0] , robots[target_robot].y+dict[1])
                        pos_1 = Node(robots[target_robot].x+dict[0],robots[target_robot].y+dict[1])
                        if min(pos[0],pos[1]) >= 0 and max(pos[0] , pos[1]) <= 199 and pos != paths[target_robot][track_index[target_robot]] and pos_1 not in obstacles_set and pos_1 not in robot_next_pos_1 and pos_1 not in now_position: # 测试时修改为live_points_1，同时传入
                            if track_index[target_robot] >= 2 and pos == paths[target_robot][track_index[target_robot]-2]:
                                continue
                            wait_pos.append(pos)
                            left_right_flag = True
                    if not left_right_flag: # 没有左右的执行回退
                        track_index[target_robot] = max(0 , track_index[target_robot]-2)
                        reback_status[target_robot] = 3
                    else:
                        pos = wait_pos[0]
                        waits[target_robot] = wait_pos
                        paths[target_robot].insert(track_index[target_robot] , pos)
                        paths[target_robot].insert(track_index[target_robot]+1 , (robots[target_robot].x , robots[target_robot].y))
                        reback_status[target_robot] = 2 # 发生过左右的情况
                elif reback_status[target_robot] == 2:# 这里是对之前相撞于一点的情况进行处理
                    left_right_flag = False # 判断其他两个方向有没有空地
                    wait_pos = [] #构建可选点，长度为1或者2
                    for dict in direction:
                        pos = (robots[target_robot].x+dict[0] , robots[target_robot].y+dict[1])
                        pos_1 = Node(robots[target_robot].x+dict[0] , robots[target_robot].y+dict[1])
                        if min(pos[0],pos[1]) >= 0 and max(pos[0] , pos[1]) <= 199 and pos != paths[target_robot][track_index[target_robot]+1] and pos not in obstacles and pos_1 not in robot_next_pos_1 and pos_1 not in now_position: # 测试时修改为live_points_1，同时传入
                            if track_index[target_robot] >= 1 and pos == paths[target_robot][track_index[target_robot]-1]:
                                continue
                            wait_pos.append(pos)
                            left_right_flag = True
                    if not left_right_flag: # 没有左右的执行回退
                        track_index[target_robot] = max(0 , track_index[target_robot]-1)
                        reback_status[target_robot] = 3
                    else:
                        pos = wait_pos[0]
                        waits[target_robot] = wait_pos
                        paths[target_robot].insert(track_index[target_robot] , pos)
                        reback_status[target_robot] = 2 # 发生过左右的情况
                collision_flag = True

                    # # 更新robot_next_pos
                if isinstance(paths[target_robot][track_index[target_robot]] , tuple) and len(paths[target_robot][track_index[target_robot]]) > 1:
                    robot_next_pos[target_robot] = Node(paths[target_robot][track_index[target_robot]][0] , paths[target_robot][track_index[target_robot]][0])
                    robot_next_pos_1 = set(robot_next_pos)
    return track_index,paths,connected_locks