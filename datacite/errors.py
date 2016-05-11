# -*- coding: utf-8 -*-
#
# This file is part of DataCite.
#
# Copyright (C) 2015 CERN.
#
# DataCite is free software; you can redistribute it and/or modify it
# under the terms of the Revised BSD License; see LICENSE file for
# more details.

"""Errors for the DataCite API.

MDS error responses will be converted into an exception from this module.
Connection issues raises :py:exc:`datacite.errors.HttpError` while DataCite
MDS error responses raises a subclass of
:py:exc:`datacite.errors.DataCiteError`.
"""
from __future__ import absolute_import, print_function
import logging


class HttpError(Exception):
    """Exception raised when a connection problem happens."""


class DataCiteError(Exception):
    """Exception raised when the server returns a known HTTP error code.

    Known HTTP error codes include:

    * 204 No Content
    * 400 Bad Request
    * 401 Unauthorized
    * 403 Forbidden
    * 404 Not Found
    * 410 Gone (deleted)
    """

    @staticmethod
    def factory(request):
        """Factory for creating exceptions based on the HTTP error code."""
        error_code = request.code
        error_mapping = {
            '204': DataCiteNoContentError,
            '400': DataCiteBadRequestError,
            '401': DataCiteUnauthorizedError,
            '403': DataCiteForbiddenError,
            '404': DataCiteNotFoundError,
            '410': DataCiteGoneError,
            '412': DataCitePreconditionError,
        }
        Err = error_mapping.get(error_code, DataCiteServerError)
        return Err(request)


    def __init__(self, request):
        """Sets a (bit more) usefull errormessage and removes the password
        from debug data."""
        super(DataCiteError, self).__init__(
            "{request.code}: {request.data}".format(request=request))
        self.error_code = request.code
        info = request.__dict__.copy()
        info.pop("password")
        logging.debug(str(info))


class DataCiteServerError(DataCiteError):
    """An internal server error happened on the DataCite end. Try later.

    Base class for all 5XX-related HTTP error codes.
    """


class DataCiteRequestError(DataCiteError):
    """A DataCite request error. You made an invalid request.

    Base class for all 4XX-related HTTP error codes as well as 204.
    """


class DataCiteNoContentError(DataCiteRequestError):
    """DOI is known to MDS, but not resolvable.

    This might be due to handle's latency.
    """


class DataCiteBadRequestError(DataCiteRequestError):
    """Bad request error.

    Bad requests can include e.g. invalid XML, wrong domain, wrong prefix.
    Request body must be exactly two lines: DOI and URL
    One or more of the specified mime-types or urls are invalid (e.g. non
    supported mimetype, not allowed url domain, etc.)
    """


class DataCiteUnauthorizedError(DataCiteRequestError):
    """Bad username or password."""


class DataCiteForbiddenError(DataCiteRequestError):
    """Login problem, dataset belongs to another party or quota exceeded."""


class DataCiteNotFoundError(DataCiteRequestError):
    """DOI does not exist in the database."""


class DataCiteGoneError(DataCiteRequestError):
    """Requested dataset was marked inactive (using DELETE method)."""


class DataCitePreconditionError(DataCiteRequestError):
    """Metadata must be uploaded first."""
