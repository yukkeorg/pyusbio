pyusbio
=======

これは、[USB-IO2.0](http://km2net.com/usb-io2.0/index.shtml)をコントロールする
ためのライブラリです。


使い方
------
    >>> import pyusbio
    >>> usbio = usbio.USBIO()
    >>> if usbio.find_and_init():
    ...   port0, port1 = usbio.send2read([0x00, 0x01])
    ...   print("{0:x}, {1:x}".format(port0, port1))


必須依存ライブラリ
------------------

* [PyUSB](https://github.com/pyusb/pyusb)


動作を確認しているOS
--------------------

* Linux (Debian Sid)
* Windows10


対応Python
-------

Python3.6以上  
(Python2系列は未サポートです。)


制限事項
--------

* １つのUSB-IO2.0しか認識できません。


ライセンス
----------

MIT


おまけ
------

付属のusbio\_config.pyは、USB-IO2.0の内部設定を変更するツールです。
使い方については、 python usbio\_config.py --help で表示されるヘルプ情報を参照してください。
