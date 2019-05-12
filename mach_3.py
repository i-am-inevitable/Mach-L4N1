from colorfight import Colorfight
from colorfight.position import Position
import time
import random
from colorfight.constants import BLD_GOLD_MINE, BLD_ENERGY_WELL, BLD_FORTRESS

HOME_I = ( 0, 1000 )
HOME_II = ( 1000, 1000 )
HOME_III = ( 2000, 2000 )

ENERGY_I = ( 0, 100 )
ENERGY_II = ( 0, 200 )
ENERGY_III = ( 0, 400 )

GOLD_I = ( 0, 100 )
GOLD_II = ( 0, 200 )
GOLD_III = ( 0, 400 )

FORTRESS_I = ( 0, 100 )
FORTRESS_II = ( 0, 200 )
FORTRESS_III = ( 0, 400 )

class Inevitable:
    def __init__( self ):
        self.game = Colorfight()
        pass

    def Start( self ):
        self.game.connect(room = 'public')
        if self.game.register( username = 'Inevitable', password = "LeilaniFlores" ):
            while True:
                if self.Refresh():
                    self.FetchInfo()
                    self.GameLoop()
                    self.Send()

    def GetCell( self, pos ):
        return self.game.game_map[ pos ]

    def GetUser( self, uid ):
        return self.game.users[ uid ]

    def Attack( self, cell, energy = None ):
        if energy == None:
            energy = cell.attack_cost
        self.me.energy -= energy
        self.cmdList.append( self.game.attack( cell.position, energy ) )
        self.attackList.append( cell.position )

    def Upgrade( self, cell ):
        cellType = cell.building.name
        cellLevel = cell.building.level
        if cellType == "home":
            if cellLevel == 1:
                self.me.energy -= HOME_I[ 0 ]
                self.me.gold -= HOME_I[ 1 ]
            elif cellLevel == 2:
                self.me.energy -= HOME_II[ 0 ]
                self.me.gold -= HOME_II[ 1 ]
        elif cellType == "energy_well":
            if cellLevel == 1:
                self.me.energy -= ENERGY_I[ 0 ]
                self.me.gold -= ENERGY_I[ 1 ]
            elif cellLevel == 2:
                self.me.energy -= ENERGY_II[ 0 ]
                self.me.gold -= ENERGY_II[ 1 ]
        elif cellType == "gold_mine":
            if cellLevel == 1:
                self.me.energy -= GOLD_I[ 0 ]
                self.me.gold -= GOLD_I[ 1 ]
            elif cellLevel == 2:
                self.me.energy -= GOLD_II[ 0 ]
                self.me.gold -= GOLD_II[ 1 ]
        elif cellType == "fortress":
            if cellLevel == 1:
                self.me.energy -= FORTRESS_I[ 0 ]
                self.me.gold -= FORTRESS_I[ 1 ]
            elif cellLevel == 2:
                self.me.energy -= FORTRESS_II[ 0 ]
                self.me.gold -= FORTRESS_II[ 1 ]
        self.cmdList.append( self.game.upgrade( cell.position ) )

    def CanSnap( self, base ):
        owner = self.GetUser( base.owner )
        if self.me.energy >= ( owner.energy_source + base.attack_cost ):
            return owner.energy_source + base.attack_cost
        else:
            return -1

    def CanBuild( self, building ):
        if building == BLD_ENERGY_WELL:
            return self.me.energy >= ENERGY_I[ 0 ] and self.me.gold >= ENERGY_I[ 1 ]
        elif building == BLD_GOLD_MINE:
            return self.me.energy >= GOLD_I[ 0 ] and self.me.gold >= GOLD_I[ 1 ]
        elif building == BLD_FORTRESS:
            return self.me.energy >= FORTRESS_I[ 0 ] and self.me.gold >= FORTRESS_I[ 1 ]

    def CanUpgrade( self, cell ):
        cellType = cell.building.name
        cellLevel = cell.building.level
        if cellType == "home":
            if cellLevel == 1:
                return self.me.energy >= HOME_I[ 0 ] and self.me.gold >= HOME_I[ 1 ]
            elif cellLevel == 2:
                return self.me.energy >= HOME_II[ 0 ] and self.me.gold >= HOME_II[ 1 ]
            else:
                return False
        elif cellType == "energy_well":
            if cellLevel == 1:
                return self.me.energy >= ENERGY_I[ 0 ] and self.me.gold >= ENERGY_I[ 1 ]
            elif cellLevel == 2:
                return self.me.energy >= ENERGY_II[ 0 ] and self.me.gold >= ENERGY_II[ 1 ]
            else:
                return False
        elif cellType == "gold_mine":
            if cellLevel == 1:
                return self.me.energy >= GOLD_I[ 0 ] and self.me.gold >= GOLD_I[ 1 ]
            elif cellLevel == 2:
                return self.me.energy >= GOLD_II[ 0 ] and self.me.gold >= GOLD_II[ 1 ]
            else:
                return False
        elif cellType == "fortress":
            if cellLevel == 1:
                return self.me.energy >= FORTRESS_I[ 0 ] and self.me.gold >= FORTRESS_I[ 1 ]
            elif cellLevel == 2:
                return self.me.energy >= FORTRESS_II[ 0 ] and self.me.gold >= FORTRESS_II[ 1 ]
            else:
                return False

    def Build( self, cell, building ):
        if building == BLD_ENERGY_WELL:
            self.me.energy -= ENERGY_I[ 0 ]
            self.me.gold -= ENERGY_I[ 1 ]
        elif building == BLD_GOLD_MINE:
            self.me.energy -= GOLD_I[ 0 ]
            self.me.gold -= GOLD_I[ 1 ]
        elif building == BLD_FORTRESS:
            self.me.energy -= FORTRESS_I[ 0 ]
            self.me.gold -= FORTRESS_I[ 1 ]
        self.cmdList.append( self.game.build( cell.position, building ) )

    def FetchAdjacent( self, cell ):
        return [ self.game.game_map[ pos ] for pos in cell.position.get_surrounding_cardinals() ]

    def Empty( self, cell ):
        return cell.owner == 0

    def Own( self, cell ):
        return cell.owner == self.game.uid

    def Enemy( self, cell ):
        return not ( cell.owner == 0 or cell.owner == self.game.uid )

    def FetchInfo( self ):
        self.me = self.game.me
        self.mode = 0
        self.tech = 0

        self.data = {}

        self.data[ "adjacent" ] = {}
        self.data[ "adjacent" ][ "all" ] = set()
        self.data[ "adjacent" ][ "empty" ] = set()
        self.data[ "adjacent" ][ "enemy" ] = {}
        self.data[ "adjacent" ][ "enemy" ][ "all" ] = set()
        self.data[ "adjacent" ][ "enemy" ][ "empty" ] = set()
        self.data[ "adjacent" ][ "enemy" ][ "energy" ] = [ set(), set(), set() ]
        self.data[ "adjacent" ][ "enemy" ][ "gold" ] = [ set(), set(), set() ]
        self.data[ "adjacent" ][ "enemy" ][ "bases" ] = [ set(), set(), set() ]
        self.data[ "adjacent" ][ "enemy" ][ "forts" ] = [ set(), set(), set() ]

        self.data[ "own" ]  = {}
        self.data[ "own" ][ "all" ] = set()
        self.data[ "own" ][ "empty" ] = set()
        self.data[ "own" ][ "energy" ] = [ set(), set(), set() ]
        self.data[ "own" ][ "gold" ] = [ set(), set(), set() ]
        self.data[ "own" ][ "bases" ] = [ set(), set(), set() ]
        self.data[ "own" ][ "forts" ] = [ set(), set(), set() ]

        self.data[ "edges" ] = set()

        self.data[ "enemy" ] = {}
        self.data[ "enemy" ][ "all" ] = set()
        self.data[ "enemy" ][ "empty" ] = set()
        self.data[ "enemy" ][ "energy" ] = [ set(), set(), set() ]
        self.data[ "enemy" ][ "gold" ] = [ set(), set(), set() ]
        self.data[ "enemy" ][ "bases" ] = [ set(), set(), set() ]
        self.data[ "enemy" ][ "forts" ] = [ set(), set(), set() ]

        self.cmdList = []
        self.attackList = []

        for x in range( 30 ):
            for y in range( 30 ):
                pos = Position( x, y )
                cell = self.GetCell( pos )
                if self.Own( cell ):
                    self.data[ "own" ][ "all" ].add( pos )
                    cellType = cell.building.name
                    if cellType == "empty":
                        self.data[ "own" ][ "empty" ].add( pos )
                    elif cellType == "home":
                        self.data[ "own" ][ "bases" ][ cell.building.level - 1 ].add( pos )
                    elif cellType == "energy_well":
                        self.data[ "own" ][ "energy" ][ cell.building.level - 1 ].add( pos )
                    elif cellType == "gold_mine":
                        self.data[ "own" ][ "gold" ][ cell.building.level - 1 ].add( pos )
                    elif cellType == "fortress":
                        self.data[ "own" ][ "forts" ][ cell.building.level - 1 ].add( pos )
                    for adj in self.FetchAdjacent( cell ):
                        if not self.Own( adj ):
                            self.data[ "adjacent" ][ "all" ].add( adj.position )
                            if self.Enemy( adj ):
                                self.data[ "edges" ].add( pos )
                                self.data[ "adjacent" ][ "enemy" ][ "all" ].add( adj.position )
                                adjType = adj.building.name
                                if adjType == "empty":
                                    self.data[ "own" ][ "empty" ].add( adj.position )
                                elif adjType == "home":
                                    self.data[ "own" ][ "bases" ][ adj.building.level - 1 ].add( adj.position )
                                elif adjType == "energy_well":
                                    self.data[ "own" ][ "energy" ][ adj.building.level - 1 ].add( adj.position )
                                elif adjType == "gold_mine":
                                    self.data[ "own" ][ "gold" ][ adj.building.level - 1 ].add( adj.position )
                                elif adjType == "fortress":
                                    self.data[ "own" ][ "forts" ][ adj.building.level - 1 ].add( adj.position )
                            else:
                                self.data[ "adjacent" ][ "empty" ].add( adj.position )

    def Refresh( self ):
        self.game.update_turn()
        return not self.game.me == None

    def Send( self ):
        self.game.send_cmd( self.cmdList )

    def Defend( self ):
        base = None
        if len( self.data[ "own" ][ "bases" ][ 0 ] ) > 0:
            base = self.GetCell( list( self.data[ "own" ][ "bases" ][ 0 ] )[ 0 ] )
        if len( self.data[ "own" ][ "bases" ][ 1 ] ) > 0:
            base = self.GetCell( list( self.data[ "own" ][ "bases" ][ 1 ] )[ 0 ] )
        if len( self.data[ "own" ][ "bases" ][ 2 ] ) > 0:
            base = self.GetCell( list( self.data[ "own" ][ "bases" ][ 2 ] )[ 0 ] )
        if base:
            self.tech = base.building.level
            if self.CanUpgrade( base ):
                self.Upgrade( base )

    def Expand( self ):
        if self.me.gold <= 500:
            self.BuildEnergy()
        targets = [ self.GetCell( t ) for t in self.data[ "adjacent" ][ "empty" ] ]
        targets.sort( key = lambda cell: ( cell.natural_energy, -cell.attack_cost ), reverse = True )
        for target in targets:
            if target.attack_cost <= self.me.energy:
                self.Attack( target )

    def Bread( self ):
        self.BuildGold()
        targets = [ self.GetCell( t ) for t in self.data[ "adjacent" ][ "empty" ] ]
        targets.sort( key = lambda cell: ( cell.natural_gold, -cell.attack_cost ), reverse = True )
        for target in targets:
            if target.attack_cost <= self.me.energy:
                self.Attack( target ) 

    def BuildEnergy( self ):
        energyTargets = [ self.GetCell( e ) for e in self.data[ "own" ][ "empty" ] ]
        energyTargets.sort( key = lambda cell: ( cell.natural_energy ), reverse = True )
        for energyTarget in energyTargets:
            if self.CanBuild( BLD_ENERGY_WELL ):
                self.Build( energyTarget, BLD_ENERGY_WELL )

    def BuildGold( self ):
        goldTargets = [ self.GetCell( e ) for e in self.data[ "own" ][ "empty" ] ]
        goldTargets.sort( key = lambda cell: ( cell.natural_gold ), reverse = True )
        for goldTarget in goldTargets:
            if self.CanBuild( BLD_GOLD_MINE ):
                self.Build( goldTarget, BLD_GOLD_MINE )

    def UpgradeEnergy( self, level ):
        energyTargets = [ self.GetCell( e ) for e in self.data[ "own" ][ "energy" ][ level - 1 ] ]
        energyTargets.sort( key = lambda cell: ( cell.natural_energy ), reverse = True )
        for energyTarget in energyTargets:
            if self.CanUpgrade( energyTarget ):
                self.Upgrade( energyTarget )

    def UpgradeGold( self, level ):
        goldTargets = [ self.GetCell( e ) for e in self.data[ "own" ][ "gold" ][ level - 1 ] ]
        goldTargets.sort( key = lambda cell: ( cell.natural_energy ), reverse = True )
        for goldTarget in goldTargets:
            if self.CanUpgrade( goldTarget ):
                self.Upgrade( goldTarget )

    def Armor( self ):
        for edge in self.data[ "edges" ]:
            edge = self.GetCell( edge )
            if self.me.energy >= 1:
                self.Attack( edge, 1 )

    def Loot( self ):
        for i in ( 2, 1, 0 ):
            if len( self.data[ "adjacent" ][ "enemy" ][ "gold" ][ i ] ) > 0:
                goldTargets = [ self.GetCell( b ) for b in self.data[ "adjacent" ][ "enemy" ][ "gold" ][ i ] ]
                goldTargets.sort( key = lambda cell: ( cell.attack_cost ) )
                for goldTarget in goldTargets:
                    if goldTarget.attack_cost <= self.me.energy:
                        self.Attack( goldTarget )

    def Recharge( self ):
        for i in ( 2, 1, 0 ):
            if len( self.data[ "adjacent" ][ "enemy" ][ "energy" ][ i ] ) > 0:
                goldTargets = [ self.GetCell( b ) for b in self.data[ "adjacent" ][ "enemy" ][ "energy" ][ i ] ]
                goldTargets.sort( key = lambda cell: ( cell.attack_cost ) )
                for goldTarget in goldTargets:
                    if goldTarget.attack_cost <= self.me.energy:
                        self.Attack( goldTarget )

    def Dominate( self ):
        targets = [ self.GetCell( t ) for t in self.data[ "adjacent" ][ "empty" ] ]
        targets.sort( key = lambda cell: ( cell.attack_cost ) )
        for target in targets:
            if target.attack_cost <= self.me.energy:
                self.Attack( target )
        targets = [ self.GetCell( t ) for t in self.data[ "adjacent" ][ "all" ] ]
        targets.sort( key = lambda cell: ( cell.attack_cost ) )
        for target in targets:
            if target.attack_cost <= self.me.energy:
                self.Attack( target ) 

    def Snap( self ):
        for i in ( 2, 1, 0 ):
            if len( self.data[ "adjacent" ][ "enemy" ][ "bases" ][ i ] ) > 0:
                bases = [ self.GetCell( b ) for b in self.data[ "adjacent" ][ "enemy" ][ "bases" ][ i ] ]
                for base in bases:
                    snapCost = self.CanSnap( base )
                    if not snapCost == -1:
                        self.Attack( base, snapCost )

    def AllSpark( self ):
        if random.choice( ( 0, 1 ) ) == 0:
            self.UpgradeEnergy( 1 )
            self.UpgradeEnergy( 2 )
            self.BuildEnergy()
        else:
            self.UpgradeGold( 1 )
            self.UpgradeGold( 2 )
            self.BuildGold()
        self.Snap()
        self.Armor()
        order = random.choice( ( 0, 1, 2 ) )
        if order == 0:
            self.Dominate()
            if random.choice( ( 0, 1 ) ) == 0:
                self.Recharge()
                self.Loot()
            else:
                self.Loot()
                self.Recharge()
        elif order == 1:
            self.Recharge()
            self.Dominate()
            self.Loot()
        elif order == 2:
            self.Loot()
            self.Dominate()
            self.Recharge()
            
    def GameLoop( self ):
        print( str( len( self.data[ "edges" ] ) ) )
        print( str( len( self.data[ "adjacent" ][ "empty" ] ) ) )
        self.Defend()
        if self.tech == 1:
            self.Expand()
        elif self.tech == 2:
            self.Bread()
        else:
            self.AllSpark()
            #self.Expand()

inevitable = Inevitable()
inevitable.Start()