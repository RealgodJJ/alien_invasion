import sys
import pygame
from pygame.sprite import Group
from time import sleep
from bullet import Bullet
from alien import Alien
from ship_life import ShipLife


def check_events(ai_settings, screen, stats, scoreboard, play_button, ship, aliens, bullets, ship_lifes):
    """响应按键和鼠标事件"""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            check_keydown_events(event, ai_settings, screen, ship, bullets)
        elif event.type == pygame.KEYUP:
            check_keyup_events(event, ship)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            check_play_button(ai_settings, screen, stats, scoreboard, play_button, mouse_x, mouse_y, ship, aliens,
                              bullets, ship_lifes)


def check_keydown_events(event, ai_settings, screen, ship, bullets):
    if event.key == pygame.K_LEFT:
        ship.moving_left = True
    elif event.key == pygame.K_RIGHT:
        ship.moving_right = True
    elif event.key == pygame.K_SPACE:
        fire_bullets(ai_settings, screen, ship, bullets)
    if event.key == pygame.K_q:
        sys.exit()


def check_keyup_events(event, ship):
    if event.key == pygame.K_LEFT:
        ship.moving_left = False
    elif event.key == pygame.K_RIGHT:
        ship.moving_right = False


def check_play_button(ai_settings, screen, stats, scoreboard, play_button, mouse_x, mouse_y, ship, aliens, bullets,
                      ship_lifes):
    """在玩家单机Play按钮时开始新游戏"""
    button_clicked = play_button.rect.collidepoint(mouse_x, mouse_y)
    if button_clicked and not stats.game_active:
        # ~ print(mouse_x, mouse_y)
        # 重置游戏统计信息
        stats.reset_stats()
        # ~ print(ai_settings.ship_limit)
        stats.game_active = True
        pygame.mouse.set_visible(False)
        ai_settings.initialize_dynamic_settings()

        # 重置记分牌图像
        scoreboard.prep_score()
        scoreboard.prep_high_score()
        scoreboard.prep_level()

        # 清空外星人列表和子弹列表
        aliens.empty()
        bullets.empty()

        # 创建一群新的外星人，并让飞船居中
        create_fleet(ai_settings, screen, ship, aliens)
        ship.center_ship()
        create_ship_life_fleet(ai_settings, screen, ship_lifes, stats)


def fire_bullets(ai_settings, screen, ship, bullets):
    # 创建一颗子弹，并将其加入到编组bullets中
    if len(bullets) < ai_settings.bullets_allowed:
        new_bullet = Bullet(ai_settings, screen, ship)
        bullets.add(new_bullet)


def update_bullets(ai_settings, screen, stats, scoreboard, ship, aliens, bullets):
    """更新子弹的设置，并删除已消失的子弹"""
    # 更新子弹的位置
    bullets.update()

    # 删除已消失的子弹
    for bullet in bullets.copy():
        if bullet.rect.bottom <= 0:
            bullets.remove(bullet)
    # ~ print(len(bullets))

    check_bullet_alien_collisions(ai_settings, screen, stats, scoreboard, ship, aliens, bullets)


def check_bullet_alien_collisions(ai_settings, screen, stats, scoreboard, ship, aliens, bullets):
    # 检查是否有子弹击中了外星人
    # 如果是这样，就删除相应的子弹和外星人
    collisions = pygame.sprite.groupcollide(bullets, aliens, True, True)

    if collisions:
        for aliens in collisions.values():
            stats.score += ai_settings.alien_points * len(aliens)
            scoreboard.prep_score()
        check_high_score(stats, scoreboard)

    if len(aliens) == 0:
        # 删除现有的子弹并创建一群新的外星人，并提高一个等级
        bullets.empty()
        aliens.empty()
        ai_settings.increase_speed()
        create_fleet(ai_settings, screen, ship, aliens)
        stats.level += 1
        scoreboard.prep_level()


def create_fleet(ai_settings, screen, ship, aliens):
    """创建外星人群"""
    # 创建一个外星人，并计算一行可容纳多少外星人
    # 外星人间距为1/3的外星人宽度
    alien = Alien(ai_settings, screen)
    number_aliens_x = get_number_aliens_x(ai_settings, alien.rect.width)
    number_rows = get_number_rows(ai_settings, ship.rect.height,
                                  alien.rect.height)

    # 创建外星人阵列
    for row_number in range(number_rows):
        for alien_number in range(number_aliens_x):
            create_alien(ai_settings, screen, aliens, alien_number,
                         row_number, ship)


def create_alien(ai_settings, screen, aliens, alien_number, row_number, ship):
    """创建一个外星人并将其加入当前行"""
    alien = Alien(ai_settings, screen)
    alien_width = alien.rect.width
    alien_height = alien.rect.height
    alien.x = 1 / 3 * alien_width + 4 / 3 * alien_width * alien_number
    alien.rect.x = alien.x
    alien.rect.y = 1 / 3 * alien_height + 2 * alien_height * row_number + ship.rect.height
    aliens.add(alien)


def get_number_aliens_x(ai_settings, alien_width):
    """计算每行可容纳多少个外星人"""
    available_space_x = ai_settings.screen_width - 2 / 3 * alien_width
    number_aliens_x = int(available_space_x / (4 / 3 * alien_width))
    return number_aliens_x


def get_number_rows(ai_settings, ship_height, alien_height):
    """计算屏幕可容纳多少行外星人"""
    available_space_y = (ai_settings.screen_height - 100 -
                         (7 / 3 * (alien_height)) - ship_height)
    number_rows = int(available_space_y / (2 * alien_height))
    return number_rows


def update_aliens(ai_settings, stats, screen, ship, aliens, bullets, ship_lifes):
    """检查是否有外星人位于屏幕的边缘，并更新外星人群中所有外星人的位置"""
    check_fleet_edges(ai_settings, aliens)
    aliens.update()

    # 检测外星人和飞船之间的碰撞
    if pygame.sprite.spritecollideany(ship, aliens):
        print("Ship hit!!!")
        ship_hit(ai_settings, stats, screen, ship, aliens, bullets, ship_lifes)

    # 检查是否有外星人到达屏幕底端
    check_aliens_bottom(ai_settings, stats, screen, ship, aliens, bullets, ship_lifes)


def check_fleet_edges(ai_settings, aliens):
    """有外星人到达边缘时采取相应的措施"""
    for alien in aliens.sprites():
        if alien.check_edges():
            change_fleet_direction(ai_settings, aliens)
            break


def change_fleet_direction(ai_settings, aliens):
    """将整群外星人下移，并改变它们的方向"""
    for alien in aliens.sprites():
        alien.rect.y += ai_settings.alien_drop_speed
    ai_settings.fleet_direction = - ai_settings.fleet_direction


def check_aliens_bottom(ai_settings, stats, screen, ship, aliens, bullets, ship_lifes):
    """检查是否有外星人到达屏幕底端"""
    screen_rect = screen.get_rect()
    for alien in aliens.sprites():
        if alien.rect.bottom >= ship.rect.top:
            # ~ ship.rect.top
            # 像飞船被撞到一样处理
            ship_hit(ai_settings, stats, screen, ship, aliens, bullets, ship_lifes)
            break


def ship_hit(ai_settings, stats, screen, ship, aliens, bullets, ship_lifes):
    """响应飞船被外星人撞到"""
    if stats.ships_left > 1:
        # 将ships_left减1
        stats.ships_left -= 1

        # 清空外星人列表和子弹列表
        aliens.empty()
        bullets.empty()
        ship_lifes.empty()
        # ~ ai_settings.ship_limit -= 1

        # 创建一群新的外星人，并将飞船放到屏幕中央
        create_fleet(ai_settings, screen, ship, aliens)
        create_ship_life_fleet(ai_settings, screen, ship_lifes, stats)
        ship.center_ship()

        # 暂停
        sleep(0.5)
    else:
        # ~ print("Set 'False' right!!")
        stats.game_active = False
        pygame.mouse.set_visible(True)


def create_ship_life(ai_settings, screen, ship_lifes, ship_life_number):
    """创建一个飞机剩余数的计数图"""
    ship_life = ShipLife(ai_settings, screen)
    ship_life_width = ship_life.rect.width
    ship_life.rect.x = ship_life_number * ship_life_width
    ship_life.y = 0
    ship_lifes.add(ship_life)


def create_ship_life_fleet(ai_settings, screen, ship_lifes, stats):
    """创建三条命"""
    # 创建一个飞船图，再创建两个
    ship_life = ShipLife(ai_settings, screen)

    # 创建飞船三张图
    for ship_life_number in range(stats.ships_left):
        create_ship_life(ai_settings, screen, ship_lifes, ship_life_number)


def check_high_score(stats, scoreboard):
    """检查是否诞生了新的最高分"""
    if stats.score > stats.high_score:
        stats.high_score = stats.score
        scoreboard.prep_high_score()


def update_screen(ai_settings, screen, stats, ship, aliens, ship_lifes, bullets, play_button, scoreboard):
    """更新屏幕上的图像，并切换到新屏幕"""
    # 每次循环是都重绘屏幕
    screen.fill(ai_settings.bg_color)
    ship.blitme()
    aliens.draw(screen)
    ship_lifes.draw(screen)

    # 显示得分
    scoreboard.show_score()

    # 重绘所有子弹
    for bullet in bullets.sprites():
        bullet.draw_bullet()

    # 如果游戏处于非活动状态，就绘制Play按钮
    if not stats.game_active:
        play_button.draw_button()

    # 让最近绘制的屏幕可见
    pygame.display.flip()
