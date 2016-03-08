# -*- coding: utf-8 -*-

import time
from serial import rs485
import serial
from serial.tools.list_ports import comports
from hextools import *
import binascii

class SerialPortProblem(Exception):
    pass

class OledButton(object):
    '''
    oled cy-7031
    The OLED BUTTON SWITCH and DISPLAY MODULE programmable into different images.
    '''
    
    def __init__(self):
        self.mode = "RS232" # "RS232", "RS485"
        self.device_id = 1
        self.package_base = self.get_package_base()
        self.serial = None
        
    def connect(self, port='COM5'):
        ports = []
        for n, (port, desc, hwid) in enumerate(sorted(comports()), 1):
            ports.append(port)
        if (len(ports) == 0) or not (port in ports):
            raise SerialPortProblem("Connect button!")
        
        if self.mode == "RS232":
            self.serial = serial.Serial(port, baudrate=115200, timeout=1, write_timeout=1, inter_byte_timeout=0.1)
        elif self.mode == "RS485":
            self.serial = rs485.RS485(port, 115200, timeout=1)
            self.serial.rs485_mode = rs485.RS485Settings()
        
        if self.serial.is_open:
            self.serial.close()
        self.serial.open()
    
    def disconnect(self):
        self.serial.close()

    def get_package_base(self):
        package = bytearray()
        package.append(0x1B)
        package.append(self.device_id)
        package.append(0xFF - self.device_id)
        return package
    
    def send(self, payload) :
        command = bytearray(self.package_base)
        if type(payload) is str:
            command += bytes(payload, 'utf-8')
        elif type(payload) is bytes or type(payload) is bytearray:
            command.extend(payload)
        else:
            raise SerialPortProblem("Not supported payload format: %s" % type(payload))
        
        # handle with transmit buffer
        
        def write_and_echo(b):
            #string = binascii.b2a_qp(b).decode("utf-8")
            #wr.write(string + "\n\n")
            self.serial.write(b)
            
        init_l = 7
        if init_l > 0:
            write_and_echo(command[:init_l])
            self.serial.flush()
            time.sleep(0.1)
        packet_l = 1024
        if len(command) > packet_l: 
            for i in range(init_l, len(command), packet_l):
                end_i = min(i + packet_l, len(command))
                chunk = command[i:end_i]
                write_and_echo(chunk)
                self.serial.flush()
                time.sleep(0.1)
            #wr.close()
        else:
            return self.serial.write(command)
        
    def display_internal_image(self, id):
        self.send("D" + str(id).zfill(3)) # D000, D001, ... D024
    
    def save_image(self, id):
        self.send("S" + str(id).zfill(3)) # S000, S001, ... S024
        
    def on(self):
        self.send("d1")
        
    def off(self):
        self.send("d0")
    
    def set_brightness(value):
        self.send("B" + str(id).zfill(2))
        
    def transfer_image(self, filename):
        payload = bytearray()
        payload.append(chr2hex("G"))
        data = get_rgb565_bytes_from_image(filename)
        length = len(data)
        length_b = int2bytes(length, 4)
        payload.extend(length_b)
        payload.append(chr2hex("S"))
        payload.extend(data)
        self.send(payload)

    def get_info(self):
        self.send("I")
        direction = self.serial.read(3).decode("cp437") 
        print(direction)
        product_info = self.serial.read(12).decode("cp437") 
        print("Product ID", product_info[:7])
        print("firmware version", product_info[7:])
        
    def is_pressed(self):
        self.send("T")
        state = self.serial.read(3).decode("cp437")
        return state[-1] == '1'
        
    def response(self):
       result_hex = self.serial.read(5)
       result = hex2str(result_hex)
       print("response", result)
       return result[-2:] == 'OK'
