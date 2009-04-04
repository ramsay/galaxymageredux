import pyggel
from pyggel import *

import objects

class MessageBox(pyggel.gui.Frame):
    def __init__(self, app, num_messages=15, **kwargs):
        pyggel.gui.Frame.__init__(self, app, **kwargs)
        self.num_messages = num_messages

##        self.theme = pyggel.gui.Theme(self)
##        self.theme.load("data/gui/theme.py")
        self.theme = self.app.theme
        self.theme.theme = dict(self.theme.theme)
        self.theme.theme["Label"]["background-image"] = None

        self.packer.pack_upwards = self.pack_upwards
        self.packer.packtype = "upwards"
        self._messages = []

    def pack_upwards(self):
        bottom = self.size[1]-self.tsize[1]*2
        self.widgets.reverse() #flip them!
        for i in self.widgets:
            pos = (0, bottom-i.size[1])
            bottom -= i.size[1]
            i.force_pos_update(pos)
        self.widgets.reverse()

    def add_message(self, message, color=(1,1,1,1)):
        x = pyggel.gui.Label(self, message, font_color=color, font_color_inactive=color)
        self._messages.append(x)
        if len(self.widgets) > self.num_messages:
            x = self._messages[0]
            self.widgets.remove(x)
            self._messages.remove(x)

class GameState(object):
    def __init__(self, game, parent=None):
        self.game = game
        self.parent = parent
        self.children = {}

        self.active_child = None

    def goback(self):
        if self.parent:
            self.parent.active_child = None

    def goto(self, child_name):
        self.active_child = self.children[child_name](self.game, self)

    def update(self):
        if self.active_child:
            self.active_child.update()

    def get_netMessage(self, message):
        if self.active_child:
            self.active_child.get_netMessage(message)

    def get_errorMessage(self, message):
        if self.active_child:
            self.active_child.get_errorMessage(message)

    def send_netMessage(self, message):
        self.game.sendMessage(message)

class MainMenu(GameState):
    def __init__(self, game, parent=None):
        GameState.__init__(self, game)
        self.children = {"chat":ChatWindow,
                         "test_map":TestMap}

        self.event_handler = pyggel.event.Handler()
        self.scene = pyggel.scene.Scene()
        self.app = pyggel.gui.App(self.event_handler)
        self.app.theme.load("data/gui/theme.py")
        self.app.packer.packtype="center"
        self.settings_app = pyggel.gui.App(self.event_handler)
        self.settings_app.theme.load("data/gui/theme.py")
        self.settings_app.packer.packtype="center"

        frame = pyggel.gui.Frame(self.settings_app, size=(350,125))
        #TODO: add widgets to swap back!!!
        self.checks = pyggel.gui.MultiChoiceRadio(frame, options=["FPS",
                                                                  "sound",
                                                                  "fullscreen",
                                                                  "verbose_logging"])
        self.checks.dispatch.bind("change", self.need_restart)
        self.resolution = pyggel.gui.Radio(frame, options=["640x480",
                                                           "800x600",
                                                           "1024x768",
                                                           "1680x1050"])
        self.resolution.dispatch.bind("change", self.need_restart)

        self.alert_quit_window = pyggel.gui.Frame(self.settings_app, size=(135, 50), pos=(0,0))
        self.alert_quit_window.packer.packtype="center"
        self.alert_quit_window.visible = False
        pyggel.gui.Button(self.alert_quit_window, "Quit Now", callbacks=[self.force_quit])
        pyggel.gui.Button(self.alert_quit_window, "Later...", callbacks=[self.toggle_alert_quit_window])

        pyggel.gui.NewLine(frame)
        pyggel.gui.Button(frame, "Save Changes", callbacks=[self.save_options])
        pyggel.gui.Button(frame, "Back", callbacks=[self.app.activate])
        self.alert_label = pyggel.gui.Label(frame, "Game must be restarted before\nchanges will take effect!",
                                            font_color=(1,0,0,1), font_color_inactive=(1,0,0,1),
                                            background_image=None)
        self.alert_label.visible = False
        self.scene.add_2d(self.settings_app)
        self.app.activate()

        pyggel.gui.Button(self.app, "Single Player", callbacks=[lambda:self.goto("test_map")])
        pyggel.gui.NewLine(self.app)
        pyggel.gui.Button(self.app, "Multiplayer", callbacks=[lambda:self.goto("chat")])
        pyggel.gui.NewLine(self.app)
        pyggel.gui.Button(self.app, "Options", callbacks=[self.run_options])
        pyggel.gui.NewLine(self.app)
        pyggel.gui.Button(self.app, "Exit", callbacks=[self.force_quit])
        self.scene.add_2d(self.app)

    def run_options(self):
        self.settings_app.activate()
        for i in self.checks.options:
            name, check, label, state = i
            state = int(self.game.config[name])
            check.state = state
            i[0], i[1], i[2], i[3] = name, check, label, state

        x = "%sx%s"%self.game.config["resolution"]
        if x in self.resolution.states:
            for i in self.resolution.options:
                name, check, label, state = i
                if name == x:
                    state = 1
                    check.state = 1
                else:
                    state = 0
                    check.state = 0
                i[0], i[1], i[2], i[3] = name, check, label, state
        else:
            pass
        self.alert_label.visible = False

    def need_restart(self, state):
        if bool(self.checks.states["fullscreen"]) != self.game.config["fullscreen"]:
            self.alert_label.visible = True
        elif self.get_option_resolution() != self.game.config["resolution"]:
            self.alert_label.visible = True
        else:
            self.alert_label.visible = False

    def toggle_alert_quit_window(self):
        self.alert_quit_window.visible = not self.alert_quit_window.visible
        self.alert_quit_window.focus()
        self.alert_quit_window.pos = self.alert_quit_window.app.get_mouse_pos()

    def get_option_resolution(self):
        r = "640x480"
        for i in self.resolution.states:
            if self.resolution.states[i]: r = i
        a, b = r.split("x")
        return (int(a), int(b))

    def save_options(self):
        fobj = open("data/config.txt", "w")
        fobj.write("name='reduxian'\nFPS=%s\nsound=%s\nfullscreen=%s\nverbose_logging=%s\nresolution=%s"%(
            bool(self.checks.states["FPS"]),
            bool(self.checks.states["sound"]),
            bool(self.checks.states["fullscreen"]),
            bool(self.checks.states["verbose_logging"]),
            self.get_option_resolution()))
        fobj.close()
        if self.alert_label.visible:
            self.toggle_alert_quit_window()

    def force_quit(self):
        self.event_handler.quit = True

    def update(self):
        if self.active_child:
            self.active_child.update()
        else:
            self.event_handler.update()
            if self.event_handler.quit:
                self.exit()
                return None
            pyggel.view.clear_screen()
            self.scene.render()
            pyggel.view.refresh_screen()

    def exit(self):
        self.game.close()
        self.game.running = False
        pyggel.quit()

class ChatWindow(GameState):
    def __init__(self, game, parent=None):
        GameState.__init__(self, game, parent)
        self.event_handler = pyggel.event.Handler()
        self.scene = pyggel.scene.Scene()
        self.app = pyggel.gui.App(self.event_handler)
        self.app.theme.load("data/gui/theme.py")
        self.message_frame = MessageBox(self.app, size=(200, 200))
        pyggel.gui.NewLine(self.app)
        self.input = pyggel.gui.Input(self.app, callback=self.send_netMessage, font_color=(1,1,1,1),
                                      width=200)
        pyggel.gui.NewLine(self.app)
        pyggel.gui.Button(self.app, "Menu", callbacks=[self.stop])
        self.scene.add_2d(self.app)
        self.game.connect()

    def stop(self):
        self.goback()
        self.game.disconnect()

    def update(self):
        GameState.update(self)
        if not self.input.key_active:
            self.input.key_active = True #make sure the input always takes, well, input...

        self.event_handler.update()
        if self.event_handler.quit:
            self.game.close()
            self.game.running = False
            pyggel.quit()
            return None

        pyggel.view.clear_screen()
        self.scene.render()
        pyggel.view.refresh_screen()

    def get_netMessage(self, message):
        GameState.get_netMessage(self, message)
        self.message_frame.add_message(message)
    
    def get_errorMessage(self, message):
        GameState.get_netMessage(self, message)
        self.message_frame.add_message(message, color=(1,.1,.1,1))

class TestMap(GameState):
    def __init__(self, game, parent=None):
        GameState.__init__(self, game, parent)

        self.event_handler = pyggel.event.Handler()
        self.scene = pyggel.scene.Scene()
        self.scene.pick = True
        self.app = pyggel.gui.App(self.event_handler)
        self.app.theme.load("data/gui/theme.py")
        pyggel.gui.Button(self.app, "Menu", callbacks=[self.goback])
        self.scene.add_2d(self.app)

        tiles = objects.parse_map("data/core/map/test_map.py")
        self.scene.add_3d(tiles)

        self.camera = pyggel.camera.LookAtCamera((0,0,0), distance=15)

        light = pyggel.light.Light((2,100,2), (1,1,1,1),
                                  (1,1,1,1), (0,0,0,0),
                                  (0,0,0), True)
        self.scene.add_light(light)

        _image = pyggel.image.Image3D("data/core/image/unit_example.png")

        self.unit = objects.Unit(tiles[1],#lets see how that works ;)
                                 pos=(0,0),
                                 image=_image, colorize=(1,1,1,1))
        self.scene.add_3d(self.unit)

        self.last_touching = (None, None)

    def update(self):
        GameState.update(self)

        self.event_handler.update()
        if self.event_handler.quit:
            self.game.close()
            self.game.running = False
            pyggel.quit()
            return None

        if K_LEFT in self.event_handler.keyboard.active:
            self.camera.roty -= 1
        if K_RIGHT in self.event_handler.keyboard.active:
            self.camera.roty += 1
        if K_UP in self.event_handler.keyboard.active:
            self.camera.rotx -= 1
        if K_DOWN in self.event_handler.keyboard.active:
            self.camera.rotx += 1

        pyggel.view.clear_screen()
        touching = self.scene.render(self.camera)
        if self.last_touching[0]:
            self.last_touching[0].colorize = self.last_touching[1]
        if touching:
            if isinstance(touching, objects.Unit):
                touching = touching.tile
            self.last_touching = (touching, touching.colorize)
            touching.colorize = (1,0,0,1)
        else:
            self.last_touching = (None, None)
        pyggel.view.refresh_screen()