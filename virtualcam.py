
'''

调用OBS虚拟摄像头在直播间显示SD模型生成的图像

单开线程，监听prompt文本，显示在obs摄像头，没有图像，显示透明
'''
import pyvirtualcam
import cv2
import threading
import requests
import time
import queue

class MyThread(threading.Thread):
    def __init__(self,sd_url,prompt_queue):
        super(MyThread,self).__init__()
        self.sd_url = sd_url
        self.prompt_queue = prompt_queue
        self.start_time = None
        self.end_time = None
        self.image = None
        self.background = cv2.imread("./background/tip.png")
        # self.background = cv2.imread("./test.jpg")

    def run(self):

        with pyvirtualcam.Camera(width=512, height=512, fps=25) as cam:
            print(f'Using virtual camera: {cam.device}')
            while True:
                if self.prompt_queue.empty() :
                    # 显示test.jpg 10s
                    if self.start_time is None:
                        self.background  = self.background [:, :, [2, 1, 0]]

                        cam.send(self.background )
                        cam.sleep_until_next_frame()

                        # print("111111111111111")
                        continue
                    self.end_time = time.time()
                    if ((self.end_time-self.start_time) <= 20) and (self.image is not None):
                        # 转换为RGB：由于 cv2 读出来的图片默认是 BGR，因此需要转换成 RGB
                        # image = cv2.resize(image,(640,640))
                        # with pyvirtualcam.Camera(width=512, height=512, fps=25) as cam:
                        cam.send(self.image)
                        cam.sleep_until_next_frame()
                        continue

                        # print("22222222222222222")
                    else:
                        self.start_time = None
                        # print("22222222222222222-1")
                        continue
                    
                    

                prompt = self.prompt_queue.get(1)

                sd_get_url = self.sd_url + prompt
                r = requests.get(sd_get_url)
                with open('test.jpg', 'wb') as file: #保存到本地的文件名
                    file.write(r.content)
                  

                self.image = cv2.imread("test.jpg")
                # 转换为RGB：由于 cv2 读出来的图片默认是 BGR，因此需要转换成 RGB
                # image = cv2.resize(image,(640,640))
                self.image = self.image[:, :, [2, 1, 0]]
                # with pyvirtualcam.Camera(width=512, height=512, fps=25) as cam:
                #     print(f'Using virtual camera: {cam.device}')
                #     cam.send(image)
                #     cam.sleep_until_next_frame()

                # print("33333333333333333")

                self.start_time = time.time()


if __name__ == '__main__':

    prompt_queue = queue.Queue()
    sd_url = "http://10.10.15.106:8068/sd/"
    sd_thread = MyThread(sd_url,prompt_queue)

    sd_thread.start()
    prompt_queue.put("红色衣服蓝色头发的美女")
    print("-----------")


