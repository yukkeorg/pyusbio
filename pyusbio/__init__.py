#!/usr/bin/env python

import time
import usb.core
import usb.util


class USBIO(object):
  VENDOR_ID = 0x1352      # Km2Net
  PRODUCT_ID_ORIG = 0x0120 # USB-IO2.0 ORIGINAL
  PRODUCT_ID_AKI = 0x0121  # USB-IO2.0(AKI)

  def __init__(self):
    self.device = None
    self.is_aki = False
    self.inEpAddr = 0
    self.outEpAddr = 0
    self._seq = 0

  def find_and_init(self):
    for product_id in (USBIO.PRODUCT_ID_ORIG, USBIO.PRODUCT_ID_AKI):
      self.device = usb.core.find(idVendor=USBIO.VENDOR_ID, idProduct=product_id)
      if self.device:
        if product_id == USBIO.PRODUCT_ID_AKI:
          self.is_aki = True
        print("USB-IO(0x{0:x}, 0x{1:x}) is found.".format(USBIO.VENDOR_ID, product_id))
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


  def _cmd(self, command, writedata=None, do_read=True, cmdsize=64):
    self._seq = (self._seq + 1) & 0xff

    cmd = [0x00] * cmdsize
    cmd[0] = command
    cmd[cmdsize-1] = self._seq

    if writedata:
      length = len(writedata)
      if length > cmdsize-2: length = cmdsize-2
      for i in xrange(length):
        cmd[i+1] = writedata[i]

    sendsize = self.device.write(self.outEpAddr, cmd, 0, 5000)
    if sendsize != cmdsize:
      return False

    if do_read:
      data = self.device.read(self.inEpAddr, cmdsize)
      if data[0] != cmd[0] or data[cmdsize-1] != cmd[cmdsize-1]:
        raise ValueError, "Different recived data."
      return data[1:cmdsize-1]
    else:
      return True


  def send2read(self, setdata=None):
    return (self._cmd(0x20, writedata=setdata))[0:2]

  def getSysConf(self):
    sc = SysConf()
    return sc.fromArray(self._cmd(0xf8))

  def setSysConf(self, sysconf):
    if not isinstance(sysconf, SysConf):
      raise TypeError, "sysconf is not SysConf type."
    return self._cmd(0xf9, writedata=sysconf.toArray(), do_read=False)


class SysConf(object):
  def __init__(self, is_pullup=True, portIO=None, init=None):
    self.is_pullup = is_pullup
    self.portIO = portIO or (0x00, 0x0f)
    self.init = init or (0x00, 0x00)

  def toArray(self):
    data = [0] * 62
    data[1] = 0 if self.is_pullup else 1
    data[4],data[5] = self.portIO
    data[8],data[9] = self.init
    return data

  def fromArray(self, ar):
    self.is_pullup = (ar[1] == 0)
    self.portIO = (ar[4], ar[5])
    self.init = (ar[8], ar[9])
    return self

  def copy(self):
    return SysConf(self.is_pullup, self.portIO, self.init)

  def __repr__(self):
    return "<SysConf is_pullup={is_pullup}, portIO={portIO}, init={init}>".format(**self.__dict__)
