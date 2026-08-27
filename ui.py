import pygame


class Hotbar:
	SLOT_SIZE = 72
	BAR_HEIGHT = 88
	ICON_SIZE = 32
	SELECTED_ICON_SIZE = 64
	SLOT_GAP = 4
	BLOCK_COUNT = 6
	PREVIEW_NAMES = ("grass", "dirt", "stone", "coal", "log", "leaf")

	def __init__(self, renderer, width, height, assets):
		self.renderer = renderer
		self.width = width
		self.height = height
		self.assets = assets

		bar_width = self.BLOCK_COUNT * self.SLOT_SIZE
		self.rect = pygame.Rect(
			(width - bar_width) // 2,
			height - self.BAR_HEIGHT - 16,
			bar_width,
			self.BAR_HEIGHT,
		)
		self.background = pygame.Surface(self.rect.size, pygame.SRCALPHA)
		self.background.fill((20, 24, 28, 220))
		self.icons = {
			block_id: {
				self.ICON_SIZE: pygame.transform.scale(
					assets.image(preview_name),
					(self.ICON_SIZE, self.ICON_SIZE),
				),
				self.SELECTED_ICON_SIZE: pygame.transform.scale(
					assets.image(preview_name),
					(self.SELECTED_ICON_SIZE, self.SELECTED_ICON_SIZE),
				),
			}
			for block_id, preview_name in enumerate(self.PREVIEW_NAMES)
		}

	def draw(self, selected_block):
		"""Draw every block slot, enlarging the currently selected block."""
		self.renderer.draw_surface(self.background, self.rect)

		for block_id in range(self.BLOCK_COUNT):
			is_selected = block_id == selected_block
			icon_size = (
				self.SELECTED_ICON_SIZE
				if is_selected
				else self.ICON_SIZE
			)
			icon = self.icons[block_id][icon_size]
			slot_x = self.rect.x + block_id * self.SLOT_SIZE
			icon_rect = icon.get_rect(center=(
				slot_x + self.SLOT_SIZE // 2,
				self.rect.centery,
			))

			if is_selected:
				self.renderer.draw_rect(
					icon_rect.inflate(self.SLOT_GAP, self.SLOT_GAP),
					(240, 220, 120, 255),
					width=3,
					skeleton=True,
				)
			self.renderer.draw_surface(icon, icon_rect)
