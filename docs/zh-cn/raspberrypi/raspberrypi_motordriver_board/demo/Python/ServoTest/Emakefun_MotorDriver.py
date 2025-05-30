#!/usr/bin/python

import time
import math
from Emakefun_I2C import Emakefun_I2C

# ============================================================================
# Raspi PCA9685 16-Channel PWM Servo Driver
# ============================================================================

class PWM :
  # Registers/etc.
  __MODE1              = 0x00
  __MODE2              = 0x01
  __SUBADR1            = 0x02
  __SUBADR2            = 0x03
  __SUBADR3            = 0x04
  __PRESCALE           = 0xFE
  __LED0_ON_L          = 0x06
  __LED0_ON_H          = 0x07
  __LED0_OFF_L         = 0x08
  __LED0_OFF_H         = 0x09
  __ALL_LED_ON_L       = 0xFA
  __ALL_LED_ON_H       = 0xFB
  __ALL_LED_OFF_L      = 0xFC
  __ALL_LED_OFF_H      = 0xFD

  # Bits
  __RESTART            = 0x80
  __SLEEP              = 0x10
  __ALLCALL            = 0x01
  __INVRT              = 0x10
  __OUTDRV             = 0x04

  general_call_i2c = Emakefun_I2C(0x60)

  @classmethod
  def softwareReset(cls):
    "Sends a software reset (SWRST) command to all the servo drivers on the bus"
    cls.general_call_i2c.writeRaw8(0x06)        # SWRST

  def __init__(self, address=0x60, debug=False):
    self.i2c = Emakefun_I2C(address)
    self.i2c.debug = debug
    self.address = address
    self.debug = debug
    if (self.debug):
      print ("Reseting PCA9685 MODE1 (without SLEEP) and MODE2")
    self.setAllPWM(0, 0)
    self.i2c.write8(self.__MODE2, self.__OUTDRV)
    self.i2c.write8(self.__MODE1, self.__ALLCALL)
    time.sleep(0.005)                                       # wait for oscillator
    
    mode1 = self.i2c.readU8(self.__MODE1)
    mode1 = mode1 & ~self.__SLEEP                 # wake up (reset sleep)
    self.i2c.write8(self.__MODE1, mode1)
    time.sleep(0.005)                             # wait for oscillator

  def setPWMFreq(self, freq):
    "Sets the PWM frequency"
    prescaleval = 25000000.0    # 25MHz
    prescaleval /= 4096.0       # 12-bit
    prescaleval /= float(freq)
    prescaleval -= 1.0
    if (self.debug):
      print ("Setting PWM frequency to %d Hz" % freq)
      print ("Estimated pre-scale: %d" % prescaleval)
    prescale = math.floor(prescaleval + 0.5)
    if (self.debug):
      print ("Final pre-scale: %d" % prescale)

    oldmode = self.i2c.readU8(self.__MODE1);
    newmode = (oldmode & 0x7F) | 0x10             # sleep
    self.i2c.write8(self.__MODE1, newmode)        # go to sleep
    self.i2c.write8(self.__PRESCALE, int(math.floor(prescale)))
    self.i2c.write8(self.__MODE1, oldmode)
    time.sleep(0.005)
    self.i2c.write8(self.__MODE1, oldmode | 0x80)

  def setPWM(self, channel, on, off):
    "Sets a single PWM channel"
    #databuf = [int(on) & 0xFF , int(on) >> 8 ,int(off) & 0xFF, int(off) >> 8]
    #self.i2c.writeList(self.__LED0_ON_L + channel << 2, databuf)
    self.i2c.write8(self.__LED0_ON_L + 4 * channel, int(on) & 0xFF)
    self.i2c.write8(self.__LED0_ON_H + 4 * channel, int(on) >> 8)
    self.i2c.write8(self.__LED0_OFF_L + 4 * channel, int(off) & 0xFF)
    self.i2c.write8(self.__LED0_OFF_H + 4 * channel, int(off) >> 8)

  def setAllPWM(self, on, off):
    "Sets a all PWM channels"
    #databuf = [int(on) & 0xFF , int(on) >> 8 ,int(off) & 0xFF, int(off) >> 8]
    #self.i2c.writeList(self.__ALL_LED_ON_L, databuf)
    self.i2c.write8(self.__ALL_LED_ON_L, int(on) & 0xFF)
    self.i2c.write8(self.__ALL_LED_ON_H, int(on) >> 8)
    self.i2c.write8(self.__ALL_LED_OFF_L, int(off) & 0xFF)
    self.i2c.write8(self.__ALL_LED_OFF_H, int(off) >> 8)