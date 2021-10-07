# PyCoil
#### Language: Python
Code to drive a 3-axis Helmholtz coil with a GUI (based on a Contec AO-1604LX-USB analog output device)

---

This was one of my very first Python projects, so please don't slap me for some very complicated code structure. However, the project grew over time and has some nice features (which are obviously very specific to my needs). All it does is to drive an Analog Output device (Contec AO-1604LX-USB), which was connected to an amplifier and a custom 3-axis electromagnet.

The GUI is able to create a constant magnet field and time-varying fields (i.e. sine waves) in arbitrary directions. The magnetic field amplitude can be calibrated manually by measuring the real field in the coil with a Gauss-Meter or a simple Hall sensor.

Any GUI action is automatically logged into a .txt file. This was quite helpful when the magnetic fields were synchronized with other equipments such as cameras.

---

**Note:** The low level communication with the AO device can be found in <code>Caio_ctype.py</code> and was written by somebody else:
https://github.com/cboulay/caio_python

---
