# PyCoil
#### Language: Python
Code to drive a 3-axis Helmholtz coil with a GUI (based on a Contec AO-1604LX-USB analog output device)

---

This was one of my very first Pyton projects, so please don't slap me for some very complicated code structure. However, it grew over time and all it does is to drive an Analog Output device (Contec AO-1604LX-USB), which was connected to an amplifier and a custom 3-axis electromagnet.
The GUI was able to create a constant magnet field and time-varying fields in arbitrary directions.

**Note: The low level communication with the AO device can be found in <code>Caio_ctype.py</code> and was written by somebody else:
https://github.com/cboulay/caio_python
