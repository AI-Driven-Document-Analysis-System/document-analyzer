from typing import List
class BoundingBox:
    """Represents a bounding box with coordinates"""
    x1: int
    y1: int
    x2: int
    y2: int
    
    @property
    def coordinates(self) -> List[int]:
        return [self.x1, self.y1, self.x2, self.y2]
    
    @property
    def width(self) -> int:
        return self.x2 - self.x1
    
    @property
    def height(self) -> int:
        return self.y2 - self.y1
    
    @property
    def area(self) -> int:
        return self.width * self.height