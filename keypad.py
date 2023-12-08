#!micropython

# https://github.com/micropython/micropython/.../ports/rp2/

from machine import Pin
from rp2 import PIO
from rp2 import StateMachine

# Rows driven by open-drain (pull-up + direction enable)
ROW_PIN_BASE = 11
ROW_PIN_COUNT = 5

# Columns read in parallel
COL_PIN_BASE = 16
COL_PIN_COUNT = 7

def keypad_init_sm(i_sm: int, scan_Hz: int = 200):
    scan_Hz = max(scan_Hz, 7)  # 137-MHz / 2^16-1
    row_pin_base = Pin(ROW_PIN_BASE, Pin.OUT, Pin.PULL_UP)
    col_pin_base = Pin(COL_PIN_BASE, Pin.IN, Pin.PULL_UP)
    sm = rp2.StateMachine(i_sm,
                          freq=300 * scan_Hz,
                          prog=keyscan_prog,
                          in_base=col_pin_base,
                          set_base=row_pin_base)
    sm.active(1)
    return sm

def keyscan_read(sm: rp2.StateMachine) -> str:
    return ~sm.get() & 0x1ffffff if sm.rx_fifo() else 0


@rp2.asm_pio(
    in_shiftdir=rp2.PIO.SHIFT_LEFT,
    #push_thresh=25,
    #autopush=False,
    set_init=( PIO.OUT_LOW, ) * ROW_PIN_COUNT,  # Open-drain via pindirs
)
def keyscan_prog():
    label('changed')
    push(noblock)  # Block and lose events or drop and corrupt state.
    mov(y, x)

    wrap_target()
    set(pins, 0)
    mov(isr, null)  # Clear, otherwise junk is cycled.

    # for row, count in enumerate(( 5, 6, 6, 7, 1 )):
    # set(pindirs, 1 << row)[24]
    # in_(pins, count)

    # row=11 -- 0=2 .=4 -=8 +=1 enter=16
    set(pindirs, 0b0_0001)	[24]
    in_(pins, 5)		[24]

    # row=12 -- 1=2 2=4 3=8 x=1 green=32
    set(pindirs, 0b0_0010)	[24]
    in_(pins, 6)		[24]

    # row=13 -- 4=2 5=4 6=8 /=1 red=32
    set(pindirs, 0b0_0100)	[24]
    in_(pins, 6)		[24]

    # row=14 -- 7=4 8=2 9=8 shift=1 fn=16 white=64
    set(pindirs, 0b0_1000)	[24]
    in_(pins, 7)		[24]

    # row=15 -- orange=1
    set(pindirs, 0b1_0000)	[24]
    in_(pins, 1)		[24]

    # Compare current value to previous, only push when it changes.
    mov(x, isr)			[24]
    jmp(x_not_y, 'changed')	[24]
    wrap()

    # label('changed') belongs here, but failed?


KEYMAP = (
    'Orange',
    'Shift',
    '8',
    '7',
    '9',
    'Fn',
    None,
    'White',
    '/',
    '4',
    '5',
    '6',
    None,
    'Red',
    '*',
    '1',
    '2',
    '3',
    None,
    'Green',
    '+',
    '0',
    '.',
    '-',
    'Enter',
)

def keyscan_decode(x):
    rv = [ ]
    for s in KEYMAP:
        b, x = x & 1, x >> 1
        if s and b:
            rv.append(s)
    return rv

#---------------------------------------------------------------------#

import time

# Manual Pin init makes things work...?
pins_matrix_rows = [ Pin(n, Pin.IN, Pin.PULL_UP)
                     for n in range(11, 15+1) ]
pins_matrix_cols = [ Pin(n, Pin.IN, Pin.PULL_UP)
                     for n in range(16, 22+1) ]

sm = keypad_init_sm(4, 200)

old_x = -1
while True:
    x = keyscan_read(sm)
    if x != -1 and x != old_x:
        #print('%07x' % x)
        print(keyscan_decode(x))
        old_x = x
    #time.sleep(1)



#--#
