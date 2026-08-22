from PIL import Image
import numpy as np

WIDTH = 1920
HEIGHT = 1080

# Size of the completely clear central area.
# This is intentionally small because scaling the image
# will make this region larger/smaller on screen.
CLEAR_RADIUS = 100

# How gradually the vignette transitions into black.
FEATHER = 900

POWER = 2

OUTPUT = "vignette_default.png"


def create_vignette():
    y, x = np.ogrid[0:HEIGHT, 0:WIDTH]

    cx = WIDTH / 2
    cy = HEIGHT / 2

    distance = np.sqrt(
        (x - cx) ** 2 +
        (y - cy) ** 2
    )

    # 0 = transparent
    # 1 = opaque black
    alpha = np.clip(
        (distance - CLEAR_RADIUS) / FEATHER,
        0.0,
        1.0
    )

    alpha = alpha ** POWER

    rgba = np.zeros(
        (HEIGHT, WIDTH, 4),
        dtype=np.uint8
    )

    rgba[:, :, 3] = (alpha * 255).astype(np.uint8)

    Image.fromarray(rgba, "RGBA").save(OUTPUT)


if __name__ == "__main__":
    create_vignette()
    print(f"Created {OUTPUT}")