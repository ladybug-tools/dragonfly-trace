# coding=utf-8
"""Model TACE Properties."""
from __future__ import division

from ladybug_geometry.geometry2d import Point2D, Polygon2D
from ladybug_geometry.geometry3d import Point3D, Face3D
from honeybee.units import parse_distance_string


class ModelTraceProperties(object):
    """TRACE Properties for Dragonfly Model.

    Args:
        host: A dragonfly_core Model object that hosts these properties.

    Properties:
        * host
    """
    # dictionary mapping validation error codes to a corresponding check function
    ERROR_MAP = {
        '040101': 'check_no_sloped_roofs',
        '040102': 'check_no_room_2d_floor_plate_holes',
        '040103': 'check_story_floor_plates',
        '040104': 'check_no_skylights',
        '040105': 'check_windows_above_origin'
    }

    def __init__(self, host):
        """Initialize ModelTraceProperties."""
        self._host = host

    @property
    def host(self):
        """Get the Model object hosting these properties."""
        return self._host

    def check_for_extension(self, raise_exception=True, detailed=False):
        """Check that the Model is valid for TRACE 3D Plus simulation.

        This process includes all relevant dragonfly-core checks as well as checks
        that apply only for TRACE 3D Plus.

        Args:
            raise_exception: Boolean to note whether a ValueError should be raised
                if any errors are found. If False, this method will simply
                return a text string with all errors that were found. (Default: True).
            detailed: Boolean for whether the returned object is a detailed list of
                dicts with error info or a string with a message. (Default: False).

        Returns:
            A text string with all errors that were found or a list if detailed is True.
            This string (or list) will be empty if no errors were found.
        """
        # set up defaults to ensure the method runs correctly
        detailed = False if raise_exception else detailed
        msgs = []
        tol = self.host.tolerance
        ang_tol = self.host.angle_tolerance

        # perform checks for duplicate identifiers, which might mess with other checks
        msgs.append(self.host.check_all_duplicate_identifiers(False, detailed))

        # perform checks for key dragonfly model schema rules
        msgs.append(self.host.check_degenerate_room_2ds(tol, False, detailed))
        msgs.append(self.host.check_self_intersecting_room_2ds(tol, False, detailed))
        msgs.append(self.host.check_plenum_depths(tol, False, detailed))
        msgs.append(self.host.check_window_parameters_valid(tol, False, detailed))
        msgs.append(self.host.check_no_room2d_overlaps(tol, False, detailed))
        msgs.append(self.host.check_collisions_between_stories(tol, False, detailed))
        msgs.append(self.host.check_roofs_above_rooms(tol, False, detailed))
        msgs.append(self.host.check_room2d_floor_heights_valid(False, detailed))
        msgs.append(self.host.check_missing_adjacencies(False, detailed))
        msgs.append(self.host.check_all_room3d(tol, ang_tol, False, detailed))

        # perform checks that are specific to TRACE 3D Plus
        msgs.append(self.check_no_sloped_roofs(False, detailed))
        msgs.append(self.check_no_room_2d_floor_plate_holes(False, detailed))
        msgs.append(self.check_story_floor_plates(tol, False, detailed))
        msgs.append(self.check_no_skylights(False, detailed))
        msgs.append(self.check_windows_above_origin(tol, False, detailed))

        # output a final report of errors or raise an exception
        full_msgs = [msg for msg in msgs if msg]
        if detailed:
            return [m for msg in full_msgs for m in msg]
        full_msg = '\n'.join(full_msgs)
        if raise_exception and len(full_msgs) != 0:
            raise ValueError(full_msg)
        return full_msg

    def check_generic(self, raise_exception=True, detailed=False):
        """Check generic of the aspects of the Model TRACE 3D Plus properties.

        This includes checks for everything except holes in floor plates and
        courtyard stories.

        Args:
            raise_exception: Boolean to note whether a ValueError should be raised
                if any errors are found. If False, this method will simply
                return a text string with all errors that were found.
            detailed: Boolean for whether the returned object is a detailed list of
                dicts with error info or a string with a message. (Default: False).

        Returns:
            A text string with all errors that were found or a list if detailed is True.
            This string (or list) will be empty if no errors were found.
        """
        # set up defaults to ensure the method runs correctly
        detailed = False if raise_exception else detailed
        msgs = []
        # output a final report of errors or raise an exception
        full_msgs = [msg for msg in msgs if msg]
        if detailed:
            return [m for msg in full_msgs for m in msg]
        full_msg = '\n'.join(full_msgs)
        if raise_exception and len(full_msgs) != 0:
            raise ValueError(full_msg)
        return full_msg

    def check_all(self, raise_exception=True, detailed=False):
        """Check all of the aspects of the Model TRACE 3D Plus properties.

        Args:
            raise_exception: Boolean to note whether a ValueError should be raised
                if any errors are found. If False, this method will simply
                return a text string with all errors that were found.
            detailed: Boolean for whether the returned object is a detailed list of
                dicts with error info or a string with a message. (Default: False).

        Returns:
            A text string with all errors that were found or a list if detailed is True.
            This string (or list) will be empty if no errors were found.
        """
        # set up defaults to ensure the method runs correctly
        detailed = False if raise_exception else detailed
        msgs = []
        tol = self.host.tolerance
        # perform checks for specific TRACE 3D Plus simulation rules
        msgs.append(self.check_no_sloped_roofs(False, detailed))
        msgs.append(self.check_no_room_2d_floor_plate_holes(False, detailed))
        msgs.append(self.check_story_floor_plates(tol, False, detailed))
        msgs.append(self.check_no_skylights(False, detailed))
        msgs.append(self.check_windows_above_origin(tol, False, detailed))
        # output a final report of errors or raise an exception
        full_msgs = [msg for msg in msgs if msg]
        if detailed:
            return [m for msg in full_msgs for m in msg]
        full_msg = '\n'.join(full_msgs)
        if raise_exception and len(full_msgs) != 0:
            raise ValueError(full_msg)
        return full_msg

    def check_no_sloped_roofs(self, raise_exception=True, detailed=False):
        """Check whether any stories have sloped roofs.

        The TRACE 3D Plus interface has no support for sloped roofs.

        Args:
            raise_exception: If True, a ValueError will be raised if a story
                has a sloped roof. (Default: True).
            detailed: Boolean for whether the returned object is a detailed list of
                dicts with error info or a string with a message. (Default: False).

        Returns:
            A string with the message or a list with a dictionary if detailed is True.
        """
        detailed = False if raise_exception else detailed
        msgs = []
        for bldg in self.host.buildings:
            for story in bldg.unique_stories:
                if story.roof is not None:
                    msg = 'Story "{}" contains {} sloped roof geometries, which TRACE ' \
                        '3D Plus cannot represent.'.format(
                            story.display_name, len(story.roof)
                        )
                    if detailed:
                        msg = {
                            'type': 'ValidationError',
                            'code': '040101',
                            'error_type': 'Story Has Sloped Roofs',
                            'extension_type': 'TRACE3D',
                            'element_type': 'Room2D',
                            'element_id': [r.identifier for r in story.room_2ds],
                            'element_name': [r.display_name for r in story.room_2ds],
                            'message': msg
                        }
                    msgs.append(msg)
        if detailed:
            return msgs
        full_msg = '\n'.join(msgs)
        if raise_exception and len(msgs) != 0:
            raise ValueError(full_msg)
        return full_msg

    def check_no_room_2d_floor_plate_holes(self, raise_exception=True, detailed=False):
        """Check whether any Room2D floor geometry has holes.

        TRACE 3D Plus currently has no way to represent holes.

        Args:
            raise_exception: If True, a ValueError will be raised if the Room2D
                floor plate has one or more holes. (Default: True).
            detailed: Boolean for whether the returned object is a detailed list of
                dicts with error info or a string with a message. (Default: False).

        Returns:
            A string with the message or a list with a dictionary if detailed is True.
        """
        detailed = False if raise_exception else detailed
        msgs = []
        for room in self.host.room_2ds:
            msg = room.properties.trace.check_no_floor_plate_holes(False, detailed)
            if detailed:
                msgs.extend(msg)
            elif msg != '':
                msgs.append(msg)
        if detailed:
            return msgs
        full_msg = '\n'.join(msgs)
        if raise_exception and len(msgs) != 0:
            raise ValueError(full_msg)
        return full_msg

    def check_story_floor_plates(self, tolerance=None, raise_exception=True, detailed=False):
        """Check Story floor plates for courtyards.

        Args:
            tolerance: The tolerance to be used when joining the Room2D floor
                plates together into a Story floor plate. If None, the Model
                tolerance will be used. (Default: None).
            raise_exception: Boolean to note whether a ValueError should be raised
                if the story contains a courtyard. (Default: True).
            detailed: Boolean for whether the returned object is a detailed list of
                dicts with error info or a string with a message. (Default: False).

        Returns:
            A string with the message or a list with a dictionary if detailed is True.
        """
        # establish the tolerance and gap width at which point it is clearly a courtyard
        tolerance = self.host.tolerance if tolerance is None else tolerance
        court_width = parse_distance_string('1ft', self.host.units)
        # loop through the stories and identify any courtyards
        story_msgs = []
        for bldg in self.host.buildings:
            for story in bldg.unique_stories:
                floor_geos = [room.floor_geometry for room in story.room_2ds]
                joined_geos = self._grouped_floor_boundary(floor_geos, tolerance)
                c_count = 0
                for geo in joined_geos:
                    if geo.has_holes:
                        for hole in geo.holes:
                            try:
                                h_geo = Face3D(hole)
                                h_geo = h_geo.remove_colinear_vertices(court_width)
                                max_len = max(s.length for s in h_geo.boundary_segments)
                                tol_area = max_len * court_width
                                if h_geo.area > tol_area:
                                    c_count += 1
                            except (AssertionError, ValueError):
                                pass  # gap is too small to be a true courtyard
                if c_count != 0:
                    hole_msg = 'a courtyard' if c_count == 1 \
                        else '{} courtyards'.format(c_count)
                    msg = 'The geometry of Story "{}" contains {}, which TRACE 3D Plus ' \
                        'cannot represent.'.format(story.display_name, hole_msg)
                    if detailed:
                        msg = {
                            'type': 'ValidationError',
                            'code': '040103',
                            'error_type': 'Story Floor Plate Contains Courtyards',
                            'extension_type': 'TRACE3D',
                            'element_type': 'Room2D',
                            'element_id': [r.identifier for r in story.room_2ds],
                            'element_name': [r.display_name for r in story.room_2ds],
                            'message': msg
                        }
                    story_msgs.append(msg)
        if detailed:
            return story_msgs
        if story_msgs != []:
            msg = 'The following Stories have issues with their floor plates' \
                ':\n{}'.format('\n'.join(story_msgs))
            if raise_exception:
                raise ValueError(msg)
            return msg
        return ''

    def check_no_skylights(self, raise_exception=True, detailed=False):
        """Check whether any Room2D floor geometry has skylights.

        Args:
            raise_exception: If True, a ValueError will be raised if a Room2D
                has skylights. (Default: True).
            detailed: Boolean for whether the returned object is a detailed list of
                dicts with error info or a string with a message. (Default: False).

        Returns:
            A string with the message or a list with a dictionary if detailed is True.
        """
        detailed = False if raise_exception else detailed
        msgs = []
        for room in self.host.room_2ds:
            msg = room.properties.trace.check_no_skylights(False, detailed)
            if detailed:
                msgs.extend(msg)
            elif msg != '':
                msgs.append(msg)
        if detailed:
            return msgs
        full_msg = '\n'.join(msgs)
        if raise_exception and len(msgs) != 0:
            raise ValueError(full_msg)
        return full_msg

    def check_windows_above_origin(
        self, tolerance=None, raise_exception=True, detailed=False
    ):
        """Check whether the Room2D has windows below the scene origin.

        TRACE 3D Plus currently fails to import these windows since it believes
        that they are below ground.

        Args:
            tolerance: The maximum difference between coordinate values of two
                vertices at which they can be considered equivalent. (Default: 0.01,
                suitable for objects in meters).
            raise_exception: Boolean to note whether a ValueError should be raised
                if the story contains a courtyard. (Default: True).
            detailed: Boolean for whether the returned object is a detailed list of
                dicts with error info or a string with a message. (Default: False).

        Returns:
            A string with the message or a list with a dictionary if detailed is True.
        """
        detailed = False if raise_exception else detailed
        msgs = []
        for room in self.host.room_2ds:
            msg = room.properties.trace.check_windows_above_origin(tolerance, False, detailed)
            if detailed:
                msgs.extend(msg)
            elif msg != '':
                msgs.append(msg)
        if detailed:
            return msgs
        full_msg = '\n'.join(msgs)
        if raise_exception and len(msgs) != 0:
            raise ValueError(full_msg)
        return full_msg

    @staticmethod
    def _grouped_floor_boundary(floor_geos, tolerance=0.01):
        """Get a list of Face3D for the boundary around several horizontal Face3Ds.

        Args:
            floor_geos: A list of Honeybee Rooms for which the horizontal boundary will
                be computed.
            tolerance: The maximum difference between coordinate values of two
                vertices at which they can be considered equivalent. (Default: 0.01,
                suitable for objects in meters).
        """
        # remove colinear vertices and degenerate faces
        clean_floor_geos = []
        for geo in floor_geos:
            try:
                clean_floor_geos.append(geo.remove_colinear_vertices(tolerance))
            except AssertionError:  # degenerate geometry to ignore
                pass
        if len(clean_floor_geos) == 0:
            return []  # no Room boundary to be found

        # convert the floor Face3Ds into counterclockwise Polygon2Ds
        floor_polys, z_vals = [], []
        for flr_geo in clean_floor_geos:
            z_vals.append(flr_geo.min.z)
            b_poly = Polygon2D([Point2D(pt.x, pt.y) for pt in flr_geo.boundary])
            floor_polys.append(b_poly)
            if flr_geo.has_holes:
                for hole in flr_geo.holes:
                    h_poly = Polygon2D([Point2D(pt.x, pt.y) for pt in hole])
                    floor_polys.append(h_poly)
        z_min = min(z_vals)

        # find the joined intersected boundary
        closed_polys = Polygon2D.joined_intersected_boundary(floor_polys, tolerance)

        # remove colinear vertices from the resulting polygons
        clean_polys = []
        for poly in closed_polys:
            try:
                clean_polys.append(poly.remove_colinear_vertices(tolerance))
            except AssertionError:
                pass  # degenerate polygon to ignore

        # figure out if polygons represent holes in the others and make Face3D
        if len(clean_polys) == 0:
            return []
        elif len(clean_polys) == 1:  # can be represented with a single Face3D
            pts3d = [Point3D(pt.x, pt.y, z_min) for pt in clean_polys[0]]
            return [Face3D(pts3d)]
        else:  # need to separate holes from distinct Face3Ds
            bound_faces = []
            for poly in clean_polys:
                pts3d = tuple(Point3D(pt.x, pt.y, z_min) for pt in poly)
                bound_faces.append(Face3D(pts3d))
            return Face3D.merge_faces_to_holes(bound_faces, tolerance)

    def ToString(self):
        return self.__repr__()

    def __repr__(self):
        return 'Model TRACE Properties: [host: {}]'.format(self.host.display_name)
