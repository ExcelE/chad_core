import curses, serial, time

screen_help_text = """
========

Use W,A,S,D to move without changing the direction its facing
Use K,L to rotate the bot
Use 1, 2 to decrease or increase speed

"""

class Controller:
    def __init__(self, ser=None):
        # get the curses screen window
        self.screen = curses.initscr()
        
        # turn off input echoing
        curses.noecho()
        
        # respond to keys immediately (don't wait for enter)
        curses.cbreak()
        
        # map arrow keys to special values
        self.screen.keypad(True)
        self.ser = ser

        self.speed = 100
    
    def clear_top(self):
        self.screen.addstr(0, 0, "                                                           ")

    def manual(self):
        try:
            while True:
                char = self.screen.getch()
                self.screen.addstr(6, 0, screen)
                self.screen.addstr(3, 0, "Current speed: {}\n".format(self.speed))
                if char == ord('q'):
                    self.ser.write(b"stop")
                    break
                elif char == ord('1'):
                    if self.speed > 10:
                        self.speed -= 10
                        self.screen.addstr(0, 0, "Current updated speed: {}             ".format(self.speed))
                elif char == ord('2'):
                    if self.speed < 200:
                        self.screen.addstr(0, 0, "Current updated speed: {}             ".format(self.speed))
                        self.speed += 10
                elif char == curses.KEY_RIGHT or char == ord('d'):
                    # print doesn't work with curses, use addstr instead
                    self.ser.write("drive {} 1\n".format(self.speed).encode())
                    self.screen.addstr(0, 0, 'right                       ')
                elif char == curses.KEY_LEFT or char == ord('a'):
                    self.ser.write("drive {} 3\n".format(self.speed).encode())
                    self.screen.addstr(0, 0, 'left                    ')       
                elif char == curses.KEY_UP or char == ord('w'):
                    self.ser.write("drive {} 0\n".format(self.speed).encode())
                    self.screen.addstr(0, 0, 'up                           ')       
                elif char == curses.KEY_DOWN or char == ord('s'):
                    self.ser.write("drive {} 2\n".format(self.speed).encode())
                    self.screen.addstr(0, 0, 'down                        ')
                elif char == curses.KEY_SLEFT or char == ord('k'):
                    self.ser.write("rotate {} 0\n".format(self.speed).encode())
                    self.screen.addstr(0, 0, 'rotate left                      ')
                elif char == curses.KEY_SRIGHT or char == ord('l'):
                    self.ser.write("rotate {} 1\n".format(self.speed).encode())
                    self.screen.addstr(0, 0, 'rotate right                    ')
                self.ser.write(b"stop")
        finally:
            # shut down cleanly
            curses.nocbreak(); self.screen.keypad(0); curses.echo()
            curses.endwin()

ser = serial.Serial('/dev/ttyACM0')

p = Controller(ser=ser)
p.manual()
