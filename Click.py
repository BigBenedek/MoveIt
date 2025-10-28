
# not used yet
class Click:
    def __init__(self, x, y, button=None, delay=0, is_double_click=False):
        self.x = x
        self.y = y
        self.button = button
        self.delay = delay
        self.is_double_click = is_double_click

    def __repr__(self):
        return f"Click(x={self.x}, y={self.y}) button={self.button}, delay={self.delay}, is_double_click={self.is_double_click})"
    
    def to_array(self):
        return [self.x, self.y, self.button, self.delay, self.is_double_click]