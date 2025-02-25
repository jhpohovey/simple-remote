import pygame
from pygame import gfxdraw
from roku_remote import RokuRemote
import argparse 
import logging

class RokuRemoteApp:
    def __init__(self, ip_address, port=8060):
        pygame.init()

        self.WIDTH, self.HEIGHT = 300, 600
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Roku Remote Interface")

        # arbitrary colors
        self.BLACK = (20, 20, 20)
        self.WHITE = (255, 255, 255)
        self.PURPLE = (128, 0, 128)
        self.DARK_GRAY = (50, 50, 50)
        self.RED = (200, 0, 0)

        self.remote = RokuRemote(ip_address, port)

        # input fsm
        self.inputs = [
            "InputTuner", "InputHDMI1", "InputHDMI2", 
            "InputHDMI3", "InputHDMI4", "InputAV1"
        ]
        self.current_input_index = 0

        # text input state
        self.typing = False
        self.input_text = ""

        # power state
        self.power_on = False

        # button positions and sizes
        self.create_buttons()

    def create_buttons(self):
        self.buttons = {
            "power": (260, 50, 20, self.toggle_power),
            "cycle_input": pygame.Rect(170, 80, 60, 40),
            "home": pygame.Rect(120, 80, 40, 40),
            "back": pygame.Rect(60, 80, 40, 40),
            "dpad_up": pygame.Rect(110, 140, 60, 40),
            "dpad_left": pygame.Rect(70, 180, 40, 60),
            "dpad_right": pygame.Rect(170, 180, 40, 60),
            "dpad_down": pygame.Rect(110, 240, 60, 40),
            "dpad_center": (140, 210, 30, self.remote.select),
            "play_pause": pygame.Rect(120, 350, 40, 40),
            "rewind": pygame.Rect(60, 350, 40, 40),
            "fast_forward": pygame.Rect(180, 350, 40, 40),
            "vol_up": pygame.Rect(50, 450, 40, 40),
            "vol_down": pygame.Rect(50, 500, 40, 40),
            "type_input": pygame.Rect(130, 500, 40, 40),
            "volume_mute": pygame.Rect(50, 550, 40, 40),
            "ch_up": pygame.Rect(210, 450, 40, 40),
            "ch_down": pygame.Rect(210, 500, 40, 40),
            "instant_replay": pygame.Rect(120, 400, 40, 40),
            "info": pygame.Rect(120, 550, 40, 40),
            "backspace": pygame.Rect(120, 600, 40, 40),
            "search": pygame.Rect(120, 650, 40, 40),
            "enter": pygame.Rect(120, 700, 40, 40),
            "find_remote": pygame.Rect(120, 750, 40, 40),
        }

    def draw_circle_button(self, surface, color, position, radius, border_color, border_width=2):
        pygame.gfxdraw.filled_circle(surface, *position, radius, color)
        pygame.gfxdraw.aacircle(surface, *position, radius, border_color)

    def draw_power_symbol(self, surface, position):
        x, y = position
        pygame.draw.circle(surface, self.WHITE, (x, y), 18, 2)
        pygame.draw.line(surface, self.WHITE, (x, y - 10), (x, y + 5), 2)

    def draw_text(self, surface, text, position, font_size=20, color=None):
        if color is None:
            color = self.WHITE
        font = pygame.font.Font(None, font_size)
        text_surf = font.render(text, True, color)
        text_rect = text_surf.get_rect(center=position)
        surface.blit(text_surf, text_rect)

    def draw_house(self, surface, rect):
        x, y, w, h = rect
        house_width = w // 2
        house_height = h // 2
        pygame.draw.polygon(surface, self.WHITE, [
            (x + w // 2, y + h // 4),  # Top of the roof
            (x + w // 4, y + h // 2),  # Left corner of the roof
            (x + 3 * w // 4, y + h // 2)  # Right corner of the roof
        ])
        pygame.draw.rect(surface, self.WHITE, (
            x + w // 4, y + h // 2, house_width, house_height
        ))

    def draw_arrow(self, surface, rect, direction):
        x, y, w, h = rect
        if direction == "left":
            pygame.draw.polygon(surface, self.WHITE, [(x + w, y), (x, y + h // 2), (x + w, y + h)])
        elif direction == "right":
            pygame.draw.polygon(surface, self.WHITE, [(x, y), (x + w, y + h // 2), (x, y + h)])
        elif direction == "up":
            pygame.draw.polygon(surface, self.WHITE, [(x, y + h), (x + w // 2, y), (x + w, y + h)])
        elif direction == "down":
            pygame.draw.polygon(surface, self.WHITE, [(x, y), (x + w // 2, y + h), (x + w, y)])

    def draw_play_pause_symbol(self, surface, rect):
        x, y, w, h = rect
        pygame.draw.polygon(surface, self.WHITE, [
            (x + w // 4, y + h // 4),
            (x + w // 4, y + 3 * h // 4),
            (x + 3 * w // 4, y + h // 2)
        ])
        pygame.draw.rect(surface, self.WHITE, (x + w // 2, y + h // 4, w // 8, h // 2))
        pygame.draw.rect(surface, self.WHITE, (x + 5 * w // 8, y + h // 4, w // 8, h // 2))

    def draw_rewind_symbol(self, surface, rect):
        x, y, w, h = rect
        pygame.draw.polygon(surface, self.WHITE, [
            (x + 3 * w // 4, y + h // 4),
            (x + w // 4, y + h // 2),
            (x + 3 * w // 4, y + 3 * h // 4)
        ])
        pygame.draw.polygon(surface, self.WHITE, [
            (x + w // 2, y + h // 4),
            (x, y + h // 2),
            (x + w // 2, y + 3 * h // 4)
        ])

    def draw_fast_forward_symbol(self, surface, rect):
        x, y, w, h = rect
        pygame.draw.polygon(surface, self.WHITE, [
            (x + w // 4, y + h // 4),
            (x + 3 * w // 4, y + h // 2),
            (x + w // 4, y + 3 * h // 4)
        ])
        pygame.draw.polygon(surface, self.WHITE, [
            (x + w // 2, y + h // 4),
            (x + w, y + h // 2),
            (x + w // 2, y + 3 * h // 4)
        ])

    def handle_click(self, pos):
        for name, rect in self.buttons.items():
            if name == "power":
                if (pos[0] - rect[0]) ** 2 + (pos[1] - rect[1]) ** 2 <= rect[2] ** 2:
                    rect[3]()
                    return
            elif name == "dpad_center":
                if (pos[0] - rect[0]) ** 2 + (pos[1] - rect[1]) ** 2 <= rect[2] ** 2:
                    rect[3]()
                    return
            elif name == "cycle_input":
                if rect.collidepoint(pos):
                    self.cycle_input()
                    return
            elif name == "type_input":
                if rect.collidepoint(pos):
                    self.typing = True
                    return
            else:
                if rect.collidepoint(pos):
                    if name == "home":
                        self.remote.home()
                    elif name == "back":
                        self.remote.back()
                    elif name == "dpad_up":
                        self.remote.up()
                    elif name == "dpad_left":
                        self.remote.left()
                    elif name == "dpad_right":
                        self.remote.right()
                    elif name == "dpad_down":
                        self.remote.down()
                    elif name == "play_pause":
                        self.remote.play()
                    elif name == "rewind":
                        self.remote.rewind()
                    elif name == "fast_forward":
                        self.remote.fast_forward()
                    elif name == "vol_up":
                        self.remote.volume_up()
                    elif name == "vol_down":
                        self.remote.volume_down()
                    elif name == "volume_mute":
                        self.remote.volume_mute()
                    elif name == "ch_up":
                        self.remote.channel_up()
                    elif name == "ch_down":
                        self.remote.channel_down()
                    elif name == "instant_replay":
                        self.remote.instant_replay()
                    elif name == "info":
                        self.remote.info()
                    elif name == "backspace":
                        self.remote.backspace()
                    elif name == "search":
                        self.remote.search()
                    elif name == "enter":
                        self.remote.enter()
                    elif name == "find_remote":
                        self.remote.find_remote()
                    return

    def cycle_input(self):
        self.current_input_index = (self.current_input_index + 1) % len(self.inputs)
        current_input = self.inputs[self.current_input_index]
        self.remote.send_command(current_input)

    def type_input(self):
        for char in self.input_text:
            self.remote.send_command(f"Lit_{char}")
        self.input_text = ""
        self.typing = False

    def toggle_power(self):
        if self.power_on:
            self.remote.power_off()
        else:
            self.remote.power_on()
        self.power_on = not self.power_on

    def draw_buttons(self):
        for name, rect in self.buttons.items():
            if name == "power":
                self.draw_circle_button(self.screen, self.RED, rect[:2], rect[2], self.WHITE)
                self.draw_power_symbol(self.screen, rect[:2])
            elif name == "dpad_center":
                self.draw_circle_button(self.screen, self.PURPLE, rect[:2], rect[2], self.WHITE)
                self.draw_text(self.screen, "OK", rect[:2])
            elif name == "cycle_input":
                pygame.draw.rect(self.screen, self.DARK_GRAY, rect, border_radius=10)
                pygame.draw.rect(self.screen, self.WHITE, rect, 2, border_radius=10)
                self.draw_text(self.screen, "Input", rect.center, font_size=15)
            elif name == "type_input":
                pygame.draw.rect(self.screen, self.DARK_GRAY, rect, border_radius=10)
                pygame.draw.rect(self.screen, self.WHITE, rect, 2, border_radius=10)
                self.draw_text(self.screen, "Type", rect.center, font_size=15)
            else:
                color = self.PURPLE if "dpad" in name else self.DARK_GRAY
                pygame.draw.rect(self.screen, color, rect, border_radius=10)
                pygame.draw.rect(self.screen, self.WHITE, rect, 2, border_radius=10)
                if name == "home":
                    self.draw_house(self.screen, rect)
                elif name == "back":
                    self.draw_arrow(self.screen, rect, "left")
                elif name == "dpad_up":
                    self.draw_arrow(self.screen, rect, "up")
                elif name == "dpad_left":
                    self.draw_arrow(self.screen, rect, "left")
                elif name == "dpad_right":
                    self.draw_arrow(self.screen, rect, "right")
                elif name == "dpad_down":
                    self.draw_arrow(self.screen, rect, "down")
                elif name == "play_pause":
                    self.draw_play_pause_symbol(self.screen, rect)
                elif name == "rewind":
                    self.draw_rewind_symbol(self.screen, rect)
                elif name == "fast_forward":
                    self.draw_fast_forward_symbol(self.screen, rect)
                elif name == "vol_up":
                    self.draw_text(self.screen, "Vol+", rect.center, font_size=15)
                elif name == "vol_down":
                    self.draw_text(self.screen, "Vol-", rect.center, font_size=15)
                elif name == "volume_mute":
                    self.draw_text(self.screen, "Mute", rect.center, font_size=15)
                elif name == "ch_up":
                    self.draw_text(self.screen, "CH+", rect.center, font_size=15)
                elif name == "ch_down":
                    self.draw_text(self.screen, "CH-", rect.center, font_size=15)
                elif name == "instant_replay":
                    self.draw_text(self.screen, "IR", rect.center, font_size=15)
                elif name == "info":
                    self.draw_text(self.screen, "Info", rect.center, font_size=15)
                elif name == "backspace":
                    self.draw_text(self.screen, "Back", rect.center, font_size=15)
                elif name == "search":
                    self.draw_text(self.screen, "Search", rect.center, font_size=15)
                elif name == "enter":
                    self.draw_text(self.screen, "Enter", rect.center, font_size=15)
                elif name == "find_remote":
                    self.draw_text(self.screen, "Find", rect.center, font_size=15)

        # Draw the text input box if typing
        if self.typing:
            pygame.draw.rect(self.screen, self.WHITE, (50, 300, 200, 40), 2)
            self.draw_text(self.screen, self.input_text, (150, 320), font_size=20, color=self.WHITE)

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)
                elif event.type == pygame.KEYDOWN and self.typing:
                    if event.key == pygame.K_RETURN:
                        self.type_input()
                    elif event.key == pygame.K_BACKSPACE:
                        self.input_text = self.input_text[:-1]
                    else:
                        self.input_text += event.unicode

            self.screen.fill(self.BLACK)
            self.draw_buttons()
            pygame.display.flip()

        pygame.quit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Roku Remote GUI Application")
    parser.add_argument("--ip", type=str, default="192.168.50.59", help="IP address of the Roku TV (default: 192.168.1.100)")
    parser.add_argument("--port", type=int, default=8060, help="Port of the Roku TV (default: 8060)")
    parser.add_argument("--enable_logging", action="store_true", help="Enable logging")
    args = parser.parse_args()

    if args.enable_logging:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.CRITICAL)

    app = RokuRemoteApp(args.ip, args.port)
    app.run()
