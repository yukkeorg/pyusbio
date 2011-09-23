#!/usr/bin/env python
# coding: utf-8

import sys
import time
from pyusbio import USBIO

def main():
  usbio = USBIO()
  if not usbio.find_and_init():
    return 1

  is_on = False
  count = 0
  while 1:
    port0, port1 = usbio.send2read()
    if port1 & 0x01 == 1:
      if not is_on:
        count += 1
        is_on = True
    else:
      is_on = False
    sys.stderr.write("0x%x  %-5d\r" % (port1, count))
    time.sleep(0.1)

if __name__ == '__main__':
  main()
