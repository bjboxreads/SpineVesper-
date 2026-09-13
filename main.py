"""
StoryStrand — Flet version, pandas-free.

Run locally:      flet run main.py
Build the APK:     flet build apk
"""

import flet as ft
import data

APP_TITLE = "StoryStrand"
APP_TAGLINE = "a library that rises one story at a time"

STAT_FILTER_MAP = {
    "Books": "All",
    "Read": "Read",
    "Unread": "Want to Read",
    "Favorites": "Favorites",
}
STAT_TAB_MAP = {"Authors": "tree", "Series": "tree"}

NAV_ITEMS = [
    ("tree", "StoryStrand"),
    ("books", "📚 Books"),
    ("add", "➕ Add Book"),
    ("manage", "✏️ Edit / Delete"),
    ("import", "📥 Import"),
]


def main(page: ft.Page):
    page.title = APP_TITLE
    page.padding = 0
    page.scroll = ft.ScrollMode.AUTO
    page.fonts = {
        "Cormorant": "https://fonts.gstatic.com/s/cormorantgaramond/v16/co3bmX5slCNuHLi8bLeY9MK7whWMhyjYrEtGhtRXO0k.ttf",
        "Baskerville": "https://fonts.gstatic.com/s/librebaskerville/v14/kmKnZrc3Hgbbcjq75U4uslyuy4kn0qNZaxLBpg.ttf",
    }

    state = {
        "theme_name": "Emerald Grimoire",
        "library": data.load_library(),
        "tab": "tree",
        "tree_status": "All Books",
        "tree_group": "Author",
        "tree_search": "",
        "books_status": "All",
        "books_group": "Author",
        "books_search": "",
        "tree_series_only": False,
        "tree_open": set(),  # keys of expanded author/series tree nodes
        "fetch_message": None,  # (type, text)
    }

    body = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)

    def T():
        return data.THEMES[state["theme_name"]]

    def color(key):
        return T()[key]

    def pill_radius():
        return ft.border_radius.only(top_left=12, top_right=5, bottom_left=12, bottom_right=5)

    # ---------------- shared widgets ----------------

    def stat_tile(number, label):
        def on_click(e):
            if label in STAT_FILTER_MAP:
                target = STAT_FILTER_MAP[label]
                state["tab"] = "books"
                state["books_status"] = target if target != "Favorites" else "Favorites"
            else:
                state["tab"] = STAT_TAB_MAP[label]
                state["tree_series_only"] = (label == "Series")
            render()

        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(str(number), size=24, weight=ft.FontWeight.BOLD,
                             color=color("accent"), font_family="Cormorant"),
                    ft.Text(label, size=11, color=color("text"), font_family="Baskerville",
                             no_wrap=True, text_align=ft.TextAlign.CENTER),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=2,
            ),
            bgcolor=color("card"),
            border=ft.border.all(1, color("accent")),
            border_radius=pill_radius(),
            padding=ft.padding.symmetric(horizontal=6, vertical=12),
            alignment=ft.alignment.center,
            width=106,
            on_click=on_click,
            ink=True,
        )

    def stats_row():
        lib = state["library"]
        total = len(lib)
        authors = len({b["Author"] for b in lib}) if total else 0
        series_count = len({b["Series"] for b in lib if b["Series"] != "Standalone"}) if total else 0
        read_count = sum(1 for b in lib if b["Status"] == "Read")
        unread_count = sum(1 for b in lib if b["Status"] == "Want to Read")
        favorites = sum(1 for b in lib if b["Favorite"])
        pairs = [
            (total, "Books"), (authors, "Authors"), (series_count, "Series"),
            (read_count, "Read"), (unread_count, "Unread"), (favorites, "Favorites"),
        ]
        return ft.Row([stat_tile(n, l) for n, l in pairs], spacing=8, wrap=True, run_spacing=8)

    def nav_bar():
        buttons = []
        for key, label in NAV_ITEMS:
            active = state["tab"] == key
            buttons.append(
                ft.ElevatedButton(
                    label,
                    bgcolor=color("accent") if active else color("surface"),
                    color=color("page") if active else color("text"),
                    on_click=lambda e, k=key: switch_tab(k),
                    expand=True,
                )
            )
        return ft.Row(buttons, spacing=6)

    def switch_tab(key):
        state["tab"] = key
        render()

    def theme_selector():
        return ft.Dropdown(
            label="Library theme",
            value=state["theme_name"],
            options=[ft.dropdown.Option(name) for name in data.THEMES.keys()],
            on_change=on_theme_change,
            width=280,
        )

    def on_theme_change(e):
        state["theme_name"] = e.control.value
        render()

    def status_stripe(status):
        return color(data.status_stripe_color(status))

    def toggle_favorite(idx):
        state["library"][idx]["Favorite"] = not bool(state["library"][idx]["Favorite"])
        data.save_library(state["library"])
        render()

    def book_card(book, idx):
        title = str(book.get("Title", ""))
        author = str(book.get("Author", ""))
        status = str(book.get("Status", ""))
        genre = str(book.get("Genre", "") or "")
        cover = str(book.get("Cover", "") or "")
        is_fav = bool(book.get("Favorite", False))

        leading = (
            ft.Image(src=cover, width=40, height=58, fit=ft.ImageFit.COVER,
                      border_radius=ft.border_radius.only(top_left=3, top_right=8, bottom_left=3, bottom_right=8))
            if cover else
            ft.Container(width=40, height=58, bgcolor=color("surface2"),
                          border_radius=ft.border_radius.only(top_left=3, top_right=8, bottom_left=3, bottom_right=8))
        )

        subtitle = f"{author} — {status}"
        if genre:
            subtitle += f" · {genre}"

        return ft.Container(
            content=ft.Row(
                [
                    leading,
                    ft.Column(
                        [
                            ft.Text(f"📖 {title}", color=color("text"), weight=ft.FontWeight.BOLD,
                                     size=14, font_family="Baskerville"),
                            ft.Text(subtitle, color=color("muted"), size=12),
                        ],
                        expand=True, spacing=2,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.STAR if is_fav else ft.Icons.STAR_BORDER,
                        icon_color=color("accent"),
                        tooltip="Toggle favorite",
                        on_click=lambda e, i=idx: toggle_favorite(i),
                    ),
                    ft.IconButton(
                        icon=ft.Icons.EDIT, icon_color=color("muted"),
                        tooltip="Edit",
                        on_click=lambda e, i=idx: open_edit_dialog(i),
                    ),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=color("surface"),
            border_radius=ft.border_radius.only(top_left=5, top_right=20, bottom_left=5, bottom_right=20),
            border=ft.border.only(left=ft.border.BorderSide(4, status_stripe(status))),
            padding=10,
            margin=ft.margin.only(bottom=6),
        )

    def toggle_tree_node(key):
        state["tree_open"].symmetric_difference_update({key})
        render()

    def tree_branch(key, icon, label, count, title_color_key, header_bg_key, children_builder):
        """One collapsible node in the ancestor-style tree: an
        arrow + label header, and when expanded, its children hung
        off a vertical trunk line so the parent/child relationship
        is visible instead of everything looking like a flat list."""
        is_open = key in state["tree_open"]
        arrow = "▼" if is_open else "▶"
        header = ft.Container(
            content=ft.TextButton(
                content=ft.Row(
                    [
                        ft.Text(arrow, color=color("accent"), size=13),
                        ft.Text(f"{icon} {label} ({count})", color=color(title_color_key),
                                 weight=ft.FontWeight.BOLD, font_family="Cormorant", size=16),
                    ],
                    spacing=6,
                ),
                on_click=lambda e: toggle_tree_node(key),
                style=ft.ButtonStyle(padding=0),
            ),
            bgcolor=color(header_bg_key),
            border_radius=6,
            padding=ft.padding.symmetric(vertical=6, horizontal=8),
        )
        if not is_open:
            return header
        return ft.Column(
            [
                header,
                ft.Row(
                    [
                        ft.Container(width=2, bgcolor=color("line")),
                        ft.Column(children_builder(), spacing=6),
                    ],
                    spacing=10,
                ),
            ],
            spacing=0,
        )

    def series_tile(author_name, series_name, series_items):
        label = "Standalone" if series_name == "Standalone" else series_name
        key = f"series::{author_name}::{series_name}"

        def build_children():
            rows = [
                ft.Row(
                    [
                        ft.Text("└─", color=color("line"), size=13),
                        ft.Container(book_card(book, idx), expand=True),
                    ],
                    spacing=4,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                )
                for idx, book in series_items
            ]
            return rows

        return tree_branch(key, "📂", label, len(series_items), "text", "surface2", build_children)

    def author_tile(group_name, items, group_icon):
        series_groups = {}
        for idx, book in items:
            series = str(book.get("Series", "") or "Standalone")
            series_groups.setdefault(series, []).append((idx, book))

        key = f"author::{group_name}"

        def build_children():
            return [
                series_tile(group_name, name, series_groups[name])
                for name in sorted(series_groups.keys(), key=lambda x: str(x).lower())
            ]

        return tree_branch(key, group_icon, group_name, len(items), "accent", "card", build_children)

    def group_items(books_with_idx, group_by):
        def group_key(book):
            return data.clean_genre(book.get("Genre", "")) if group_by == "Genre" \
                else data.clean_author(book.get("Author", ""))
        groups = {}
        for idx, book in books_with_idx:
            groups.setdefault(group_key(book), []).append((idx, book))
        return groups

    def simple_grouped_list(books_with_idx, group_by):
        """Books tab — flat single-column Author/Genre -> Series -> books."""
        groups = group_items(books_with_idx, group_by)
        icon = "🏷️" if group_by == "Genre" else "🗼"
        tiles = [
            author_tile(name, groups[name], icon)
            for name in sorted(groups.keys(), key=lambda x: str(x).lower())
        ]
        return ft.Column(tiles, spacing=8)

    def lettered_grid_tree(books_with_idx, group_by):
        """StoryStrand tab — same grouping, laid out as a single
        vertical column of author tiles under A/B/C letter
        dividers. (Previously used a wrapping Row grid, but
        combining expand=True children inside a wrap=True Row
        is an unstable Flutter layout combination on mobile and
        was causing the tree to stop rendering partway through.)"""
        groups = group_items(books_with_idx, group_by)
        icon = "🏷️" if group_by == "Genre" else "🗼"
        sorted_names = sorted(groups.keys(), key=lambda x: str(x).lower())

        letter_blocks = []
        current_letter = None
        current_names = []
        for name in sorted_names:
            letter = str(name).strip()[:1].upper() or "#"
            if letter != current_letter:
                if current_names:
                    letter_blocks.append((current_letter, current_names))
                current_letter = letter
                current_names = []
            current_names.append(name)
        if current_names:
            letter_blocks.append((current_letter, current_names))

        sections = []
        for letter, names in letter_blocks:
            sections.append(
                ft.Row(
                    [
                        ft.Text(letter, size=20, color=color("accent"), font_family="Cormorant"),
                        ft.Container(expand=True, height=1, bgcolor=color("line"), opacity=0.6),
                    ],
                    spacing=10,
                )
            )
            for name in names:
                sections.append(author_tile(name, groups[name], icon))

        return ft.Column(sections, spacing=10)

    def search_matches(book, q):
        haystack = " ".join([
            str(book.get("Title", "")), str(book.get("Author", "")), str(book.get("Series", "")),
            str(book.get("Genre", "")), str(book.get("Tags", "")), str(book.get("Description", "")),
            str(book.get("ISBN", "")),
        ]).lower()
        return q in haystack

    # ---------------- edit dialog (with delete confirmation) ----------------

    def open_edit_dialog(idx):
        book = state["library"][idx]

        title_f = ft.TextField(label="Title", value=str(book["Title"]))
        author_f = ft.TextField(label="Author", value=str(book["Author"]))
        series_f = ft.TextField(label="Series", value=str(book["Series"]))
        series_num_f = ft.TextField(label="Series #", value=str(book.get("Series Number", "")))
        genre_f = ft.TextField(label="Genre", value=str(book["Genre"]))
        tags_f = ft.TextField(label="Tags", value=str(book.get("Tags", "")))
        isbn_f = ft.TextField(label="ISBN", value=str(book.get("ISBN", "")))
        rating_f = ft.TextField(label="My Rating (0-5)", value=str(book.get("My Rating", "")))
        status_f = ft.Dropdown(
            label="Status", value=str(book["Status"]),
            options=[ft.dropdown.Option(s) for s in ["Want to Read", "Currently Reading", "Read"]],
        )
        fav_f = ft.Checkbox(label="Favorite", value=bool(book.get("Favorite", False)))

        def save(e):
            state["library"][idx].update({
                "Title": title_f.value, "Author": author_f.value, "Series": series_f.value or "Standalone",
                "Series Number": series_num_f.value, "Genre": genre_f.value, "Tags": tags_f.value,
                "ISBN": data.clean_isbn(isbn_f.value), "My Rating": rating_f.value,
                "Status": status_f.value, "Favorite": fav_f.value,
            })
            data.save_library(state["library"])
            page.close(dlg)
            render()

        def ask_delete(e):
            page.close(dlg)
            open_delete_confirm(idx)

        dlg = ft.AlertDialog(
            title=ft.Text("Edit Book"),
            content=ft.Column(
                [title_f, author_f, series_f, series_num_f, genre_f, tags_f,
                 isbn_f, rating_f, status_f, fav_f],
                tight=True, width=360, scroll=ft.ScrollMode.AUTO, height=420,
            ),
            actions=[
                ft.TextButton("Delete", icon=ft.Icons.DELETE, on_click=ask_delete),
                ft.TextButton("Cancel", on_click=lambda e: page.close(dlg)),
                ft.FilledButton("Save", on_click=save),
            ],
        )
        page.open(dlg)

    def open_delete_confirm(idx):
        title = state["library"][idx]["Title"]

        def confirm(e):
            state["library"].pop(idx)
            data.save_library(state["library"])
            page.close(dlg)
            render()

        dlg = ft.AlertDialog(
            title=ft.Text("Confirm delete"),
            content=ft.Text(f'Delete "{title}" from your library? This can\'t be undone.'),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: page.close(dlg)),
                ft.FilledButton("🗑️ Confirm delete", on_click=confirm, bgcolor=ft.Colors.RED_700),
            ],
        )
        page.open(dlg)

    # ---------------- TREE (Book Spire) TAB ----------------

    def tree_tab():
        search_f = ft.TextField(
            hint_text="Search author, title, series, genre, tag, theme, or ISBN...",
            value=state["tree_search"],
        )
        status_group = ft.RadioGroup(
            value=state["tree_status"],
            content=ft.Row([
                ft.Radio(value="All Books", label="All Books"),
                ft.Radio(value="Read", label="Read"),
                ft.Radio(value="Unread", label="Unread"),
            ], wrap=True),
        )
        group_by_group = ft.RadioGroup(
            value=state["tree_group"],
            content=ft.Row([
                ft.Radio(value="Author", label="Author"),
                ft.Radio(value="Genre", label="Genre"),
            ], wrap=True),
        )
        root_label_text = ft.Text("", size=24, font_family="Cormorant", color=color("page"))
        root_banner = ft.Container(
            content=root_label_text, bgcolor=color("accent"),
            border_radius=ft.border_radius.only(top_left=5, top_right=20, bottom_left=5, bottom_right=20),
            padding=ft.padding.symmetric(horizontal=30, vertical=10),
            alignment=ft.alignment.center, margin=ft.margin.symmetric(vertical=16),
        )
        results = ft.Column()

        def apply_filters(e=None):
            state["tree_search"] = search_f.value or ""
            state["tree_status"] = status_group.value
            state["tree_group"] = group_by_group.value

            root_label_text.value = {
                "All Books": "🗼 MY LIBRARY", "Read": "🗼 MY READ BOOKS", "Unread": "🗼 MY UNREAD BOOKS",
            }[state["tree_status"]]

            lib = state["library"]
            if not lib:
                results.controls = [ft.Text(
                    "Your spire is just a foundation — import your library or add your first book to help it rise.",
                    color=color("muted"))]
                page.update()
                return

            items = list(enumerate(lib))

            if state["tree_series_only"]:
                items = [(i, b) for i, b in items if b.get("Series", "Standalone") not in ("", "Standalone")]

            if state["tree_status"] == "Read":
                items = [(i, b) for i, b in items if b["Status"] == "Read"]
            elif state["tree_status"] == "Unread":
                items = [(i, b) for i, b in items if b["Status"] != "Read"]

            q = state["tree_search"].strip().lower()
            if q:
                items = [(i, b) for i, b in items if search_matches(b, q)]

            root_label_text.value = {
                "All Books": "🗼 MY LIBRARY", "Read": "🗼 MY READ BOOKS", "Unread": "🗼 MY UNREAD BOOKS",
            }[state["tree_status"]]

            if not items:
                results.controls = [ft.Text(
                    f'No books matched "{q}".' if q else f'No books found for "{state["tree_status"]}".',
                    color=color("muted"))]
            else:
                results.controls = [lettered_grid_tree(items, state["tree_group"])]
            page.update()

        search_f.on_change = apply_filters
        status_group.on_change = apply_filters
        group_by_group.on_change = apply_filters
        apply_filters()
        state["tree_series_only"] = False  # consumed once, like st.session_state.pop

        return ft.Column(
            [
                ft.Text("Search My Spire", size=18, color=color("accent"), font_family="Cormorant"),
                search_f,
                ft.Text("Show", size=12, color=color("muted")),
                status_group,
                ft.Text("Organize by", size=12, color=color("muted")),
                group_by_group,
                ft.Divider(color=color("line")),
                root_banner,
                results,
            ],
            spacing=8,
        )

    # ---------------- BOOKS TAB ----------------

    def fetch_message_banner():
        if not state["fetch_message"]:
            return ft.Container()
        kind, text = state["fetch_message"]
        state["fetch_message"] = None
        bg = {"success": ft.Colors.GREEN_700, "warning": ft.Colors.AMBER_700, "error": ft.Colors.RED_700}[kind]
        return ft.Container(ft.Text(text, color=ft.Colors.WHITE), bgcolor=bg, padding=10, border_radius=8,
                             margin=ft.margin.only(bottom=8))

    def books_tab():
        search_f = ft.TextField(
            hint_text="Search title, author, series, genre, tag, theme, or ISBN...",
            value=state["books_search"],
        )
        status_f = ft.Dropdown(
            value=state["books_status"], width=190,
            options=[ft.dropdown.Option(s) for s in
                     ["All", "Favorites", "Read", "Currently Reading", "Want to Read"]],
        )
        group_f = ft.Dropdown(
            value=state["books_group"], width=140,
            options=[ft.dropdown.Option("Author"), ft.dropdown.Option("Genre")],
        )
        results = ft.Column()
        fetch_row = ft.Row(wrap=True, spacing=10)

        def build_fetch_buttons(shown_books):
            fetch_row.controls = []
            checks = {
                "cover": ("🖼️ Fetch missing covers", "cover(s) shown here have no cover yet."),
                "description": ("📝 Fetch missing descriptions", "book(s) shown here have no description yet — needed for topic search."),
                "genre": ("🏷️ Fetch missing genres", "book(s) shown here have no genre yet — grouped under \"Unknown Genre\"."),
                "pubinfo": ("📅 Fetch missing publisher/pages/date", "book(s) shown here are missing publisher, page count, or publication date."),
            }
            for field, (label, caption_suffix) in checks.items():
                if field == "pubinfo":
                    missing = sum(1 for b in shown_books if not (
                        str(b.get("Publisher") or "").strip()
                        and str(b.get("Pages") or "").strip()
                        and str(b.get("Publication Date") or "").strip()
                    ))
                else:
                    key = {"cover": "Cover", "description": "Description", "genre": "Genre"}[field]
                    missing = sum(1 for b in shown_books if not str(b.get(key) or "").strip())

                if missing == 0:
                    continue

                def make_click(f=field):
                    def on_click(e):
                        run_fetch(f)
                    return on_click

                fetch_row.controls.append(
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text(f"{missing} {caption_suffix}", size=11, color=color("muted")),
                                ft.ElevatedButton(label, on_click=make_click()),
                            ],
                            spacing=4,
                        ),
                        width=260,
                    )
                )

        def run_fetch(field):
            progress = ft.ProgressRing(width=20, height=20)
            page.overlay.append(progress)
            page.update()
            found, total = data.fetch_missing_field(state["library"], field)
            data.save_library(state["library"])
            page.overlay.remove(progress)

            label = {"cover": "covers", "description": "descriptions", "genre": "genres", "pubinfo": "publisher/page/date info"}[field]
            if total == 0:
                state["fetch_message"] = ("success", f"Every book already has {label}.")
            elif found == total:
                state["fetch_message"] = ("success", f"✓ Found {label} for all {total} book(s)!")
            elif found:
                state["fetch_message"] = ("warning", f"Found {label} for {found} of {total} book(s). "
                                                       f"The rest had none available, or the lookup was rate-limited — try again in a bit.")
            else:
                reason = f" Last error: {data.last_network_error}" if data.last_network_error else ""
                state["fetch_message"] = ("error", f"Couldn't find {label} for any of the {total} book(s) checked.{reason}")
            render()

        def apply_filters(e=None):
            state["books_search"] = search_f.value or ""
            state["books_status"] = status_f.value
            state["books_group"] = group_f.value

            lib = state["library"]
            if not lib:
                results.controls = [ft.Text("No books yet — add or import some first.", color=color("muted"))]
                fetch_row.controls = []
                page.update()
                return

            items = list(enumerate(lib))

            if state["books_status"] == "Favorites":
                items = [(i, b) for i, b in items if b["Favorite"]]
            elif state["books_status"] != "All":
                items = [(i, b) for i, b in items if b["Status"] == state["books_status"]]

            q = state["books_search"].strip().lower()
            if q:
                items = [(i, b) for i, b in items if search_matches(b, q)]

            if not items:
                results.controls = [ft.Text(f'No books matched "{q}".', color=color("muted"))]
                fetch_row.controls = []
            else:
                results.controls = [simple_grouped_list(items, state["books_group"])]
                build_fetch_buttons([b for _, b in items])
            page.update()

        search_f.on_change = apply_filters
        status_f.on_change = apply_filters
        group_f.on_change = apply_filters
        apply_filters()

        return ft.Column(
            [
                fetch_message_banner(),
                search_f,
                ft.Row([status_f, group_f], spacing=10),
                ft.Divider(color=color("line")),
                results,
                ft.Divider(color=color("line")),
                fetch_row,
            ],
            spacing=10,
        )

    # ---------------- ADD TAB ----------------

    def add_tab():
        title_f = ft.TextField(label="Title")
        author_f = ft.TextField(label="Author")
        series_f = ft.TextField(label="Series", hint_text="Leave blank for standalone")
        number_f = ft.TextField(label="Series number", hint_text="e.g. 1, 2.5...")
        genre_f = ft.TextField(label="Genre", hint_text="Fantasy, Romance, Mystery...")
        tags_f = ft.TextField(label="Tags", hint_text="Christmas, cozy, found family...")
        isbn_f = ft.TextField(label="ISBN")
        status_f = ft.Dropdown(
            label="Status", value="Want to Read",
            options=[ft.dropdown.Option(s) for s in ["Want to Read", "Currently Reading", "Read"]],
        )

        rating_state = {"value": None}
        star_icons = []

        def redraw_stars():
            for i, ic in enumerate(star_icons):
                filled = rating_state["value"] is not None and i < rating_state["value"]
                ic.icon = ft.Icons.STAR if filled else ft.Icons.STAR_BORDER
            page.update()

        def make_star(i):
            def on_click(e):
                rating_state["value"] = i + 1
                redraw_stars()
            btn = ft.IconButton(icon=ft.Icons.STAR_BORDER, icon_color=color("accent"), on_click=on_click)
            star_icons.append(btn)
            return btn

        stars_row = ft.Row([make_star(i) for i in range(5)], spacing=0)

        fav_f = ft.Checkbox(label="Favorite")
        status_text = ft.Text("", color=color("accent2"))

        def submit(e):
            if not title_f.value or not title_f.value.strip():
                status_text.value = "Please enter a title."
                status_text.color = ft.Colors.RED_400
                page.update()
                return
            if not author_f.value or not author_f.value.strip():
                status_text.value = "Please enter an author."
                status_text.color = ft.Colors.RED_400
                page.update()
                return

            status_text.value = "Looking up metadata..."
            status_text.color = color("muted")
            page.update()

            metadata = data.fetch_book_metadata(title_f.value, author_f.value, isbn_f.value)
            actual_genre = (genre_f.value or "").strip() or metadata.get("genre", "")

            new_book = data.blank_book()
            new_book.update({
                "Title": title_f.value.strip(), "Author": author_f.value.strip(),
                "Series": (series_f.value or "").strip() or "Standalone",
                "Series Number": number_f.value or "",
                "Genre": actual_genre, "Tags": (tags_f.value or "").strip(),
                "ISBN": data.clean_isbn(isbn_f.value),
                "My Rating": rating_state["value"] if rating_state["value"] is not None else "",
                "Status": status_f.value, "Favorite": fav_f.value,
                "Cover": metadata.get("cover", ""), "Description": metadata.get("description", ""),
                "Publisher": metadata.get("publisher", ""), "Pages": metadata.get("pages", ""),
                "Publication Date": metadata.get("publication_date", ""),
            })
            state["library"].append(new_book)
            data.save_library(state["library"])

            status_text.value = f'"{new_book["Title"]}" was added to your spire!'
            status_text.color = color("accent2")
            for f in (title_f, author_f, series_f, number_f, genre_f, tags_f, isbn_f):
                f.value = ""
            status_f.value = "Want to Read"
            fav_f.value = False
            rating_state["value"] = None
            redraw_stars()
            page.update()

        return ft.Column(
            [
                ft.Text("Add a Book", size=22, color=color("accent"), font_family="Cormorant"),
                title_f, author_f, series_f, number_f, genre_f, tags_f, isbn_f, status_f,
                ft.Text("Rating", size=12, color=color("muted")),
                stars_row,
                fav_f,
                ft.FilledButton("Add to My Spire", on_click=submit),
                status_text,
            ],
            spacing=12,
        )

    # ---------------- MANAGE / EDIT-DELETE TAB ----------------

    def manage_tab():
        lib = state["library"]
        if not lib:
            return ft.Column([ft.Text("No books yet — add or import some first.", color=color("muted"))])

        rows = []
        for idx, book in enumerate(lib):
            rows.append(book_card(book, idx))

        return ft.Column(
            [
                ft.Text("Edit / Delete Books", size=22, color=color("accent"), font_family="Cormorant"),
                ft.Text(
                    "Tap the pencil to edit any field, or delete a book (you'll be asked to confirm).",
                    size=12, color=color("muted"),
                ),
                ft.Divider(color=color("line")),
                ft.Column(rows, spacing=6),
            ],
            spacing=10,
        )

    # ---------------- IMPORT TAB ----------------

    def import_tab():
        picked_path = {"path": None, "name": None, "size": None}
        status_text = ft.Text(
            "Upload a Goodreads CSV, StoryGraph export, Excel spreadsheet, plain text list, or PDF book list.",
            color=color("muted"),
        )
        file_info = ft.Text("", color=color("muted"))

        merge_radio = ft.RadioGroup(
            value="Merge with my existing library",
            content=ft.Column([
                ft.Radio(value="Merge with my existing library", label="Merge with my existing library"),
                ft.Radio(value="Replace my entire library with this file", label="Replace my entire library with this file"),
            ]),
            visible=bool(state["library"]),
        )
        merge_caption = ft.Text(
            "Books already in your library (matched by title + author) are left untouched — "
            "favorites, ratings, and covers you've set won't be overwritten. Only new books "
            "from this file are added.",
            size=11, color=color("muted"), visible=bool(state["library"]),
        )

        def on_merge_change(e):
            replacing = merge_radio.value == "Replace my entire library with this file"
            merge_caption.value = (
                "⚠️ This removes every book currently in your library and replaces it "
                "with only what's in this file."
                if replacing else
                "Books already in your library (matched by title + author) are left "
                "untouched — favorites, ratings, and covers you've set won't be "
                "overwritten. Only new books from this file are added."
            )
            page.update()

        merge_radio.on_change = on_merge_change

        fetch_covers_f = ft.Checkbox(label="Fetch cover art", value=True)
        fetch_desc_f = ft.Checkbox(label="Fetch descriptions", value=True)
        fetch_genre_f = ft.Checkbox(label="Fetch genres", value=True)
        fetch_pub_f = ft.Checkbox(label="Fetch publisher, page count, and publication date", value=True)

        def on_file_picked(e: ft.FilePickerResultEvent):
            if not e.files:
                return
            f = e.files[0]
            picked_path["path"] = f.path
            picked_path["name"] = f.name
            picked_path["size"] = f.size
            status_text.value = f"✓ {f.name} uploaded successfully"
            status_text.color = color("accent2")
            file_info.value = f"File size: {f.size:,} bytes" if f.size else ""
            page.update()

        file_picker = ft.FilePicker(on_result=on_file_picked)
        page.overlay.append(file_picker)

        def do_import(e):
            if not picked_path["path"]:
                status_text.value = "Choose a file first."
                status_text.color = ft.Colors.RED_400
                page.update()
                return

            status_text.value = "Reading your book list..."
            status_text.color = color("muted")
            page.update()

            rows, err = data.load_rows_from_path(picked_path["path"])
            if err:
                status_text.value = err
                status_text.color = ft.Colors.RED_400
                page.update()
                return

            merge_choice = merge_radio.value == "Merge with my existing library"

            combined, added, skipped, new_indices, err2 = data.import_books_from_rows(
                rows, state["library"], merge=merge_choice
            )
            if err2:
                status_text.value = err2
                status_text.color = ft.Colors.RED_400
                page.update()
                return

            state["library"] = combined
            data.save_library(combined)

            want_any = fetch_covers_f.value or fetch_desc_f.value or fetch_genre_f.value or fetch_pub_f.value
            stats = {"isbn": 0, "title_author": 0, "none": 0}
            if want_any and added:
                status_text.value = f"Fetching metadata for {added} new book(s)..."
                page.update()

                def progress(done, total):
                    status_text.value = f"Looked up {done} of {total} book(s)..."
                    page.update()

                stats = data.fetch_missing_metadata_parallel(
                    state["library"], new_indices,
                    want_cover=fetch_covers_f.value, want_description=fetch_desc_f.value,
                    want_genre=fetch_genre_f.value, want_pubinfo=fetch_pub_f.value,
                    on_progress=progress,
                )
                data.save_library(state["library"])

            base_msg = f"✓ Added {added} new book(s)."
            if merge_choice and skipped:
                base_msg += f" Skipped {skipped} already in your library."
            status_text.value = base_msg
            status_text.color = color("accent2")

            if added and want_any:
                file_info.value = (
                    f"Metadata lookup: {stats.get('isbn', 0)} matched by ISBN, "
                    f"{stats.get('title_author', 0)} matched by title/author fallback, "
                    f"{stats.get('none', 0)} had no match from either source. Unmatched "
                    f"books stay in your library — use the \"Fetch missing...\" buttons "
                    f"on the Books tab to retry them anytime."
                )
                if stats.get("isbn", 0) == 0 and stats.get("title_author", 0) == 0 and data.last_network_error:
                    file_info.value += f" Last error seen: {data.last_network_error}"
            else:
                file_info.value = ""

            page.update()
            render()

        return ft.Column(
            [
                ft.Text("Import Your Library", size=22, color=color("accent"), font_family="Cormorant"),
                status_text,
                ft.Text(
                    "Text and PDF files: one book per line, formatted as \"Title\", "
                    "\"Title - Author\", or \"Title by Author\".",
                    size=11, color=color("muted"),
                ),
                ft.ElevatedButton(
                    "Choose File",
                    on_click=lambda e: file_picker.pick_files(
                        allowed_extensions=["csv", "xlsx", "xlsm", "pdf", "txt"]
                    ),
                ),
                file_info,
                merge_radio,
                merge_caption,
                ft.Divider(color=color("line")),
                fetch_covers_f, fetch_desc_f, fetch_genre_f, fetch_pub_f,
                ft.Text(
                    "Everything is looked up automatically. Anything missed can be "
                    "fetched later from the Books tab.",
                    size=11, color=color("muted"),
                ),
                ft.FilledButton("🗼 Raise My Spire", on_click=do_import),
            ],
            spacing=10,
        )

    # ---------------- render ----------------

    def render():
        page.bgcolor = color("page")

        tab = state["tab"]
        try:
            if tab == "tree":
                content = tree_tab()
            elif tab == "books":
                content = books_tab()
            elif tab == "add":
                content = add_tab()
            elif tab == "manage":
                content = manage_tab()
            else:
                content = import_tab()
        except Exception as ex:
            # A tab crashing used to leave the whole screen blank
            # with nothing else rendered below it and no way back.
            # Surfacing the error as content instead means there's
            # always at least the nav bar to tap back to another
            # tab, and the actual exception is visible instead of
            # silently vanishing.
            content = ft.Column(
                [
                    ft.Text("Something went wrong loading this screen.",
                             color=ft.Colors.RED_300, weight=ft.FontWeight.BOLD),
                    ft.Text(f"{type(ex).__name__}: {ex}", color=ft.Colors.RED_200, selectable=True),
                ],
                spacing=8,
            )

        body.controls = [
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text(
                            APP_TITLE, size=40, weight=ft.FontWeight.BOLD,
                            color=color("accent"), font_family="Cormorant",
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Text(
                            APP_TAGLINE, italic=True, color=color("muted"), size=13,
                            text_align=ft.TextAlign.CENTER, font_family="Baskerville",
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=ft.padding.only(top=30, bottom=10),
                alignment=ft.alignment.center,
            ),
            ft.Container(theme_selector(), padding=ft.padding.symmetric(horizontal=16)),
            ft.Container(stats_row(), padding=ft.padding.symmetric(horizontal=16, vertical=10)),
            ft.Container(nav_bar(), padding=ft.padding.symmetric(horizontal=16, vertical=10)),
            ft.Container(content, padding=ft.padding.symmetric(horizontal=16, vertical=6)),
        ]
        page.update()

    page.add(ft.SafeArea(content=body, expand=True))
    render()


ft.app(target=main)
