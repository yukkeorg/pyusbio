#!/usr/bin/env python
# coding: utf-8

import sys
from optparse import OptionParser
from pyusbio import USBIO

def toInt(val):
  if val is None:
    return None

  if isinstance(val, (int, long)):
    return val

  val = val.lower()
  if val[0:2] == "0x":
    return int(val, 16)
  elif val[0:2] == "0b":
    return int(val, 2)
  elif val[0] == "0":
    return int(val, 8)
  else:
    return int(val, 10)


def main():
  parser = OptionParser()
  parser.add_option("--enable-pullup", action="store_true", dest="is_pullup", help="Enable Port1 pullup.")
  parser.add_option("--disable-pullup", action="store_false", dest="is_pullup", help="Disable Port1 pullup.")
  parser.add_option("--port1", dest="port1", help="Port1 pin setting. 0bxxxxxxxx [7..0], x=[0:Out, 1:In]")
  parser.add_option("--port2", dest="port2", help="Port2 pin setting. 0b0000xxxx [3..0], x=[0:Out, 1:In]")
  parser.add_option("--init1", dest="init1", help="Port1 initilaize value. (ORIG only)")
  parser.add_option("--init2", dest="init2", help="Port2 initialize value. (ORIG only)")

  if len(sys.argv) < 2:
    parser.print_help()
    sys.exit(1)

  (opts, args) = parser.parse_args()

  dev = USBIO()
  if not dev.find_and_init():
    print("USB-IO is not found.")
    sys.exit(1)

  oldsc = dev.getSysConf()
  sc = oldsc.copy()
  if not opts.is_pullup is None:
    sc.is_pullup = opts.is_pullup 
  sc.portIO = ((toInt(opts.port1) if opts.port1 is not None else sc.portIO[0]), 
               (toInt(opts.port2) if opts.port2 is not None else sc.portIO[1]))
  sc.init = ((toInt(opts.init1) if opts.init1 is not None else sc.init[0]), 
             (toInt(opts.init2) if opts.init2 is not None else sc.init[1]))
  dev.setSysConf(sc)
  print dev.getSysConf()
  print "Setting Complete. You most reconect USB-IO from your PC."


if __name__ == '__main__':
  main()
