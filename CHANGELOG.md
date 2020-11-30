# Flask-RestX Changelog
Basic structure is 

```
## VERSION
### Bug Fixes or Enchancements
    * Message (TICKET) [CONTRIBUTOR]
```

## Opening a release
If you're the first contributor, add a new semver release to the document. Place your addition in the correct category, giving a short description (matching something in a git commit), the issue ID (or PR ID if no issue opened), and your Github username for tracking contributors!

Releases prior to 0.3.0 were "best effort" filled out, but are missing some info. If you see your contribution missing info, please open a PR on the Changelog!


## 0.3.0

### Bug Fixes

    * Make error handlers order of registration respected when handling errors (#202) [avilaton]
    * add prefix to config setting (#114) [heeplr]
    * Doc fixes [openbrian, mikhailpashkov, rich0rd, Rich107, kashyapm94, SteadBytes, ziirish]
    * Use relative path for `api.specs_url` (#188) [jslay88]
    * Allow example=False (#203) [ogenstad]
    * Add support for recursive models (#110) [peterjwest, buggyspace, Drarok, edwardfung123]
    * generate choices schema without collectionFormat (#164) [leopold-p]
    * Catch TypeError in marshalling (#75) [robyoung]


### Enhancements
   
    * Update Python versions [johnthagen]
    * allow strict mode when validating model fields (#186) [maho]
    * Make it possible to include "unused" models in the generated swagger documentation (#90)[volfpeter]


## 0.2.0

This release properly fixes the issue raised by the release of werkzeug 1.0.

### Bug Fixes

    * Remove deprecated werkzeug imports (#35)
    * Fix OrderedDict imports (#54)
    * Fixing Swagger Issue when using @api.expect() on a request parser (#20)

### Enhancements

    * use black to enforce a formatting codestyle (#60)
    * improve test workflows

## 0.1.1

This release is mostly a hotfix release to address incompatibility issue with the recent release of werkzeug 1.0.

### Bug Fixes

    * pin werkzeug version (#39)
    * register wildcard fields in docs (#24)
    * update package.json version accordingly with the flask-restx version and update the author (#38)

### Enhancements

    * use github actions instead of travis-ci (#18)


## 0.1.0

### Bug Fixes

    * Fix exceptions/error handling bugs https://github.com/noirbizarre/flask-restplus/pull/706/files noirbizarre/flask-restplus#741
    * Fix illegal characters in JSON references to model names noirbizarre/flask-restplus#653
    * Support envelope parameter in Swagger documentation noirbizarre/flask-restplus#673
    * Fix polymorph field ambiguity noirbizarre/flask-restplus#691
    * Fix wildcard support for fields.Nested and fields.List noirbizarre/flask-restplus#739

### Enhancements

    * Api/Namespace individual loggers noirbizarre/flask-restplus#708
    * Various deprecated import changes noirbizarre/flask-restplus#732 noirbizarre/flask-restplus#738
    * Start the Flask-RESTX fork!
        * Rename all the things (#2 #9)
        * Set up releases from CI (#12)
            * Not a library enhancement but this was much needed - thanks @ziirish !
