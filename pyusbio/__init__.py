#!/usr/bin/env python

import usb.core
import usb.util

# Device Information
VENDOR_ID = 0x1352       # Km2Net
PRODUCT_ID_ORIG = 0x0120 # USB-IO2.0 ORIGINAL
PRODUCT_ID_AKI = 0x0121  # USB-IO2.0(AKI)

# Command list
CMD_READ_SEND = 0x20
CMD_SEND_READ = 0x21
CMD_SEND_REPEAT = 0x22
CMD_FLASHROM_READ = 0xf0
CMD_FLASHROM_WRITE = 0xf1
CMD_SYSCONF_READ = 0xf8
CMD_SYSCONF_WRITE = 0xf9

TIMEOUT = 5000
MAX_CMD_LENGTH = 64


class USBIO(object):
  def __init__(self):
    self.device = None
    self.is_aki = False
    self.inEpAddr = 0
    self.outEpAddr = 0
    self._seq = 0

  def find_and_init(self):
    for product_id in (PRODUCT_ID_ORIG, PRODUCT_ID_AKI):
      self.device = usb.core.find(idVendor=USBIO.VENDOR_ID, idProduct=product_id)
      if self.device:
        if product_id == PRODUCT_ID_AKI:
          self.is_aki = True
        print("USB-IO(0x{0:x}, 0x{1:x}) is found.".format(VENDOR_ID, product_id))
        break
    if not self.device:
      print("USB-IO Device is NOT found.")
      return False

    for cnf in self.device:
      for ifc in cnf:
        for ep in ifc:
          if ep.bEndpointAddress & usb.util._ENDPOINT_DIR_MASK:
            self.inEpAddr = ep.bEndpointAddress
            print("IN endpoint address of interface {0} : 0x{1:x}" \
                   .format(ifc.bInterfaceNumber, ep.bEndpointAddress))
          else:
            self.outEpAddr = ep.bEndpointAddress
            print("OUT endpoint address of interface {0} : 0x{1:x}" \
                   .format(ifc.bInterfaceNumber, ep.bEndpointAddress))

        if self.device.is_kernel_driver_active(ifc.bInterfaceNumber):
          self.device.detach_kernel_driver(ifc.bInterfaceNumber)
          print("interface {0} of USB-IO was detached from the kernel driver." \
                   .format(ifc.bInterfaceNumber))
    return True


  def _cmd(self, command, writedata=None, do_read=True, cmdsize=MAX_CMD_LENGTH):
    self._seq = (self._seq + 1) & 0xff

    cmd = [0x00] * cmdsize
    cmd[0] = command
    cmd[cmdsize-1] = self._seq

    if writedata:
      length = len(writedata)
      if length > cmdsize-2: length = cmdsize-2
      for i in xrange(length):
        cmd[i+1] = writedata[i]

    sendsize = self.device.write(self.outEpAddr, cmd, 0, TIMEOUT)
    if sendsize != cmdsize:
      return False

    if do_read:
      data = self.device.read(self.inEpAddr, cmdsize, TIMEOUT)
      if data[0] != cmd[0] or data[cmdsize-1] != cmd[cmdsize-1]:
        raise ValueError, "Different recived data."
      return data[1:cmdsize-1]
    else:
      return True


  def send2read(self, setdata=None):
    return (self._cmd(CMD_READ_SEND, writedata=setdata))[0:2]

  def getSysConf(self):
    sc = SysConf()
    return sc.fromArray(self._cmd(CMD_SYSCONF_READ))

  def setSysConf(self, sysconf):
    if not isinstance(sysconf, SysConf):
      raise TypeError, "sysconf is not SysConf type."
    return self._cmd(CMD_SYSCONF_WRITE, writedata=sysconf.toArray(), do_read=False)


class SysConf(object):
  def __init__(self, is_pullup=True, port1=0x00, port2=0x0f, init1=0x00, init2=0x00):
    self.is_pullup = is_pullup
    self.port1 = port1
    self.port2 = port2
    self.init1 = init1
    self.init2 = init2

  def toArray(self):
    data = [0] * (MAX_CMD_LENGTH - 2)
    data[1] = 0 if self.is_pullup else 1
    data[4] = self.port1
    data[5] = self.port2
    data[8] = self.init1
    data[9] = self.init2
    return data

  def fromArray(self, data):
    self.is_pullup = (data[1] == 0)
    self.port1 = data[4]
    self.port2 = data[5]
    self.init1 = data[8]
    self.init2 = data[9]
    return self

  def copy(self):
    return SysConf(self.is_pullup, self.port1, self.port2, self.init1, self.init2)

  def __repr__(self):
    return "<SysConf is_pullup={is_pullup}, portIO={portIO}, init={init}>".format(**self.__dict__)
