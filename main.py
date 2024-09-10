import time
import xiaomi_pb2
from google.protobuf import message
import os
import secrets
import binascii
import asyncio
from bleak import BleakClient

XIAOMI_AuthServ_DEV2BAND = "00000052-0000-1000-8000-00805f9b34fb"
XIAOMI_AuthServ_BAND2DEV = "00000051-0000-1000-8000-00805f9b34fb"
Mac="D0:62:2C:0F:0C:C0"
#***********************************************Part 1 验证**********************************************
CMD_TYPE_AUTH = 1
CMD_TYPE_SYSTEM = 2
CMD_AUTH_NONCE = 26
CMD_AUTH_AUTH = 27
# 生成一个长度为 16 字节的随机字节串
nonce_length = 16  # 根据需要调整长度
nonce = secrets.token_bytes(nonce_length)

PackHead = b'\x00\x00\x02\x02' 

#Step 1 创建随机数命令
def CreateNonceCommand():
    # 创建 PhoneNonce 对象
    phone_nonce = xiaomi_pb2.PhoneNonce()
    phone_nonce.nonce = nonce
    # 创建 Auth 对象
    auth = xiaomi_pb2.Auth()
    auth.phoneNonce.CopyFrom(phone_nonce)
    # 创建 Command 对象
    command = xiaomi_pb2.Command()
    command.type = CMD_TYPE_AUTH
    command.subtype = CMD_AUTH_NONCE
    command.auth.CopyFrom(auth)
    # 将 Command 对象转换为字节数组
    byte_array =PackHead +  command.SerializeToString()
    hex_string = ' '.join(f'{byte:02x}' for byte in byte_array)
    print(hex_string)  # 打印 Protobuf 序列字符串
    return byte_array

#Step 2 步骤1手环回复的解析
def AuthFeedBackAnaly(data):
    output_numbers = list(data)
    deserialized_message = xiaomi_pb2.Command()
    deserialized_message.ParseFromString(data)
    if(deserialized_message.subtype == CMD_AUTH_NONCE):
        print("阶段1，拿到手环随机数")
    print("Deserialized Data message:", deserialized_message)
    print("手环回复")
    print(output_numbers)




#***********************************************Part 2 通信**********************************************
def notification_handler(sender, data):
    AuthFeedBackAnaly(data[4:])
    




#***********************************************Part 3 主程序**********************************************
test =b'\x00\x00\x02\x02\x08\x01\x10\x1a\x1a\x15\xf2\x01\x12\x0a\x10\xf0\x18\x33\x73\x47\xc7\x65\xa8\x26\x25\x21\x05\xe0\x0e\x1f\x25'
async def main(address):
    global cmd
    client = BleakClient(address)
    print("连接中")
    client._timeout=100
    await client.connect()
    await asyncio.sleep(5.0)
    await client.start_notify(XIAOMI_AuthServ_BAND2DEV, notification_handler)
    print("验证中")
    await asyncio.sleep(2.0)
    await client.write_gatt_char(XIAOMI_AuthServ_DEV2BAND,CreateNonceCommand())
    while True:
        await asyncio.sleep(5.0)
asyncio.run(main(Mac))