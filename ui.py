import pygame

from block import BlockType

#[small tex, big tex] in self.icons[x]

class Hotbar:
	SLOT_SIZE = 72
	BAR_HEIGHT = 88
	ICON_SIZE = 32
	SELECTED_ICON_SIZE = 64
	SLOT_GAP = 4
	BLOCK_COUNT = 8
	PREVIEW_NAMES = {
		BlockType.GRASS: "grass",
		BlockType.DIRT: "dirt",
		BlockType.STONE: "stone",
		BlockType.COAL: "coal",
		BlockType.LOG: "log",
		BlockType.LEAF: "leaf",
	}

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
		self.icons = {}
		for key, value in self.PREVIEW_NAMES.items():
			textures = [
				self.assets.image(value, output_size=(self.ICON_SIZE, self.ICON_SIZE)),
				self.assets.image(value, output_size=(self.SELECTED_ICON_SIZE, self.SELECTED_ICON_SIZE))
			]
			self.icons[key] = textures
		self.icons[None] = [
			pygame.Surface((self.ICON_SIZE, self.ICON_SIZE), pygame.SRCALPHA),
			pygame.Surface((self.SELECTED_ICON_SIZE, self.SELECTED_ICON_SIZE), pygame.SRCALPHA),
		]

		self.surface = None
		self.selected_block = None
		self.inventory = None
		self.selected_center_x = 0

	def _create_surface(self, selected_block, inventory):
		icons = []
		for i in range(self.BLOCK_COUNT):
			if i == selected_block:
				icons.append(self.icons[inventory[i]][1])
			else:
				icons.append(self.icons[inventory[i]][0])

		bar_width = sum(icon.get_width() for icon in icons)
		bar_width += self.SLOT_GAP * (self.BLOCK_COUNT - 1)
		bar_height = max(icon.get_height() for icon in icons)
		surface = pygame.Surface((bar_width, bar_height), pygame.SRCALPHA)
		x = 0
		for block_id, icon in enumerate(icons):
			y = (bar_height - icon.get_height()) // 2
			surface.blit(icon, (x, y))
			if block_id == selected_block:
				self.selected_center_x = x + icon.get_width() // 2
				
			x += icon.get_width() + self.SLOT_GAP

		return surface

	def draw(self, selected_block, inventory):
		if selected_block != self.selected_block or inventory != self.inventory:
			if self.surface is not None:
				self.renderer.invalidate_surface(self.surface)
			self.surface = self._create_surface(selected_block, inventory)
			self.selected_block = selected_block
			self.inventory = list(inventory)
			self.rect.size = self.surface.get_size()
			self.rect.centerx = (
				self.width // 2
				+ self.surface.get_width() // 2
				- self.selected_center_x
			)
			self.rect.bottom = self.height - 16

		self.renderer.draw_surface(self.surface, self.rect)
