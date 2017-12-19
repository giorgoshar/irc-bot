class Colors:
    WHITE = '0'
    BLACK = '1'
    GREEN = '3'
    RED   = '4'
    BROWN = '5'
    PURPLE= '6'
    ORANGE= '7'
    YELLOW= '8'
    LGREEN= '9'
    CYAN  = '10'
    LCYAN = '11'
    LBLUE = '12'
    PINK  = '13'
    GREY  = '14'
    LGREY = '15'

class Style:
    def colored(text, bg = '0', color = '1'): 
        return '\x03{},{}{}\x03'.format(bg, color, text)
    def bold(text): 
        return '\x02{}\x02'.format(text)
    def italic(text):
        return '\x1D{}\x1D'.format(text)
    def underline(text):
        return '\x1F{}\x1F'.format(text)
    def swap(text):
        return '\x16{}\x16'.format(text)
    def reset(text):
        return '\x0F{}\x0F'.format(text)