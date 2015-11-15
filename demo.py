#!/usr/bin/python

from gi.repository import Gtk, Gdk, GLib, Pango
import cairo
import inspect, pprint

class UI(Gtk.Window):

    def __init__(self):
        super(UI, self).__init__()

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

        if event.string == "q":
             Gtk.main_quit()

        elif event.string == "f":
             self.update_text("Search for:")

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
