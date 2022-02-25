# GisFIRE-Lightnings
GisFIRE module to manage lightning information, clustering and routing for wildfire surveillance

# GisFIRE

GisFIRE is a set of plugins for QGIS that implements several tools used by fire agencies. The Lightnings module 
implements Lightning information retrieval from different sources and provides clustering and routing for aerial 
inspection of possible wildfire ignitions.

## Getting Started

To get familiar with the project follow all the information in the wiki and then clone the project to continue 
developing or testing it.

### Prerequisites

To use GisFIRE you need QGIS and all of its requirements. Visit the QGIS website and follow install instructions.
[https://qgis.org/en/site/forusers/download.html](https://qgis.org/en/site/forusers/download.html)

### Installing

The plugin is not published in the QGIS repository. The easiest way to install the plugin is to download de the latest 
distribution zip file and install it with QGIS. In the "Plugins" menu entry of QGIS select the "Manage and Install 
Plugins..." and in the plugins interface select the "Install from ZIP" option.

## Development

Fork the repo and enjoy

### Compiling the resources

```console
pyrcc5 resources.qrc -o resources.py
```

### Translations

First generate the `.ts` file from the `.py` and `.ui` files.
```console
pylupdate5 ../GisFIRE-Lightnings/src/gisfire_lightnings/gisfire_lightnings.py -ts ../GisFIRE-Lightnings/src/gisfire_lightnings/i18n/gisfire_spread_simulation_ca.ts
pylupdate5 ../GisFIRE-Lightnings/src/gisfire_lightnings/ui/dialogs/settings.ui -ts ../GisFIRE-Lightnings/src/gisfire_lightnings/i18n/gisfire_spread_simulation_ca.ts
```

Then use QLinguist to translate to different languages

Finally, compile the `.ts` translation files to binary `.qm` files.
```console
lrelease ../GisFIRE-Lightnings/src/gisfire_lightnings/i18n/gisfire_spread_simulation_ca.ts
```
### Running the tests

Testing was inspired by lots of tutorials and also with lots of problems. This is the best I get running.
```console
 python3 -m pytest -x -v --cov-report=html:html_gisfire_lightnings_test_results --cov=../GisFIRE-Lightnings/ ../GisFIRE-Lightnings/test/
```

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of
conduct, and the process for submitting pull requests to us.

## Authors

* **Jaume Figueras** - *GisFIRE Plugin* - [JaumeFigueras](https://github.com/JaumeFigueras)
* **Clara Portalés** - *Octave analysis*
* **Toni Guasch** - *Data analysis*


See also the list of [contributors](https://github.com/JaumeFigueras/GisFIRE-Lightnings/contributors)
who participated in this project.

## License

This project is licensed under the GNU GPLv3 License - see the [COPYING](COPYING)
file for details

## Acknowledgments

* Bombers de la Generalitat de Catalunya
