Title: Managing Context Metadata in Django-PGHistory: Solving the Persistence Problem
Date: 2025-04-02
Modified: 2025-04-02
Category:  Django Development, Python Best Practices, Database & ORM, Audit & Compliance, Code Architecture
Tags:  django, programming, python, django-pghistory, diversio, audit-trails, context-management, django-middleware, python-contextvars, database-tracking, django-models, code-patterns, postgresql, django-orm, debugging
Slug: managing-context-metadata-django-pghistory-solving-persistence-problem
Authors: Ashwini Chaudhary
Summary: Learn how to prevent metadata leakage between contexts in django-pghistory for cleaner, more accurate audit trails in your Django applications.

In this post you would learn how `pghistory.context` works and some of its gotchas that we faced at Diversio(thanks to [Amal Raj B R](https://github.com/amalrajdiversio) who identified this) and how we adjusted our approach to avoid saving context metadata that is not relevant to the current business logic but is being carried over from a parent context.

### What is `pghistory.context`?

`pghistory.context` is a decorator and a function that is part of the fantastic [`django-pghistory`](https://django-pghistory.readthedocs.io/en/stable/) project. I would cover how we use `django-pghistory` in a separate post.

When `django-pghistory` is keeping track of changes to Django models, there are several instances where we want to include additional information with the tracked changes. This is where `pghistory.context` comes into picture to easily capture such metadata.

We are making use of [`pghistory.middleware.HistoryMiddleware`](https://django-pghistory.readthedocs.io/en/3.5.5/context/?h=historymiddleware#middleware) to collect basic fields that we want to store with each change. This includes IP address, URL and the User who made the request. Some of this is done by the [library itself](https://github.com/AmbitionEng/django-pghistory/blob/e991e610ddfc393aa7e3f39945627485e0d7bc60/pghistory/middleware.py#L42) (comments removed for brevity) as seen in the code below.


```python
class HistoryMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def get_context(self, request) -> Dict[str, Any]:
        user = (
            request.user._meta.pk.get_db_prep_value(request.user.pk, connection)
            if hasattr(request, "user") and hasattr(request.user, "_meta")
            else None
        )
        return {"user": user, "url": request.path}

    def __call__(self, request):
        if request.method in config.middleware_methods():
            with pghistory.context(**self.get_context(request)):
                if isinstance(request, DjangoWSGIRequest):
                    request.__class__ = WSGIRequest
                elif isinstance(request, DjangoASGIRequest):
                    request.__class__ = ASGIRequest

                return self.get_response(request)
        else:
            return self.get_response(request)
```

An interesting thing happening here is that the request-response is wrapped in the `pghistory.context` context manager. That means all call to `pghistory.context` anywhere in views would keep on accumulating the metadata that `pghistory.context` is getting. This is a powerful pattern for audit tracking without having to manually pass context through your application code. Every database change automatically gets tagged with "who" (user) and "where" (URL) the change happened.

But this also has an unintended effect, let's use an example to explain it([gist](https://gist.github.com/ashwch/1fc98f3f76860b95936bf278ba38dbba))

```python

In [1]: import pghistory
   ...:
   ...: with pghistory.context(url="/foo/bar", user="bugs-bunny") as pg:
   ...:     print(f"Level 1-1: {pg.metadata}")
   ...:
   ...:     with pghistory.context(foo="bar"):
   ...:         print(f"Level 2-1: {pg.metadata}")
   ...:         with pghistory.context(spam="eggs"):
   ...:             print(f"Level 3-1: {pg.metadata}")
   ...:
   ...:         with pghistory.context(hannah="montana"):
   ...:             print(f"Level 3-2: {pg.metadata}")
   ...:             with pghistory.context(timon="pumba"):
   ...:                 print(f"Level 4-1: {pg.metadata}")
   ...:
   ...:     print(f"Level 1-2: {pg.metadata}")
   ...:     with pghistory.context(monty="python"):
   ...:         print(f"Level 2-2: {pg.metadata}")
   ...:
   ...:
   ...: with pghistory.context(guido="bdfl") as pg_2:
   ...:     print(f"Level 1-4: {pg_2.metadata}")
   ...:
   ...: print(f"Level 1-5: {pg.metadata}")
   ...: print(f"Level 1-6: {pg_2.metadata}")
   ...:

Level 1-1: {'url': '/foo/bar', 'user': 'bugs-bunny'}
Level 2-1: {'url': '/foo/bar', 'user': 'bugs-bunny', 'foo': 'bar'}
Level 3-1: {'url': '/foo/bar', 'user': 'bugs-bunny', 'foo': 'bar', 'spam': 'eggs'}
Level 3-2: {'url': '/foo/bar', 'user': 'bugs-bunny', 'foo': 'bar', 'spam': 'eggs', 'hannah': 'montana'}
Level 4-1: {'url': '/foo/bar', 'user': 'bugs-bunny', 'foo': 'bar', 'spam': 'eggs', 'hannah': 'montana', 'timon': 'pumba'}
Level 1-2: {'url': '/foo/bar', 'user': 'bugs-bunny', 'foo': 'bar', 'spam': 'eggs', 'hannah': 'montana', 'timon': 'pumba'}
Level 2-2: {'url': '/foo/bar', 'user': 'bugs-bunny', 'foo': 'bar', 'spam': 'eggs', 'hannah': 'montana', 'timon': 'pumba', 'monty': 'python'}
Level 1-4: {'url': '/foo/bar', 'user': 'bugs-bunny', 'foo': 'bar', 'spam': 'eggs', 'hannah': 'montana', 'timon': 'pumba', 'monty': 'python', 'guido': 'bdfl'}
Level 1-5: {'url': '/foo/bar', 'user': 'bugs-bunny', 'foo': 'bar', 'spam': 'eggs', 'hannah': 'montana', 'timon': 'pumba', 'monty': 'python', 'guido': 'bdfl'}
Level 1-6: {'url': '/foo/bar', 'user': 'bugs-bunny', 'foo': 'bar', 'spam': 'eggs', 'hannah': 'montana', 'timon': 'pumba', 'monty': 'python', 'guido': 'bdfl'}
```

Here as we can see, regardless of which level of context manager we are in, or even if it's a completely new context manager, the keys keep on accumulating. 

This is not something we want because there are multiple places in our business logic where we want to track different changes with different metadata instead of using the metadata from previous calls to `pghistory.context`.

```python

def my_view(request):
    if request.method == "POST":
        with pghistory.context(type="POST"):
            # Perform some action
            # save audit log
            pass

    elif request.method == "GET":
        with pghistory.context(type="GET"):
            # Perform some action
            # save audit log
            pass

    # External API call
    # Update an internal state
    with pghistory.context(type="EXTERNAL"):
        # Perform some action
        # save audit log
        pass

    # Another action that updates the internal state
    with pghistory.context(type="INTERNAL"):
        # Perform some action
        # save audit log
        pass

```

Now for the above, the ideal behaviour we want is that every audit log should get the keys that were included in its context, but not the ones added by other contexts, apart from the common keys coming from the middleware.

### Solution

We want a solution where we want the keys added by the middleware to persist, but we do not want the keys added inside the views to persist, and every time we exit from a context the keys should be removed from the metadata.

For this the solution was to override the default implementation of [`pghistory.context`](https://github.com/AmbitionEng/django-pghistory/blob/e991e610ddfc393aa7e3f39945627485e0d7bc60/pghistory/runtime.py#L115). Let's say the custom implementation is called `custom_pg_context`, then we want the output of the program we had earlier on to be:

The key change we made was introducing a new parameter called `persist`. When set to `True` (the default), metadata keys will persist across nested contexts and remain available to other contexts. When set to `False`, metadata keys added in the current context will automatically be removed upon exiting the context, ensuring they don't leak into subsequent operations.

Here only want the `user` and `url` to persist (later on `timon` as well)

```bash

Level 1-1: {'url': '/foo/bar', 'user': 'bugs-bunny'}
Level 2-1: {'url': '/foo/bar', 'user': 'bugs-bunny', 'foo': 'bar'}
Level 3-1: {'url': '/foo/bar', 'user': 'bugs-bunny', 'foo': 'bar', 'spam': 'eggs'}
# Notice the lack of 'spam': 'eggs' in 3-2
Level 3-2: {'url': '/foo/bar', 'user': 'bugs-bunny', 'foo': 'bar', 'hannah': 'montana'}
Level 4-1: {'url': '/foo/bar', 'user': 'bugs-bunny', 'foo': 'bar', 'hannah': 'montana', 'timon': 'pumba'}
# Everything has been removed when we hit 1-2 except for url and user
# and timon, because these we want to persist.
Level 1-2: {'url': '/foo/bar', 'user': 'bugs-bunny', 'timon': 'pumba'}
Level 2-2: {'url': '/foo/bar', 'user': 'bugs-bunny', 'timon': 'pumba', 'monty': 'python'}
Level 1-4: {'url': '/foo/bar', 'user': 'bugs-bunny', 'timon': 'pumba', 'guido': 'bdfl'}
Level 1-5: {'url': '/foo/bar', 'user': 'bugs-bunny', 'timon': 'pumba', 'guido': 'bdfl'}
Level 1-6: {'url': '/foo/bar', 'user': 'bugs-bunny', 'timon': 'pumba', 'guido': 'bdfl'}
```


Now this is what the code looks like now([gist](https://gist.github.com/ashwch/87a32121b80e41446260be0b3a89bf7e)):

```python

from __future__ import annotations

from contextvars import ContextVar
from copy import deepcopy

import pghistory

context_stack: ContextVar[list[custom_pg_context]] = ContextVar(
    "context_stack", default=[]
)


class custom_pg_context(pghistory.context):
    def __init__(self, *, persist: bool = True, **metadata):
        self._persist = persist
        self._local_metadata = deepcopy(metadata)
        self.token = context_stack.set(context_stack.get() + [self])
        super().__init__(**metadata)

    def __enter__(self):
        return_value = super().__enter__()
        self._tracker_value = return_value
        return return_value

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if not self._persist:
                # Removing keys added in this context from parent contexts
                stack = context_stack.get()[:-1]
                for parent in stack:
                    if parent._tracker_value:
                        for key in self._local_metadata:
                            parent._tracker_value.metadata.pop(key, None)

            return super().__exit__(exc_type, exc_val, exc_tb)
        finally:
            current_stack = context_stack.get()
            if current_stack and current_stack[-1] is self:
                context_stack.set(current_stack[:-1])

    @staticmethod
    def get_parent_context() -> custom_pg_context | None:
        stack = context_stack.get()
        return stack[-2] if len(stack) > 1 else None


with custom_pg_context(url="/foo/bar", user="bugs-bunny", persist=True) as pg:
    print(f"Level 1-1: {pg.metadata}")

    with custom_pg_context(foo="bar", persist=False):
        print(f"Level 2-1: {pg.metadata}")
        with custom_pg_context(spam="eggs", persist=False):
            print(f"Level 3-1: {pg.metadata}")

        with custom_pg_context(hannah="montana", persist=False):
            print(f"Level 3-2: {pg.metadata}")
            with custom_pg_context(timon="pumba", persist=True):
                print(f"Level 4-1: {pg.metadata}")

    print(f"Level 1-2: {pg.metadata}")
    with custom_pg_context(monty="python", persist=False):
        print(f"Level 2-2: {pg.metadata}")


with custom_pg_context(guido="bdfl") as pg_2:
    print(f"Level 1-4: {pg_2.metadata}")

print(f"Level 1-5: {pg.metadata}")
print(f"Level 1-6: {pg_2.metadata}")
```


#### What's happening here?

1. We are making use of `ContextVar` from the [`contextvars`](https://docs.python.org/3/library/contextvars.html) module to maintain a stack of all contexts and identify parents and children of any particular context we are in.
2. We create a custom class `custom_pg_context` that inherits from `pghistory.context`, with an additional `persist` parameter that defaults to `True`.
3. In the constructor, we keep a copy of the local metadata and add ourselves to the context stack.
4. During `__enter__`, we store the tracker object returned by the parent class for later use.
5. The magic happens in `__exit__`: 
   - If `persist=False`, we look through all parent contexts in the stack and remove any keys from our local metadata.
   - This ensures that temporary metadata isn't carried forward to other contexts.
   - Keys with `persist=True` (like our `user`, `url`, and `timon`) remain in the metadata across all contexts.
6. We also maintain proper stack management by removing our context from the stack when exiting.
7. The `get_parent_context()` static method provides a way to access the parent context if needed.

This implementation solves our problem by allowing us to control which metadata persists across different parts of our application. We can use `persist=True` for global tracking (like user and URL from middleware) and `persist=False` for local, context-specific metadata that shouldn't leak into other operations.

### Using the Custom Context in Django

To implement this in a Django project, you would:

1. Create a new module (e.g., `core/context.py`) with the `custom_pg_context` implementation.
2. Update your middleware to use this custom context manager instead of the default one:

```python
from core.context import custom_pg_context

class CustomHistoryMiddleware(HistoryMiddleware):
    def __call__(self, request):
        if request.method in config.middleware_methods():
            # Use our custom context manager with persist=True
            with custom_pg_context(persist=True, **self.get_context(request)):
                if isinstance(request, DjangoWSGIRequest):
                    request.__class__ = WSGIRequest
                elif isinstance(request, DjangoASGIRequest):
                    request.__class__ = ASGIRequest

                return self.get_response(request)
        else:
            return self.get_response(request)
```

3. In your views and services, use the custom context manager with `persist=False` for operation-specific metadata:

```python
from core.context import custom_pg_context

def my_view(request):
    # Use persist=False for view-specific metadata
    with custom_pg_context(operation="view_details", persist=False):
        # Perform database operations
        item.save()  # This will include the operation metadata
        
    # Start a new context without leaking previous metadata
    with custom_pg_context(operation="update_related", persist=False):
        # Perform more operations
        related_item.save()  # Only includes this operation's metadata
```

### Performance Considerations

One thing to note is that this approach does add some overhead, especially with deeply nested contexts. For most applications, this overhead is negligible compared to database operations, but it's something to keep in mind for performance-critical code paths.

If you're concerned about performance, you could optimize the implementation further:

1. Use a more efficient data structure for the context stack
2. Limit the depth of context nesting
3. Consider using a profiler to identify bottlenecks in your specific use case

### Conclusion

By extending `pghistory.context` with our custom implementation, we've solved the metadata leakage problem while maintaining the convenience of the context-based tracking system. This approach gives us fine-grained control over which metadata persists across different operations, making our audit logs more accurate and meaningful.

In a real-world Django application, this means we can add specific tracking metadata to different operations without polluting the audit trail of unrelated operations, while still maintaining the global context from middleware.
