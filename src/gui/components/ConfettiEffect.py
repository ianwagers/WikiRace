from PyQt6.QtWidgets import QWidget, QGraphicsView, QGraphicsScene, QGraphicsItem
from PyQt6.QtCore import QTimer, QPropertyAnimation, QEasingCurve, QRectF, QPointF, pyqtSignal, Qt
from PyQt6.QtGui import QColor, QBrush, QPen, QPainter, QPainterPath
import random
import math


class ConfettiPiece(QGraphicsItem):
    """Individual confetti piece"""
    
    def __init__(self, x, y, color, shape='rectangle'):
        super().__init__()
        self.x = x
        self.y = y
        self.color = color
        self.shape = shape
        self.rotation = 0
        # Much more varied directions for maximum diversity
        self.velocity_x = random.uniform(-15, 15)  # Extremely wide horizontal spread
        self.velocity_y = random.uniform(-12, 2)  # Some pieces can even go upward initially
        self.angular_velocity = random.uniform(-25, 25)  # Maximum spinning variety
        self.gravity = random.uniform(0.1, 0.8)  # Very variable gravity
        self.bounce = random.uniform(0.1, 1.0)  # Full range of bounciness
        self.friction = random.uniform(0.90, 0.99)  # More variable friction
        self.life = 1.0
        self.decay = random.uniform(0.0005, 0.003)  # Even slower decay for longer life
        self.wind_effect = random.uniform(-1.0, 1.0)  # Stronger wind effect
        self.initial_direction = random.uniform(0, 360)  # Random initial direction in degrees
        
        # Set initial position
        self.setPos(x, y)
        
    def boundingRect(self):
        return QRectF(-5, -5, 10, 10)
    
    def paint(self, painter, option, widget):
        # Enhanced rendering for better graphical quality
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        
        # Create a more vibrant color with alpha based on life
        alpha = int(255 * self.life)
        enhanced_color = QColor(self.color)
        enhanced_color.setAlpha(alpha)
        
        # Add subtle glow effect
        glow_color = QColor(enhanced_color)
        glow_color.setAlpha(alpha // 3)
        painter.setPen(QPen(glow_color, 2))
        painter.setBrush(QBrush(enhanced_color))
        
        painter.save()
        painter.translate(self.x, self.y)
        painter.rotate(self.rotation)
        
        # Enhanced shapes with better graphics
        if self.shape == 'circle':
            # Draw circle with gradient effect
            painter.drawEllipse(-4, -4, 8, 8)
            # Add inner highlight
            highlight_color = QColor(enhanced_color)
            highlight_color.setAlpha(alpha // 2)
            painter.setBrush(QBrush(highlight_color))
            painter.drawEllipse(-2, -2, 4, 4)
        elif self.shape == 'triangle':
            path = QPainterPath()
            path.moveTo(0, -5)
            path.lineTo(-4, 4)
            path.lineTo(4, 4)
            path.closeSubpath()
            painter.drawPath(path)
        elif self.shape == 'star':
            # Enhanced star with more points
            path = QPainterPath()
            import math
            points = 8
            outer_radius = 4
            inner_radius = 2
            for i in range(points * 2):
                angle = (i * math.pi) / points
                if i % 2 == 0:
                    radius = outer_radius
                else:
                    radius = inner_radius
                x = radius * math.cos(angle)
                y = radius * math.sin(angle)
                if i == 0:
                    path.moveTo(x, y)
                else:
                    path.lineTo(x, y)
            path.closeSubpath()
            painter.drawPath(path)
        elif self.shape == 'diamond':
            # Enhanced diamond with facets
            path = QPainterPath()
            path.moveTo(0, -4)
            path.lineTo(4, 0)
            path.lineTo(0, 4)
            path.lineTo(-4, 0)
            path.closeSubpath()
            painter.drawPath(path)
            # Add inner diamond
            inner_path = QPainterPath()
            inner_path.moveTo(0, -2)
            inner_path.lineTo(2, 0)
            inner_path.lineTo(0, 2)
            inner_path.lineTo(-2, 0)
            inner_path.closeSubpath()
            highlight_color = QColor(enhanced_color)
            highlight_color.setAlpha(alpha // 2)
            painter.setBrush(QBrush(highlight_color))
            painter.drawPath(inner_path)
        else:  # rectangle
            # Enhanced rectangle with rounded corners
            painter.drawRoundedRect(-5, -3, 10, 6, 2, 2)
        
        painter.restore()
    
    def advance(self, phase):
        if phase == 0:
            return
        
        # Update physics with wind effect
        self.velocity_y += self.gravity
        self.velocity_x += self.wind_effect * 0.1  # Wind affects horizontal movement
        self.velocity_x *= self.friction
        self.velocity_y *= self.friction
        
        # Add some randomness to make it more dynamic
        if random.random() < 0.1:  # 10% chance for random movement
            self.velocity_x += random.uniform(-0.5, 0.5)
            self.velocity_y += random.uniform(-0.2, 0.2)
        
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.rotation += self.angular_velocity
        
        # Update life
        self.life -= self.decay
        
        # Update position
        self.setPos(self.x, self.y)
        
        # Remove if life is over
        if self.life <= 0:
            if self.scene():
                self.scene().removeItem(self)


class ConfettiEffect(QGraphicsView):
    """Confetti effect widget"""
    
    effect_finished = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        
        # Configure the view
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setFrameStyle(0)
        self.setStyleSheet("background: transparent; border: none;")
        
        # Animation timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateConfetti)
        
        # Confetti pieces
        self.confetti_pieces = []
        
        # Extended colors for confetti - more vibrant and varied
        self.colors = [
            QColor(255, 0, 0),      # Red
            QColor(0, 255, 0),      # Green
            QColor(0, 0, 255),      # Blue
            QColor(255, 255, 0),    # Yellow
            QColor(255, 0, 255),    # Magenta
            QColor(0, 255, 255),    # Cyan
            QColor(255, 165, 0),    # Orange
            QColor(128, 0, 128),    # Purple
            QColor(255, 192, 203),  # Pink
            QColor(0, 128, 0),      # Dark Green
            QColor(255, 20, 147),   # Deep Pink
            QColor(0, 191, 255),    # Deep Sky Blue
            QColor(255, 69, 0),     # Red Orange
            QColor(138, 43, 226),   # Blue Violet
            QColor(255, 215, 0),    # Gold
            QColor(50, 205, 50),    # Lime Green
            QColor(255, 105, 180),  # Hot Pink
            QColor(0, 255, 127),    # Spring Green
            QColor(255, 140, 0),    # Dark Orange
            QColor(147, 112, 219),  # Medium Purple
        ]
        
        # Shapes
        self.shapes = ['rectangle', 'circle', 'triangle', 'star', 'diamond']
        
    def startEffect(self, duration=3000):
        """Start the confetti effect"""
        # Clear any existing confetti
        self.clearConfetti()
        
        # Create initial confetti burst
        self.createConfetti()
        
        # Start animation
        self.timer.start(16)  # ~60 FPS
        
        # Add additional confetti bursts throughout the duration for more dynamic effect
        burst_times = [100, 300, 800, 1300]  # Quick bursts at 1.5s and 3s for 4s duration
        for burst_time in burst_times:
            if burst_time < duration:
                QTimer.singleShot(burst_time, self.addConfettiBurst)
        
        # Stop after duration
        QTimer.singleShot(duration, self.stopEffect)
    
    def addConfettiBurst(self):
        """Add a burst of additional confetti during the effect"""
        if not self.scene:
            return
            
        # Get the size of the view
        width = self.width()
        height = self.height()
        
        # Create a smaller burst of confetti
        for i in range(270):  # Triple burst size for ultra-dense effect
            x = random.randint(-50, width + 50)
            y = random.randint(-100, 0)
            
            color = random.choice(self.colors)
            shape = random.choice(self.shapes)
            
            piece = ConfettiPiece(x, y, color, shape)
            self.scene.addItem(piece)
            self.confetti_pieces.append(piece)
        
    def createConfetti(self):
        """Create confetti pieces"""
        if not self.scene:
            return
            
        # Get the size of the view
        width = self.width()
        height = self.height()
        
        # Create confetti pieces across the top of the screen
        for i in range(1350):  # ULTRA-DENSE confetti pieces for maximum celebration
            x = random.randint(-50, width + 50)  # Start from wider area including off-screen
            y = random.randint(-100, 0)  # Start from higher up for more dramatic effect
            
            color = random.choice(self.colors)
            shape = random.choice(self.shapes)
            
            piece = ConfettiPiece(x, y, color, shape)
            self.scene.addItem(piece)
            self.confetti_pieces.append(piece)
    
    def updateConfetti(self):
        """Update all confetti pieces"""
        if not self.scene:
            return
            
        # Update all pieces
        for piece in self.confetti_pieces[:]:  # Copy list to avoid modification during iteration
            piece.advance(1)
            
            # Remove pieces that are off screen or have no life (allow them to fall further)
            if (piece.y > self.height() + 200 or  # Allow falling much further
                piece.x < -100 or piece.x > self.width() + 100 or  # Allow wider spread
                piece.life <= 0):
                if piece in self.scene.items():
                    self.scene.removeItem(piece)
                if piece in self.confetti_pieces:
                    self.confetti_pieces.remove(piece)
        
        # Check if all confetti is gone
        if not self.confetti_pieces:
            self.stopEffect()
    
    def stopEffect(self):
        """Stop the confetti effect"""
        self.timer.stop()
        self.clearConfetti()
        self.effect_finished.emit()
    
    def clearConfetti(self):
        """Clear all confetti pieces"""
        if self.scene:
            for piece in self.confetti_pieces:
                if piece in self.scene.items():
                    self.scene.removeItem(piece)
        self.confetti_pieces.clear()
    
    def resizeEvent(self, event):
        """Handle resize events"""
        super().resizeEvent(event)
        if self.scene:
            self.scene.setSceneRect(0, 0, self.width(), self.height())


class ConfettiWidget(QWidget):
    """Widget that can be overlaid on other widgets to show confetti"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setStyleSheet("background: transparent;")
        
        # Create confetti effect
        self.confetti_view = ConfettiEffect(self)
        
        # Layout
        from PyQt6.QtWidgets import QVBoxLayout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.confetti_view)
        
        # Connect finished signal
        self.confetti_view.effect_finished.connect(self.hide)
        
    def startConfetti(self, duration=3000):
        """Start confetti effect"""
        self.show()
        self.confetti_view.startEffect(duration)
        
    def resizeEvent(self, event):
        """Handle resize events"""
        super().resizeEvent(event)
        self.confetti_view.resize(self.size())
