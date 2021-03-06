import pygame
from pygame.sprite import Group
from settings import Settings
from game_stats import GameStats
import game_functions as gf
from alien import Alien
from ship import Ship
from ship_life import ShipLife
from button import Button
from scoreboard import Scoreboard


def run_game():
    # 初始化游戏并创建一个屏幕对象
    pygame.init()
    ai_settings = Settings()
    screen = pygame.display.set_mode(
        (ai_settings.screen_width, ai_settings.screen_height))
    pygame.display.set_caption("Alien Invasion")

    # 创建一个play按钮
    play_button = Button(ai_settings, screen, "Play")

    # 创建一个用于存储游戏统计信息的实例,并创建一个记分牌
    stats = GameStats(ai_settings)
    scoreboard = Scoreboard(ai_settings, screen, stats)

    # 创建一艘飞船
    ship = Ship(ai_settings, screen)
    ship_life = ShipLife(ai_settings, screen)

    # 创建一个用于存储子弹的编组
    bullets = Group()

    # 创建一个外星人编组
    aliens = Group()

    # 创建外星人群
    gf.create_fleet(ai_settings, screen, ship, aliens)

    # 创建一个飞船剩余数量编组
    ship_lifes = Group()

    # 创建飞船三条命示意图
    gf.create_ship_life_fleet(ai_settings, screen, ship_lifes, stats)

    # 开始游戏的主循环
    while True:
        # 监视键盘和鼠标事件
        gf.check_events(ai_settings, screen, stats, scoreboard, play_button, ship, aliens, bullets, ship_lifes)

        if stats.game_active:
            # 更新屏幕中飞船、子弹和外星人的位置
            ship.update()
            gf.update_bullets(ai_settings, screen, stats, scoreboard, ship, aliens, bullets)
            gf.update_aliens(ai_settings, stats, screen, ship, aliens, bullets, ship_lifes)

        # ~ else:
        # ~ print("Set 'False' succcess!")

        # 每次循环时都重绘屏幕，让最近绘制的屏幕可见
        gf.update_screen(ai_settings, screen, stats, ship, aliens, ship_lifes, bullets, play_button, scoreboard)


run_game()
