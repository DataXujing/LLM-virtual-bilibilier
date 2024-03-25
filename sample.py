# -*- coding: utf-8 -*-
import asyncio
import http.cookies
import random
from typing import *

import aiohttp

import blivedm
import blivedm.models.web as web_models

import pygame
# from playsound import playsound
# import openai
import logging as log
import requests
import json

import subprocess

import time
import edge_tts

from virtualcam import *
import queue

import configparser
config = configparser.ConfigParser() # 类实例化

# ----------定义config文件路径-----------------
config.read('config.ini',encoding="utf-8")
room_id = config.get('bilibili','room_id')
llm_url = f"http://{config.get('llm','host')}:{config.get('llm','port')}/llm/"
sd_url = f"http://{config.get('sd','host')}:{config.get('sd','port')}/sd/"
tts_url = f"http://{config.get('tts','host')}:{config.get('tts','port')}/tts/"
sd_prefix = config.get('sd','prefix')  #"画"

speaker = config.get('tts','speaker')

print("你的直播间ID是：{}".format(room_id))
print("你选择的AI语音是：{}".format(speaker))
print("配置完成，程序开始运行...")   


pygame.init()
pygame.mixer.init()

# 开启虚拟摄像头线程
prompt_queue = queue.Queue()
sd_thread = MyThread(sd_url,prompt_queue)
sd_thread.start()

# 直播间ID的取值看直播间URL
TEST_ROOM_IDS = [
    room_id,
]

# 这里填一个已登录账号的cookie的SESSDATA字段的值。不填也可以连接，但是收到弹幕的用户名会打码，UID会变成0
SESSDATA = ''

session: Optional[aiohttp.ClientSession] = None


async def main():
    init_session()
    try:
        await run_single_client()
        await run_multi_clients()
    finally:
        await session.close()


def init_session():
    cookies = http.cookies.SimpleCookie()
    cookies['SESSDATA'] = SESSDATA
    cookies['SESSDATA']['domain'] = 'bilibili.com'

    global session
    session = aiohttp.ClientSession()
    session.cookie_jar.update_cookies(cookies)


async def run_single_client():
    """
    演示监听一个直播间
    """
    room_id = random.choice(TEST_ROOM_IDS)
    client = blivedm.BLiveClient(room_id, session=session)
    handler = MyHandler()
    client.set_handler(handler)

    client.start()
    try:
        # 演示5秒后停止
        await asyncio.sleep(5)
        client.stop()

        await client.join()
    finally:
        await client.stop_and_close()


async def run_multi_clients():
    """
    演示同时监听多个直播间
    """
    clients = [blivedm.BLiveClient(room_id, session=session) for room_id in TEST_ROOM_IDS]
    handler = MyHandler()
    for client in clients:
        client.set_handler(handler)
        client.start()

    try:
        await asyncio.gather(*(
            client.join() for client in clients
        ))
    finally:
        await asyncio.gather(*(
            client.stop_and_close() for client in clients
        ))


class MyHandler(blivedm.BaseHandler):
    # # 演示如何添加自定义回调
    # _CMD_CALLBACK_DICT = blivedm.BaseHandler._CMD_CALLBACK_DICT.copy()
    #
    # # 入场消息回调
    # def __interact_word_callback(self, client: blivedm.BLiveClient, command: dict):
    #     print(f"[{client.room_id}] INTERACT_WORD: self_type={type(self).__name__}, room_id={client.room_id},"
    #           f" uname={command['data']['uname']}")
    # _CMD_CALLBACK_DICT['INTERACT_WORD'] = __interact_word_callback  # noqa

    def _on_heartbeat(self, client: blivedm.BLiveClient, message: web_models.HeartbeatMessage):
        print(f'[{client.room_id}] 心跳')

    def _on_danmaku(self, client: blivedm.BLiveClient, message: web_models.DanmakuMessage):
        print(f'[{client.room_id}] {message.uname}：{message.msg}')


        if sd_prefix == message.msg[:len(sd_prefix)]: #<------------启动词，如果是 “画”开始的，就调stable diffusion
            message.msg = message.msg.replace(sd_prefix, '')

            prompt_queue.put(message.msg)
            answer = "完成" + message.msg +"的作画"

        elif len(message.msg) > 0:  # 开始调大模型
            llm_get_url = llm_url + message.msg
            r = requests.get(llm_get_url)
            r.encoding="utf-8"
            answer = json.loads(r.text)["llm_response"]
            print(answer) 

      
        # TTS
        answer = answer.replace('\n','')
        # gk = message.uname +','+'说'+','+ message.msg
        # #answer2由gk和answer组成
        # answer2 = gk +'。' + answer
        answer2 = answer

        # command = f'edge-tts --rate=+10% --voice "{speaker}" --text "{answer2}" --write-media test.mp3'    
        # # 开启新进程,TTS目前对长文本还太慢，需要改进，目前只是demo
        # subprocess.run(command, shell=True)
        # # WEBVTT_FILE = "test.vtt"
        # # submaker = edge_tts.SubMaker()
        # # with open(WEBVTT_FILE, "w", encoding="utf-8") as file:  
        # #     file.write(submaker.generate_subs())   
        # # WEBVTT_FILE2 = "test.txt"
        # # with open(WEBVTT_FILE2, "w", encoding="utf-8") as file:
        # #     #写入提问、换行、回答    
        # #     file.write(f'{answer}')
        tts_get_url = tts_url + answer2
        r = requests.get(tts_get_url)
        with open('test.mp3', 'wb') as file: #保存到本地的文件名
            file.write(r.content)
            file.flush()
        print('TTS over...')

        # 初始化 Pygame
        pygame.mixer.init()
        # 加载语音文件
        pygame.mixer.music.load("test.mp3")
        # 播放语音
        pygame.mixer.music.play()
        # 等待语音播放结束
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

        # 退出临时语音文件
        pygame.mixer.quit()

        #playsound("./test.mp3")
        print("audio play over...")

    

    def _on_gift(self, client: blivedm.BLiveClient, message: web_models.GiftMessage):
        print(f'[{client.room_id}] {message.uname} 赠送{message.gift_name}x{message.num}'
              f' （{message.coin_type}瓜子x{message.total_coin}）')

    def _on_buy_guard(self, client: blivedm.BLiveClient, message: web_models.GuardBuyMessage):
        print(f'[{client.room_id}] {message.username} 购买{message.gift_name}')

    def _on_super_chat(self, client: blivedm.BLiveClient, message: web_models.SuperChatMessage):
        print(f'[{client.room_id}] 醒目留言 ¥{message.price} {message.uname}：{message.message}')


if __name__ == '__main__':
    asyncio.run(main())

    sd_thread.join()