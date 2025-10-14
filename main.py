import yaml
from yaml import CLoader as Loader

from modules.ics_export import IcsExportModule
from modules.json_export import JsonExportModule
from scraper import Scraper

available_modules = {
    "json": JsonExportModule,
    "ics": IcsExportModule
}

def main():
    print("UMinho Schedule tool")

    with open("config.yml") as f:
        config = yaml.load(f.read(), Loader)

    scraper = Scraper(config["scraper"])

    for export_method in config["export"].keys():
        if export_method in available_modules.keys():
            export_module = available_modules[export_method](config["export"][export_method])
            export_module.export(scraper.lessons)

    print("Finished")


if __name__ == "__main__":
    main()
