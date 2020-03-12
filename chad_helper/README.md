# Manual Control Script for Chad Bot

## Running the script

`python manual_controls.py`

## Editing the Script

You can bind any keys using:  
```python3
elif char == ord('d'):
    self.ser.write("drive {} 1\n".format(self.speed).encode())
    self.screen.addstr(0, 0, 'right             ')
```

Where in this case, `ord('d')` binds to the 'D' key. You can change it to any lower case key.

The `self.ser.write("<YOUR CUSTOM COMMAND HERE>".encode())` sends whatever command to be triggered when the key is pressed.

The `self.screen.addstr(0,0, '<YOU MESSAGE HERE>')` is there to give you feedback on whether your key is triggered. Optional, but highly recommended.