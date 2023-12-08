#!micropython

'''
GP09	= numlock
GP10	= backlight
GP11-15	= 5x rows
GP16-22	= 7x columns
'''

from machine import Pin

pin_numlock = Pin(9)
pin_numlock.init(pin_numlock.OUT)
pin_numlock.value(0)	# On
pin_numlock.value(1)	# Off

pin_backlight = Pin(10)
pin_backlight.init(pin_backlight.OUT)
pin_backlight.value(0)	# On
pin_backlight.value(1)	# Off

import time

if False:
    # Flash the backlight and numlock LEDs
    for _ in range(20):
        pin_numlock.value(0)
        pin_backlight.value(0)
        time.sleep(0.5)
        pin_numlock.value(1)
        pin_backlight.value(1)
        time.sleep(0.5)

from machine import mem32 #, mem16, mem8

# peek/poke with mem32[adr]
GPIO_IN		= 0xd000_0004
GPIO_OUT	= 0xd000_0010
GPIO_OUT_SET	= 0xd000_0014
GPIO_OUT_CLR	= 0xd000_0018
GPIO_OUT_XOR	= 0xd000_001c
GPIO_OE		= 0xd000_0020
GPIO_OE_SET	= 0xd000_0024
GPIO_OE_CLR	= 0xd000_0028
GPIO_OE_XOR	= 0xd000_002c

# pico nope: Pin.OPEN_DRAIN
pins_matrix_rows = [ Pin(n, Pin.IN, Pin.PULL_UP)
                     for n in range(11, 15+1) ]
pins_matrix_cols = [ Pin(n, Pin.IN, Pin.PULL_UP)
                     for n in range(16, 22+1) ]

mem32[GPIO_OUT_CLR] = 31 << 11	# GPIO11-15=0

def scan_keys():
    rv = [ ]
    for row in range(11, 15+1):
        mem32[GPIO_OE_CLR] = 31 << 11
        mem32[GPIO_OE_SET] = 1 << row
        cols = (~(mem32[GPIO_IN] >> 16) & 0x7f)
        rv.append((row, cols))
    return rv

if False:
    # Show raw scan values
    while True:
        print()
        for row, cols in scan_keys():
            print(f'{row=} {cols=}')
        time.sleep(1)

# row=11 -- 0=2 .=4 -=8 +=1 enter=16
# row=12 -- 1=2 2=4 3=8 x=1 green=32
# row=13 -- 4=2 5=4 6=8 /=1 red=32
# row=14 -- 7=4 8=2 9=8 shift=1 fn=16 wht=64
# row=15 -- org=1
KEYMAP = (
    ('+', '0', '.', '-', 'Enter'),
    ('*', '1', '2', '3', None, 'Green'),
    ('/', '4', '5', '6', None, 'Red'),
    ('Shift', '8', '7', '9', 'Fn', None, 'White'),
    ('Orange',),
)

def scan_pressed():
    busy = False
    for keys, (row, cols) in zip(KEYMAP, scan_keys()):
        for bit, c in enumerate(keys):
            if c is None:
                continue
            mask = 1 << bit
            if cols & mask:
                print(c)
                busy = True
    if busy:
        print()

while True:
    DELAY = 0.050

    scan_pressed()
    pin_numlock.value(0)
    pin_backlight.value(0)
    time.sleep(DELAY)

    scan_pressed()
    pin_numlock.value(1)
    pin_backlight.value(1)
    time.sleep(DELAY)

#--#
