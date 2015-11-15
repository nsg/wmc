#!/usr/bin/python
# -*- coding: utf-8 -*-

from gi.repository import Gtk, Gdk, GLib, Pango, Wnck
import cairo, inspect, pprint, re, os.path, yaml

class ConfigMWC():
    config_file = os.environ['HOME'] + "/.wmc-config.yml"
    _settings = {}

    def __init__(self):
        print self.config_file
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
    search_string = "";

    def __init__(self):
        super(UI, self).__init__()

        config = ConfigMWC()
        print(config.settings())

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

        if event.string == '\x1b': # ESC
             Gtk.main_quit()
             return

        if self.search_mode:
            if event.string == '\r': # Return
                self.search_mode = False
                print "Search mode: OFF"
            if event.string == '\x08': # Backspace
                self.search_string = self.search_string[:-1]
            else:
                self.search_string = self.search_string + event.string.strip()

            screen = Wnck.Screen.get_default()
            screen.force_update()
            m = []
            for window in screen.get_windows():
                if re.match(".*" +self.search_string+ ".*", window.get_name(), flags=re.IGNORECASE):
                    m.append(window.get_name())
                    if not self.search_mode:
                        now = timestamp = Gtk.get_current_event_time()
                        window.activate(now)
                        Gtk.main_quit()
                        return

            self.update_text("▶ " + self.search_string + "\n\n" + "\n".join(m))
            return

        elif event.string == "/":
            self.update_text("Search Mode")
            self.search_mode = True
            print "Search mode: ON"

        elif event.string == "s":
            screen = Wnck.Screen.get_default()
            screen.force_update()
            for window in screen.get_windows():
                if re.match(".*Spotify.*", window.get_name()):
                    window.activate(0)

        else:
            pp = pprint.PrettyPrinter(indent=4)
            pp.pprint(inspect.getmembers(event))

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
