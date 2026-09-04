"""Shared Qt stylesheets for the Kivo overlay."""

STYLESHEET = """
#container {
    background-color: rgba(10, 14, 22, 118);
    border-radius: 20px;
    border: 1px solid rgba(125, 211, 252, 36);
}

#container[paused="true"] {
    border: 1px solid rgba(251, 191, 36, 90);
}

#header {
    background-color: rgba(255, 255, 255, 6);
    border-top-left-radius: 20px;
    border-top-right-radius: 20px;
}

#brand {
    color: #7dd3fc;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1.4px;
}

#filename {
    color: rgba(226, 232, 240, 210);
    font-size: 12px;
    font-weight: 500;
}

#chip {
    background-color: rgba(125, 211, 252, 28);
    color: #e0f2fe;
    border-radius: 9px;
    padding: 3px 8px;
    font-size: 11px;
    font-weight: 600;
}

#chip[state="paused"] {
    background-color: rgba(251, 191, 36, 36);
    color: #fde68a;
}

#closeButton {
    background: transparent;
    color: rgba(148, 163, 184, 220);
    border: none;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 600;
    padding: 0;
}

#closeButton:hover {
    background-color: rgba(248, 113, 113, 40);
    color: #fecaca;
}

#footer {
    background: transparent;
}

QTextEdit {
    background: transparent;
    color: #f8fafc;
    border: none;
    font-weight: 600;
    padding: 8px 18px 10px 18px;
    selection-background-color: rgba(125, 211, 252, 70);
    selection-color: #f8fafc;
}

#topFade, #bottomFade {
    background: transparent;
}

#pauseBadge {
    background-color: rgba(15, 23, 42, 170);
    color: #fde68a;
    border: 1px solid rgba(251, 191, 36, 80);
    border-radius: 12px;
    padding: 6px 14px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1.6px;
}

#hint, #toast {
    background-color: rgba(15, 23, 42, 180);
    color: #cbd5e1;
    border: 1px solid rgba(255, 255, 255, 22);
    border-radius: 10px;
    padding: 5px 10px;
    font-size: 11px;
}

#helpButton {
    background: transparent;
    color: rgba(148, 163, 184, 220);
    border: none;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 700;
    padding: 0;
}

#helpButton:hover {
    background-color: rgba(125, 211, 252, 36);
    color: #e0f2fe;
}

#helpCard {
    background-color: rgba(10, 14, 22, 210);
    color: #e2e8f0;
    border: 1px solid rgba(125, 211, 252, 50);
    border-radius: 12px;
    padding: 10px 14px;
    font-size: 11px;
}

QProgressBar#seekBar {
    background-color: rgba(255, 255, 255, 22);
    border: none;
    border-radius: 2px;
    max-height: 4px;
    min-height: 4px;
}

QProgressBar#seekBar::chunk {
    background-color: #7dd3fc;
    border-radius: 2px;
}

QSizeGrip {
    width: 14px;
    height: 14px;
    background: transparent;
}
"""
