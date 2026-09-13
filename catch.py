import cv2
import os


def extract_frames(video_path, output_dir, num_frames=500):
    """
    从视频中均匀抽取指定数量的帧

    Args:
        video_path: 视频文件路径
        output_dir: 输出图片目录
        num_frames: 需要抽取的帧数
    """
    # 创建输出目录
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 打开视频
    cap = cv2.VideoCapture(video_path)

    # 获取视频总帧数
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    if total_frames == 0:
        print("无法读取视频或视频为空")
        cap.release()
        return

    print(f"视频总帧数: {total_frames}")

    # 如果总帧数小于需要的帧数，则调整抽取数量
    if total_frames < num_frames:
        num_frames = total_frames
        print(f"视频帧数不足500，改为抽取全部 {num_frames} 帧")

    # 计算步长（均匀抽取）
    step = total_frames / num_frames

    # 抽取并保存帧
    count = 0
    saved_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # 判断当前帧是否需要保存
        if int(count % step) == 0 and saved_count < num_frames:
            # 生成文件名（4位数字编号）
            filename = f"frame_{saved_count:04d}.jpg"
            filepath = os.path.join(output_dir, filename)

            # 保存图片
            cv2.imwrite(filepath, frame)
            saved_count += 1
            print(f"已保存: {filename} ({saved_count}/{num_frames})")

        count += 1

    # 释放资源
    cap.release()
    print(f"\n完成！共抽取 {saved_count} 张图片，保存在 {output_dir}")

    # 如果实际保存的少于目标数量，是因为最后没有正好落在步长上
    if saved_count < num_frames:
        # 补充保存最后一帧
        if saved_count > 0:
            cap = cv2.VideoCapture(video_path)
            cap.set(cv2.CAP_PROP_POS_FRAMES, total_frames - 1)
            ret, last_frame = cap.read()
            if ret:
                filename = f"frame_{saved_count:04d}.jpg"
                filepath = os.path.join(output_dir, filename)
                cv2.imwrite(filepath, last_frame)
                saved_count += 1
                print(f"补充保存最后一帧: {filename}")
            cap.release()
        print(f"最终共保存 {saved_count} 张图片")


if __name__ == "__main__":
    # 使用示例
    video_path = "belt.mp4"  # 修改为你的视频路径
    output_dir = "frames"  # 输出文件夹名称

    extract_frames(video_path, output_dir, 500)