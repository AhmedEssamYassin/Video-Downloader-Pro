from abc import ABC, abstractmethod

class NotificationService(ABC):
    """Abstract base class for notification services"""

    @abstractmethod
    def sendNotification(self, title: str, message: str):
        pass

class DesktopNotifier(NotificationService):
    """Desktop notification implementation"""

    def __init__(self):
        try:
            from plyer import notification
            self.notification = notification
        except ImportError:
            self.notification = None

    def sendNotification(self, title: str, message: str):
        if self.notification:
            try:
                self.notification.notify(
                    title=title,
                    message=message,
                    app_name="Video Downloader Pro",
                    timeout=10
                )
            except Exception as e:
                print(f"Failed to send notification: {e}")
        else:
            print(f"INFO: Notification service not available. Please install 'plyer'.\n{title}: {message}")