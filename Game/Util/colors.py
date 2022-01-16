class bcolors:
    def __init__(self):
        self.sColors = [
            '\u001b[31m', # Red
            '\u001b[32m', # Yellow
            '\u001b[33m', # Green
            '\u001b[34m', # Blue
            '\u001b[35m', # Magenta
            '\u001b[36m' # Cyan
        ]
        self.wColors = {
            'header':'\033[95m',
            'okblue':'\033[94m',
            'okcyan':'\033[96m',
            'success':'\033[92m',
            'warning':'\033[93m',
            'fail':'\033[91m'
        }
        self.reset = '\033[0m'
        self.bold = '\033[1m'
        self.underline = '\033[4m'
    def getColors(self):
        return self.sColors
    def getWColors(self):
        return self.wColors
