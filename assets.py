import pygame

class Assets:
    def __init__(self):
        # Normal images
        self.images = {}

        # Sounds
        self.sounds = {}

        # Fonts
        self.fonts = {}

        # Spritesheets
        self.sheets = {}

        # Atlas files
        self.atlases = {}

        # Processed atlas textures
        self.atlas_textures = {}

    # --------------------------------------------------
    # Images
    # --------------------------------------------------

    def image(self, name, alpha=True):
        """Load an image once and cache it."""
        path = f"media/images/{name}.png"

        if name not in self.images:
            image = pygame.image.load(path)

            if alpha:
                image = image.convert_alpha()
            else:
                image = image.convert()

            self.images[name] = image

        return self.images[name]

    # --------------------------------------------------
    # Sounds
    # --------------------------------------------------

    def sound(self, name):
        """Load a sound once and cache it."""
        path = f"media/sounds/{name}.png"

        if name not in self.sounds:
            self.sounds[name] = pygame.mixer.Sound(path)

        return self.sounds[name]

    # --------------------------------------------------
    # Fonts
    # --------------------------------------------------

    def font(self, name, size):
        """Load a font once and cache it."""
        path = f"media/fonts/{name}.ttf"

        key = (name, size)

        if key not in self.fonts:
            self.fonts[key] = pygame.font.Font(path, size)

        return self.fonts[key]

    # --------------------------------------------------
    # Spritesheets
    # --------------------------------------------------

    def spritesheet(
        self,
        name,
        frame_size,
        frame_count,
        row=0,
        output_size=None,
        flip_x=False,
    ):
        """
        Load and process frames from a spritesheet.

        frame_size:
            Size of each source frame.

        frame_count:
            Number of frames to extract.

        row:
            Which row of the spritesheet to use.

        output_size:
            Size to scale each frame to.

        flip_x:
            Flip every frame horizontally.
        """
        path = f"media/sheets/{name}.png"

        key = (
            name,
            frame_size,
            frame_count,
            row,
            output_size,
            flip_x,
        )

        if key in self.sheets:
            return self.sheets[key]

        sheet = pygame.image.load(path).convert_alpha()

        frame_width, frame_height = frame_size

        frames = []

        for i in range(frame_count):
            rect = pygame.Rect(
                i * frame_width,
                row * frame_height,
                frame_width,
                frame_height,
            )

            frame = sheet.subsurface(rect)

            if output_size is not None:
                frame = pygame.transform.scale(
                    frame,
                    output_size,
                )

            if flip_x:
                frame = pygame.transform.flip(
                    frame,
                    True,
                    False,
                )

            frames.append(frame)

        self.sheets[key] = frames

        return frames

    # --------------------------------------------------
    # Texture Atlases
    # --------------------------------------------------

    def atlas_texture(
        self,
        atlas_name,
        texture_id,
        tile_size=16,
        output_size=(64, 64),
    ):
        """Get one cached texture from a regular atlas."""
        atlas_path = f"media/atlases/{atlas_name}.png"

        if atlas_name not in self.atlas_textures:
            self.atlas_textures[atlas_name] = {}

        textures = self.atlas_textures[atlas_name]

        if texture_id in textures:
            return textures[texture_id]

        if atlas_name not in self.atlases:
            atlas = pygame.image.load(
                atlas_path
            ).convert_alpha()

            width, height = atlas.get_size()

            if width % tile_size != 0 or height % tile_size != 0:
                raise ValueError(
                    f"Atlas '{atlas_path}' dimensions must "
                    f"be divisible by {tile_size}."
                )

            self.atlases[atlas_name] = atlas

        atlas = self.atlases[atlas_name]

        width, height = atlas.get_size()

        columns = width // tile_size
        rows = height // tile_size


        if texture_id >= columns * rows:
            raise ValueError(
                f"Texture '{texture_id}' is outside the atlas."
            )

        tile_x = texture_id % columns
        tile_y = texture_id // columns

        rect = pygame.Rect(
            tile_x * tile_size,
            tile_y * tile_size,
            tile_size,
            tile_size,
        )

        texture = atlas.subsurface(rect)

        if output_size != (tile_size, tile_size):
            texture = pygame.transform.scale(
                texture,
                output_size,
            )

        textures[texture_id] = texture

        return texture

    # --------------------------------------------------
    # Cache management
    # --------------------------------------------------

    def clear(self):
        """Clear all cached processed assets."""

        self.images.clear()
        self.sounds.clear()
        self.fonts.clear()
        self.sheets.clear()
        self.atlases.clear()
        self.atlas_textures.clear()