#!/usr/bin/python
# -*- coding: utf-8 -*-

from gi.repository import Gtk, Gdk, GLib, Pango, Wnck
import cairo, inspect, pprint, re, os.path, yaml, time

class ConfigMWC():
    config_file = os.environ['HOME'] + "/.wmc-config.yml"
    _settings = {}

    def __init__(self):
        if os.path.isfile(self.config_file):
            with open(self.config_file, 'r') as fh:
                self._settings = yaml.load(fh)

    def settings(self):
        return self._settings

    def get(self, key):
        if key in self._settings:
            return self._settings[key]
        else:
            return None


class UI(Gtk.Window):

    search_mode = False
    tag_mode = False
    search_string = "";
    search_last_window = None

    def __init__(self):
        super(UI, self).__init__()

        self.config = ConfigMWC()

        self.set_app_paintable(True)
        #self.set_type_hint(Gdk.WindowTypeHint.NOTIFICATION)
        self.set_decorated(False)

        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual != None and screen.is_composited():
            self.set_visual(visual)

        self.draw_ui()

        self.resize(640, 480)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.connect("delete-event", Gtk.main_quit)
        self.connect("key_press_event", self.on_key_press)
        self.connect("draw", self.on_draw)

        self.show_all()

    def draw_ui(self):

        self.lbl = Gtk.Label()
        self.lbl.set_text("Ready")

        fd = Pango.FontDescription("Serif 20")
        self.lbl.modify_font(fd)
        self.lbl.modify_fg(Gtk.StateFlags.NORMAL,Gdk.color_parse("white"))

        self.add(self.lbl)

    def on_draw(self, wid, cr):
        cr.set_operator(cairo.OPERATOR_CLEAR)
        cr.paint()
        cr.set_operator(cairo.OPERATOR_OVER)

    def on_key_press(self, widget, event):
        global text

        screen = Wnck.Screen.get_default()
        screen.force_update()
        self.active_window = screen.get_active_window()
        self.active_window.set_fullscreen(Gtk.get_current_event_time())

        if event.string == '\x1b': # ESC
             Gtk.main_quit()
             return

        if self.search_mode:
                self.search_string = self.search_string + event.string.strip()

        if self.tag_mode:
            self.tag_mode = False
            if self.config.get("search") and event.string in self.config.get("search"):
                self.search_mode = True
                self.search_string = self.config.get("search")[event.string]
                self.update_text("Search Mode")
            else:
                self.update_text("Ready")
                return

        if self.search_mode:
            if event.string == '\r': # Return
                self.search_mode = False
                self.search_string = ".*{}.*".format(self.search_string[:-1])
            if event.string == '\x08': # Backspace
                self.search_string = self.search_string[:-2]

            m = []
            for window in screen.get_windows():
                if re.match(self.search_string, window.get_name(), flags=re.IGNORECASE):
                    m.append(window.get_name())
                    if not self.search_mode:
                        now = timestamp = Gtk.get_current_event_time()
                        window.activate(now)
                        self.search_last_window = window
                        self.focus()
                        self.search_string = ""
                        return

            self.update_text("▶ {}\n\n{}".format(self.search_string, "\n".join(m)))
            return

        if event.string == "/":
            self.update_text("Search Mode")
            self.search_string = ""
            self.search_mode = True

        elif event.string == "q":
            self.update_text("Quick Search Mode")
            self.tag_mode = True

        elif self.search_last_window:
            if event.string == "m":
                self.search_last_window.minimize()
            elif event.string == "M":
                self.search_last_window.maximize()
            elif event.string == "-":
                self.search_last_window.unminimize(Gtk.get_current_event_time())

            self.focus()

        #else:
        #    pp = pprint.PrettyPrinter(indent=4)
        #    pp.pprint(inspect.getmembers(event))

    def focus(self):
        time.sleep(1)
        now = timestamp = Gtk.get_current_event_time()
        self.active_window.activate(now + 1)

    def update_text(self, text):
        self.lbl.set_text(text)
        self.queue_draw()


def main():

    app = UI()
    Gtk.main()


if __name__ == "__main__":
    # Workaround for ^C
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    main()
