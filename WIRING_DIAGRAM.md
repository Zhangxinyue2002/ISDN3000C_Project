## Hardware Wiring Diagram - Elderly Fall Detection System

### Quick Reference Card

```
┌─────────────────────────────────────────────────────────────────┐
│                    RDK X5 GPIO CONNECTIONS                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  BUTTON 1 (Manual Emergency - Call 999)                        │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━                         │
│                                                                 │
│     3.3V (Pin 1)                                               │
│        │                                                        │
│        └──[Button]──┬── Pin 11 (GPIO 17)                      │
│                     │                                           │
│                     └──[10kΩ]── GND (Pin 14)                  │
│                                                                 │
│                                                                 │
│  BUTTON 2 (Cancel Emergency)                                   │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━                                 │
│                                                                 │
│     3.3V (Pin 1)                                               │
│        │                                                        │
│        └──[Button]──┬── Pin 13 (GPIO 27)                      │
│                     │                                           │
│                     └──[10kΩ]── GND (Pin 20)                  │
│                                                                 │
│                                                                 │
│  LED 1 (Fall Indicator - Red)                                  │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━                                │
│                                                                 │
│     Pin 22 (GPIO 25) ──[220Ω]──(LED+)──(LED-)── GND (Pin 6)   │
│                                  │                              │
│                            Long leg (anode)                     │
│                                                                 │
│                                                                 │
│  LED 2 (Emergency Indicator - Red)                             │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━                           │
│                                                                 │
│     Pin 33 (GPIO 13) ──[220Ω]──(LED+)──(LED-)── GND (Pin 9)   │
│                                  │                              │
│                            Long leg (anode)                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Breadboard Layout

```
                        BREADBOARD VIEW
  ┌───────────────────────────────────────────────────────┐
  │                                                       │
  │   3.3V Rail  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
  │      │         │           │                          │
  │      │         │           │                          │
  │   Button1   Button2                                   │
  │      │         │                                       │
  │      ├─────────┼──→ Pin 11 (Button1)                 │
  │      │         └──→ Pin 13 (Button2)                 │
  │      │                                                 │
  │   [10kΩ]    [10kΩ]                                   │
  │      │         │                                       │
  │   GND Rail  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
  │                                                       │
  │                                                       │
  │   Pin 22 ──[220Ω]──┬──(LED1+)                       │
  │                     │                                 │
  │                  (LED1-)                              │
  │                     │                                 │
  │                    GND                                │
  │                                                       │
  │                                                       │
  │   Pin 33 ──[220Ω]──┬──(LED2+)                       │
  │                     │                                 │
  │                  (LED2-)                              │
  │                     │                                 │
  │                    GND                                │
  │                                                       │
  └───────────────────────────────────────────────────────┘
```

### RDK X5 GPIO Header Pinout

```
        RDK X5 40-Pin GPIO Header
        ========================

3.3V     1 ●─┐ 2  5V
GPIO2    3 ● │ 4  5V
GPIO3    5 ● │ 6  GND ────→ LED1 (-)
GPIO4    7 ● │ 8  GPIO14
GND      9 ●─┼→●10 GPIO15  ← LED2 (-)
GPIO17  11 ●←┼─●12 GPIO18  (Button 1)
GPIO27  13 ●←┼─●14 GND ───→ 10kΩ (Button1)
GPIO22  15 ● │ 16 GPIO23
3.3V    17 ● └─●18 GPIO24
GPIO10  19 ● ● 20 GND ────→ 10kΩ (Button2)
GPIO9   21 ● ● 22 GPIO25 ──→ LED1 (via 220Ω)
GND     23 ● ● 24 GPIO8
GPIO11  25 ● ● 26 GPIO7
...
GPIO13  33 ●─────→ LED2 (via 220Ω)
...
```

### Component Specifications

```
┌──────────────┬──────────────┬─────────────────────────┐
│ Component    │ Value        │ Notes                   │
├──────────────┼──────────────┼─────────────────────────┤
│ LED Resistor │ 220Ω - 330Ω │ Limits current to 10mA  │
│ Button R     │ 10kΩ         │ Pull-down resistor      │
│ LEDs         │ 5mm Red      │ Forward voltage ~2V     │
│ Buttons      │ Momentary NO │ Normally-open switch    │
│ Wire Gauge   │ 22 AWG       │ Solid core recommended  │
│ Power        │ 3.3V         │ DO NOT USE 5V!          │
└──────────────┴──────────────┴─────────────────────────┘
```

### Step-by-Step Assembly

```
STEP 1: PREPARE COMPONENTS
└─ Gather: 2 LEDs, 2 Buttons, 2×220Ω, 2×10kΩ, wires

STEP 2: CONNECT LED 1 (Fall Indicator)
├─ Connect Pin 22 to 220Ω resistor
├─ Connect resistor to LED long leg (+)
└─ Connect LED short leg (-) to GND (Pin 6)

STEP 3: CONNECT LED 2 (Emergency Indicator)
├─ Connect Pin 33 to 220Ω resistor
├─ Connect resistor to LED long leg (+)
└─ Connect LED short leg (-) to GND (Pin 9)

STEP 4: CONNECT BUTTON 1 (Emergency Call)
├─ Connect 3.3V (Pin 1) to Button terminal A
├─ Connect Button terminal B to Pin 11
├─ Connect Pin 11 to 10kΩ resistor
└─ Connect resistor to GND (Pin 14)

STEP 5: CONNECT BUTTON 2 (Cancel)
├─ Connect 3.3V (Pin 1) to Button terminal A
├─ Connect Button terminal B to Pin 13
├─ Connect Pin 13 to 10kΩ resistor
└─ Connect resistor to GND (Pin 20)

STEP 6: TEST CONNECTIONS
└─ Run: python3 test_components.py
```

### Testing Checklist

```
□ LED 1 lights up when test runs
□ LED 2 lights up when test runs
□ LED 2 flashes in test
□ Button 1 press detected
□ Button 2 press detected
□ No shorts (check with multimeter)
□ Correct voltage (3.3V not 5V)
□ LED polarity correct (long leg to +)
```

### Safety Warnings

```
⚠️  DO NOT CONNECT TO 5V - Use 3.3V only!
⚠️  Check LED polarity - Long leg to resistor
⚠️  Use resistors - LEDs will burn without them
⚠️  Button pull-down - 10kΩ to GND required
⚠️  Test individually - One component at a time
⚠️  Power off - Before making changes
```

### Quick Troubleshooting

```
LED NOT LIGHTING:
├─ Check polarity (long leg to +)
├─ Check resistor value (220-330Ω)
└─ Test LED separately with 3.3V

BUTTON NOT WORKING:
├─ Check pull-down resistor (10kΩ to GND)
├─ Test button continuity with multimeter
└─ Check wiring to correct GPIO pin

SHORT CIRCUIT:
├─ Power off immediately
├─ Check for crossed wires
└─ Verify resistors in place
```

### Color Coding (Optional)

```
Use colored wires to make identification easier:

Red    = 3.3V power
Black  = GND
Yellow = Button signals (GPIO 17, 27)
Green  = LED signals (GPIO 25, 13)
```

---

Print this page and keep it next to your RDK while wiring!
