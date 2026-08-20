
class Camera:
    def __init__(self, width, height):
        self.x = 0
        self.y = 0

        self.width = width
        self.height = height

    def update(self, target):
        self.x = target.rect.centerx - self.width // 2
        self.y = target.rect.centery - self.height // 2