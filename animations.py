import tkinter as tk
import math

def fade_in(window, steps=10, delay=30):
    """Fade in a Toplevel window (if supported)."""
    def _fade(step):
        alpha = step / steps
        window.attributes('-alpha', alpha)
        if step < steps:
            window.after(delay, _fade, step + 1)
    window.attributes('-alpha', 0)
    _fade(0)

def flash_bg(widget, flash_color="#ffff99", flashes=3, delay=150):
    """Flash a widget's background color."""
    orig_color = widget.cget("background")
    def _flash(count):
        if count > 0:
            widget.config(background=flash_color)
            widget.after(delay, lambda: widget.config(background=orig_color))
            widget.after(delay * 2, lambda: _flash(count - 1))
        else:
            widget.config(background=orig_color)
    _flash(flashes)

def grow_from_center(widget, duration=600, steps=60, on_finish=None):
    """Animate a widget growing from the center."""
    widget.pack(expand=True, fill="both")
    widget.update_idletasks()
    w = widget.winfo_width()
    h = widget.winfo_height()
    widget.pack_forget()
    widget.place(relx=0.5, rely=0.5, anchor="center", width=0, height=0)
    def animate(step):
        if step > steps:
            widget.place(relx=0.5, rely=0.5, anchor="center", width=w, height=h)
            widget.after(20, finish_transition)
            return
        frac = step / steps
        widget.place(relx=0.5, rely=0.5, anchor="center",
                     width=int(w * frac), height=int(h * frac))
        widget.after(duration // steps, animate, step + 1)
    def finish_transition():
        widget.place_forget()
        if on_finish:
            on_finish()
    animate(1)

def slide(widget, duration=700, steps=30, direction="right", on_finish=None):
    """
    Simple slide animation: slides the widget left or right and back.
    """
    widget.update_idletasks()
    w = widget.winfo_width()
    h = widget.winfo_height()
    widget.place(relx=0.5, rely=0.5, anchor="center", width=w, height=h)
    def animate(step):
        frac = step / steps
        if direction == "right":
            offset = int(w * frac)
        else:
            offset = -int(w * frac)
        widget.place(relx=0.5, rely=0.5, anchor="center", width=w, height=h, x=offset)
        if step < steps:
            widget.after(duration // steps, animate, step + 1)
        else:
            widget.place_forget()
            if on_finish:
                on_finish()
    animate(0)