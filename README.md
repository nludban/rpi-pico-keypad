# rpi-pico-keypad
PIO keypad matrix driver for Raspberry Pi pico

## Summary

This project uses micropython and PIO to scan the switch matrix of a
scavenged USB number keypad.
Design and availability of the keypad is subject to the whims of the
manufacturer, so it's more of a process HOWTO than a completed project.

## Hardware

(pic - donor)

The USB keypad is a couple years old (2021?), selected based on number
of positive reviews and the "mx" style switches allowing the keycaps
to be replaced.
The original intent was to plug the USB into a Raspberry Pi, open the
raw USB device, and remap the keys in the application, but the
microcontroller in the keypad implemented extra features that made it
difficult to use this way:

(from memory)
1. Function key was used internally, never sent as a keypress
2. Macros and programming suspended keypress events
3. Multiple keys held resulted in a stream of events, rules TBD

The case opened easily after removing keycaps to reveal the screws.

(pic - front)

Keycaps are "ma" profile - mostly Blue Cat style, remainders from a
full set of caps used on a tenkeyless keyboard.

## Wiring

The USB cable and U1 (microcontroller) were first desoldered.

A digital multimeter in continuity mode was used to figure out which
key switch pins were connected in rows and columns.
While the keys are in a 4x6 pattern, the matrix turned out to be 5x7
with traces skipping around quite a bit.

24 gauge wires were soldered to the terminals of the edge key switches
with the other ends collected into connectors to the pico board.

The current from continuity mode was enough to light up the LEDs, the
backlights and numlock indicator were found to be powered from USB with
the backlight switched through a FET and the numlock ground switched
through the microcontroller.
LED power wires were soldered to the USB pads.
A control wire for the backlight was soldered in place of a zero ohm
resistor while the control wire for numlock was soldered directly to
the LED for strength.


##
