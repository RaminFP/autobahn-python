from twisted.internet.defer import inlineCallbacks as coroutine

@coroutine
def component1_setup(reactor, session):
    # the session is joined and ready for use.
    def shutdown():
        print('backend component shutting down ..')
        session.leave()

    yield session.subscribe(shutdown, u'com.example.shutdown')
#    yield session.subscribe(u'com.example.shutdown', shutdown)

    def add2(a, b):
        print('backend component: add2()')
        return a + b

    yield session.register(add2, u'com.example.add2')
#    yield session.register(u'com.example.add2', add2)

    print('backend component ready.')

    # as we exit, this signals we are ready! the session must be kept.


@coroutine
def component2_main(reactor, session):
    # the session is joined and ready
    result = yield session.call(u'com.example.add2', 2, 3)
    print('result={}'.format(result))

    session.publish(u'com.example.shutdown')

    # as we exit, this signals we are done with the session! the session
    # can be recycled


if __name__ == '__main__':
    from autobahn.twisted.component import Component
    from twisted.internet.task import react

    #component = Component(setup=component1_setup)
    #react(component.start)


    from autobahn.twisted.component import Component, run
    transports = [
        {
            'type': 'rawsocket',
            'serializer': 'msgpack',
            'endpoint': {
                'type': 'unix',
                'path': '/tmp/cb1.sock'
            }
        },
        {
            'type': 'websocket',
            'url': 'ws://127.0.0.1:8080/ws',
            'endpoint': {
                'type': 'tcp',
                'host': '127.0.0.1',
                'port': 8080
            }
        }
    ]

    config = {
        'realm': u'realm1',
        'extra': {
            'foo': 23
        }
    }

    components = [
        Component(setup=component1_setup, transports=transports, config=config),
        Component(main=component2_main, transports=transports, config=config)
    ]

    react(run, [components])