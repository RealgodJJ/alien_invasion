import pygame
from pygame.sprite import Sprite


class ShipLife(Sprite):
    """在界面左上角用于显示剩余的飞船数目"""

    def __init__(self, ai_settings, screen):
        """初始化飞船显示生命数的初始位置"""
        super().__init__()
        self.screen = screen
        self.ai_settings = ai_settings

        # 加载飞船图像并获取其外接矩形
        self.image = pygame.image.load('images/ship.bmp')
        self.rect = self.image.get_rect()
        self.screen_rect = screen.get_rect()

        # 将三艘新飞船放在屏幕左上角
        self.rect.left = self.screen_rect.left
        self.rect.top = self.screen_rect.top

    def update(self):
        """根据剩余生飞船数，更新右上角的飞船数"""
        print("update three ships.")

    def blitme(self):
        """在指定位置绘制飞船"""
        self.screen.blit(self.image, self.rect)
