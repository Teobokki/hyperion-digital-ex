"""HYPERION DIGITAL EX - built-in catalog of EX Inc. apps and games.
©2026 EX Inc./HYPERION DIGITAL ©2026"""

GAMES, APPS = "Games", "Apps & Tools"

CATALOG = [
    dict(
        id="dream-vine", name="DREAM VINE", repo="dream-vine", category=GAMES, genre="Sandbox · Survival · Creative",
        exe="DREAM VINE.exe", folder="DREAM VINE", portable=["DREAM VINE.exe", "DREAM.VINE.Portable.exe"],
        version="1.3.2",
        tagline="An original block-building sandbox. Explore endless worlds, mine, craft, build and survive the night.",
        about=("DREAM VINE is an original block-building sandbox game by EX Inc. Explore endless procedurally generated "
               "worlds, mine, craft and build, survive the night, or fly around freely in Creative. All code, textures, "
               "names, mobs and logos are original, and everything is generated procedurally."),
        features=[
            "Infinite chunked worlds from a seed: beaches, water, hills and mountains, forests, caves, ores and bedrock",
            "Survival (health, hunger, fall damage, tool tiers) and Creative (all blocks, instant break, flying)",
            "9-slot hotbar, 27-slot inventory and crafting: tools from wood to diamond, glass, bricks, Dream Vine blocks",
            "Day/night cycle with sunsets, sun, moon, clouds and fog",
            "Mobs: Mossbuck (passive grazer) and Gloomer (hostile at night, glowing eyes)",
            "Text chat with commands: /gamemode, /time, /tp, /seed, /build, /undo and more",
            "VINE BUILD (Creative): describe any building and Vine AI builds it in front of you, fully offline",
        ]),
    dict(
        id="piknott-celestika", name="PIKNOTT CELESTIKA", repo="piknott-celestika", category=GAMES,
        genre="RPG · Monster catching · Cel-shaded",
        exe="PIKNOTT CELESTIKA.exe", folder="PIKNOTT CELESTIKA",
        portable=["PIKNOTT CELESTIKA.exe", "PIKNOTT.CELESTIKA.Portable.exe"], version="1.0.0",
        tagline="A fully cel-shaded monster-catching RPG. Catch 13 PIKNOTT across the Celestika region.",
        about=("Explore the Celestika region as a boy in a red hoodie, sneak through tall grass, throw PIKCEL balls to "
               "catch wild PIKNOTT, and battle them with your team using an action-order battle system with "
               "Normal / Strong / Agile move styles. Custom toon shaders with ink outlines give the whole world a "
               "hand-drawn look."),
        features=[
            "Catch 13 PIKNOTT with three kinds of PIKCEL balls",
            "Action-order battles with Normal, Strong and Agile move styles",
            "Sneak through tall grass while crouching to stay hidden",
            "Team screen, CELESTIKA DOK and a region map",
            "Rest and heal at camp fires; progress is saved automatically",
            "Keyboard + mouse and basic gamepad support",
        ]),
    dict(
        id="hyperia", name="HYPERIA", repo="hyperia", category=APPS, genre="Desktop shell",
        exe="HYPERIA.exe", folder="HYPERIA", portable=[], version="1.1.23",
        tagline="A creative desktop shell for Windows: wallpaper, taskbar, Start menu and windows inside the shell.",
        about=("HYPERIA is a creative desktop shell from EX Inc. that runs on Windows: wallpaper, taskbar, Start menu, "
               "desktop icons and windows that open inside the shell. It is an app, not an operating system. Web apps "
               "open the real websites in a HYPERIA web window (uses the Microsoft Edge WebView2 Runtime)."),
        features=[
            "Built in: HYPERIA Store, Notebook, Files, Terminal (PowerShell), Settings, Clock",
            "Games inside the shell: Pong and Fireout 1997, an original retro top-down racer",
            "Web windows: EX SAFARIA LITE browser and shortcuts to popular sites",
            "F11 fullscreen; Esc closes the Start menu",
        ]),
    dict(
        id="ex-creator-studio", name="EX CREATOR STUDIO", repo="ex-creator-studio", category=APPS,
        genre="Creative · Lip-sync · Video",
        exe="EX CREATOR STUDIO.exe", folder="EX CREATOR STUDIO", portable=[], version="1.3.0",
        tagline="One board. Any character. Type a line and watch it talk, then download it as an MP4.",
        about=("Upload any character or art to the REX BOARD and type what it should say. EX CREATOR STUDIO speaks it "
               "with an offline Windows voice and lip-syncs the character's mouth to it, then renders the result as "
               "an MP4. EX STUDIO adds a built-in screen recorder."),
        features=[
            "Auto character detection for anime/cartoon faces and real faces, with mouth location",
            "Set mouth manually by clicking or dragging a box, so any character can talk",
            "Offline SAPI5 text-to-speech with your installed Windows voices and a speed setting",
            "Pin screenshots onto the board, drag and resize them",
            "Download renders an H.264/AAC MP4 to your Downloads folder",
            "EX STUDIO screen recorder",
        ]),
    dict(
        id="ex-network", name="EX NETWORK", repo="ex-network", category=APPS, genre="Utility · Network",
        exe="EX NETWORK.exe", folder="EX NETWORK", portable=[], version="1.2.1",
        tagline="Keeps your WiFi connection stable: fewer drop-outs, auto-reconnect and one-click repairs.",
        about=("A small Windows app that helps keep your WiFi connection stable. It does not make your internet faster; "
               "it cuts down on drop-outs and lag spikes caused by Windows power saving, reconnects automatically when "
               "the link dies, and gives you one-click versions of the usual network repair commands."),
        features=[
            "Live status: SSID, signal, receive/transmit rate, band and channel",
            "Stabilize: turns off WiFi adapter power saving (restores your settings when turned off)",
            "Auto-reconnect watchdog after 3 failed pings",
            "Repair: flush DNS, release/renew, optional Winsock reset",
            "Ping test with average/min/max latency and packet loss",
        ]),
    dict(
        id="ex-sudo-terminal", name="EX SUDO TERMINAL", repo="ex-sudo-terminal", category=APPS,
        genre="Utility · Terminal",
        exe="EX SUDO TERMINAL.exe", folder="EX SUDO TERMINAL", portable=[], version="1.1.2",
        tagline="A GUI terminal for PowerShell with a persistent ConPTY session and one-click Run as admin.",
        about=("EX SUDO TERMINAL is a Windows GUI terminal for PowerShell. It runs a persistent ConPTY PowerShell session "
               "(so cd and variables stick), streams output live, and can relaunch itself as administrator when you "
               "need elevated rights."),
        features=[
            "Persistent ConPTY PowerShell session; interactive tools run inside the window",
            "Monospace output and an input line with history (Up/Down), Enter to run, Ctrl+C to stop",
            "Run as admin relaunches the app elevated",
            "One-click Install Grok CLI button (runs only when you click it)",
        ]),
    dict(
        id="fireout-revolution", name="FIREOUT REVOLUTION\u2122", repo="fireout-revolution", category=APPS,
        genre="Viewer · Slides",
        exe="FIREOUT REVOLUTION.exe", folder="FIREOUT REVOLUTION", portable=[], version="1.0.3",
        tagline="Live viewer for FIREOUT REVOLUTION Slides.pdf from your Downloads folder.",
        about=("FIREOUT REVOLUTION\u2122 is a live viewer for FIREOUT REVOLUTION Slides.pdf in your Downloads folder. "
               "It fits each slide to the window and refreshes live when the PDF changes."),
        features=["Fit-to-window slide view", "Live refresh when the PDF changes",
                  "Left/Right arrow keys change slides", "Built-in update check"]),
]

# release asset sizes (bytes) at the time HYPERION DIGITAL EX 1.0.0 shipped; live sizes come from GitHub.
KNOWN_SIZES = {
    "DREAM.VINE.Setup.1.3.2.exe": 58799178, "DREAM.VINE.1.3.2.Windows.x64.zip": 81397329,
    "PIKNOTT.CELESTIKA.Setup.1.0.0.exe": 30078007, "FIREOUT.REVOLUTION.Setup.1.0.3.exe": 36570264,
    "FIREOUT.REVOLUTION.zip": 52791095, "HYPERIA.Setup.1.1.23.exe": 15319842, "HYPERIA.zip": 16477249,
    "EX.CREATOR.STUDIO.Setup.1.3.0.exe": 69162520, "EX.CREATOR.STUDIO.zip": 102129520,
    "EX.NETWORK.Setup.1.2.1.exe": 10069445, "EX_NETWORK.zip": 10861118,
    "EX.SUDO.TERMINAL.Setup.1.1.2.exe": 11926787, "EX_SUDO_TERMINAL.zip": 13609861,
    "DREAM.VINE.LAUNCHER.Setup.1.0.2.exe": 13957793, "DREAM.VINE.LAUNCHER.1.0.2.Windows.x64.zip": 17697430,
}
