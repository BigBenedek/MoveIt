
class Click:
    def __init__(self, x, y, button=None, delay=0, is_double_click=False, offset_x=0, offset_y=0, is_scroll=False, scroll_amount=0):
        self.x = x
        self.y = y
        self.button = button
        self.delay = delay  # Time to wait after this click
        self.is_double_click = is_double_click
        self.offset_x = offset_x  # Offset to add after each replay cycle
        self.offset_y = offset_y  # Offset to add after each replay cycle
        # Scroll action support
        self.is_scroll = is_scroll
        self.scroll_amount = scroll_amount

    def __repr__(self):
        return f"Click(x={self.x}, y={self.y}, delay={self.delay}, offset=({self.offset_x},{self.offset_y}), double={self.is_double_click}, scroll={self.is_scroll},{self.scroll_amount})"

    def to_array(self):
        return [self.x, self.y, self.button, self.delay, self.is_double_click, self.offset_x, self.offset_y]

    def to_dict(self):
        return {
            'x': self.x,
            'y': self.y,
            'button': self.button,
            'delay': self.delay,
            'is_double_click': self.is_double_click,
            'offset_x': self.offset_x,
            'offset_y': self.offset_y,
            'is_scroll': self.is_scroll,
            'scroll_amount': self.scroll_amount
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            x=data['x'],
            y=data['y'],
            button=data.get('button'),
            delay=data.get('delay', 0),
            is_double_click=data.get('is_double_click', False),
            offset_x=data.get('offset_x', 0),
            offset_y=data.get('offset_y', 0),
            is_scroll=data.get('is_scroll', False),
            scroll_amount=data.get('scroll_amount', 0)
        )