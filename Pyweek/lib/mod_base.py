import load_mod_file
import glob

class Unit(object):
    type = 'base'
    def __init__(self):
        self.name = ''
        self.pos = (0,0)
        self.level = 1
        self.image = ''

        self.team = ''

        self.base_stats = {}

        self.gfx_entity = None

    def load_stats(self, stats):
        self.name, self.pos, self.level = stats


class UnitHandler(object):
    def __init__(self):
        self.units = {}

    def load_dir(self, path):
        self.units = {}
        access = {'BaseUnit':Unit}
        for unit in glob.glob(path+'*.py'):
            store = load_mod_file.load(unit, access)
            if store == False:
                print 'fail load unit <%s>'%unit
            else:
                self.units[store.unit.type] = store.unit

class Scenario(object):
    def __init__(self, engine, scenario):
        self.engine = engine

        self.unith = UnitHandler()
        self.unith.load_dir('data/scenarios/%s/units/'%scenario)
        self.unith.load_dir('data/units/')

        access = {'Unit':self.make_unit,
                  'engine':self.engine,
                  'parent':self}
        store = load_mod_file.load('data/scenarios/%s/scenario.py'%scenario, access)
        if store == False:
            print 'fail load scenario <%s>'%scenario
        else:
            self.mod = store.scenario

        self.units = []

        self.mod.initialize()

    def make_unit(self, type, team, stats):
        new = self.unith.units[type]()
        new.load_stats(stats)
        new.team = team
        new.gfx_entity = self.engine.gfx.mapd.make_entity(new.image, new.pos, new.name)
        self.units.append(new)

    def update(self):
        self.mod.update()
