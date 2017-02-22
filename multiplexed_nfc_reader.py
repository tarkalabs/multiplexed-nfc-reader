#!/usr/bin/env python

import RPi.GPIO as GPIO
import MFRC522
import signal

import spidev
import time

class MultiplexedNFCReader:
    A3 = 40 # GPIO 21
    A2 = 37 # GPIO 20
    A1 = 36 # GPIO 16
    A0 = 32 # GPIO 12

    def __init__(self, device_number):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(MultiplexedNFCReader.A3, GPIO.OUT)
        GPIO.setup(MultiplexedNFCReader.A2, GPIO.OUT)
        GPIO.setup(MultiplexedNFCReader.A1, GPIO.OUT)
        GPIO.setup(MultiplexedNFCReader.A0, GPIO.OUT)
        self.select_device(device_number)
        self.mfrfc_reader = MFRC522.MFRC522()

    def select_device(self, device_number):
        a3_value = (device_number >> 3) & 1
        a2_value = (device_number >> 2) & 1
        a1_value = (device_number >> 1) & 1
        a0_value = device_number & 1

        print "Setting value: " + str(a3_value) + " " + str(a2_value) + " " + str(a1_value) + " " + str(a0_value)

        GPIO.output(MultiplexedNFCReader.A3, a3_value)
        GPIO.output(MultiplexedNFCReader.A2, a2_value)
        GPIO.output(MultiplexedNFCReader.A1, a1_value)
        GPIO.output(MultiplexedNFCReader.A0, a0_value)

    def has_tag(self):
        (status, TagType) = self.mfrfc_reader.MFRC522_Request(self.mfrfc_reader.PICC_REQIDL)
        return status == self.mfrfc_reader.MI_OK

    def read_NFC(self):
        (status, uid) = self.mfrfc_reader.MFRC522_Anticoll()
        if status == self.mfrfc_reader.MI_OK:
            return str(uid[0])+","+str(uid[1])+","+str(uid[2])+","+str(uid[3])
        else:
            return ""

    def cleanup(self):
        GPIO.cleanup()


continue_reading = True
def end_read(signal,frame):
    global continue_reading
    print "Ctrl+C captured, ending read."
    continue_reading = False
    GPIO.cleanup()
signal.signal(signal.SIGINT, end_read)

while continue_reading:
    for device in range(0, 16):
        multiplexed_nfc_reader = MultiplexedNFCReader(device)
        print "Reading device: " + str(device)
        for _ in range(10):
            if multiplexed_nfc_reader.has_tag():
                tag_uid = multiplexed_nfc_reader.read_NFC()
                print "Card read " + str(device) + "! UID: "+ tag_uid
        multiplexed_nfc_reader.cleanup()
