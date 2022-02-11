Logging
=======

We added `Python's logging system <https://docs.python.org/3/library/logging.html#module-logging>`_ to our CfgNet to better understand the flow that our application goes through.
The logging system allows us to log various information about when and where a log is triggered, as well as to log certain messages when we apply CfgNet to software repositories.
Having good logs are very useful, not only for debugging but also to provide insights in CfgNet or in the analysis we perform.

Logging Handler
---------------

Logging handler are components that specify how and what kind of log messages are written in a log file or displayed in the console.
They can be specified regarding the logging level, format, or filter.
Currently, we have two preconfigured logging handler that are added to the root logger and that are responsible for our logging:

- :code:`repo_logging_handler`: specifies log messages for a software repository that will be written in a log file
- :code:`console_logging_handler`: specifies log messages that will be displayed in the console

Logging Levels
--------------

Logging levels correspond to the importance of log messages.
There are six log levels that are showed below in order of severity:

- :code:`DEBUG`
- :code:`INFO`
- :code:`WARNING`
- :code:`ERROR`
- :code:`CRITICAL`

A logging level indicates which log messages are logged.
Each logging level allows to log only messages with the same or higher severity.
For instance, a logging handler configured with :code:`DEBUG` logs messages of all other levels.
However, a logging handler specified with :code:`WARNING` only logs messages with the same or higher severity (:code:`WARNING`, :code:`ERROR`, :code:`CRITICAL`).
The :code:`Error` level should only be used in situations where the CfgNet is terminated, e.g. due to errors or when we exit the process on purpose.
By contrast, the level :code:`WARNING` should be used when problems occur that don't terminate the CfgNet, e.g. when files couldn't be parsed.

Our logging handler are preconfigured with the following levels:

- :code:`repo_logging_handler`: :code:`Debug`
- :code:`console_logging_handler`: :code:`INFO`

Logging Formatter
-----------------

Logging formatter basically specify the format of log messages by adding context information to it, such as the Python file, line number, method or additional context such as the thread and process.
We use a default format that looks like as follows:

.. code:: python

   log_formatter = logging.Formatter('%(asctime)s | %(levelname)8s | %(module)20s | %(message)s')

In addition to the log message, this format allows to display the time/module when/in which the logging was triggered and the logging level.
To add a new format, we need to create the format and set it in the corresponding logging handler.

Assume we want to change the format for the :code:`console_logging_handler`:

.. code:: python

   new_formatter = logging.Formatter('%(levelname)8s | %(filename)20s | %(funcName)s | %(lineno)d')
   console_logging_handler.setFormatter(new_formatter)

Logging Filter
--------------

Logging filter can be used by logging handler for more sophisticated filtering than is provided by logging levels.
For instance, the example below filters out all log messages fired by the :code:`cmd`.

.. code:: python

   class LogFileFilter(logging.Filter):
       """Logging filter to suppress logs fired by module 'cmd'."""
       def filter(self, record):
           return record.module != "cmd"

To add a new logging filter, we need to create a new filter as shown in the example and add it to the corresponding logging handler.

Flags
-----

We use a additional flag in order to configure the :code:`repo_logging_handler`.

- :code:`--verbose`: all logging messages (:code:`DEBUG` and higher) are also logged in the console.

Usage
-----

Since our logging handler are preconfigured, we only need to import :code:`logging` to be able to log messages.
Depending on the severity of a message, the usage looks like this:

.. code:: python

   import logging

   logging.debug("print debug message")
   logging.info("print info message")
   logging.warning("print warning message")
   logging.error("print error message")
   logging.critical("print critical message")