
# Version: Test
from distutils.core import setup
import py2exe

setup(console=['cdp2p0.py'],
      packages=['api', 'gui', 'AppData','bin', 'chassis_controller'],
      )