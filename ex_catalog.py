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
        id="fireout-shine", name="\u30d5\u30a1\u30a4\u30a2\u30a2\u30a6\u30c8\u30fb\u30b7\u30e3\u30a4\u30f3", repo="fireout-shine", category=GAMES,
        genre="Racing \u00b7 \u6307\u540d\u624b\u914d\u3055\u308c\u308b GET WANTED \u00b7 Open world",
        exe="FIREOUT SHINE.exe", folder="FIREOUT SHINE",
        portable=["FIREOUT SHINE.exe", "FIREOUT-SHINE-Portable.exe"], version="1.0.1", release="2026",
        publisher="EX Inc./HYPERION DIGITAL", developer="EX Inc./HYPERION DIGITAL",
        tagline="Open-world neon Tokyo and Hikari Beach: race, escape the police and live the night as ANA and DANIEL.",
        about=("\u30d5\u30a1\u30a4\u30a2\u30a2\u30a6\u30c8\u30fb\u30b7\u30e3\u30a4\u30f3 (FIREOUT SHINE) 1.0.1 is an open-world driving game set in "
               "an original neon Tokyo and the seaside Hikari Beach. Play as ANA and DANIEL, switch between them at any "
               "time, take any car with F, enter street races and activities, and GET WANTED: outrun the police as your wanted "
               "stars climb. Customise your ride at FRGARAGE, go home to Ana and Daniel's house to sleep, save and change "
               "outfits, and use the EX IX G9 phone to call a JP Taxi. "
               "Publisher: EX Inc./HYPERION DIGITAL. \u00a92026 EX Inc./HYPERION DIGITAL \u00a92026."),
        features=[
            "Open-world neon Tokyo plus Hikari Beach: scramble crossing, sign-lined streets, an elevated expressway and glass skyscrapers",
            "Play as ANA and DANIEL and switch between them at any time (Q)",
            "Take any car with F; street races against AI rivals, a time trial, a drift zone and speed cameras",
            "FRGARAGE: choose your car (including the DEBAUCHE sedan), paint it and set a custom number plate",
            "Weapon wheel (Tab): fists, baseball bat, pickaxe, taser, pistol, SMG and shotgun",
            "\u6307\u540d\u624b\u914d\u3055\u308c\u308b GET WANTED: wanted stars (1-5) and police chases. Escape to lose them, or get BUSTED",
            "Ana and Daniel's house: sleep, save, take a shower and change outfits in the wardrobe",
            "EX IX G9 phone with JP Taxi and Emergency Services, map waypoints and a day/night cycle",
        ]),
    dict(
        id="ex-sports-sfc27", name="EX SPORTS\u2122 SFC 27 STANDARD EDITION", repo="ex-sports-sfc27", category=GAMES,
        genre="Sports \u00b7 Football \u00b7 Online",
        exe="EX SPORTS SFC 27.exe", folder="EX SPORTS SFC 27",
        portable=["EX SPORTS SFC 27.exe", "EX-SPORTS-SFC27-Portable.exe"], version="1.0.0", release="2026",
        publisher="EX Inc.", developer="EX Inc.",
        tagline="7-a-side football at the SFC 27 stadium: quick matches against the AI, or online with friends using a join code.",
        about=("EX SPORTS\u2122 SFC 27 STANDARD EDITION is 7-a-side football at the EX SPORTS SFC 27 stadium. The pitch is full "
               "size with standard markings, goals with nets, stands packed with a crowd, and floodlights. Play a QUICK MATCH "
               "against the AI, or go ONLINE: host a session, share your SFC27-XXXX-XXXX join code and play with friends, with "
               "the AI filling the empty spots. Matches are UNLIMITED by default: the clock counts up and you end the match "
               "whenever you like. Every club and player is fictional. Online play needs no admin rights and no firewall setup. "
               "Publisher: EX Inc. \u00a92026 EX Inc./HYPERION DIGITAL \u00a92026."),
        features=[
            "QUICK MATCH VS AI: pass, shoot, tackle and sprint with kickoffs, goals, a scoreboard and a match clock",
            "ONLINE with friends via SFC27-XXXX-XXXX join codes: ALL OF US VS AI or SPLIT TEAMS, with AI fill, kick and ping",
            "UNLIMITED matches by default (END MATCH any time), or timed 4, 8, 12 and 90 minute games",
            "TEAMS: fictional clubs, an all-yellow kit and your own player look and name",
            "Full-size stadium: standard pitch markings, nets, four stands with a crowd and plain floodlights",
            "Per-user install, no admin rights; built-in update check",
        ]),
    dict(
        id="the-anulment", name="THE ANULMENT", repo="the-anulment", category=GAMES,
        genre="Story \u00b7 Open world \u00b7 Investigation",
        exe="THE ANULMENT.exe", folder="THE ANULMENT",
        portable=["THE ANULMENT.exe", "THE-ANULMENT-Portable.exe"], version="1.0.0", release="2026",
        publisher="EX Inc./HYPERION DIGITAL", developer="EX Inc./HYPERION DIGITAL",
        tagline="Rainy night in Valdora: the vote is annulled, CLN is arrested, and MIYOYAZU sets out to find the truth.",
        about=("THE ANULMENT 1.0.0 (Chapter 1: The Annulled Vote) is a story game set at night in the fictional country of Valdora. "
               "The Constitutional Court has annulled the first round of the presidential election and charged its winner, CLN. "
               "You play MIYOYAZU, an ordinary blogger in a grey hoodie: join the peaceful protest at the court, photograph and "
               "recover evidence, interview the prosecutors' aide and publish the truth. Take any vehicle with F, and stay calm when "
               "POLI\u021aIA VALDOREI pursue you. Type English with T and MIYOYAZU says it in an offline Romanian voice. "
               "All characters, parties, countries and events in this game are fictional. "
               "Publisher: EX Inc./HYPERION DIGITAL. \u00a92026 EX Inc./HYPERION DIGITAL \u00a92026."),
        features=[
            "Rainy night-time Valdora with wet streets and letterbox cutscenes",
            "Peaceful protest at the Constitutional Court: placards, candles and the chant CLN PRE\u0218EDINTE! / TURUL DOI \u00ceNAPOI!",
            "Fictional police (POLI\u021aIA VALDOREI): shield line, questioning, a pressure meter and pursuits that box you in",
            "Traffic with fictional brands: take any vehicle non-violently with F",
            "T chat: type English, MIYOYAZU speaks it with the offline Romanian Piper voice (bubble + subtitles)",
            "EX IX G10 phone: CAMERA with SELMOTES, MESSAGES, NEWS, MAP, EVIDENCE, RECORDER and SETTINGS",
            "Evidence board, interview and the PUBLISH THE TRUTH ending; minimap, full map and save/load",
            "Per-user install, no admin rights; built-in update check",
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

# upcoming games: shown in the store with a status tag; never installed, scanned or update-checked (none right now)
UPCOMING = []

# release asset sizes (bytes) at the time HYPERION DIGITAL EX 1.0.0 shipped; live sizes come from GitHub.
KNOWN_SIZES = {
    "DREAM.VINE.Setup.1.3.2.exe": 58799178, "DREAM.VINE.1.3.2.Windows.x64.zip": 81397329,
    "PIKNOTT.CELESTIKA.Setup.1.0.0.exe": 30078007, "FIREOUT.REVOLUTION.Setup.1.0.3.exe": 36570264,
    "FIREOUT.REVOLUTION.zip": 52791095, "HYPERIA.Setup.1.1.23.exe": 15319842, "HYPERIA.zip": 16477249,
    "EX.CREATOR.STUDIO.Setup.1.3.0.exe": 69162520, "EX.CREATOR.STUDIO.zip": 102129520,
    "EX.NETWORK.Setup.1.2.1.exe": 10069445, "EX_NETWORK.zip": 10861118,
    "EX.SUDO.TERMINAL.Setup.1.1.2.exe": 11926787, "EX_SUDO_TERMINAL.zip": 13609861,
    "FIREOUT-SHINE-Setup-1.0.1.exe": 137226943, "FIREOUT-SHINE-1.0.1-Windows-x64.zip": 163677077, "FIREOUT-SHINE-Portable.exe": 163032983,
    "EX-SPORTS-SFC27-Setup-1.0.0.exe": 30014857, "EX-SPORTS-SFC27-1.0.0-Windows-x64.zip": 44052043, "EX-SPORTS-SFC27-Portable.exe": 43955016,
    "THE-ANULMENT-Setup-1.0.0.exe": 158224328, "THE-ANULMENT-1.0.0-Windows-x64.zip": 184610333, "THE-ANULMENT-Portable.exe": 184200266,
    "DREAM.VINE.LAUNCHER.Setup.1.0.2.exe": 13957793, "DREAM.VINE.LAUNCHER.1.0.2.Windows.x64.zip": 17697430,
}
