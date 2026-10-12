import math
from typing import Tuple, Union, Optional

import numpy as np


def calculate_angle(line1, line2):
    """
    计算两条线段之间的最小夹角
    :param line1: ((x1, y1), (x2, y2))
    :param line2: ((x3, y3), (x4, y4))
    :return: 角度值（0-90度）
    """
    # 计算方向向量
    vec1 = np.array([line1[0][0] - line1[1][0], line1[0][1] - line1[1][1]])
    print('>>>line2:', line2)
    vec2 = np.array([line2[0][0] - line2[1][0], line2[0][1] - line2[1][1]])

    print('vec1:', vec1, 'vec2:', vec2)

    # 计算点积
    dot_product = np.dot(vec1, vec2)

    # 计算模长
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)

    # 处理除零错误
    if norm1 == 0 or norm2 == 0:
        return 0.0

    # 计算余弦值并限制范围
    cos_theta = dot_product / (norm1 * norm2)
    cos_theta = np.clip(cos_theta, -1.0, 1.0)

    # 计算角度（弧度转角度）
    theta_deg = np.degrees(np.arccos(cos_theta))

    # 取最小夹角（0-90度）
    return min(theta_deg, 180 - theta_deg)


# 从识别的轮廓获取左边界和右边界
def get_border(keypts, border_left_p0, border_left_p1, border_right_p0, border_right_p1):
    # 将识别轮廓的所有边与正常边界的夹角排序（从小到大)
    # 遍历之，其中第一个线段长度大于一个阈值（如300）的
    # 线段就是识别的边界
    reco_border_left = None
    reco_border_left_id = -1

    reco_border_right = None
    reco_border_right_id = -1

    reco_border_list = []
    for i in range(len(keypts)):
        x0 = keypts[i][0][0]
        y0 = keypts[i][0][1]
        x1 = keypts[(i + 1) % len(keypts)][0][0]
        y1 = keypts[(i + 1) % len(keypts)][0][1]
        d = math.sqrt((y1 - y0) ** 2 + (x1 - x0) ** 2)
        line2 = ((x0, y0), (x1, y1))
        angle_with_left = calculate_angle(line2, (border_left_p0, border_left_p1))
        angle_with_right = calculate_angle(line2, (border_right_p0, border_right_p1))
        reco_border_list.append({'id': i, 'angle_left': angle_with_left, 'angle_right': angle_with_right,
                                 'd': d, 'line': ((x0, y0), (x1, y1))})

    sorted_reco_border_left_list = sorted(reco_border_list, key=lambda x: x['angle_left'])
    sorted_reco_border_right_list = sorted(reco_border_list, key=lambda x: x['angle_right'])

    print('sorted left list:', sorted_reco_border_left_list)
    print('sorted right list:', sorted_reco_border_right_list)
    for one in sorted_reco_border_left_list:
        if one['d'] > 300:
            reco_border_left_id = one['id']
            reco_border_left = one['line']
            break

    for one in sorted_reco_border_right_list:
        if one['d'] > 300:
            reco_border_right_id = one['id']
            reco_border_right = one['line']
            break

    print('reco_border_left:', reco_border_left, 'reco_border_right:', reco_border_right)
    if reco_border_left is not None and reco_border_right is not None and reco_border_left_id != reco_border_right_id:
        print('left:', reco_border_left, 'right:', reco_border_right)
        return reco_border_left, reco_border_right

    return None, None


# 已知上边和下边跟水平线平行的梯形
# 的两条边上的两条线段：line1:((x0,y0),(x1,y1)), line2:((x2,y2),(x3,y3))
# 求梯形的上边和下边的中心点坐标
def mid_line(line1: Tuple[Tuple[int, int], Tuple[int, int]], line2: Tuple[Tuple[int, int], Tuple[int, int]]) \
        -> Union[Tuple[None, None], Tuple[Tuple[int, int], Tuple[int, int]]]:
    """

    :param line1: 左边界两个端点坐标 ((x0,y0),(x1,y1))
    :param line2: 右边界两个端点坐标 ((x2,y2),(x3,y3))
    """
    x0 = line1[0][0]
    y0 = line1[0][1]
    x1 = line1[1][0]
    y1 = line1[1][1]
    points_of_line1 = []
    points_of_line1.append((x0, y0))
    points_of_line1.append((x1, y1))

    x2 = line2[0][0]
    y2 = line2[0][1]
    x3 = line2[1][0]
    y3 = line2[1][1]
    points_of_line2 = []
    points_of_line2.append((x2, y2))
    points_of_line2.append((x3, y3))

    # y=mx+b
    if x0 != x1:
        m0 = (y1 - y0) / (x1 - x0)
        b0 = y1 - m0 * x1
        if m0 == 0:
            return None, None
        points_of_line1.append(((y2 - b0) / m0, y2))
        points_of_line1.append(((y3 - b0) / m0, y3))
    else:
        points_of_line1.append((x0, y2))
        points_of_line1.append((x0, y3))

    if x2 != x3:
        m1 = (y3 - y2) / (x3 - x2)
        b1 = y3 - m1 * x3
        if m1 == 0:
            return None, None
        points_of_line2.append(((y0 - b1) / m1, y0))
        points_of_line2.append(((y1 - b1) / m1, y1))
    else:
        points_of_line2.append((x3, y0))
        points_of_line2.append((x3, y1))

    # 根据y排序
    sorted_points_of_line1 = sorted(points_of_line1, key=lambda x: x[1])
    sorted_points_of_line2 = sorted(points_of_line2, key=lambda x: x[1])

    p0 = sorted_points_of_line1[0]
    p1 = sorted_points_of_line1[3]
    p2 = sorted_points_of_line2[0]
    p3 = sorted_points_of_line2[3]
    top_mid_x = int((p0[0] + p2[0]) / 2)
    bottom_mid_x = int((p1[0] + p3[0]) / 2)
    return (top_mid_x, p0[1]), (bottom_mid_x, p1[1])


# 计算偏移距离，取两条中线的最大距离，像素距离要根据皮带实际宽度换算
def calculate_dist(org_mid_line: Tuple[Tuple[int, int], Tuple[int, int]], \
                   reco_mid_line: Tuple[Tuple[int, int], Tuple[int, int]], \
                   org_border_left: Tuple[Tuple[int, int], Tuple[int, int]], \
                   org_border_right: Tuple[Tuple[int, int], Tuple[int, int]], belt_width: float) -> \
        float:
    """

    :param org_mid_line, 预设边缘的中线，如：((x0,y0),(x1,y1)):
    :param reco_mid_line: 识别边缘的中线，如:((x2,y2),(x3,y3))
    :param org_border_left: 预设边缘的左边缘，如((x4,y4),(x5,y5))
    :param org_border_right: 预设边缘的右边缘，如((x6,y6),(x7,y7))
    :param belt_width: 皮带的宽度，如2米
    :return: 偏移距离，如0.2米
    """
    # 左边缘线，右边缘线，原中线，识别后中线 4个直线方程
    # y=mx+b
    # org_mid_line
    print('in calculate_dist, org_mid_line:', org_mid_line)
    print('in calculate_dist, reco_mid_line:', reco_mid_line)
    org_mid_line_p0 = org_mid_line[0]
    org_mid_line_p1 = org_mid_line[1]
    if org_mid_line_p0[0] != org_mid_line_p1[0]:
        m_org_mid_line = (org_mid_line_p1[1] - org_mid_line_p0[1]) / (org_mid_line_p1[0] - org_mid_line_p0[0])
        b_org_mid_line = org_mid_line_p1[1] - m_org_mid_line * org_mid_line_p1[0]
        org_mid_line_is_vertline = False
    else:
        org_mid_line_is_vertline = True

    # reco_mid_line
    reco_mid_line_p0 = reco_mid_line[0]
    reco_mid_line_p1 = reco_mid_line[1]
    if reco_mid_line_p0[0] != reco_mid_line_p1[0]:
        m_reco_mid_line = (reco_mid_line_p1[1] - reco_mid_line_p0[1]) / (reco_mid_line_p1[0] - reco_mid_line_p0[0])
        b_reco_mid_line = reco_mid_line_p1[1] - m_reco_mid_line * reco_mid_line_p1[0]
        reco_mid_line_is_vertline = False
    else:
        reco_mid_line_is_vertline = True

    # org_border_left
    org_border_left_p0 = org_border_left[0]
    org_border_left_p1 = org_border_left[1]
    if org_border_left_p0[0] != org_border_left_p1[0]:
        m_org_border_left = (org_border_left_p1[1] - org_border_left_p0[1]) / (
                    org_border_left_p1[0] - org_border_left_p0[0])
        b_org_border_left = org_border_left_p1[1] - m_org_border_left * org_border_left_p1[0]
        org_border_left_is_vertline = False
    else:
        org_border_left_is_vertline = True

    # org_border_right
    org_border_right_p0 = org_border_right[0]
    org_border_right_p1 = org_border_right[1]
    if org_border_right_p0[0] != org_border_right_p1[0]:
        m_org_border_right = (org_border_right_p1[1] - org_border_right_p0[1]) / (
                    org_border_right_p1[0] - org_border_right_p0[0])
        b_org_border_right = org_border_right_p1[1] - m_org_border_right * org_border_right_p1[0]
        org_border_right_is_vertline = False
    else:
        org_border_right_is_vertline = True

    #4条线出现垂线
    if org_border_left_is_vertline or org_border_right_is_vertline or org_mid_line_is_vertline or reco_mid_line_is_vertline:
        return 0.0

    start_y = min(reco_mid_line_p0[1], reco_mid_line_p1[1])
    end_y = max(reco_mid_line_p0[1], reco_mid_line_p1[1])
    max_dist = 0
    for y in range(start_y, end_y):
        # TBD: 4条线出现垂线的情况
        d_pixel_mid_line = abs((y - b_org_mid_line) / m_org_mid_line - (y - b_reco_mid_line) / m_reco_mid_line)
        d_pixel_border_line = abs(
            (y - b_org_border_left) / m_org_border_left - (y - b_org_border_right) / m_org_border_right)
        dist = (d_pixel_mid_line / d_pixel_border_line) * belt_width
        if dist > max_dist:
            max_dist = dist

    return max_dist