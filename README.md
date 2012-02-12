pyusbio
=======

使い方
------
    >>> import pyusbio
    >>> usbio = usbio.USBIO()
    >>> if usbio.find_and_init():
    ...   port0, port1 = usbio.send2read([0x00, 0x01])
    ...   print("{0:x}, {1:x}".format(port0, port1))

制限事項
--------
 * 現在１つのUSB-IOしか認識できません。
 * 動作を確認しているOSはLinuxのみとなります。
 　Windows環境での動作テストを行なっていません。 

ライセンス
----------
 2条項BSDライセンス
 2-clause BSD License

おまけ
------
付属のusbio\_config.pyは、USB-IO2.0の内部設定を変更するツールです。  
使い方については、 python usbio\_config.py --help で表示されるヘルプ情報を参照してください。
