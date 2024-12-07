Point = tuple[float, float]

class Actor():
    def move(self):
        raise NotImplementedError("Abstract method")
    
    def draw(self) -> None:
        raise NotImplementedError("Abstract method")

    def position(self) -> Point:
        raise NotImplementedError("Abstract method")

    def size(self) -> Point:
        raise NotImplementedError("Abstract method")

def check_collision(a1: Actor, a2: Actor) -> bool:
    x1, y1, w1, h1 = a1.position() + a1.size()
    x2, y2, w2, h2 = a2.position() + a2.size()
    return (y2 <= y1 + h1 and y1 <= y2 + h2 and
            x2 <= x1 + w1 and x1 <= x2 + w2)