import pickle
import math
import time
import os
import numpy as np

import codegen.node_alloc as alloc
import codegen.gen_input as gen_in
import codegen.count as count
import codegen.map2 as map2

from dparser.ast import SNN


def get_headpack(x, y):
    x1 = x % 24
    y1 = y % 24
    tmp = (x << 18) | (y << 12) | (48 << 6) | (47)  ###(24,23)input
    if x1 == 23:
        return (y1 << 38) | (0b10 << 36) | (0b1 << 32) | (0b1 << 29) | (0x1 << 24) | tmp
    else:
        return (y1 << 38) | (0b10 << 36) | (0b1 << 32) | (0b1 << 29) | (0x4 << 24) | tmp


def get_bodypackhead(y):
    y1 = y % 24
    return (y1 << 38) | (0b1 << 32)


def get_tailpackhead(y):
    y1 = y % 24
    return (y1 << 38) | (0b01 << 36) | (0b1 << 32)


def create_config(path: str, snn: SNN):
    ###############################################输入参数，其中neurontype 和 leaksign, leak 因为每层的参数都一样，所以这里是用一个值表示
    ## 该例子神经元层： input_spike,input,fc1,fc2,fc3, 注意input_spike是输入层，input反而不是，这里可能是应用命名的问题
    # neurontype = 1  # 1表示IF,0表示LIF，
    # leaksign = -1  # leak_mode
    # leak = 0  # leak_value
    # vth = [1, 4022, 179, 1831]  # vThreshold ,分别为input,fc1,fc2,fc3
    # reset_mode = [0, 0, 0, 0]  # 分别为input,fc1,fc2,fc3
    # layerWidth = [300, 300, 400, 400, 3,
    #               1]  # 每层的神经元数量，分别为input_spike,input,fc1,fc2,fc3，  注意映射会加上一个芯片外的输出层，一个神经元，即最后的1，所以这里最后要加1
    #
    # netDepth = 5
    # connfiles = [
    #     'darwin2_config/connections_to_input_spike_forward.pickle',
    #     'darwin2_config/connections_input_to_fc1.pickle',
    #     'darwin2_config/connections_fc1_to_fc2.pickle',
    #     'darwin2_config/connections_fc2_to_fc3.pickle',
    # ]

    ############################################################################################################输入  结束
    leaksign = snn.leak_sign
    leak = 0  # ?
    vth = [x.v_threshold for x in snn.neuron_groups][1:]
    reset_mode = [x.reset_mode for x in snn.neuron_groups][1:]
    layerWidth = [x.neuron_size for x in snn.neuron_groups]
    layerWidth.append(1)

    netDepth = snn.net_depth
    work_dir = os.path.dirname(path)
    connfiles = [os.path.join(work_dir, c.synapses) for c in snn.connect_config]

    delay = snn.delay_type

    board_num = 1  # 板子个数
    childboard_num = 3  # 单块板子的子板个数
    # chip_num = [1, 1, 1] #单块子板一条边的芯片个数，单块子板有chip_num*chip_num块芯片
    node_num = 24  # 单块芯片一条边的节点个数，单块芯片有node_num* node_num个节点
    neuron_num = 256  # 每个节点神经元数目

    tmp = []

    print("start")
    flag = 0
    firstlayer = []

    # mapping
    layers, avg_conn = count.count_neucon2(connfiles)  #####
    print("layers:", layers)
    print("avg_conn:", avg_conn)

    nodes, neus = count.count_nodes(layers, avg_conn, neuron_num)  # only nodes will be used
    print('nodes:', nodes)
    print('neus:', neus)

    node_link = count.neuron_link(connfiles, netDepth, layers, nodes)
    print(node_link)
    layer_num = len(layers)
    layer_id = 0
    print("layer_num:", layer_num)

    board_id = 1
    forward_node = []
    while board_id <= board_num:
        childboard_id = 1

        while childboard_id <= childboard_num:
            id1 = layer_id + 1
            ID = '%d' % board_id + '_' + '%d' % childboard_id
            print(ID)
            print(childboard_id)
            # print(chip_num[childboard_id-1])
            # nodelist, zero_ref, layer_id = mapping.mapping_board(nodes, neus, layer_num, layer_id, chip_num[childboard_id-1])
            nodelist, zerolist, layer_id, forward_res = map2.map_chip11(nodes, node_link, layer_num, layer_id,
                                                                        forward_node)
            forward_node = forward_res
            print(forward_node)
            if id1 == 1:
                firstlayer = nodelist[0]
                # f = open('conn2/input_to_fc1', 'rb')
                # get_input(f, layerWidth, firstlayer)

            print("mapping done")
            print(zerolist)
            cnt_node = 0
            for i in range(len(nodelist)):
                cnt_node += len(nodelist[i])

            print("cnt_node:", cnt_node)

            ########################已经全部映射完成
            if (layer_id >= layer_num):
                flag = 1
                linkout = []  #######################(最后输出节点与最后一层的链接文件)
                for i in range(layers[-1]):
                    linkout.append((i, 0, i, 0))
                fw = open('linkout', 'wb')
                pickle.dump(linkout, fw)  # 保存到文件中
                fw.close()
                connfiles.append('linkout')

                ## output
                output = [[49, 49]]
                nodelist.append(output)
            else:
                nodelist.append(forward_node)

            id2 = layer_id + 1
            print("id2：", id2)
            # print(layerWidth[1:])
            # print(layerWidth[id1:id2 + 1])
            # print(len(connfiles))
            # print(connfiles[1:])
            # print(len(layerWidth))
            # print(connfiles[id1:id2])
            print("=================")
            print((ID, connfiles[id1:id2], id2 - id1 + 1, layerWidth[id1:id2 + 1], nodelist,
                   zerolist, delay, vth[id1 - 1:id2 - 1], leak, reset_mode[id1 - 1:id2 - 1], leaksign))
            print("=================")
            alloc.buildNetwork(ID, connfiles[id1:id2], id2 - id1 + 1, layerWidth[id1:id2 + 1], nodelist,
                               zerolist, delay, vth[id1 - 1:id2 - 1], leak, reset_mode[id1 - 1:id2 - 1], leaksign)
            print("config done")

            str1 = 'connfiles' + ID
            print(str1)
            fw = open(str1, 'wb')
            pickle.dump(connfiles, fw)
            fw.close()

            str2 = 'layerWidth' + ID
            fw = open(str2, 'wb')
            pickle.dump(layerWidth, fw)
            fw.close()

            str3 = 'nodelist' + ID
            fw = open(str3, 'wb')
            pickle.dump(nodelist, fw)
            fw.close()

            c_head = '40000'
            str4 = os.path.join(ID + "clear.txt")
            f = open(str4, "w")
            for i in range(id2 - id1):
                for x, y in nodelist[i]:
                    tmp = get_headpack(x, y)
                    body_pack_head = get_bodypackhead(y)
                    tail_pack_head = get_tailpackhead(y)
                    ss = "%011x" % tmp  # head
                    f.write(c_head + ss + '\n')
                    tmp = (0b1 << 31) | 0x0
                    ss = "%011x" % (tmp + body_pack_head)
                    f.write(c_head + ss + '\n')
                    tmp = 2
                    ss = "%011x" % (tmp + tail_pack_head)
                    f.write(c_head + ss + '\n')
            f.close()

            str5 = os.path.join(ID + "enable.txt")
            f = open(str5, "w")
            for i in range(id2 - id1):
                # print("i:", i)
                for x, y in nodelist[i]:
                    tmp = get_headpack(x, y)
                    body_pack_head = get_bodypackhead(y)
                    tail_pack_head = get_tailpackhead(y)
                    ss = "%011x" % tmp  # head
                    f.write(c_head + ss + '\n')
                    tmp = (0b1 << 31) | 0x0
                    ss = "%011x" % (tmp + body_pack_head)
                    f.write(c_head + ss + '\n')
                    tmp = 1
                    ss = "%011x" % (tmp + tail_pack_head)
                    f.write(c_head + ss + '\n')
            f.close()

            for node in nodelist:
                print(node)
            # print(nodelist)

            if (flag == 1):
                break
            childboard_id += 1
        # print(childboard_id)
        ########################已经全部映射完成
        if (flag == 1):
            break

        board_id += 1

    # # ------------------------------------- input ----------------------------------------------总共只要一个
    # # 加载输入层
    # f = open('darwin2_config/connections_to_input_spike_forward.pickle', 'rb')
    # in_conv1 = pickle.load(f)
    # f.close()
    #
    # # 加载spikes
    # t1 = []
    # for i in range(300):  #### 输入层neuron number
    #     t1.append([i, [1]])
    # # f = open('stimuli_sample/0.pickle', 'rb')
    # # t1 = pickle.load(f)
    # # f.close()
    #
    #
    # print("in_conv1 len: ", len(in_conv1))
    # times = time.time()
    #
    # input_node_map = {}
    # neuron_num = int(math.ceil(layerWidth[1] / float(len(firstlayer))))
    # print(neuron_num)
    # print(len(firstlayer))
    #
    # interval = 100  #
    #
    # for line in in_conv1:
    #     src = int(line[0])
    #     dst = int(line[1])
    #     node_x = firstlayer[dst // neuron_num][0]
    #     node_y = firstlayer[dst // neuron_num][1]
    #     nodenumber = node_x * 64 + node_y
    #     if not nodenumber in input_node_map.keys():
    #         input_node_map[nodenumber] = {}
    #     input_node_map[nodenumber].update({dst % neuron_num: dst})
    # gen_in.change_format(in_conv1)
    #
    # time1 = time.time()
    # print(time1)
    #
    # # inputlist1, rowlist1 = gen_in.gen_inputdata(new_con, t1, input_node_map, int(interval),
    # #                     'input1.txt', 'row1.txt')
    #
    # # inputlist1, rowlist1 = gen_in.gen_inputdata_list(new_con, t1, input_node_map, int(interval))
    # gen_in.gen_inputdata(in_conv1, t1, input_node_map, int(interval), 'input.txt', 'row.txt')
    #
    # inputlist1, rowlist1 = gen_in.gen_inputdata_list(in_conv1, t1, input_node_map, int(interval))
    #
    # print(len(inputlist1))
    # print('input done')
    #
    # time2 = time.time()
    # print(time2 - time1)

# if __name__ == "__main__":
#     create_config()
