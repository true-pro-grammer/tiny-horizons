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
		self.surface = None
		self.selected_block = None

	def _create_surface(self, selected_block):
		surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)
		surface.fill((20, 24, 28, 220))
		slot_x = selected_block * self.SLOT_SIZE
		selected_rect = pygame.Rect(
			slot_x + (self.SLOT_SIZE - self.SELECTED_ICON_SIZE) // 2,
			(self.BAR_HEIGHT - self.SELECTED_ICON_SIZE) // 2,
			self.SELECTED_ICON_SIZE,
			self.SELECTED_ICON_SIZE,
		).inflate(self.SLOT_GAP, self.SLOT_GAP)
		pygame.draw.rect(
			surface,
			(240, 220, 120, 255),
			selected_rect,
			width=3,
		)

		for block_id in range(self.BLOCK_COUNT):
			icon_size = (
				self.SELECTED_ICON_SIZE
				if block_id == selected_block
				else self.ICON_SIZE
			)
			icon = self.icons[block_id][icon_size]
			slot_x = block_id * self.SLOT_SIZE
			icon_rect = icon.get_rect(center=(
				slot_x + self.SLOT_SIZE // 2,
				self.BAR_HEIGHT // 2,
			))
			surface.blit(icon, icon_rect)

		return surface

	def draw(self, selected_block):
		"""Draw the cached bar, rebuilding it only after selection changes."""
		if selected_block != self.selected_block:
			if self.surface is not None:
				self.renderer.invalidate_surface(self.surface)
			self.surface = self._create_surface(selected_block)
			self.selected_block = selected_block

		self.renderer.draw_surface(self.surface, self.rect)
