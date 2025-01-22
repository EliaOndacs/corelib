class Loop:
    def __init__(self) -> None:
        self.alive = False
        self.count = 0

    def start(self):
        assert not self.alive, "cannot call `start()` function on a running loop."
        self.alive = True

    def kill(self):
        self.alive = False

    def __iter__(self):
        self.count += 1
        return self.count


