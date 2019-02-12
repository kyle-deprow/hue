#! /usr/bin.env python
import serial
import time
import struct
import numpy as np

class ArduinoController():

    def __init__(self, port = None, baudrate = 57600, timeout = .25):
        self.ser = None
        if port:
            self.init_port(port,baudrate,timeout)

    def send_receive(self,arduino_case,msg=None,encoding=None,incoming_msgsize=1):
        if self.ser:
            packet = bytearray(struct.pack('B',arduino_case))
            if msg:
                packet += struct.pack(encoding,msg)

            response = self.send_receive_arduino(packet, incoming_msgsize)
            return response[1:]

        else:
            print ('Serial Communication not Established')

    def send_receive_arduino(self,packet,incoming_msgsize):
        checksum = sum(packet) & 0xFF
        checksum_received = None
        resend_count = 0

        while checksum_received != checksum:
            # Simple error handling only used if repeating loop
            if (checksum_received):
                if (resend_count < 1e2):
                    #print('Checksum did not agree! Resending', packet[0], checksum, checksum_received)
                    resend_count += 1
                    time.sleep(0.001)
                else:
                    print('Message Timeout to Arduino')
                    raise RuntimeError

            # write outgoing_packet
            self.ser.write(packet)

            # Read data packet off of serial line, we know how large this data should be..
            data = self.ser.read(incoming_msgsize)
             
            if len(data) < incoming_msgsize:
                checksum_received = None
                time.sleep(0.001)
            else:
                checksum_received = struct.unpack('B', data[0])[0]

        return data

    def init_port(self, port, baudrate, timeout = 0.25):
        if self.ser:
            self.ser.close()
        else:
            self.ser = serial.Serial(port = port, baudrate = baudrate, timeout = timeout)
            time.sleep(2)
            count = 0
            while not self.ser.isOpen():
                count += 1
                if count > 1e5:
                    raise RuntimeError
            self.ser.flushInput()
            self.ser.flushInput()
            self.ser.flushInput()
            self.ser.flushOutput()
            self.ser.flushOutput()
            self.ser.flushOutput()

    def close_port(self):
        if self.ser:
            self.ser.close()

if ( __name__ == "__main__" ):
    arduino = frequency_controller(port = '/dev/ttyARDUINO', baudrate = 57600)
