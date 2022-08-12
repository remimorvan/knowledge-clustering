class Blabla:
    def __init__(self):
        self.a = 5

    def val(self, x):
        self.x = x

    def print_val(self):
        print(self.x)


b = Blabla()
b.val(4)
b.print_val()
