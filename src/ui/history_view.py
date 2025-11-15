"""
Enhanced history view with proper asset integration and internationalization
"""

import customtkinter as ctk
from tkinter import ttk, filedialog
import tkinter as tk
from .theme import Theme
from .custom_messagebox import CustomMessageBox
from ..utils import AssetLoader, getTranslation

class HistoryView(ctk.CTkToplevel):
    """Enhanced history view window with i18n support"""

    def __init__(self, parent, mainGUI):
        super().__init__(parent)
        self.mainGUI = mainGUI
        self.controller = mainGUI.controller
        
        # Load translations
        self.config = AssetLoader.loadConfig()
        self.currentLanguage = self.config['settings']['language']
        
        # Set window title
        self.title(self._t("history.title"))
        
        # Set icon
        try:
            iconPath = AssetLoader.getImagePath("icon.ico")
            if iconPath.exists():
                self.iconbitmap(iconPath)
        except Exception as e:
            print(f"Could not load icon: {e}")
        
        # Center window on screen
        windowWidth = 1000
        windowHeight = 700
        screenWidth = self.winfo_screenwidth()
        screenHeight = self.winfo_screenheight()
        centerX = int(screenWidth/2 - windowWidth/2)
        centerY = int(screenHeight/2 - windowHeight/2)
        self.geometry(f'{windowWidth}x{windowHeight}+{centerX}+{centerY}')
        self.minsize(900, 600)
        self.configure(fg_color=Theme.BG_COLOR)
        
        # Make window stay on top
        self.attributes('-topmost', True)
        self.lift()
        self.focus_force()
        
        # After a short delay, remove topmost but keep it above parent
        self.after(100, lambda: self.attributes('-topmost', False))
        self.after(150, lambda: self.lift())
        
        # Add fade-in effect
        self.attributes('-alpha', 0.0)
        self._createWidgets()
        self.populateHistory()
        self._fadeIn()
        
        # Handle window close properly
        self.protocol("WM_DELETE_WINDOW", self._onClose)
        
        # Toast notification container
        self.toastFrame = None
    
    def _t(self, key):
        """Shorthand for getting translations"""
        return getTranslation(key, self.currentLanguage)

    def _fadeIn(self):
        """Smooth fade-in animation"""
        alpha = self.attributes('-alpha')
        if alpha < 1.0:
            self.attributes('-alpha', alpha + 0.1)
            self.after(20, self._fadeIn)
    
    def _onClose(self):
        """Handle window close event"""
        self.destroy()
    
    def _showToast(self, message, duration=2000, isSuccess=True):
        """Show a toast notification"""
        # Remove existing toast if any
        if self.toastFrame:
            self.toastFrame.destroy()
        
        # Create toast frame
        self.toastFrame = ctk.CTkFrame(
            self,
            fg_color=Theme.SUCCESS_COLOR if isSuccess else Theme.ACCENT_COLOR,
            corner_radius=12,
            border_width=0
        )
        
        # Toast icon and message
        toastContent = ctk.CTkFrame(self.toastFrame, fg_color="transparent")
        toastContent.pack(padx=20, pady=12)
        
        icon = "✅" if isSuccess else "❌"
        iconLabel = ctk.CTkLabel(
            toastContent,
            text=icon,
            font=("Segoe UI", 16),
            text_color="white"
        )
        iconLabel.pack(side="left", padx=(0, 10))
        
        messageLabel = ctk.CTkLabel(
            toastContent,
            text=message,
            font=("Segoe UI", 12, "bold"),
            text_color="white"
        )
        messageLabel.pack(side="left")
        
        # Position toast at bottom center
        self.toastFrame.place(relx=0.5, rely=0.92, anchor="center")
        
        # Fade in
        self.toastFrame.lift()
        self._animateToastIn(self.toastFrame, duration)
    
    def _animateToastIn(self, toast, duration):
        """Animate toast in and schedule fade out"""
        toast.configure(fg_color=toast.cget("fg_color"))
        self.after(duration, lambda: self._animateToastOut(toast))
    
    def _animateToastOut(self, toast):
        """Animate toast out"""
        if toast and toast.winfo_exists():
            toast.place_forget()
            toast.destroy()
            self.toastFrame = None

    def _calculateTitleWidth(self, historyData):
        """Calculate optimal width for title column"""
        if not historyData:
            return 300
        
        # Find longest title
        maxTitleLength = max(len(item['title']) for item in historyData)
        
        # Approximate width: ~8 pixels per character (for Segoe UI 12)
        calculatedWidth = min(maxTitleLength * 8, 300)
        
        # Ensure minimum width
        return max(calculatedWidth, 150)

    def _createWidgets(self):
        """Create and layout all GUI widgets"""
        
        # Main container
        mainContainer = ctk.CTkFrame(self, fg_color="transparent")
        mainContainer.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header (fixed)
        self._createHeader(mainContainer)
        
        # Content card (fixed)
        contentCard = ctk.CTkFrame(
            mainContainer, 
            fg_color=Theme.CARD_COLOR, 
            corner_radius=Theme.BORDER_RADIUS
        )
        contentCard.pack(fill="both", expand=True, pady=(0, 0))
        
        # Search/Filter bar (fixed)
        self._createFilterBar(contentCard)
        
        # Scrollable treeview container (only this scrolls) - with fixed height
        treeFrame = ctk.CTkFrame(contentCard, fg_color="transparent", height=350)
        treeFrame.pack(fill="both", expand=False, padx=20, pady=(0, 16))
        treeFrame.pack_propagate(False)  # Prevent frame from shrinking

        # Create enhanced treeview style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Get current theme colors - check appearance mode
        current_mode = ctk.get_appearance_mode().lower()
        
        if current_mode == "light":
            bg_color = "#f5f5f5"
            fg_color = "#1a1a1a"
            field_bg = "#ffffff"
            selected_bg = "#4dabf7"
            heading_bg = "#e9ecef"
            hover_bg = "#f8f9fa"
        else:
            bg_color = "#2b2b2b"
            fg_color = "#e9ecef"
            field_bg = "#2b2b2b"
            selected_bg = Theme.SECONDARY_COLOR
            heading_bg = "#262638"
            hover_bg = "#333333"
        
        # Configure treeview colors with larger fonts
        style.configure("Modern.Treeview",
                       background=bg_color,
                       foreground=fg_color,
                       fieldbackground=field_bg,
                       borderwidth=0,
                       rowheight=50,
                       font=('Segoe UI', 12))
        
        style.configure("Modern.Treeview.Heading",
                       background=heading_bg,
                       foreground=fg_color,
                       borderwidth=0,
                       relief="flat",
                       font=('Segoe UI', 13, 'bold'),
                       padding=10)
        
        style.map('Modern.Treeview',
                 background=[('selected', selected_bg)],
                 foreground=[('selected', 'white')])
        
        style.map('Modern.Treeview.Heading',
                 background=[('active', hover_bg)])

        # Treeview with scrollbars
        self.tree = ttk.Treeview(
            treeFrame, 
            columns=("Title", "URL", "Path", "Status", "Date"), 
            show="headings",
            style="Modern.Treeview",
            selectmode="browse"
        )
        
        # Configure columns with responsive sizing
        self.tree.heading("Title", text=f"🎬 {self._t('labels.video_title')}")
        self.tree.heading("URL", text="🔗 URL")
        self.tree.heading("Path", text=f"📁 {self._t('labels.save_location')}")
        self.tree.heading("Status", text=self._t('labels.status'))
        self.tree.heading("Date", text="📅 Date")
        
        # Column widths - Title will be set dynamically
        self.tree.column("Title", width=300, minwidth=150)
        self.tree.column("URL", width=250, minwidth=150)
        self.tree.column("Path", width=250, minwidth=150)
        self.tree.column("Status", width=100, minwidth=80)
        self.tree.column("Date", width=140, minwidth=120)

        # Vertical scrollbar
        vScrollbarFrame = ctk.CTkFrame(treeFrame, fg_color=Theme.INPUT_BG, width=14, corner_radius=7)
        vScrollbarFrame.pack(side="right", fill="y", padx=(10, 0))
        
        vScrollbar = ttk.Scrollbar(
            vScrollbarFrame, 
            orient="vertical", 
            command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=vScrollbar.set)
        vScrollbar.pack(fill="y", expand=True)
        
        # Horizontal scrollbar
        hScrollbarFrame = ctk.CTkFrame(treeFrame, fg_color=Theme.INPUT_BG, height=14, corner_radius=7)
        hScrollbarFrame.pack(side="bottom", fill="x", pady=(10, 0))
        
        hScrollbar = ttk.Scrollbar(
            hScrollbarFrame, 
            orient="horizontal", 
            command=self.tree.xview
        )
        self.tree.configure(xscrollcommand=hScrollbar.set)
        hScrollbar.pack(fill="x", expand=True)
        
        # Pack tree
        self.tree.pack(side="left", fill="both", expand=True)
        
        # Add hover effect to rows
        self.tree.bind('<Motion>', self._onTreeHover)
        
        # Enable horizontal scrolling with touchpad/mouse wheel
        self.tree.bind('<Shift-MouseWheel>', self._onHorizontalScroll)
        # For Linux
        self.tree.bind('<Shift-Button-4>', self._onHorizontalScroll)
        self.tree.bind('<Shift-Button-5>', self._onHorizontalScroll)
        # For touchpad horizontal scroll
        self.tree.bind('<MouseWheel>', self._onMouseWheel)

        # Action buttons (fixed at bottom)
        self._createActionButtons(contentCard)

    def _onMouseWheel(self, event):
        """Handle mouse wheel scrolling - vertical by default, horizontal with shift"""
        if event.state & 0x1:  # Shift key is pressed
            self._onHorizontalScroll(event)
            return "break"
        # If no shift, default vertical scroll happens automatically
    
    def _onHorizontalScroll(self, event):
        """Handle horizontal scrolling with shift + wheel or touchpad"""
        if event.num == 4 or event.delta > 0:
            self.tree.xview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.tree.xview_scroll(1, "units")
        return "break"

    def _createHeader(self, parent):
        """Create header section"""
        headerFrame = ctk.CTkFrame(parent, fg_color="transparent")
        headerFrame.pack(fill="x", pady=(0, 16))
        
        # Title with icon
        titleContainer = ctk.CTkFrame(headerFrame, fg_color="transparent")
        titleContainer.pack(side="left")
        
        iconLabel = ctk.CTkLabel(
            titleContainer,
            text="📋",
            font=("Segoe UI", 28)
        )
        iconLabel.pack(side="left", padx=(0, 12))
        
        titleStack = ctk.CTkFrame(titleContainer, fg_color="transparent")
        titleStack.pack(side="left")
        
        titleLabel = ctk.CTkLabel(
            titleStack, 
            text=self._t("history.title"),
            font=("Segoe UI", 24, "bold"),
            text_color=Theme.TEXT_COLOR
        )
        titleLabel.pack(anchor="w")
        
        subtitleLabel = ctk.CTkLabel(
            titleStack,
            text=self._t("history.subtitle"),
            font=Theme.SMALL_FONT,
            text_color=Theme.TEXT_SECONDARY
        )
        subtitleLabel.pack(anchor="w")

    def _createFilterBar(self, parent):
        """Create search/filter bar"""
        filterFrame = ctk.CTkFrame(parent, fg_color="transparent")
        filterFrame.pack(fill="x", padx=20, pady=(20, 16))
        
        # Search box
        searchContainer = ctk.CTkFrame(
            filterFrame,
            fg_color=Theme.INPUT_BG,
            corner_radius=12,
            border_width=1,
            border_color=Theme.INPUT_BORDER
        )
        searchContainer.pack(side="left", fill="both", expand=True, padx=(0, 12))
        
        searchIcon = ctk.CTkLabel(
            searchContainer,
            text="🔍",
            font=("Segoe UI", 14)
        )
        searchIcon.pack(side="left", padx=(14, 10))
        
        self.searchEntry = ctk.CTkEntry(
            searchContainer,
            placeholder_text=self._t("history.search_placeholder"),
            font=Theme.SMALL_FONT,
            fg_color="transparent",
            border_width=0,
            text_color=Theme.INPUT_TEXT
        )
        self.searchEntry.pack(side="left", fill="both", expand=True, padx=(0, 14), pady=12)
        self.searchEntry.bind('<KeyRelease>', self._onSearch)
        
        # Stats label
        self.statsLabel = ctk.CTkLabel(
            filterFrame,
            text="0 downloads",
            font=Theme.SMALL_FONT,
            text_color=Theme.TEXT_SECONDARY
        )
        self.statsLabel.pack(side="right")

    def _createActionButtons(self, parent):
        """Create action buttons"""
        buttonFrame = ctk.CTkFrame(parent, fg_color="transparent")
        buttonFrame.pack(fill="x", padx=20, pady=(0, 20))

        # Left side buttons
        leftButtons = ctk.CTkFrame(buttonFrame, fg_color="transparent")
        leftButtons.pack(side="left")
        
        redownloadBtn = ctk.CTkButton(
            leftButtons, 
            text=f"⬇️ {self._t('history.redownload')}",
            command=self.redownloadSelected,
            fg_color=Theme.SECONDARY_COLOR,
            hover_color=Theme.SECONDARY_HOVER,
            text_color=Theme.TEXT_COLOR,
            width=150,
            height=46,
            corner_radius=12,
            font=("Segoe UI", 13, "bold")
        )
        redownloadBtn.pack(side="left", padx=(0, 12))

        removeBtn = ctk.CTkButton(
            leftButtons, 
            text=f"🗑️ {self._t('history.remove')}",
            command=self.removeSelected,
            fg_color="#CED4DA",
            hover_color="#ADB5BD",
            text_color="gray10",
            width=120,
            height=46,
            corner_radius=12,
            font=("Segoe UI", 13, "bold")
        )
        removeBtn.pack(side="left")
        
        # Right side buttons
        rightButtons = ctk.CTkFrame(buttonFrame, fg_color="transparent")
        rightButtons.pack(side="right")
        
        clearAllBtn = ctk.CTkButton(
            rightButtons, 
            text=f"🧹 {self._t('history.clear_all')}",
            command=self.clearAll,
            fg_color=Theme.ACCENT_COLOR,
            hover_color=Theme.ACCENT_HOVER,
            text_color=Theme.TEXT_COLOR,
            width=140,
            height=46,
            corner_radius=12,
            font=("Segoe UI", 13, "bold")
        )
        clearAllBtn.pack(side="right")

    def _onTreeHover(self, event):
        """Handle tree hover effects"""
        region = self.tree.identify("region", event.x, event.y)
        if region == "cell":
            self.tree.configure(cursor="hand2")
        else:
            self.tree.configure(cursor="")

    def _onSearch(self, event):
        """Handle search functionality"""
        searchTerm = self.searchEntry.get().lower()
        
        # Clear current items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Get all history
        historyData = self.controller.getHistory()
        filteredData = []
        
        # Filter and display
        for item in historyData:
            if (searchTerm in item['title'].lower() or 
                searchTerm in item['url'].lower() or
                searchTerm in item['path'].lower()):
                
                filteredData.append(item)
                
                # Add status emoji
                statusDisplay = item['status']
                if 'success' in statusDisplay.lower() or 'complete' in statusDisplay.lower():
                    statusDisplay = f"✅ {statusDisplay}"
                elif 'fail' in statusDisplay.lower() or 'error' in statusDisplay.lower():
                    statusDisplay = f"❌ {statusDisplay}"
                
                # Don't truncate text - let horizontal scroll handle it
                self.tree.insert("", "end", values=(
                    item['title'],
                    item['url'],
                    item['path'],
                    statusDisplay,
                    item['timestamp']
                ))
        
        # Adjust title column width based on filtered data
        if filteredData:
            titleWidth = self._calculateTitleWidth(filteredData)
            self.tree.column("Title", width=titleWidth, minwidth=150)
        
        # Update stats
        total = len(historyData)
        filteredCount = len(filteredData)
        if searchTerm:
            self.statsLabel.configure(text=f"{filteredCount} of {total} downloads")
        else:
            self.statsLabel.configure(text=f"{total} download{'s' if total != 1 else ''}")

    def populateHistory(self):
        """Populate the treeview with history data"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        historyData = self.controller.getHistory()
        
        # Calculate and set title column width
        if historyData:
            titleWidth = self._calculateTitleWidth(historyData)
            self.tree.column("Title", width=titleWidth, minwidth=150)
        
        for item in historyData:
            # Add status emoji
            statusDisplay = item['status']
            if 'success' in statusDisplay.lower() or 'complete' in statusDisplay.lower():
                statusDisplay = f"✅ {statusDisplay}"
            elif 'fail' in statusDisplay.lower() or 'error' in statusDisplay.lower():
                statusDisplay = f"❌ {statusDisplay}"
            
            # Don't truncate text - let horizontal scroll handle it
            self.tree.insert("", "end", values=(
                item['title'],
                item['url'],
                item['path'],
                statusDisplay,
                item['timestamp']
            ))
        
        # Update stats
        total = len(historyData)
        self.statsLabel.configure(text=f"{total} download{'s' if total != 1 else ''}")
    
    def redownloadSelected(self):
        """Initiates the re-download process via the main GUI"""
        selectedItem = self.tree.selection()
        if not selectedItem:
            self._showToast(
                self._t("history.no_selection"),
                duration=2000,
                isSuccess=False
            )
            return

        itemValues = self.tree.item(selectedItem, 'values')
        url = itemValues[1]
        
        # Get full URL from history (in case display was truncated)
        historyData = self.controller.getHistory()
        index = self.tree.index(selectedItem[0])
        fullUrl = historyData[index]['url']
        
        initialDir = itemValues[2]

        outputPath = filedialog.askdirectory(initialdir=initialDir)
        if outputPath:
            self._showToast(
                "Re-download started successfully",
                duration=2000,
                isSuccess=True
            )
            self.after(500, self.destroy)  # Close after showing toast
            self.mainGUI.reDownload(fullUrl, outputPath)

    def removeSelected(self):
        """Remove the selected video from history"""
        selectedItem = self.tree.selection()
        if not selectedItem:
            self._showToast(
                self._t("history.no_selection"),
                duration=2000,
                isSuccess=False
            )
            return

        index = self.tree.index(selectedItem[0])
        self.controller.removeHistoryEntry(index)
        self.populateHistory()
        self._showToast(
            self._t("history.removed"),
            duration=2000,
            isSuccess=True
        )

    def clearAll(self):
        """Clear all videos from history"""
        result = CustomMessageBox.askYesNo(
            self,
            self._t("history.clear_all"),
            self._t("history.confirm_clear")
        )   
    
        if result:
            self.controller.clearHistory()
            self.populateHistory()
            self._showToast(
                self._t("history.cleared"),
                duration=2000,
                isSuccess=True
            )
            # Ensure history window stays on top
            self.lift()
            self.focus_force()