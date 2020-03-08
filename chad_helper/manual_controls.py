import curses

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
    
    def manual(self):
        try:
            while True:
                char = self.screen.getch()
                if char == ord('q'):
                    self.ser.write(b"stop")
                    break
                elif char == ord('1'):
                    if self.speed > 10:
                        self.speed -= 10
                elif char == ord('2'):
                    if self.speed < 200:
                        self.speed += 10
                elif char == curses.KEY_RIGHT:
                    # print doesn't work with curses, use addstr instead
                    self.ser.write("drive {} 1\n".format(self.speed).encode())
                    self.screen.addstr(0, 0, 'right')
                elif char == curses.KEY_LEFT:
                    self.ser.write("drive {} 3\n".format(self.speed).encode())
                    self.screen.addstr(0, 0, 'left ')       
                elif char == curses.KEY_UP:
                    self.ser.write("drive {} 0\n".format(self.speed).encode())
                    self.screen.addstr(0, 0, 'up   ')       
                elif char == curses.KEY_DOWN:
                    self.ser.write("drive {} 2\n".format(self.speed).encode())
                    self.screen.addstr(0, 0, 'down ')
                elif char == curses.KEY_SLEFT:
                    self.ser.write("rotate {} 0\n".format(self.speed).encode())
                    self.screen.addstr(0, 0, 'shift left ')
                elif char == curses.KEY_SRIGHT:
                    self.ser.write("rotate {} 1\n".format(self.speed).encode())
                    self.screen.addstr(0, 0, 'shift right ')
                self.ser.write(b"stop")
        finally:
            # shut down cleanly
            curses.nocbreak(); self.screen.keypad(0); curses.echo()
            curses.endwin()

























