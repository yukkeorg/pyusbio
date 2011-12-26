# coding: utf-8

# Copyright (c) 2011, Yusuke Ohshima
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without modification, 
# are permitted provided that the following conditions are met:
# 
#   - Redistributions of source code must retain the above copyright notice, 
#     this list of conditions and the following disclaimer.
# 
#   - Redistributions in binary form must reproduce the above copyright notice, 
#     this list of conditions and the following disclaimer in the documentation 
#     and/or other materials provided with the distribution.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND 
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED 
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. 
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, 
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, 
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, 
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY 
# OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE 
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF 
# THE POSSIBILITY OF SUCH DAMAGE.

import sys
import usb.core
import usb.util

import logging
logger = logging.getLogger('USBIO')


# Device Information
VENDOR_ID = 0x1352       # Km2Net
PRODUCT_ID_ORIG = 0x0120 # USB-IO2.0 ORIGINAL
PRODUCT_ID_AKI = 0x0121  # USB-IO2.0(AKI)

# Number of ports
N_PORT1 = 8
N_PORT2 = 4
N_PORT = N_PORT1 + N_PORT2

# Command list
# Detail to see : http://km2net.com/usb-fsio/command.shtml
CMD_READ_SEND = 0x20
CMD_SEND_READ = 0x21
CMD_SEND_REPEAT = 0x22
CMD_FLASHROM_READ = 0xf0
CMD_FLASHROM_WRITE = 0xf1
CMD_SYSCONF_READ = 0xf8
CMD_SYSCONF_WRITE = 0xf9

MAX_CMD_LENGTH = 64


class USBIO(object):
  def __init__(self, timeout=5000):
    self.device = None
    self.is_aki = False
    self.inEpAddr = 0
    self.outEpAddr = 0
    self._seq = 0
    self._timeout = timeout


  def find_and_init(self):
    for product_id in (PRODUCT_ID_ORIG, PRODUCT_ID_AKI):
      self.device = usb.core.find(idVendor=VENDOR_ID, idProduct=product_id)
      if self.device:
        if product_id == PRODUCT_ID_AKI:
          self.is_aki = True
        logger.info("USB-IO(0x{0:x}, 0x{1:x}) is found.".format(VENDOR_ID, product_id))
        break
    if not self.device:
      logger.error("USB-IO Device is NOT found.")
      return False

    for cnf in self.device:
      for ifc in cnf:
        for ep in ifc:
          if ep.bEndpointAddress & usb.util._ENDPOINT_DIR_MASK:
            self.inEpAddr = ep.bEndpointAddress
            logger.debug("IN endpoint address of interface {0} : 0x{1:x}" \
                   .format(ifc.bInterfaceNumber, ep.bEndpointAddress))
          else:
            self.outEpAddr = ep.bEndpointAddress
            logger.debug("OUT endpoint address of interface {0} : 0x{1:x}" \
                   .format(ifc.bInterfaceNumber, ep.bEndpointAddress))

        if self.device.is_kernel_driver_active(ifc.bInterfaceNumber):
          self.device.detach_kernel_driver(ifc.bInterfaceNumber)
          logger.info("interface {0} of USB-IO was detached from the kernel driver." \
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

    sendsize = self.device.write(self.outEpAddr, cmd, timeout=self._timeout)
    if sendsize != cmdsize:
      return False

    if do_read:
      data = self.device.read(self.inEpAddr, cmdsize, timeout=self._timeout)
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
