# Mrs
# Copyright 2008-2009 Brigham Young University
#
# This file is part of Mrs.
#
# Mrs is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# Mrs is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# Mrs.  If not, see <http://www.gnu.org/licenses/>.
#
# Inquiries regarding any further use of Mrs, please contact the Copyright
# Licensing Office, Brigham Young University, 3760 HBLL, Provo, UT 84602,
# (801) 422-9339 or 422-3821, e-mail copyright@byu.edu.

"""Mrs. Twist RPC

Modified variants of Twisted's RPC clients and servers.  We add the ability to
deal with timeouts in network code and also allow RPC calls to happen from
threads outside the reactor.  We also allow RPC methods on the server to
receive the client object.

Most Mrs code uses FromThreadProxy and RequestXMLRPC.
"""

DEFAULT_TIMEOUT = 30.0

import xmlrpclib
from twisted.web import server, xmlrpc
from twisted.internet import reactor, defer
from twist import reactor_call, block

class TimeoutQueryFactory(xmlrpc._QueryFactory):
    """XMLRPC Query Factory that supports timeouts.

    We extend Twisted's QueryFactory to allow connections to timeout.
    When a timeout occurs, we'll errback to the normal deferred.
    """
    def __init__(self, *args, **kwds):
        if 'timeout' in kwds:
            self.timeout = kwds['timeout']
            del kwds['timeout']
        else:
            self.timeout = None
        self.timed_out = False
        xmlrpc._QueryFactory.__init__(self, *args, **kwds)

    def buildProtocol(self, addr):
        p = xmlrpc._QueryFactory.buildProtocol(self, addr)
        if self.timeout:
            self._timeout_call = reactor.callLater(self.timeout,
                    self._timeout_func, p)
            self.deferred.addBoth(self._cancel_timeout)
        return p

    def _timeout_func(self, p):
        """Called when a timeout occurs."""
        self.timed_out = True
        p.transport.loseConnection()
        error = defer.TimeoutError()
        self.deferred.errback(error)

    def _cancel_timeout(self, result):
        """Called when the deferred is done (either succeeded or failed)"""
        if self._timeout_call.active():
            self._timeout_call.cancel()
        return result

    # We override this so the deferred doesn't get 2 errbacks calls:
    def clientConnectionLost(self, *args):
        if not self.timed_out:
            xmlrpc._QueryFactory.clientConnectionLost(self, *args)

    clientConnectionFailed = clientConnectionLost


class TimeoutProxy(xmlrpc.Proxy):
    """XMLRPC Proxy that supports timeouts.

    We extend Twisted's Proxy to allow connections to timeout.  When a timeout
    occurs, we'll errback to the normal deferred.
    """
    queryFactory = TimeoutQueryFactory

    def __init__(self, url, timeout=DEFAULT_TIMEOUT, **kwds):
        self.timeout = timeout

        cleaned_url = rpc_url(url)
        xmlrpc.Proxy.__init__(self, cleaned_url, **kwds)

    def callRemote(self, *args):
        deferred, connector = self.powerful_call(*args)
        return deferred

    # ripped almost exactly from twisted.web.xmlrpc:
    def powerful_call(self, method, *args):
        """Call a remote RPC method and return a deferred and a connector.

        This is almost the same as callRemote in twisted.web.xmlrpc, but
        it's much more powerful because you have more control over the
        connection.
        """
        factory = self.queryFactory(
            self.path, self.host, method, self.user,
            self.password, self.allowNone, args, timeout=self.timeout)
        if self.secure:
            from twisted.internet import ssl
            connector = reactor.connectSSL(self.host, self.port or 443,
                               factory, ssl.ClientContextFactory())
        else:
            connector = reactor.connectTCP(self.host, self.port or 80, factory)
        return factory.deferred, connector

    def blocking_call(self, *args):
        """Make a blocking XML RPC call to a remote server.
        
        This can be called from another thread.
        """
        # pause between 'blocking call' and 'calling'
        deferred = self.deferred_call(*args)
        result = block(deferred)
        return result

    def deferred_call(self, *args):
        """Make a deferred XML RPC call to a remote server.
        
        This can be called from another thread.
        """
        deferred = reactor_call(self.callRemote, *args)
        return deferred


def rpc_url(urlstring):
    """Tidy a URL to be used to connect to an XML RPC server.

    >>> rpc_url('http://localhost')
    'http://localhost/RPC2'
    >>> rpc_url('http://localhost/')
    'http://localhost/RPC2'
    >>> rpc_url('http://localhost/path/to/xmlrpc')
    'http://localhost/path/to/xmlrpc'
    >>> rpc_url('localhost/path/to/xmlrpc')
    'http://localhost/path/to/xmlrpc'
    >>>
    """
    from urlparse import urlsplit, urlunsplit

    if '://' not in urlstring:
        urlstring = 'http://' + urlstring

    scheme, netloc, path, query, fragment = urlsplit(urlstring)
    if not path and not query and not fragment:
        path = '/RPC2'
    return urlunsplit((scheme, netloc, path, query, fragment))


class RequestXMLRPC(xmlrpc.XMLRPC):
    """Extension of XMLRPC which passes the client to RPC methods."""

    # We redefine the render function to send in the named parameters.
    def render(self, request):
        request.content.seek(0, 0)
        args, functionPath = xmlrpclib.loads(request.content.read())
        try:
            function = self._getFunction(functionPath)
        except Fault, f:
            self._cbRender(f, request)
        else:
            request.setHeader("content-type", "text/xml")
            if hasattr(function, "uses_request"):
                args = (request,) + args
            defer.maybeDeferred(function, *args).addErrback(
                self._ebRender
            ).addCallback(
                self._cbRender, request
            )
        return server.NOT_DONE_YET

def uses_request(f):
    """Decorate f with the attribute `uses_request`.

    When XMLRPC renders the given XML RPC method, it will pass the Request
    as the first argument.
    """
    f.uses_request = True
    return f


# vim: et sw=4 sts=4
