import os
import shutil
import pygame

# 初始化pygame
pygame.mixer.init()

# 获取test.mp3的初始大小
last_file_size = os.path.getsize('test.mp3')

# 标记是否需要播放音乐
need_play = False

while True:
    # 检测文件是否更新
    try:    
        if os.path.getsize('test.mp3') != last_file_size and os.path.getsize('test.mp3') > 30:
            # 如果文件大小变化且大于30，就重新获取文件大小
            pygame.time.wait(3000)
            last_file_size = os.path.getsize('test.mp3')

            # 复制文件并重命名
            shutil.copy2('test.mp3', 'test2.mp3')

            # 标记需要播放音乐
            need_play = True

        if need_play:
            # 播放音乐
            pygame.mixer.init()
            pygame.mixer.music.load('test2.mp3')
            pygame.mixer.music.play()

            # 等待音乐播放结束
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)

            # 退出临时音乐文件
            pygame.mixer.quit()

            # 重置标记
            need_play = False

        # 等待一段时间再进行下一次检测
        pygame.time.wait(3000)
    except Exception as e:
        print("播放器出错")
        pygame.time.wait(3000)
