Flask-RestX Changelog
=====================

Basic structure is

::

    ADD LINK (..) _section-VERSION
    VERSION
    -------
    ADD LINK (..) _bug_fixes-VERSION OR _enhancments-VERSION
    Bug Fixes or Enchancements
    ~~~~~~~~~~~~~~~~~~~~~~~~~~
    * Message (TICKET) [CONTRIBUTOR]

Opening a release
-----------------

If you’re the first contributor, add a new semver release to the
document. Place your addition in the correct category, giving a short
description (matching something in a git commit), the issue ID (or PR ID
if no issue opened), and your Github username for tracking contributors!

Releases prior to 0.3.0 were “best effort” filled out, but are missing
some info. If you see your contribution missing info, please open a PR
on the Changelog!

.. _section-1.0.2:
1.0.2
-----

.. _bug_fixes-1.0.2
Bug Fixes
~~~~~~~~~

::

   * Properly remove six dependency

.. _section-1.0.1:
1.0.1
-----

.. _breaking-1.0.1

Breaking
~~~~~~~~

Starting from this release, we only support python versions >= 3.7

.. _bug_fixes-1.0.1

Bug Fixes
~~~~~~~~~

::

   * Fix compatibility issue with werkzeug 2.1.0 (#423) [stacywsmith]

.. _enhancements-1.0.1:

Enhancements
~~~~~~~~~~~~

::

   * Drop support for python <3.7

.. _section-0.5.1:
0.5.1
-----

.. _bug_fixes-0.5.1

Bug Fixes
~~~~~~~~~

::

   * Optimize email regex (#372) [kevinbackhouse]

.. _section-0.5.0:
0.5.0
-----

.. _bug_fixes-0.5.0

Bug Fixes
~~~~~~~~~

::

   * Fix Marshaled nested wildcard field with ordered=True (#326) [bdscharf]
   * Fix Float Field Handling of None (#327) [bdscharf, TVLIgnacy]
   * Fix Werkzeug and Flask > 2.0 issues (#341) [hbusul]
   * Hotfix package.json [xuhdev]

.. _enhancements-0.5.0:

Enhancements
~~~~~~~~~~~~

::

   * Stop calling got_request_exception when handled explicitly (#349) [chandlernine, VolkaRancho]
   * Update doc links (#332) [EtiennePelletier]
   * Structure demo zoo app (#328) [mehul-anshumali]
   * Update Contributing.rst (#323) [physikerwelt]
   * Upgrade swagger-ui (#316) [xuhdev]


.. _section-0.4.0:
0.4.0
-----

.. _bug_fixes-0.4.0

Bug Fixes
~~~~~~~~~

::

   * Fix Namespace error handlers when propagate_exceptions=True (#285) [mjreiss]
   * pin flask and werkzeug due to breaking changes (#308) [jchittum]
   * The Flask/Blueprint API moved to the Scaffold base class (#308) [jloehel]


.. _enhancements-0.4.0:

Enhancements
~~~~~~~~~~~~

::
   * added specs-url-scheme option for API (#237) [DustinMoriarty]
   * Doc enhancements [KAUTH, Abdur-rahmaanJ]
   * New example with loosely couple implementation [maurerle]

.. _section-0.3.0:

0.3.0
-----

.. _bug_fixes-0.3.0:

Bug Fixes
~~~~~~~~~

::

   * Make error handlers order of registration respected when handling errors (#202) [avilaton]
   * add prefix to config setting (#114) [heeplr]
   * Doc fixes [openbrian, mikhailpashkov, rich0rd, Rich107, kashyapm94, SteadBytes, ziirish]
   * Use relative path for `api.specs_url` (#188) [jslay88]
   * Allow example=False (#203) [ogenstad]
   * Add support for recursive models (#110) [peterjwest, buggyspace, Drarok, edwardfung123]
   * generate choices schema without collectionFormat (#164) [leopold-p]
   * Catch TypeError in marshalling (#75) [robyoung]
   * Unable to access nested list propert (#91) [arajkumar]

.. _enhancements-0.3.0:

Enhancements
~~~~~~~~~~~~

::

   * Update Python versions [johnthagen]
   * allow strict mode when validating model fields (#186) [maho]
   * Make it possible to include "unused" models in the generated swagger documentation (#90)[volfpeter]

.. _section-0.2.0:

0.2.0
-----

This release properly fixes the issue raised by the release of werkzeug
1.0.

.. _bug-fixes-0.2.0:

Bug Fixes
~~~~~~~~~

::

   * Remove deprecated werkzeug imports (#35)
   * Fix OrderedDict imports (#54)
   * Fixing Swagger Issue when using @api.expect() on a request parser (#20)

.. _enhancements-0.2.0:

Enhancements
~~~~~~~~~~~~

::

   * use black to enforce a formatting codestyle (#60)
   * improve test workflows

.. _section-0.1.1:

0.1.1
-----

This release is mostly a hotfix release to address incompatibility issue
with the recent release of werkzeug 1.0.

.. _bug-fixes-0.1.1:

Bug Fixes
~~~~~~~~~

::

   * pin werkzeug version (#39)
   * register wildcard fields in docs (#24)
   * update package.json version accordingly with the flask-restx version and update the author (#38)

.. _enhancements-0.1.1:

Enhancements
~~~~~~~~~~~~

::

   * use github actions instead of travis-ci (#18)

.. _section-0.1.0:

0.1.0
-----

.. _bug-fixes-0.1.0:

Bug Fixes
~~~~~~~~~

::

   * Fix exceptions/error handling bugs https://github.com/noirbizarre/flask-restplus/pull/706/files noirbizarre/flask-restplus#741
   * Fix illegal characters in JSON references to model names noirbizarre/flask-restplus#653
   * Support envelope parameter in Swagger documentation noirbizarre/flask-restplus#673
   * Fix polymorph field ambiguity noirbizarre/flask-restplus#691
   * Fix wildcard support for fields.Nested and fields.List noirbizarre/flask-restplus#739

.. _enhancements-0.1.0:

Enhancements
~~~~~~~~~~~~

::

   * Api/Namespace individual loggers noirbizarre/flask-restplus#708
   * Various deprecated import changes noirbizarre/flask-restplus#732 noirbizarre/flask-restplus#738
   * Start the Flask-RESTX fork!
       * Rename all the things (#2 #9)
       * Set up releases from CI (#12)
           * Not a library enhancement but this was much needed - thanks @ziirish !
