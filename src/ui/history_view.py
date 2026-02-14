"""
Enhanced history view window using ttkbootstrap
Displays download history in a modern, flat design
"""

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog
from .theme import Theme
from .custom_messagebox import CustomMessageBox
from ..utils import AssetLoader, getTranslation


class HistoryView(tk.Toplevel):
    """Enhanced history view window with modern flat design"""

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
        self.configure(bg=Theme.BG_COLOR)
        
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
        bgColor = Theme.SUCCESS_COLOR if isSuccess else Theme.ACCENT_COLOR
        self.toastFrame = tk.Frame(
            self,
            bg=bgColor,
            relief=FLAT
        )
        
        # Toast content
        toastContent = tk.Frame(self.toastFrame, bg=bgColor)
        toastContent.pack(padx=20, pady=12)
        
        icon = "✅" if isSuccess else "❌"
        iconLabel = tk.Label(
            toastContent,
            text=icon,
            font=("Segoe UI", 16),
            fg="white",
            bg=bgColor
        )
        iconLabel.pack(side=LEFT, padx=(0, 10))
        
        messageLabel = tk.Label(
            toastContent,
            text=message,
            font=("Segoe UI", 12, "bold"),
            fg="white",
            bg=bgColor
        )
        messageLabel.pack(side=LEFT)
        
        # Position toast at bottom center
        self.toastFrame.place(relx=0.5, rely=0.92, anchor=CENTER)
        
        # Fade in
        self.toastFrame.lift()
        self._animateToastIn(self.toastFrame, duration)
    
    def _animateToastIn(self, toast, duration):
        """Animate toast in and schedule fade out"""
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
        
        # Approximate width: ~8 pixels per character
        calculatedWidth = min(maxTitleLength * 8, 300)
        
        # Ensure minimum width
        return max(calculatedWidth, 150)

    def _createWidgets(self):
        """Create and layout all GUI widgets"""
        
        # Main container
        mainContainer = tk.Frame(self, bg=Theme.BG_COLOR)
        mainContainer.pack(fill=BOTH, expand=True, padx=20, pady=20)
        
        # Header
        self._createHeader(mainContainer)
        
        # Content card
        contentCard = tk.Frame(
            mainContainer, 
            bg=Theme.CARD_COLOR,
            relief=FLAT,
            borderwidth=1,
            highlightbackground=Theme.INPUT_BORDER,
            highlightthickness=1
        )
        contentCard.pack(fill=BOTH, expand=True, pady=(0, 0))
        
        # Search/Filter bar
        self._createFilterBar(contentCard)
        
        # Treeview container
        treeFrame = tk.Frame(contentCard, bg=Theme.CARD_COLOR)
        treeFrame.pack(fill=BOTH, expand=True, padx=20, pady=(0, 16))

        # Create treeview style
        style = ttk.Style()
        
        # Configure treeview
        self.tree = ttk.Treeview(
            treeFrame, 
            columns=("Title", "URL", "Path", "Status", "Date"), 
            show="headings",
            selectmode=BROWSE,
            bootstyle=INFO
        )
        
        # Configure columns
        self.tree.heading("Title", text=f"🎬 {self._t('labels.video_title')}")
        self.tree.heading("URL", text="🔗 URL")
        self.tree.heading("Path", text=f"📁 {self._t('labels.save_location')}")
        self.tree.heading("Status", text=self._t('labels.status'))
        self.tree.heading("Date", text="📅 Date")
        
        # Column widths
        self.tree.column("Title", width=300, minwidth=150)
        self.tree.column("URL", width=250, minwidth=150)
        self.tree.column("Path", width=250, minwidth=150)
        self.tree.column("Status", width=100, minwidth=80)
        self.tree.column("Date", width=140, minwidth=120)

        # Scrollbars
        vScrollbar = ttk.Scrollbar(
            treeFrame, 
            orient=VERTICAL, 
            command=self.tree.yview,
            bootstyle=INFO
        )
        self.tree.configure(yscrollcommand=vScrollbar.set)
        vScrollbar.pack(side=RIGHT, fill=Y)
        
        hScrollbar = ttk.Scrollbar(
            treeFrame, 
            orient=HORIZONTAL, 
            command=self.tree.xview,
            bootstyle=INFO
        )
        self.tree.configure(xscrollcommand=hScrollbar.set)
        hScrollbar.pack(side=BOTTOM, fill=X)
        
        # Pack tree
        self.tree.pack(side=LEFT, fill=BOTH, expand=True)
        
        # Add hover effect
        self.tree.bind('<Motion>', self._onTreeHover)
        
        # Action buttons
        self._createActionButtons(contentCard)

    def _createHeader(self, parent):
        """Create header section"""
        headerFrame = tk.Frame(parent, bg=Theme.BG_COLOR)
        headerFrame.pack(fill=X, pady=(0, 16))
        
        # Title with icon
        titleContainer = tk.Frame(headerFrame, bg=Theme.BG_COLOR)
        titleContainer.pack(side=LEFT)
        
        iconLabel = tk.Label(
            titleContainer,
            text="📋",
            font=("Segoe UI", 28),
            bg=Theme.BG_COLOR,
            fg=Theme.TEXT_COLOR
        )
        iconLabel.pack(side=LEFT, padx=(0, 12))
        
        titleStack = tk.Frame(titleContainer, bg=Theme.BG_COLOR)
        titleStack.pack(side=LEFT)
        
        titleLabel = tk.Label(
            titleStack, 
            text=self._t("history.title"),
            font=("Segoe UI", 24, "bold"),
            fg=Theme.TEXT_COLOR,
            bg=Theme.BG_COLOR
        )
        titleLabel.pack(anchor=W)
        
        subtitleLabel = tk.Label(
            titleStack,
            text=self._t("history.subtitle"),
            font=Theme.SMALL_FONT,
            fg=Theme.TEXT_SECONDARY,
            bg=Theme.BG_COLOR
        )
        subtitleLabel.pack(anchor=W)

    def _createFilterBar(self, parent):
        """Create search/filter bar"""
        filterFrame = tk.Frame(parent, bg=Theme.CARD_COLOR)
        filterFrame.pack(fill=X, padx=20, pady=(20, 16))
        
        # Search box
        searchContainer = tk.Frame(filterFrame, bg=Theme.INPUT_BG)
        searchContainer.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 12))
        
        searchIcon = tk.Label(
            searchContainer,
            text="🔍",
            font=("Segoe UI", 16),
            bg=Theme.INPUT_BG,
            fg=Theme.TEXT_COLOR
        )
        searchIcon.pack(side=LEFT, padx=(14, 10))
        
        self.searchEntry = ttk.Entry(
            searchContainer,
            font=Theme.SMALL_FONT,
            bootstyle=INFO
        )
        self.searchEntry.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 14), pady=12)
        self.searchEntry.bind('<KeyRelease>', self._onSearch)
        
        # Stats label
        self.statsLabel = tk.Label(
            filterFrame,
            text="0 downloads",
            font=Theme.SMALL_FONT,
            fg=Theme.TEXT_SECONDARY,
            bg=Theme.CARD_COLOR
        )
        self.statsLabel.pack(side=RIGHT)

    def _createActionButtons(self, parent):
        """Create action buttons"""
        buttonFrame = tk.Frame(parent, bg=Theme.CARD_COLOR)
        buttonFrame.pack(fill=X, padx=20, pady=(0, 20))

        # Left side buttons
        leftButtons = tk.Frame(buttonFrame, bg=Theme.CARD_COLOR)
        leftButtons.pack(side=LEFT)
        
        redownloadBtn = ttk.Button(
            leftButtons, 
            text=f"⬇️ {self._t('history.redownload')}",
            command=self.redownloadSelected,
            bootstyle=PRIMARY,
            width=15,
            cursor="hand2"
        )
        redownloadBtn.pack(side=LEFT, padx=(0, 12))

        removeBtn = ttk.Button(
            leftButtons, 
            text=f"🗑️ {self._t('history.remove')}",
            command=self.removeSelected,
            bootstyle=SECONDARY,
            width=13,
            cursor="hand2"
        )
        removeBtn.pack(side=LEFT)
        
        # Right side buttons
        rightButtons = tk.Frame(buttonFrame, bg=Theme.CARD_COLOR)
        rightButtons.pack(side=RIGHT)
        
        clearAllBtn = ttk.Button(
            rightButtons, 
            text=f"🧹 {self._t('history.clear_all')}",
            command=self.clearAll,
            bootstyle=DANGER,
            width=15,
            cursor="hand2"
        )
        clearAllBtn.pack(side=RIGHT)

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
                
                self.tree.insert("", "end", values=(
                    item['title'],
                    item['url'],
                    item['path'],
                    statusDisplay,
                    item['timestamp']
                ))
        
        # Adjust title column width
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
        
        # Get full URL from history
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
            self.after(500, self.destroy)
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
