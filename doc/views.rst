Views
=====

Introduction
------------

Morepath views are looked up through the URL path, but not through the
routing procedure. Routing stops at models. Then the last segment of
the path is taken to identify the view by name.

Named views
-----------

Let's examine a path::

  /documents/1/edit

If there's a model like this::

  @app.path(model=Document, path='/documents/{id}')
  def get_document(id):
      return query_for_document(id)

then ``/edit`` identifies a view named ``edit`` on the ``Document`` model (or
on one of its base classes). Here's how we define it::

  @app.view(model=Document, name='edit')
  def document_edit(self, request):
      return "edit view on model: %s" % self.id

Default views
-------------

Let's examine this path::

  /documents/1

If the model is published on the path ``/documents/{id}``, then this is
a path to the *default* view of the model. Here's how that view is
defined::

  @app.view(model=Document)
  def document_default(self, request):
      return "default view on model: %s" % self.id

The default view is the view that gets triggered if there is no
special path segment in the URL that indicates a specific view. The
default view has as its name the empty string ``""``, so this
registration is the equivalent of the one above::

  @app.view(model=Document, name="")
  def document_default(self, request):
      return "default view on model: %s" % self.id

Generic views
-------------

Generic views in Morepath are nothing special: the thing that makes
them generic is that their model is a base class, and inheritance does
the rest. Let's see how that works.

What if we want to have a view that works for any model that
implements a certain API? Let's imagine we have a ``Collection`` model::

  class Collection(object):
     def __init__(self, offset, limit):
         self.offset = offset
         self.limit = limit

     def query(self):
         raise NotImplementedError

A ``Collection`` represents a collection of objects, which can be
ordered somehow. We restrict the objects we actually get by offset and
limit. With offset 100 and limit 10, we get objects 100 through 109.

``Collection`` is a base class, so we don't actually implement how to
do a query. That's up to the subclasses. We do specify that query is
supposed to return objects that have an ``id`` attribute.

We can create a view to this abstract collection that displays the
ids of the things in it in a comma separated list::

  @app.view(model=Collection)
  def collection_default(self, request):
      return ", ".join([str(item.id) for item in self.query()])

This view is generic: it works for any kind of collection.

We can now create a concrete collection that fulfills the requirements::

  class Item(object):
     def __init__(self, id):
         self.id = id

  class MyCollection(Collection):
     def query(self):
         return [Item(str(i)) for i in
                 range(self.offset, self.offset + self.limit)

When we now publish the concrete ``MyCollection`` on some URL::

  @app.path(model=MyCollection, path='my_collection')
  def get_my_collection():
      return MyCollection()

it automatically gains a default view for it that represents the ids
in it as a comma separated list. So the view ``collection_default`` is
*generic*.

Details
-------

The decorator :meth:`morepath.AppBase.view` (``@app.view``) takes two
arguments here, ``model``, which is the class of the model the view is
representing, and ``name``, which is the name of the view in the URL
path.

The ``@app.view`` decorator decorates a function that takes two arguments:
a ``self`` and a ``request``.

The ``self`` object is the model that's being viewed, i.e. the one
found by the ``get_document`` function. It is going to be an instance
of the class given by the ``model`` parameter.

The ``request`` object is an instance of :class:`morepath.Request`,
which in turn is a special kind of
:class:`webob.request.BaseRequest`. You can get request information
from it like arguments or form data, and it also exposes a few special
methods, such as :meth:`morepath.Request.link`.

The ``@app.path`` and ``@app.view`` decorators are associated by
indirectly their ``model`` parameters: the view works for a given
model path if the ``model`` parameter is the same, or if the view is
associated with a base class of the model exposed by the
``@app.path`` decorator.

Ambiguity between path and view
-------------------------------

Let's examine these simple paths in an application::

  /folder
  /folder/{name}

``/folder`` shows an overview of the items in it. ``/folder/{name}``
is a way to get to an individual item.

This means::

  /folder/some_item

is a path if there is an item in the folder with the name
``some_item``.

Now what if we also want to have a path that allows you to edit the
folder? It'd be natural to spell it like this::

  /folder/edit

i.e. there is a path ``/folder`` with a view ``edit``.

But now we have a problem: how does Morepath know that ``edit`` is a
view and not a named item in the folder? The answer is that it
doesn't. You cannot reach the view this way.

Instead we have to make it explicit in the path that we want a view with
a ``+`` character::

  /folder/+edit

Now Morepath won't try to interpret ``+edit`` as a named item in the
folder, but instead looks up the view.

Any view can be addressed not just by name but also by its name with a
``+`` prefix. To generate a link to a name with a ``+`` prefix you can
use the prefix as well, so you can write::

  request.link(my_folder, '+edit')

render
------

By default ``@app.view`` returns either a :class:`morepath.Response`
object or a string that gets turned into a response. The
``content-type`` of the response is not set. For a HTML response you
want a view that sets the ``content-type`` to ``text/html``. You can
do this by passing a ``render`` parameter to the ``@app.view`` decorator::

  @app.view(class=Document, render=morepath.render_html)
  def document_default(self, request):
      return "<p>Some html</p>"

:func:`morepath.render_html` is a very simple function::

  def render_html(content):
      response = morepath.Response(content)
      response.content_type = 'text/html'
      return response

You can define your own ``render`` functions; they just need to take
some content (any object, in this case its a string), and return a
``Response`` object.

Another render function is :func:`morepath.render_json`. Here it is::

  import json

  def render_json(content):
      response = morepath.Response(json.dumps(content))
      response.content_type = 'application/json'
      return response

We'd use it like this::

  @app.view(class=Document, render=morepath.render_json)
  def document_default(self, request):
      return {'my': 'json'}

HTML views and JSON views are so common we have special shortcut decorators:

* ``@app.html`` (:meth:`morepath.AppBase.html`)

* ``@app.json`` (:meth:`morepath.AppBase.json`)

Here's how you use them::

  @app.html(class=Document)
  def document_default(self, request):
      return "<p>Some html</p>"

  @app.json(class=Document)
  def document_default(self, request):
      return {'my': 'json'}

Permissions
-----------

We can protect a view using a ``permission``. A permission is any
Python class::

  class Edit(object):
      pass

The class doesn't do anything; it's just a marker for permission.

You can use such a class with a view::

  @app.view(model=Document, name='edit', permission=Edit)
  def document_edit(self, request):
      return 'edit document'

You can define which users have what permission on which models by using
the :meth:`morepath.AppBase.permission` decorator. To learn more,
read :doc:`security`.

Manipulating the response
-------------------------

Sometimes you want to do things to the response specific to the view,
so that you cannot do it in a ``render`` function. Let's say you want
to add a cookie using :meth:`webob.Response.set_cookie`. You don't
have access to the response object in the view, as it has not been
created yet. It is only created *after* the view has returned. We can
register a callback function to be called after the view is done and
the response is ready using the :meth:`morepath.Request.after`
decorator. Here's how::

  @app.view(model=Document)
  def document_default(self, request):
      @request.after
      def manipulate_response(response):
          response.set_cookie('my_cookie', 'cookie_data')
      return "document default"


request_method
--------------

By default, a view only answers to a ``GET`` request: it doesn't
handle other request methods like ``POST`` or ``PUT`` or ``DELETE``. To
write a view that handles another request method you need to be explicit and
pass in the ``request_method`` parameter::

  @app.view(model=Document, name='edit', request_method='POST')
  def document_edit(self, request):
      return "edit view on model: %s" % self.id

Now we have a view that handles ``POST``. Normally you cannot have
multiple views for the same document with the same name: the Morepath
configuration engine rejects that. But you can if you make sure they
each have a different request method::

  @app.view(model=Document, name='edit', request_method='GET')
  def document_edit_get(self, request):
      return "get edit view on model: %s" % self.id

  @app.view(model=Document, name='edit', request_method='POST')
  def document_edit_post(self, request):
      return "post edit view on model: %s" % self.id

Predicates
----------

The ``name`` and ``request_method`` arguments on the ``@app.view``
decorator are examples of *view predicates*. You can add new ones by
using the :meth:`morepath.AppBase.predicate` decorator.

Let's say we have a view that we only want to kick in when a certain
request header is set to something::

  @app.predicate(name='something', order=100, default=None)
  def get_something_header(self, request):
      return request.headers.get('Something')

We can use any information in the request and model to construct the
predicate. Now you can use it to make a view that only kicks in when
the `Something`` header is ``special``::

  @app.view(model=Document, something='special')
  def document_default(self, request):
      return "Only if request header Something is set to special."

If you have a predicate and you *don't* use it in a ``@app.view``, or
set it to ``None``, the view works for the ``default`` value for that
predicate. If you don't care what the predicate is and want the view
to match for any value, you can pass in the special sentinel
:data:`morepath.ANY`. The ``default`` parameter is also used when
rendering a view using :meth:`morepath.Request.view` and you don't
pass in a particular value for that predicate.

The ``order`` parameter for the predicate determines which predicates
match more strongly than another; lower order matches more
strongly. If there are two view candidates that both match the
predicates for a request and model, the strongest match is picked.


request.view
------------

It is often useful to be able to compose a view from other
views. Let's look at our earlier ``Collection`` example again. What if
we wanted a generic view for our collection that included the views
for its content? This is easiest demonstrated using a JSON view::

  @app.json(model=Collection)
  def collection_default(self, request):
      return [request.view(item) for item in self.query()]

Here we have a view that for all items returned by query includes its
view in the resulting list. Since this view is generic, we cannot
refer to a *specific* view function here; we just want to use the
view function appropriate to whatever ``item`` may be. For this
we can use :meth:`morepath.Request.view`.

We could for instance have a particular item with a view like this::

  @app.json(model=ParticularItem)
  def particular_item_default(self, request):
      return {'id': self.id}

And then the result of ``collection_default`` is something like::

  [{'id': 1}, {'id': 2}]

but if we have a some other item with a view like this::

  @app.json(model=SomeOtherItem)
  def some_other_item_default(self, request):
      return self.name

where the name is some string like ``alpha`` or ``beta``, then the
output of ``collection_default`` is something like::

  ['alpha', 'beta']

So ``request.view`` can make it much easier to construct composed JSON
results where JSON representations are only loosely coupled.

You can also use ``predicates`` in ``request.view``. Here we get the
view with the ``name`` ``"edit"`` and the ``request_predicate`` ``"POST"``::

  request.view(item, name="edit", request_predicate="POST")

Exception views
---------------

Sometimes your application raises an exception. This can either be a
HTTP exception, for instance when the user goes to a URL that does not
exist, or an arbitrary exception raised by the application.

HTTP exceptions are by default rendered in the standard WebOb way,
which includes some text to describe Not Found, etc. Other exceptions
are normally caught by the web server and result in a HTTP 500 error
(internal server error).

You may instead want to customize what these exceptions look like. You
can do so by declaring a view using the exception class as the
model. Here's how you make a custom 404 Not Found::

  from webob.exc import HTTPNotFound

  @app.view(model=HTTPNotFound)
  def notfound_custom(self, request):
      def set_status_code(response):
          response.status_code = self.code # pass along 404
      request.after(set_status_code)
      return "My custom not found!"

We have to add the ``set_status_code`` to make sure the response is
still a 404; otherwise we change the 404 to a 200 Ok! This shows that
``self`` is indeed an instance of ``HTTPNotFound`` and we can access
its ``code`` attribute.

Your application may also define its own custom exceptions that have
a meaning particular to the application. You can create custom views for
those as well::

  class MyException(Exception):
      pass

  @app.view(model=MyException)
  def myexception_default(self, request):
       return "My exception"

Without an exception view for ``MyException`` any view code that raises
``MyException`` would bubble all the way up to the WSGI server and
a 500 Internal Server Error is generated.

But with the view for ``MyException`` in place, whenever
``MyException`` is raised you get the special view instead.
