from shapely.geometry import Polygon, Point


def detect(x, y, polygons):
    point = Point([x, y])
    for i, shape in polygons.items():
        polygon = Polygon(shape)
        if polygon.contains(point):
            return i  # Return the shape key containing the point
    return None  # Return None if no shape contains the point
