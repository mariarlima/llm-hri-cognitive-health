from shapely.geometry import Polygon, Point


def detect(x, y, polygons):
    point = Point([x, y])
    polygons_contain_point = []
    for i, shape in polygons.items():
        polygon = Polygon(shape)
        if polygon.contains(point):
            polygons_contain_point.append(i)  # Return the shape key containing the point
    return polygons_contain_point if len(
        polygons_contain_point) > 0 else None  # Return None if no shape contains the point
