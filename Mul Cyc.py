import cv2
import numpy as np
import socket
from mss import mss

# 定义要捕获的屏幕区域 (x, y, width, height)
# 修改这些值以匹配您想要的特定位置和大小
MONITOR = {
    "top": 415,      
    "left": 195,     
    "width": 540,    
    "height": 80    
}

def send(command):
            HOST = "127.0.0.1"
            PORT = 5000
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((HOST, PORT))
                s.sendall(command.encode('utf-8'))

def find_top_bottom_points(contours):
    results = []

    for contour in contours:
        # 将轮廓的点提取到一个二维数组中，形状为 (N, 1, 2) -> (N, 2)

        if len(contour) == 0:
            continue # 跳过空轮廓
        
        points = contour.reshape(-1, 2) # 将轮廓展平为 N 行 2 列的数组    

         # 现在 points 保证是2维的 (N, 2)
        
        # 找到 y 坐标最小的点（最高点）
        min_y = np.min(points[:, 1])
        top_candidates = points[points[:, 1] == min_y]
        # 在 y 最小的候选点中，选择 x 最大的点
        top_point = top_candidates[np.argmax(top_candidates[:, 0])]
        
        # 找到 y 坐标最大的点（最低点）
        max_y = np.max(points[:, 1])
        bottom_candidates = points[points[:, 1] == max_y]
        # 在 y 最大的候选点中，选择 x 最大的点
        bottom_point = bottom_candidates[np.argmax(bottom_candidates[:, 0])]

         # 计算从 top 到 bottom 的向量
        dx = bottom_point[0] - top_point[0]
        dy = bottom_point[1] - top_point[1]
        
        # 计算角度 (弧度 -> 度)
        # np.arctan2(dy, dx) 返回 -pi 到 pi 的角度
        angle_radians = np.arctan2(dy, dx)
        angle_degrees = np.degrees(angle_radians) # 等同于 angle_radians * 180 / np.pi
        
        results.append({
            'top': tuple(top_point),
            'bottom': tuple(bottom_point),
            'angle_degrees': angle_degrees
        })
    
    return results

def region_angle(img_bar):
    gray = cv2.cvtColor(img_bar, cv2.COLOR_BGRA2GRAY)

     # 二值化阈值   YELLOW:248      GRAY:183
    threshold_value = 187  
    max_value = 255        
    _, binary_inv = cv2.threshold(gray, threshold_value, max_value, cv2.THRESH_BINARY_INV)
    
    # 角度
    contours, _ = cv2.findContours(binary_inv, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    num_contours = len(contours)

    aver = 0.0
    dir = "N/A"

    if contours:
        angle_data = find_top_bottom_points(contours)
        angles = [data['angle_degrees'] for data in angle_data]
        # 计算平均角度
        aver = np.mean(angles)
    
    return num_contours,aver,binary_inv

#                           DOWN判断函数
def region_aver_angle(aver):
        left_angle = 70
        right_angle = 110

        if aver > right_angle:
            dir = "turn_right"
        elif right_angle >= aver >= left_angle:
            dir = "forward"
        elif left_angle > aver > 0:              
            dir = "turn_left"
        else: 
            dir = "???"
        return dir

def command_left():
    send("rotat:-5")
    send("mov:0.3")

def command_right():
    send("rotat:5")
    send("mov:0.3") 

def command_forward():
    send("mov:0.3")

def command_unknown():
    send("mov:0")   

def reset():
    send("resetpo:0,0.52,-6")
    send("resetro:0,0,0")

def start():
    with mss() as sct:

        print("按 z 开始捕获，按 q 键退出。")
        while True:

            prompt_img = np.zeros((200, 400, 3), dtype=np.uint8)
            cv2.putText(prompt_img, "Press z to Start", (50, 100), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow("Menu", prompt_img)
            
            key = cv2.waitKey(100) & 0xFF # 等待100ms，降低CPU占用
            if key == ord('q'):
                cv2.destroyAllWindows()
                return # 直接退出函数
            elif key == ord('z'): #
                print("开始捕获...")
                cv2.destroyAllWindows()
                break # 跳出等待循环，进入主捕获循环
        # --- 等待循环结束 ---
        return 
    
def capture():

    with mss() as sct:

        # 捕获指定区域
        screenshot = sct.grab(MONITOR)

        # 将原始图像数据转换为NumPy数组
        img_np = np.array(screenshot)
        
        img_bgr = cv2.cvtColor(img_np, cv2.COLOR_BGRA2BGR)

        num_cnts,aver,binary_inverted = region_angle(img_bgr)

    return num_cnts,aver,binary_inverted,

def print_imshow(num_cnts,aver,accu,binary_inv,dir_v,position):
        avg_out = f"{aver:.2f}°" if not np.isnan(aver) else "N/A"
        accu_ang = f"{accu}°"
        #图像排列
        can_wid = 710
        can_hei = 250
        can = np.zeros((can_hei,can_wid,3),dtype=np.uint8)

        pos1 = (0,170)

        h1,w1 = binary_inv.shape[:2]

        tarreg = can[pos1[1]:pos1[1]+h1,pos1[0]:pos1[0]+w1]

        tarreg[:,:,0] = binary_inv
        tarreg[:,:,1] = binary_inv        
        tarreg[:,:,2] = binary_inv

        # 7. 显示二值图像
        wx = 1000
        wy = 150
        nam = "window"
        cv2.namedWindow(nam)

        cv2.moveWindow(nam,wx,wy)
        cv2.imshow(nam, can)

        #  显示数据
        console_info = (
            f"累计旋转{accu_ang},down轮廓数: {num_cnts}, 平均角度: {avg_out}, 推荐方向: {dir_v} ,路段：{position}|"
        )
        print(console_info)


def decision(dir,accu):
    if dir == "turn_left":
        command_left()
        accu -=5

    elif dir == "forward":
        command_forward()

    elif dir == "turn_right":
        command_right()
        accu +=5
    else:
        command_unknown

    return dir,accu
    
def road1():
    accu = 0
    position = 0
    distance = 0
    dis2 = 0

    # 第一个直路
    while position == 0:
        num_cnts,aver,binary_inv = capture()
        dir_v = region_aver_angle(aver)

        dir = "forward"

        dir,accu = decision(dir,accu)

        print_imshow(num_cnts,aver,accu,binary_inv,dir_v,position)
        # 8. 按 'q' 键退出
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break   
        elif aver == 0:
                position += 1
                break
    
    # 第一个弯道
    while position == 1:
        num_cnts,aver,binary_inv = capture()
        dir_v = region_aver_angle(aver)

        dir = "turn_right"

        dir,accu = decision(dir,accu)

        print_imshow(num_cnts,aver,accu,binary_inv,dir_v,position)
        # 8. 按 'q' 键退出
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break   
        elif accu >85:
            if dir_v == "turn_left":
                position+=1
                break
    
    # 第二个弯道
    while position == 2:
        num_cnts,aver,binary_inv = capture()
        dir_v = region_aver_angle(aver)

        dir = "turn_left"

        dir,accu = decision(dir,accu)

        print_imshow(num_cnts,aver,accu,binary_inv,dir_v,position)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break   
        elif accu < 5:
                position+=1
                break

    #  第二个直路（减速带，采用距离）
    while position == 3:
        num_cnts,aver,binary_inv = capture()
        dir_v = region_aver_angle(aver)

        dir = "forward"
        distance += 1
        dir,accu = decision(dir,accu)


        print_imshow(num_cnts,aver,accu,binary_inv,dir_v,position)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break   
        elif distance > 10:
                position+=1
                break

    # 第三个弯道（在二维码之前,已清零）
    while position == 4:
        num_cnts,aver,binary_inv = capture()
        dir_v = region_aver_angle(aver)

        send("rotat:-5")
        send("mov:0.2")
        accu -= 5

        print_imshow(num_cnts,aver,accu,binary_inv,dir_v,position)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break   
        elif accu < -85:
                #如果容易走出道路就改aver条件 原版：相对角度90，推荐方向turnleft
                    distance = 0
                    position+=1
                    break
    
    #  第三个直路（岔路口）
    while position == 5:
        num_cnts,aver,binary_inv = capture()
        dir_v = region_aver_angle(aver)

        dir = "forward"
        distance += 1

        dir,accu = decision(dir,accu)

        print_imshow(num_cnts,aver,accu,binary_inv,dir_v,position)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break   
        elif distance > 55:
             position = 10
             break

    # 第四个弯道（离开岔路口）
    while position == 10:
        num_cnts,aver,binary_inv = capture()
        dir_v = region_aver_angle(aver)

        dir = "turn_right"

        dir,accu = decision(dir,accu)

        print_imshow(num_cnts,aver,accu,binary_inv,dir_v,position)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break   
        elif accu >-5:
                    position+=1
                    #distance 清零
                    distance = 0
                    break

    #  第四个直路（离开岔路口）
    while position == 11:
        num_cnts,aver,binary_inv = capture()
        dir_v = region_aver_angle(aver)

        dir = "forward"

        dir,accu = decision(dir,accu)

        print_imshow(num_cnts,aver,accu,binary_inv,dir_v,position)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break   
        elif dir_v == "turn_right":
             position += 1
             break

    # 迎接任务弯道直行：
    while position == 12:
        num_cnts,aver,binary_inv = capture()
        dir_v = region_aver_angle(aver)

        dir = "forward"
        distance += 1

        dir,accu = decision(dir,accu)

        print_imshow(num_cnts,aver,accu,binary_inv,dir_v,position)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break   
        elif distance > 5:
                    position+=1

                    break

    # 迎接任务弯道(已清零）：
    while position == 13:
        num_cnts,aver,binary_inv = capture()
        dir_v = region_aver_angle(aver)

        dir = "turn_right"

        dir,accu = decision(dir,accu)

        print_imshow(num_cnts,aver,accu,binary_inv,dir_v,position)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break   
        elif accu > 85:
                    position = 20
                    distance = 0
                    break
        
    #  排爆和反恐直路
    while position == 20:
        num_cnts,aver,binary_inv = capture()
        dir_v = region_aver_angle(aver)

        dir = "forward"
        distance += 1

        dir,accu = decision(dir,accu)

        print_imshow(num_cnts,aver,accu,binary_inv,dir_v,position)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break   
        elif distance == 75:
             position += 1
             break

    # 最后弯道直行(已清零，dis2开始使用)：
    while position == 21:
        
        num_cnts,aver,binary_inv = capture()
        dir_v = region_aver_angle(aver)

        dir = "forward"
        dis2 += 1

        dir,accu = decision(dir,accu)

        print_imshow(num_cnts,aver,accu,binary_inv,dir_v,position)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break   
        elif dis2 > 2:
                    position+=1
                    distance = 0
                    break
        
    # 最后弯道：
    while position == 22:
        num_cnts,aver,binary_inv = capture()
        dir_v = region_aver_angle(aver)

        dir = "turn_right"

        dir,accu = decision(dir,accu)

        print_imshow(num_cnts,aver,accu,binary_inv,dir_v,position)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break   
        elif accu > 175:
                    position = 30
                    distance = 0
                    break

    # 最后直路：
    while position == 30:
        
        num_cnts,aver,binary_inv = capture()
        dir_v = region_aver_angle(aver)

        dir = "forward"
        distance += 1

        dir,accu = decision(dir,accu)

        print_imshow(num_cnts,aver,accu,binary_inv,dir_v,position)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break   
        elif distance > 65:
                    position+=1
                    distance = 0
                    break
        
    # 7. 清理资源
    cv2.destroyAllWindows()


# 运行捕获函数
if __name__ == "__main__":
    reset()
    start()
    road1()