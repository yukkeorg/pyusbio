#/usr/bin/env python
# coding: utf-8

import sys
import time
from pyusbio import USBIO

N_PORT_GROUP = 3

BIT_COUNT = 0
BIT_BONUS = 1
BIT_COMBO = 2
BIT_TOTALCOUNT = 3
BIT_GROUP = 4

def main():
  usbio = USBIO()
  if not usbio.find_and_init():
    return 1

  is_on = 0
  counts = [0]*(N_PORT_GROUP * BIT_GROUP)
  while 1:
    port0, port1 = usbio.send2read()
    save_port = port = (port1 << 8) + port0 
    for i in xrange(N_PORT_GROUP):
      p = port & 0x0f;
      port = port >> 4
      for j in (BIT_COUNT, BIT_BONUS, BIT_COMBO):
        idx = i * BIT_GROUP + j
        tbit = 1 << idx
        if p & (1 << j):
          if not (is_on & tbit):
            is_on = is_on | tbit
            counts[idx] += 1
            if j == BIT_COUNT:
              counts[i*N_PORT_GROUP+BIT_TOTALCOUNT] += 1
        else:
          if is_on & tbit:
            is_on = is_on & (~tbit)
            if j == BIT_BONUS:
              counts[i*N_PORT_GROUP+BIT_COUNT] = 0

    countstr = ""
    for c in counts:
      countstr += ("{0:05d} ".format(c))
    sys.stderr.write("0x%04x 0x%04x %s\r" % (save_port, is_on, countstr))
    time.sleep(0.2)

if __name__ == '__main__':
  main()
