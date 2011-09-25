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
  parser.add_option("--show", action="store_true", dest="show", help="Display USB-IO System config.")
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

  _sc = dev.getSysConf()
  if opts.show:
    print("Port2 Pullup : {0}".format("Enable" if _sc.is_pullup else "Disable"))
    print("Port1 Pin setting : {0:0>8b}(0x{0:02x})".format(_sc.port1))
    print("Port2 Pin setting : {0:0>8b}(0x{0:02x})".format(_sc.port2))
    print("Port1 Pin init value : {0:0>8b}(0x{0:02x})".format(_sc.init1))
    print("Port2 Pin init value : {0:0>8b}(0x{0:02x})".format(_sc.init2))
    sys.exit(0)
    
    
  sc = _sc.copy()
  if not opts.is_pullup is None:
    sc.is_pullup = opts.is_pullup 
  sc.port1 = toInt(opts.port1) if opts.port1 is not None else sc.port1
  sc.port2 = toInt(opts.port2) if opts.port2 is not None else sc.port2
  sc.init1 = toInt(opts.init1) if opts.init1 is not None else sc.init1
  sc.init2 = toInt(opts.init2) if opts.init2 is not None else sc.init2
  dev.setSysConf(sc)

  print("Setting Complete. ")
  print("NOTICE:If you use this settings, You most reconnect USB-IO from your PC.")


if __name__ == '__main__':
  main()
