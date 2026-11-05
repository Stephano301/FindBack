from kivy.uix.label import Label


def single_line_label(text, font_size, color, bold=False):
    """Texte sur une seule ligne, coupé avec « … » s'il est trop long."""
    label = Label(
        text=text,
        font_size=font_size,
        color=color,
        bold=bold,
        halign="left",
        valign="middle",
        shorten=True,
        shorten_from="right",
    )
    label.bind(size=lambda inst, size: setattr(inst, "text_size", size))
    return label