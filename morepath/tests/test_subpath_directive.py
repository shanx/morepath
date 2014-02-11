import morepath
from morepath import setup
from morepath.request import Response
from morepath.error import DirectiveReportError, ConflictError

from werkzeug.test import Client
import pytest


def test_subpath_implicit_variables():
    config = setup()
    app = morepath.App(testing_config=config)

    class Container(object):
        def __init__(self, container_id):
            self.container_id = container_id

    class Item(object):
        def __init__(self, parent, id):
            self.parent = parent
            self.id = id

    @app.path(model=Container, path='{container_id}')
    def get_container(container_id):
        return Container(container_id)

    @app.subpath(model=Item, path='{id}', base=Container,
                 get_base=lambda m: m.parent)
    def get_item(base, id):
        return Item(base, id)

    @app.view(model=Item)
    def default(self, request):
        return "Item %s for parent %s" % (self.id, self.parent.container_id)

    @app.view(model=Item, name='link')
    def link(self, request):
        return request.link(self)

    config.commit()

    c = Client(app, Response)

    response = c.get('/A/a')
    assert response.data == 'Item a for parent A'

    response = c.get('/B/a')
    assert response.data == 'Item a for parent B'

    response = c.get('/A/a/link')
    assert response.data == '/A/a'

    response = c.get('/B/a/link')
    assert response.data == '/B/a'


def test_subpath_explicit_variables():
    config = setup()
    app = morepath.App(testing_config=config)

    class Container(object):
        def __init__(self, id):
            self.id = id

    class Item(object):
        def __init__(self, parent, id):
            self.parent = parent
            self.id = id

    @app.path(model=Container, path='{container_id}',
              variables=lambda m: dict(container_id=m.id))
    def get_container(container_id):
        return Container(container_id)

    @app.subpath(model=Item, path='{id}', base=Container,
                 get_base=lambda m: m.parent,
                 variables=lambda m: dict(id=m.id))
    def get_item(base, id):
        return Item(base, id)

    @app.view(model=Item)
    def default(self, request):
        return "Item %s for parent %s" % (self.id, self.parent.id)

    @app.view(model=Item, name='link')
    def link(self, request):
        return request.link(self)

    config.commit()

    c = Client(app, Response)

    response = c.get('/A/a')
    assert response.data == 'Item a for parent A'

    response = c.get('/B/a')
    assert response.data == 'Item a for parent B'

    response = c.get('/A/a/link')
    assert response.data == '/A/a'

    response = c.get('/B/a/link')
    assert response.data == '/B/a'


def test_subpath_converters():
    config = setup()
    app = morepath.App(testing_config=config)

    class Container(object):
        def __init__(self, container_id):
            self.container_id = container_id

    class Item(object):
        def __init__(self, parent, id):
            self.parent = parent
            self.id = id

    @app.path(model=Container, path='{container_id}')
    def get_container(container_id=0):
        return Container(container_id)

    @app.subpath(model=Item, path='{id}', base=Container,
                 get_base=lambda m: m.parent)
    def get_item(base, id=0):
        return Item(base, id)

    @app.view(model=Item)
    def default(self, request):
        return "Item %r for parent %r" % (self.id, self.parent.container_id)

    @app.view(model=Item, name='link')
    def link(self, request):
        return request.link(self)

    config.commit()

    c = Client(app, Response)

    response = c.get('/1/2')
    assert response.data == 'Item 2 for parent 1'

    response = c.get('/2/1')
    assert response.data == 'Item 1 for parent 2'

    response = c.get('/1/2/link')
    assert response.data == '/1/2'

    response = c.get('/2/1/link')
    assert response.data == '/2/1'


def test_subpath_url_parameters():
    config = setup()
    app = morepath.App(testing_config=config)

    class Container(object):
        def __init__(self, container_id, a):
            self.container_id = container_id
            self.a = a

    class Item(object):
        def __init__(self, parent, id, b):
            self.parent = parent
            self.id = id
            self.b = b

    @app.path(model=Container, path='{container_id}')
    def get_container(container_id, a):
        return Container(container_id, a)

    @app.subpath(model=Item, path='{id}', base=Container,
                 get_base=lambda m: m.parent)
    def get_item(base, id, b):
        return Item(base, id, b)

    @app.view(model=Item)
    def default(self, request):
        return "a: %s b: %s" % (self.parent.a, self.b)

    @app.view(model=Item, name='link')
    def link(self, request):
        return request.link(self)

    config.commit()

    c = Client(app, Response)

    response = c.get('/A/a?a=foo&b=bar')
    assert response.data == 'a: foo b: bar'

    response = c.get('/A/a')
    assert response.data == 'a: None b: None'

    response = c.get('/A/a/link?a=foo&b=bar')
    assert response.data == '/A/a?a=foo&b=bar'

    response = c.get('/A/a/link')
    assert response.data == '/A/a'

    response = c.get('A/a?base=blah')
    assert response.data == 'a: None b: None'


def test_subpath_url_parameters_converter():
    config = setup()
    app = morepath.App(testing_config=config)

    class Container(object):
        def __init__(self, container_id, a):
            self.container_id = container_id
            self.a = a

    class Item(object):
        def __init__(self, parent, id, b):
            self.parent = parent
            self.id = id
            self.b = b

    @app.path(model=Container, path='{container_id}')
    def get_container(container_id, a=0):
        return Container(container_id, a)

    @app.subpath(model=Item, path='{id}', base=Container,
                 get_base=lambda m: m.parent)
    def get_item(base, id, b=0):
        return Item(base, id, b)

    @app.view(model=Item)
    def default(self, request):
        return "a: %r b: %r" % (self.parent.a, self.b)

    @app.view(model=Item, name='link')
    def link(self, request):
        return request.link(self)

    config.commit()

    c = Client(app, Response)

    response = c.get('/A/a?a=1&b=2')
    assert response.data == 'a: 1 b: 2'

    response = c.get('/A/a')
    assert response.data == 'a: 0 b: 0'

    response = c.get('/A/a/link?a=1&b=2')
    assert response.data == '/A/a?a=1&b=2'

    response = c.get('/A/a/link')
    assert response.data == '/A/a?a=0&b=0'


def test_subpath_multiple_base():
    config = setup()
    app = morepath.App(testing_config=config)

    class Container(object):
        def __init__(self, container_id):
            self.container_id = container_id

    class ContainerA(Container):
        pass

    class ContainerB(Container):
        pass

    class Item(object):
        def __init__(self, parent, id):
            self.parent = parent
            self.id = id

    @app.path(model=ContainerA, path='a/{container_id}')
    def get_container_a(container_id):
        return ContainerA(container_id)

    @app.path(model=ContainerB, path='b/{container_id}')
    def get_container_b(container_id):
        return ContainerB(container_id)

    @app.subpath(model=Item, path='{id}', base=Container,
                 get_base=lambda m: m.parent)
    def get_item(base, id):
        return Item(base, id)


    @app.view(model=Item)
    def default(self, request):
        return "Item %s for parent %s %r" % (self.id, self.parent.container_id,
                                             type(self.parent))

    @app.view(model=Item, name='link')
    def link(self, request):
        return request.link(self)

    config.commit()

    c = Client(app, Response)

    response = c.get('a/T/t')
    assert response.data == (
        "Item t for parent T "
        "<class 'morepath.tests.test_subpath_directive.ContainerA'>")

    response = c.get('b/T/t')
    assert response.data == (
        "Item t for parent T "
        "<class 'morepath.tests.test_subpath_directive.ContainerB'>")

    response = c.get('a/T/t/link')
    assert response.data == '/a/T/t'

    response = c.get('b/T/t/link')
    assert response.data == '/b/T/t'


def test_subpath_subclass_so_not_found():
    config = setup()
    app = morepath.App(testing_config=config)

    class Container(object):
        def __init__(self, container_id):
            self.container_id = container_id

    class ContainerA(Container):
        pass

    class Item(object):
        def __init__(self, parent, id):
            self.parent = parent
            self.id = id

    @app.path(model=Container, path='a/{container_id}')
    def get_container(container_id):
        return Container(container_id)

    @app.subpath(model=Item, path='{id}', base=ContainerA,
                 get_base=lambda m: m.parent)
    def get_item(base, id):
        return Item(base, id)

    @app.view(model=Item)
    def default(self, request):
        return "Item %s for parent %s %r" % (self.id, self.parent.container_id,
                                             type(self.parent))

    config.commit()

    c = Client(app, Response)

    response = c.get('a/T/t')
    assert response.status == '404 NOT FOUND'


def test_subpath_url_parameters_required():
    config = setup()
    app = morepath.App(testing_config=config)

    class Container(object):
        def __init__(self, container_id, a):
            self.container_id = container_id
            self.a = a

    class Item(object):
        def __init__(self, parent, id, b):
            self.parent = parent
            self.id = id
            self.b = b

    @app.path(model=Container, path='{container_id}', required=['a'])
    def get_container(container_id, a):
        return Container(container_id, a)

    @app.subpath(model=Item, path='{id}', base=Container,
                 get_base=lambda m: m.parent, required=['b'])
    def get_item(base, id, b):
        return Item(base, id, b)

    @app.view(model=Item)
    def default(self, request):
        return "a: %s b: %s" % (self.parent.a, self.b)

    @app.view(model=Item, name='link')
    def link(self, request):
        return request.link(self)

    config.commit()

    c = Client(app, Response)

    response = c.get('/A/a?a=foo&b=bar')
    assert response.data == 'a: foo b: bar'

    response = c.get('/A/a?b=bar')
    assert response.status == '400 BAD REQUEST'

    response = c.get('/A/a?a=foo')
    assert response.status == '400 BAD REQUEST'


def test_multiple_subpaths_not_conflicting():
    config = setup()
    app = morepath.App(testing_config=config)

    class Container(object):
        def __init__(self, container_id):
            self.container_id = container_id

    class ContainerA(Container):
        pass

    class ContainerB(Container):
        pass

    class Item(object):
        def __init__(self, parent, id):
            self.parent = parent
            self.id = id

    class ItemA(Item):
        pass

    class ItemB(Item):
        pass

    @app.path(model=ContainerA, path='a/{container_id}')
    def get_container_a(container_id):
        return ContainerA(container_id)

    @app.path(model=ContainerB, path='b/{container_id}')
    def get_container_b(container_id):
        return ContainerB(container_id)

    @app.subpath(model=ItemA, path='{id}', base=ContainerA,
                 get_base=lambda m: m.parent)
    def get_item(base, id):
        return ItemA(base, id)

    @app.subpath(model=ItemB, path='{id}', base=ContainerB,
                 get_base=lambda m: m.parent)
    def get_item(base, id):
        return ItemB(base, id)

    config.commit()


# XXX this fails because the subpath action is in the same action group
# as the path action so that path conflicts can be detected, *but* as
# a result path actions are not executed before subpath actions, so in this
# test there is no detection of the paths.
# this whole situation should probably be rewritten to use sub directives
# anyway, so that there are only path directives in the end
@pytest.mark.xfail
def test_subpath_conflict_with_path():
    config = setup()
    app = morepath.App(testing_config=config)

    class Container(object):
        def __init__(self, container_id):
            self.container_id = container_id

    class Item(object):
        def __init__(self, parent, id):
            self.parent = parent
            self.id = id

    class Model(object):
        pass

    @app.path(model=Container, path='{container_id}')
    def get_container(container_id):
        return Container(container_id)

    @app.subpath(model=Item, path='{id}', base=Container,
                 get_base=lambda m: m.parent)
    def get_item(base, id):
        return Item(base, id)

    @app.path(model=Model, path='{container_id}/{id}')
    def get_model(container_id, id):
        return Model()

    with pytest.raises(ConflictError):
        config.commit()

# what if base variable same as sub variable? should be error

# what if container cannot be found, i.e get_base returns None

# prepare get_base, base checks

# cannot make subpath of subpath

# conflict between subpath and path?
