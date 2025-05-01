class Plot2D:
    def __init__(self, title):
        self.title = title
        self.curves = []
    
    def __str__(self)->str:
        return "\n".join([f'plot "{self.title}" {x} vs {y}' for x, y in self.curves])

    def addCurve(self, x, y):
        self.curves.append((x, y))