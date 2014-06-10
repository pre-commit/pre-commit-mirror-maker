# pylint:disable=import-error,undefined-variable,unused-import

PY2 = str is bytes
PY3 = str is not bytes

if PY2:  # pragma: no cover (py2 only)
    import xmlrpclib  # noqa
    text = unicode  # noqa
else:  # pragma: no cover (py3 only)
    import xmlrpc.client as xmlrpclib  # noqa
    text = str
