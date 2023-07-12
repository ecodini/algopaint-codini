import gamelib
import const
from ui import Paint

def main():
    gamelib.title("AlgoPaint")
    gamelib.resize(const.WIDTH, const.HEIGHT)

    paint = Paint(gamelib)

    while gamelib.loop(fps=const.FPS):
        gamelib.draw_begin()
        paint.draw()
        gamelib.draw_end()

        for ev in gamelib.get_events():
            paint.update(ev)

gamelib.init(main)
