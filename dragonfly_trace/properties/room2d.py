# coding=utf-8
"""Room2D TRACE Properties."""
from __future__ import division

from dragonfly.skylightparameter import DetailedSkylights


class Room2DTraceProperties(object):
    """TRACE Properties for Dragonfly Room2D.

    Args:
        host: A dragonfly_core Room2D object that hosts these properties.

    Properties:
        * host
    """
    __slots__ = ('_host',)

    def __init__(self, host):
        """Initialize Room2D TRACE properties."""
        # set the main properties of the Room2D
        self._host = host

    @property
    def host(self):
        """Get the Room2D object hosting these properties."""
        return self._host

    def check_no_floor_plate_holes(self, raise_exception=True, detailed=False):
        """Check whether the Room2D's floor geometry has holes.

        TRACE 3D Plus currently has no way to represent holes.

        Args:
            raise_exception: If True, a ValueError will be raised if the Room2D
                floor plate has one or more holes. (Default: True).
            detailed: Boolean for whether the returned object is a detailed list of
                dicts with error info or a string with a message. (Default: False).

        Returns:
            A string with the message or a list with a dictionary if detailed is True.
        """
        if self.host.floor_geometry.has_holes:
            hole_count = len(self.host.floor_geometry.holes)
            hole_msg = 'a hole' if hole_count == 1 else '{} holes'.format(hole_count)
            msg = 'Room2D "{}" has a floor plate with {}, which the TRACE 3D Plus ' \
                'interface cannot represent.'.format(self.host.display_name, hole_msg)
            if raise_exception:
                raise ValueError(msg)
            full_msg = self.host._validation_message_child(
                msg, self.host, detailed, '040102', extension='TRACE3D',
                error_type='Room Contains Holes')
            if detailed:
                return [full_msg]
            if raise_exception:
                raise ValueError(full_msg)
            return full_msg
        return [] if detailed else ''

    def check_no_skylights(self, raise_exception=True, detailed=False):
        """Check whether the Room2D has skylights.

        TRACE 3D Plus currently has no way to represent them.

        Args:
            raise_exception: If True, a ValueError will be raised if the Room2D
                has skylights. (Default: True).
            detailed: Boolean for whether the returned object is a detailed list of
                dicts with error info or a string with a message. (Default: False).

        Returns:
            A string with the message or a list with a dictionary if detailed is True.
        """
        if self.host.skylight_parameters is not None:
            sky_count = len(self.host.skylight_parameters.polygons) \
                if isinstance(self.host.skylight_parameters, DetailedSkylights) else 1
            sky_msg = 'a skylight' if sky_count == 1 else '{} skylights'.format(sky_count)
            msg = 'Room2D "{}" has {}, which TRACE 3D Plus ' \
                'cannot represent.'.format(self.host.display_name, sky_msg)
            if raise_exception:
                raise ValueError(msg)
            full_msg = self.host._validation_message_child(
                msg, self.host, detailed, '040104', extension='TRACE3D',
                error_type='Room Contains Skylights')
            if detailed:
                return [full_msg]
            if raise_exception:
                raise ValueError(full_msg)
            return full_msg
        return [] if detailed else ''

    def check_windows_above_origin(
        self, tolerance=0.01, raise_exception=True, detailed=False
    ):
        """Check whether the Room2D has windows below the scene origin.

        TRACE 3D Plus currently fails to import these windows since it believes
        that they are below ground.

        Args:
            tolerance: The maximum difference between coordinate values of two
                vertices at which they can be considered equivalent. (Default: 0.01,
                suitable for objects in meters).
            raise_exception: If True, a ValueError will be raised if the Room2D
                has skylights. (Default: True).
            detailed: Boolean for whether the returned object is a detailed list of
                dicts with error info or a string with a message. (Default: False).

        Returns:
            A string with the message or a list with a dictionary if detailed is True.
        """
        if self.host.floor_elevation < tolerance / 2:
            if any(wp is not None for wp in self.host.window_parameters):
                msg = 'Room2D "{}" has windows below the scene origin, which TRACE ' \
                    '3D Plus fails to import because it believes they are ' \
                    'underground.'.format(self.host.display_name)
                if raise_exception:
                    raise ValueError(msg)
                full_msg = self.host._validation_message_child(
                    msg, self.host, detailed, '040105', extension='TRACE3D',
                    error_type='Windows Below Scene Origin')
                if detailed:
                    return [full_msg]
                if raise_exception:
                    raise ValueError(full_msg)
                return full_msg
        return [] if detailed else ''

    def ToString(self):
        return self.__repr__()

    def __repr__(self):
        return 'Room2D TRACE Properties: [host: {}]'.format(self.host.display_name)
