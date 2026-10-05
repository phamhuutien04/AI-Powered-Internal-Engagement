import ctypes
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import customtkinter as ctk
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from PIL import Image

from completion_engine import build_completion_matrix
from pending_engine import generate_pending_report
from reminder_engine import generate_reminders
from summary_engine import generate_summary
from workbook_scanner import (
    classify_sheets,
    detect_key_column,
    detect_master_sheet,
    load_visible_workbook,
)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

APP_USER_MODEL_ID = "NOVA.AIInternalEngagement.Desktop.1"

if sys.platform == "win32":
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_USER_MODEL_ID)


class EngagementDesktopApp(ctk.CTk):
    COLORS = {
        "navy": "#070A16", "navy_hover": "#171B35", "blue": "#7857FF",
        "blue_hover": "#6242E8", "cyan": "#20D9FF", "green": "#22E6A7",
        "amber": "#FFB547", "page": "#080B16", "card": "#101426",
        "text": "#F7F8FF", "muted": "#8F9BB7", "border": "#252B46",
        "soft_blue": "#1B2040",
    }
    NAV_ITEMS = [
        ("workbook", "Workbook"), ("dashboard", "Dashboard"),
        ("completion", "Completion Matrix"), ("pending", "Pending Users"),
        ("reminder", "Reminder Center"),
    ]

    def __init__(self):
        super().__init__()
        self.title("AI-Powered Internal Engagement")
        self.geometry("1440x880")
        self.minsize(1120, 700)
        self.configure(fg_color=self.COLORS["page"])
        self.icon_path = Path(__file__).resolve().parent / "assets" / "app_icon.png"
        self.icon_ico_path = Path(__file__).resolve().parent / "assets" / "app_icon.ico"
        self.iconbitmap(str(self.icon_ico_path))
        self.window_icon = tk.PhotoImage(file=str(self.icon_path))
        self.iconphoto(True, self.window_icon)
        self.after(250, self._reapply_window_icon)
        self.brand_icon = ctk.CTkImage(
            light_image=Image.open(self.icon_path),
            dark_image=Image.open(self.icon_path),
            size=(30, 30),
        )
        self.completion_matrix = pd.DataFrame()
        self.pending_df = pd.DataFrame()
        self.reminder_df = pd.DataFrame()
        self.chart_canvases = []
        self.pages, self.nav_buttons, self.tables = {}, {}, []
        self._configure_table_style()
        self._build_shell()
        self.show_page("dashboard")

    def _reapply_window_icon(self):
        """Keep CustomTkinter/Windows from restoring the Python executable icon."""
        self.iconbitmap(str(self.icon_ico_path))
        self.iconphoto(True, self.window_icon)

    def _configure_table_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Modern.Treeview", background="#0D1121", fieldbackground="#0D1121",
                        foreground=self.COLORS["text"], rowheight=38,
                        font=("Segoe UI", 10), borderwidth=0, relief="flat")
        style.configure("Modern.Treeview.Heading", background="#171C33",
                        foreground="#C8D1EC", font=("Segoe UI", 10, "bold"),
                        padding=(12, 11), borderwidth=0, relief="flat")
        style.map("Modern.Treeview", background=[("selected", "#332A68")],
                  foreground=[("selected", "#FFFFFF")])
        style.map("Modern.Treeview.Heading", background=[("active", "#222946")])

    def _build_shell(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._build_sidebar()
        content = ctk.CTkFrame(self, fg_color=self.COLORS["page"], corner_radius=0)
        content.grid(row=0, column=1, sticky="nsew")
        content.grid_columnconfigure(0, weight=1)
        content.grid_rowconfigure(1, weight=1)
        self._build_topbar(content)
        self.page_host = ctk.CTkFrame(content, fg_color=self.COLORS["page"], corner_radius=0)
        self.page_host.grid(row=1, column=0, sticky="nsew", padx=30, pady=(0, 26))
        self.page_host.grid_columnconfigure(0, weight=1)
        self.page_host.grid_rowconfigure(0, weight=1)
        self._build_pages()

    def _build_sidebar(self):
        sidebar = ctk.CTkFrame(self, width=250, fg_color=self.COLORS["navy"], corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)
        sidebar.grid_rowconfigure(8, weight=1)
        brand = ctk.CTkFrame(sidebar, fg_color="transparent")
        brand.grid(row=0, column=0, sticky="ew", padx=24, pady=(30, 32))
        ctk.CTkLabel(
            brand,
            text="",
            image=self.brand_icon,
            width=44,
            height=44,
            corner_radius=12,
            fg_color="#FFFFFF",
        ).pack(side="left")
        title_box = ctk.CTkFrame(brand, fg_color="transparent")
        title_box.pack(side="left", padx=(12, 0))
        ctk.CTkLabel(title_box, text="NOVA", text_color="white",
                     font=ctk.CTkFont(size=17, weight="bold")).pack(anchor="w")
        ctk.CTkLabel(title_box, text="Engagement OS", text_color="#929EC4",
                     font=ctk.CTkFont(size=12)).pack(anchor="w")
        ctk.CTkLabel(sidebar, text="COMMAND CENTER", text_color="#596686",
                     font=ctk.CTkFont(size=10, weight="bold")).grid(
                         row=1, column=0, sticky="w", padx=26, pady=(0, 8))
        for row, (page_key, label) in enumerate(self.NAV_ITEMS, start=2):
            button = ctk.CTkButton(
                sidebar, text=label, height=44, corner_radius=10, anchor="w",
                border_spacing=14, fg_color="transparent", hover_color=self.COLORS["navy_hover"],
                text_color="#AEB8D6", font=ctk.CTkFont(size=13, weight="bold"),
                command=lambda key=page_key: self.show_page(key))
            button.grid(row=row, column=0, sticky="ew", padx=14, pady=3)
            self.nav_buttons[page_key] = button
        bottom = ctk.CTkFrame(sidebar, fg_color="#0F1427", corner_radius=14,
                              border_width=1, border_color="#282E4D")
        bottom.grid(row=9, column=0, sticky="sew", padx=16, pady=20)
        ctk.CTkLabel(bottom, text="DATA UPLINK", text_color="#687594",
                     font=ctk.CTkFont(size=10, weight="bold")).pack(
                         anchor="w", padx=16, pady=(14, 3))
        self.sidebar_file = ctk.CTkLabel(
            bottom, text="No workbook selected", wraplength=190, justify="left",
            text_color="#C8D1EC", font=ctk.CTkFont(size=11))
        self.sidebar_file.pack(anchor="w", padx=16, pady=(0, 13))

    def _build_topbar(self, parent):
        topbar = ctk.CTkFrame(parent, fg_color="transparent", corner_radius=0)
        topbar.grid(row=0, column=0, sticky="ew", padx=30, pady=(25, 18))
        topbar.grid_columnconfigure(0, weight=1)
        heading = ctk.CTkFrame(topbar, fg_color="transparent")
        heading.grid(row=0, column=0, sticky="w")
        self.page_title = ctk.CTkLabel(heading, text="Dashboard", text_color=self.COLORS["text"],
                                       font=ctk.CTkFont(size=26, weight="bold"))
        self.page_title.pack(anchor="w")
        self.status_text = tk.StringVar(value="Select an Excel workbook to begin")
        ctk.CTkLabel(heading, textvariable=self.status_text, text_color=self.COLORS["muted"],
                     font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(3, 0))
        self.open_button = ctk.CTkButton(
            topbar, text="Launch workbook", width=170, height=44, corner_radius=10,
            fg_color=self.COLORS["blue"], hover_color=self.COLORS["blue_hover"],
            font=ctk.CTkFont(size=12, weight="bold"), command=self.choose_workbook)
        self.open_button.grid(row=0, column=2, sticky="e")
        ctk.CTkLabel(
            topbar, text="●  LOCAL CORE", height=32, corner_radius=16,
            fg_color="#102C2A", text_color=self.COLORS["green"],
            font=ctk.CTkFont(size=10, weight="bold")
        ).grid(row=0, column=1, sticky="e", padx=(0, 12))

    def _build_pages(self):
        for key, _ in self.NAV_ITEMS:
            self.pages[key] = self._page_frame()
        self.metrics_frame = ctk.CTkFrame(self.pages["dashboard"], fg_color="transparent")
        self.metrics_frame.pack(fill="both", expand=True)
        self._show_dashboard({"total_users": 0, "presence_metrics": {}, "status_metrics": {}}, 0)
        self.workbook_info = tk.StringVar(value="No workbook has been loaded")
        self.workbook_table = self._table_page(
            self.pages["workbook"], "Workbook structure",
            "Detected sheets and their roles in the engagement model", info_variable=self.workbook_info)
        self.completion_table = self._table_page(
            self.pages["completion"], "Completion matrix",
            "Completion and progress values for every employee")
        self.pending_table = self._table_page(
            self.pages["pending"], "Employees requiring action",
            "People with one or more outstanding activities", "Export CSV",
            lambda: self.export_csv(self.pending_df, "pending_report.csv"))
        self.reminder_table = self._table_page(
            self.pages["reminder"], "Reminder messages",
            "Ready-to-use messages generated for pending employees", "Export CSV",
            lambda: self.export_csv(self.reminder_df, "reminder_report.csv"))

    def _page_frame(self):
        page = ctk.CTkFrame(self.page_host, fg_color="transparent", corner_radius=0)
        page.grid(row=0, column=0, sticky="nsew")
        return page

    def _table_page(self, parent, title, subtitle, action_text=None, action=None, info_variable=None):
        card = ctk.CTkFrame(parent, fg_color=self.COLORS["card"], corner_radius=16,
                            border_width=1, border_color=self.COLORS["border"])
        card.pack(fill="both", expand=True)
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(2, weight=1)
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=22, pady=(19, 14))
        header.grid_columnconfigure(0, weight=1)
        text = ctk.CTkFrame(header, fg_color="transparent")
        text.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(text, text=title, text_color=self.COLORS["text"],
                     font=ctk.CTkFont(size=17, weight="bold")).pack(anchor="w")
        ctk.CTkLabel(text, text=subtitle, text_color=self.COLORS["muted"],
                     font=ctk.CTkFont(size=11)).pack(anchor="w", pady=(3, 0))
        if action_text:
            ctk.CTkButton(header, text=action_text, width=110, height=36, corner_radius=9,
                          fg_color=self.COLORS["soft_blue"], hover_color="#272D55",
                          text_color=self.COLORS["blue"],
                          font=ctk.CTkFont(size=11, weight="bold"), command=action).grid(
                              row=0, column=1, sticky="e")
        if info_variable is not None:
            ctk.CTkLabel(card, textvariable=info_variable, height=36, corner_radius=8,
                         fg_color="#0C1020", text_color=self.COLORS["muted"], anchor="w",
                         font=ctk.CTkFont(size=11)).grid(
                             row=1, column=0, sticky="ew", padx=22, pady=(0, 12))
        container = tk.Frame(card, bg="#0D1121")
        container.grid(row=2, column=0, sticky="nsew", padx=22, pady=(0, 22))
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(0, weight=1)
        table = ttk.Treeview(container, show="headings", selectmode="browse",
                             style="Modern.Treeview")
        vertical = ttk.Scrollbar(container, orient="vertical", command=table.yview)
        horizontal = ttk.Scrollbar(container, orient="horizontal", command=table.xview)
        table.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
        table.grid(row=0, column=0, sticky="nsew")
        vertical.grid(row=0, column=1, sticky="ns")
        horizontal.grid(row=1, column=0, sticky="ew")
        self.tables.append(table)
        return table

    def show_page(self, page_key):
        self.pages[page_key].tkraise()
        self.page_title.configure(text=dict(self.NAV_ITEMS)[page_key])
        for key, button in self.nav_buttons.items():
            selected = key == page_key
            button.configure(fg_color=self.COLORS["blue"] if selected else "transparent",
                             hover_color=self.COLORS["blue_hover"] if selected else self.COLORS["navy_hover"],
                             text_color="white" if selected else "#AEB8D6")

    def choose_workbook(self):
        file_path = filedialog.askopenfilename(title="Select workbook",
                                               filetypes=[("Excel workbook", "*.xlsx")])
        if not file_path:
            return
        self.open_button.configure(state="disabled", text="Scanning data...")
        self.status_text.set(f"Analyzing {Path(file_path).name}...")
        self.sidebar_file.configure(text=Path(file_path).name)
        threading.Thread(target=self._analyze_workbook, args=(file_path,), daemon=True).start()

    def _analyze_workbook(self, file_path):
        try:
            with open(file_path, "rb") as workbook_file:
                workbook = load_visible_workbook(workbook_file)
            master_sheet = detect_master_sheet(workbook)
            key_column = detect_key_column(workbook[master_sheet])
            sheet_types = classify_sheets(workbook, master_sheet, key_column)
            completion = build_completion_matrix(workbook, master_sheet, key_column, sheet_types)
            summary = generate_summary(completion, sheet_types)
            pending = generate_pending_report(completion)
            reminders = generate_reminders(pending)
            self.after(0, lambda: self._show_results(
                Path(file_path).name, master_sheet, key_column, sheet_types,
                completion, summary, pending, reminders))
        except Exception as error:
            self.after(0, lambda: self._show_error(str(error)))

    def _show_results(self, file_name, master_sheet, key_column, sheet_types,
                      completion, summary, pending, reminders):
        self.completion_matrix, self.pending_df, self.reminder_df = completion, pending, reminders
        classification = pd.DataFrame([{"Sheet": sheet, "Type": kind}
                                       for sheet, kind in sheet_types.items()])
        self.workbook_info.set(f"  {file_name}     Master: {master_sheet}     Key: {key_column}")
        self._fill_table(self.workbook_table, classification)
        self._fill_table(self.completion_table, completion)
        self._fill_table(self.pending_table, pending)
        self._fill_table(self.reminder_table, reminders)
        self._show_dashboard(summary, len(pending))
        self.status_text.set(f"Analysis complete · {summary['total_users']} employees · "
                             f"{len(pending)} require action")
        self.open_button.configure(state="normal", text="Launch workbook")
        self.show_page("dashboard")

    def _show_dashboard(self, summary, pending_count):
        for child in self.metrics_frame.winfo_children():
            child.destroy()
        self.chart_canvases.clear()
        total = summary["total_users"]
        completed = max(total - pending_count, 0)
        rate = round(completed / max(total, 1) * 100, 1)
        cards = ctk.CTkFrame(self.metrics_frame, fg_color="transparent")
        cards.pack(fill="x", pady=(0, 18))
        for index in range(4):
            cards.grid_columnconfigure(index, weight=1, uniform="metric")
        metrics = [
            ("Total employees", total, "All records", self.COLORS["blue"]),
            ("Completed", completed, "No missing activity", self.COLORS["green"]),
            ("Pending", pending_count, "Require follow-up", self.COLORS["amber"]),
            ("Completion rate", f"{rate}%", "Overall progress", self.COLORS["cyan"]),
        ]
        for index, metric in enumerate(metrics):
            self._metric_card(cards, index, *metric)
        charts = ctk.CTkFrame(self.metrics_frame, fg_color="transparent")
        charts.pack(fill="both", expand=True)
        charts.grid_columnconfigure((0, 1), weight=1, uniform="chart")
        charts.grid_rowconfigure(0, weight=1)
        self._bar_chart(charts, 0, "Participation by activity",
                        "Share of employees participating in each program",
                        summary.get("presence_metrics", {}), self.COLORS["blue"])
        self._bar_chart(charts, 1, "Average progress",
                        "Average completion across status-based activities",
                        summary.get("status_metrics", {}), self.COLORS["green"])

    def _metric_card(self, parent, column, label, value, note, accent):
        card = ctk.CTkFrame(parent, fg_color=self.COLORS["card"], corner_radius=14,
                            border_width=1, border_color=self.COLORS["border"])
        card.grid(row=0, column=column, sticky="nsew",
                  padx=(0 if column == 0 else 7, 0 if column == 3 else 7))
        ctk.CTkFrame(card, height=5, fg_color=accent, corner_radius=3).pack(
            fill="x", padx=16, pady=(15, 12))
        ctk.CTkLabel(card, text=label.upper(), text_color=self.COLORS["muted"],
                     font=ctk.CTkFont(size=10, weight="bold")).pack(anchor="w", padx=18)
        ctk.CTkLabel(card, text=str(value), text_color=self.COLORS["text"],
                     font=ctk.CTkFont(size=28, weight="bold")).pack(
                         anchor="w", padx=18, pady=(3, 0))
        ctk.CTkLabel(card, text=note, text_color="#687594",
                     font=ctk.CTkFont(size=10)).pack(anchor="w", padx=18, pady=(0, 15))

    def _bar_chart(self, parent, column, title, subtitle, values, color):
        card = ctk.CTkFrame(parent, fg_color=self.COLORS["card"], corner_radius=16,
                            border_width=1, border_color=self.COLORS["border"])
        card.grid(row=0, column=column, sticky="nsew",
                  padx=(0, 8) if column == 0 else (8, 0))
        ctk.CTkLabel(card, text=title, text_color=self.COLORS["text"],
                     font=ctk.CTkFont(size=16, weight="bold")).pack(
                         anchor="w", padx=20, pady=(18, 0))
        ctk.CTkLabel(card, text=subtitle, text_color=self.COLORS["muted"],
                     font=ctk.CTkFont(size=10)).pack(anchor="w", padx=20, pady=(2, 3))
        figure = Figure(figsize=(5.2, 3.5), dpi=100, facecolor=self.COLORS["card"])
        axis = figure.add_subplot(111)
        axis.set_facecolor(self.COLORS["card"])
        if values:
            labels, rates = [str(label)[:25] for label in values], list(values.values())
            positions = list(range(len(labels)))
            bars = axis.barh(positions, rates, color=color, height=0.52)
            axis.set_yticks(positions, labels=labels, fontsize=8)
            axis.invert_yaxis()
            axis.set_xlim(0, 108)
            axis.set_xlabel("Percent (%)", fontsize=8, color=self.COLORS["muted"])
            for bar, value in zip(bars, rates):
                axis.text(min(value + 1.8, 100), bar.get_y() + bar.get_height() / 2,
                          f"{value:.1f}%", va="center", fontsize=8, color=self.COLORS["text"])
        else:
            axis.text(0.5, 0.5, "Open a workbook to display this chart", ha="center",
                      va="center", transform=axis.transAxes, color=self.COLORS["muted"], fontsize=9)
            axis.set_xticks([])
            axis.set_yticks([])
        axis.spines[["top", "right", "left"]].set_visible(False)
        axis.spines["bottom"].set_color(self.COLORS["border"])
        axis.tick_params(colors="#8F9BB7")
        axis.grid(axis="x", color="#242A42", linewidth=0.8)
        axis.set_axisbelow(True)
        figure.tight_layout(pad=1.7)
        canvas = FigureCanvasTkAgg(figure, master=card)
        canvas.draw()
        canvas.get_tk_widget().configure(bg=self.COLORS["card"], highlightthickness=0)
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=(0, 8))
        self.chart_canvases.append(canvas)

    def _fill_table(self, table, dataframe):
        table.delete(*table.get_children())
        columns = [str(column) for column in dataframe.columns]
        table.configure(columns=columns)
        if not columns:
            return
        total_width = max(table.winfo_width() - 20, 800)
        if columns == ["Account", "Reminder"]:
            widths = [max(int(total_width * .22), 180), max(int(total_width * .78), 520)]
        elif len(columns) == 2:
            widths = [max(int(total_width * .55), 260), max(int(total_width * .45), 220)]
        else:
            widths = [max(int(total_width / len(columns)), 145)] * len(columns)
        for column, width in zip(columns, widths):
            table.heading(column, text=column)
            table.column(column, width=width, minwidth=110, stretch=True, anchor="w")
        for index, row in enumerate(dataframe.itertuples(index=False, name=None)):
            values = ["" if pd.isna(value) else str(value) for value in row]
            table.insert("", "end", values=values, tags=("even" if index % 2 == 0 else "odd",))
        table.tag_configure("even", background="#0D1121", foreground="#DCE4FA")
        table.tag_configure("odd", background="#11162A", foreground="#DCE4FA")

    def export_csv(self, dataframe, default_name):
        if dataframe.empty:
            messagebox.showinfo("No data", "There is no data to export yet.")
            return
        destination = filedialog.asksaveasfilename(
            title="Save report", defaultextension=".csv", initialfile=default_name,
            filetypes=[("CSV file", "*.csv")])
        if destination:
            dataframe.to_csv(destination, index=False, encoding="utf-8-sig")
            messagebox.showinfo("Export complete", f"Report saved to:\n{destination}")

    def _show_error(self, message):
        self.open_button.configure(state="normal", text="Launch workbook")
        self.status_text.set("Analysis failed")
        messagebox.showerror("Unable to process workbook", message)


if __name__ == "__main__":
    EngagementDesktopApp().mainloop()
