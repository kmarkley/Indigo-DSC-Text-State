# DSC Text State

Simplest plugin ever.

Given a DSC Alarm Keypad device, this device will summarise the overall alarm state as text, in long and short versions. 

Requires Indigo [DSC Alarm](https://github.com/IndigoDomotics/DSC-Alarm) plugin.

---

## Sates

#### state

The longer text version of the overall state of the keypad device.  Values are:

* Disarmed (Ready)
* Disarmed (Not Ready)
* Away Armed
* Stay Armed
* Entry Delay
* Exit Delay
* Panic (Fire)
* Panic (Ambulance)
* Panic (Police)
* Panic (Duress)
* Tripped

#### shortState

The shorter text version of the overall state of the keypad device.  Values are:

* Ready
* Not Ready
* Away
* Stay
* Entry
* Exit
* Panic
* Tripped

#### imageState

For control page images.  Values are:

* disarmed
* away
* stay
* delay
* alarm
