Tests
=====

Here, we cover all information about how to write tests for this project.

AAA Pattern
-----------

Software testing is a process across the entire life cycle of software development to ensure the quality of a system under test.
Among others, this incorporates writing tests, which mainly aims at finding bugs introduced during the development, preventing bugs, and gaining confidence about the software quality.

One of the most important requirements in writing tests is to keep tests readable and maintainable.
The specific goal is to avoid flaky, brittle, and expensive tests.

To achieve this goal, we introduce the `Arrange-Act-Assert Pattern <https://jamescooke.info/arrange-act-assert-pattern-for-python-developers.html>`_ for writing tests, which helps to structure test code and keep it clean.
The pattern suggests dividing test methods into three sections: arrange, act, assert.
Each one of them is only responsible for the part in which they are named after.

.. note:: With the introduction of the AAA-Pattern, we expect that whenever the configuration network is extended, new tests will be written to verify the new functionality.

In this section, we describe the guidelines to write tests with using the Arrange-Act-Assert Pattern.

Definition of the test method
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* name your method something descriptive because the function name will be
  shown when the test fails
* good test method names can make docstrings redundant in simple tests

Docstrings
^^^^^^^^^^

Docstrings are not a part of the AAA pattern, but can help to describe the behavior under test.
Consider if the tests needs one.

* optional short single line
* follow the existing docstring style
* state clearly what the expected behavior is: “X does Y when Z” or “Given Z, then X does Y”

Arrange
^^^^^^^

The block of code sets up the conditions for the test action.

.. code:: python

   nodes = [A, B, C, D]

* if arrangement is to complex: extract arrangement code into a fixture

Act
^^^

The block where the action is taken.

.. code:: python

   result = nodes.reverse()

* when there is no result from the action, capture result and :code:`assert result is None`
* if you struggle to write the action, then consider extracting some of the code into the arrangement
* action can be wrapped in :code:`with ... raises` for expected exceptions

Assert
^^^^^^

The block that performs the assertions.

.. code:: python

   assert result is not None
   assert nodes = [D, C, B, A]

* first :code:`result` then side effects
* use simple blocks of assertions

The final test
^^^^^^^^^^^^^^

.. code:: python

   nodes = [A, B, C, D]

   result = nodes.reverse()

   assert result is not None
   assert nodes = [D, C, B, A]

Fixtures
--------

If the code in the arrangement block becomes too complex, extract code and create fixtures.

* in pytest fixtures are marked with :code:`@pytest.fixtures`

Patch files
-----------

To create Git repositories in the test cases where we need to create configuration networks we use patch files.

First, create a repository and commits that you want to test.
To generate the patch files, run

.. code::

   $ git format-patch 4b825dc642cb6eb9

from within the test repository and move the created :code:`*.patch` files into :code:`tests/launcher/repo/$YOURSUBFOLDER`.