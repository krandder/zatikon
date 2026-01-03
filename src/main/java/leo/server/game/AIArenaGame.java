///////////////////////////////////////////////////////////////////////
// Name: AIArenaGame
// Desc: An AI vs AI arena experience for spectators
// TODO:
///////////////////////////////////////////////////////////////////////
package leo.server.game;

// imports

import leo.server.AI;
import leo.server.GameAction;
import leo.server.Player;
import leo.server.Server;
import leo.server.User;
import leo.server.observers.ArenaObserver;
import leo.shared.Action;
import leo.shared.BattleField;
import leo.shared.Castle;
import leo.server.CastleArchive;
import leo.shared.Log;
import leo.shared.UndeployedUnit;
import leo.shared.Unit;
import leo.shared.UnitType;
import org.tinylog.Logger;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.util.Iterator;
import java.util.Random;
import java.util.Vector;


public class AIArenaGame implements Game, Runnable {

    /////////////////////////////////////////////////////////////////
    // Constants
    /////////////////////////////////////////////////////////////////
    private static final int ARENA_SIZE = 1250;
    private static final int ARENA_NORMALIZE = 2;
    private static final int MAX_COMMANDERS = 4;

    /////////////////////////////////////////////////////////////////
    // Properties
    /////////////////////////////////////////////////////////////////
    private final Server server;
    private final long seed;
    private final Random random;
    private final int level1;
    private final int level2;
    private final Castle castle1;
    private final Castle castle2;
    private final BattleField battleField;
    private final AI ai1;
    private final AI ai2;
    private final ArenaObserver observer;
    private final Vector<User> spectators = new Vector<User>();
    private final Vector<GameAction> actions = new Vector<GameAction>();
    private final Thread runner;
    private final String label1;
    private final String label2;
    private final int gameId;
    private volatile boolean over = false;
    private volatile Castle currentCastle;
    private volatile short lastWinner = Action.NOTHING;
    // Store original barracks order for index calculation
    private final Vector<Short> originalBarracks1Order = new Vector<Short>();
    private final Vector<Short> originalBarracks2Order = new Vector<Short>();


    /////////////////////////////////////////////////////////////////
    // Constructor
    /////////////////////////////////////////////////////////////////
    public AIArenaGame(Server server, int level1, int level2, CastleArchive castleArchive1, CastleArchive castleArchive2, long seed, String label1, String label2, int gameId) {
        this.server = server;
        this.level1 = level1;
        this.level2 = level2;
        this.seed = seed;
        this.label1 = label1;
        this.label2 = label2;
        this.gameId = gameId;
        random = new Random(seed);

        castle1 = buildCastle(castleArchive1);
        castle2 = buildCastle(castleArchive2);
        Logger.info("AIArenaGame constructor: After buildCastle, castle1 has " + castle1.getBarracks().size() + " unit types, castle2 has " + castle2.getBarracks().size() + " unit types");
        // Store original barracks order
        Vector<UndeployedUnit> barracks1 = castle1.getBarracks();
        for (int i = 0; i < barracks1.size(); i++) {
            originalBarracks1Order.add(barracks1.elementAt(i).getID());
        }
        Vector<UndeployedUnit> barracks2 = castle2.getBarracks();
        for (int i = 0; i < barracks2.size(); i++) {
            originalBarracks2Order.add(barracks2.elementAt(i).getID());
        }
        currentCastle = castle1;

        battleField = new BattleField(castle1, castle2);
        castle1.setBattleField(battleField);
        castle2.setBattleField(battleField);
        castle1.setLocation(BattleField.getLocation((byte) 5, (byte) 10));
        castle2.setLocation(BattleField.getLocation((byte) 5, (byte) 0));
        observer = new ArenaObserver(this);
        castle1.setObserver(observer);
        castle2.setObserver(observer);
        Logger.info("AIArenaGame constructor: Before ai(), castle1 has " + castle1.getBarracks().size() + " unit types, castle2 has " + castle2.getBarracks().size() + " unit types");
        castle1.ai();
        castle2.ai();
        Logger.info("AIArenaGame constructor: After ai(), castle1 has " + castle1.getBarracks().size() + " unit types, castle2 has " + castle2.getBarracks().size() + " unit types");
        castle1.refresh(Unit.TEAM_1);
        castle2.refresh(Unit.TEAM_1);
        Logger.info("AIArenaGame constructor: After refresh(), castle1 has " + castle1.getBarracks().size() + " unit types, castle2 has " + castle2.getBarracks().size() + " unit types");

        // Prepare the AIs
        ai1 = new AI(level1, this, battleField, castle1, castle2);
        ai2 = new AI(level2, this, battleField, castle2, castle1);

        runner = new Thread(this, "AIArenaGameThread");
        runner.start();
    }


    /////////////////////////////////////////////////////////////////
    // Build castles
    /////////////////////////////////////////////////////////////////
    private Castle buildCastle(CastleArchive archive) {
        Castle castle = new Castle();
        if (archive != null && archive.size() > 0) {
            for (int i = 0; i < archive.size(); i++) {
                castle.add(Unit.getUnit(archive.get(i), castle));
            }
            Logger.info("buildCastle: Built castle from archive with " + castle.getBarracks().size() + " unit types");
            return castle;
        }
        Castle generated = generateCastle(castle);
        Logger.info("buildCastle: Generated castle with " + generated.getBarracks().size() + " unit types");
        return generated;
    }

    private Castle generateCastle(Castle castle) {
        Logger.info("generateCastle: Starting, current barracks size: " + castle.getBarracks().size());
        castle.add(Unit.getUnit(UnitType.GENERAL.value(), castle));
        castle.add(Unit.getUnit(UnitType.GATE_GUARD.value(), castle));
        castle.add(Unit.getUnit(UnitType.TACTICIAN.value(), castle));
        castle.add(Unit.getUnit(UnitType.TACTICIAN.value(), castle));
        Logger.info("generateCastle: After initial units, barracks size: " + castle.getBarracks().size());

        int commanders = 3;
        while (castle.getValue() < ARENA_SIZE) {
            Unit unit = Unit.getUnit(((byte) random.nextInt(UnitType.UNIT_COUNT.value())), castle);

            if (unit != null && unit.getID() == UnitType.GATE_GUARD.value()) {
                unit = null;
            }

            if (unit != null && unit.getID() == UnitType.TACTICIAN.value()) {
                unit = null;
            }

            if (unit != null && (
                    unit.getID() == UnitType.GENERAL.value() ||
                            unit.getID() == UnitType.TACTICIAN.value() ||
                            unit.getID() == UnitType.COMMAND_POST.value() ||
                            unit.getID() == UnitType.SERGEANT.value()
            )) {
                if (commanders >= MAX_COMMANDERS) unit = null;
            }

            if (unit != null && (unit.getID() == UnitType.RELIC_GIFT_UNIT.value()))
                unit = null;

            if (unit != null && unit.getCastleCost() != 1001 && random.nextInt((unit.getCastleCost() / 50) + ARENA_NORMALIZE) == 0) {
                if (ARENA_SIZE - castle.getValue() >= unit.getCastleCost())
                    castle.add(unit);

                switch (unit.getEnum()) {
                    case TACTICIAN:
                    case GENERAL:
                    case COMMAND_POST:
                    case SERGEANT:
                        commanders++;
                        break;
                }

            }
        }
        return castle;
    }


    /////////////////////////////////////////////////////////////////
    // Broadcast helpers
    /////////////////////////////////////////////////////////////////
    public void addSpectator(User user) {
        if (user == null) return;
        if (!spectators.contains(user)) spectators.add(user);
        Logger.info("addSpectator: Adding spectator, castle1 has " + castle1.getBarracks().size() + " unit types, castle2 has " + castle2.getBarracks().size() + " unit types");
        user.startGame(this);
        user.sendAction(Action.NEW_GAME, Action.NOTHING, Action.NOTHING);
        user.sendAction(Action.ARENA_STATE, (short) level1, (short) level2);
        // Send castle1 to myCastle
        Logger.info("addSpectator: Sending castle1 to myCastle");
        user.sendCastle(castle1);
        // Send castle2 to enemyCastle using NEW_ENEMY_UNIT
        Logger.info("addSpectator: Sending castle2 to enemyCastle");
        sendEnemyCastle(user, castle2);
        Logger.info("addSpectator: Replaying " + actions.size() + " actions from history");
        replayHistory(user);
        // Send START_GAME to initialize the game screen
        user.sendAction(Action.START_GAME, Action.NOTHING, Action.NOTHING);
        if (currentCastle == castle1)
            user.sendAction(Action.ARENA_TURN, (short) 1, Action.NOTHING);
        else
            user.sendAction(Action.ARENA_TURN, (short) 2, Action.NOTHING);
        Logger.info("addSpectator: Completed spectator setup");
    }
    
    // Send castle units directly to enemy castle
    private void sendEnemyCastle(User user, Castle castle) {
        try {
            // Use original barracks order to match what we use for deploy actions
            Vector<Short> originalOrder = (castle == castle2) ? originalBarracks2Order : originalBarracks1Order;
            Vector<UndeployedUnit> currentBarracks = castle.getBarracks();
            Vector<Unit> deployedUnits = castle.getUnitsOut();
            
            // Create a map of unit ID to current barracks count
            java.util.HashMap<Short, Integer> barracksCounts = new java.util.HashMap<Short, Integer>();
            for (int i = 0; i < currentBarracks.size(); i++) {
                UndeployedUnit uu = currentBarracks.elementAt(i);
                barracksCounts.put(uu.getID(), uu.count());
            }
            
            // Count deployed units by ID
            java.util.HashMap<Short, Integer> deployedCounts = new java.util.HashMap<Short, Integer>();
            for (int i = 0; i < deployedUnits.size(); i++) {
                Unit deployedUnit = deployedUnits.elementAt(i);
                Short unitID = deployedUnit.getID();
                deployedCounts.put(unitID, deployedCounts.getOrDefault(unitID, 0) + 1);
            }
            
            // Send units in original order with their total counts (barracks + deployed)
            // This ensures indices match when DEPLOY_ENEMY actions are replayed
            for (short i = 0; i < originalOrder.size(); i++) {
                Short unitID = originalOrder.elementAt(i);
                int barracksCount = barracksCounts.getOrDefault(unitID, 0);
                int deployedCount = deployedCounts.getOrDefault(unitID, 0);
                int totalCount = barracksCount + deployedCount;
                
                // Send all units (barracks + deployed) to maintain index order
                // Deployed units will be added to castle, then deployed during replay
                for (int c = 0; c < totalCount; c++) {
                    user.sendAction(Action.NEW_ENEMY_UNIT, unitID, Action.NOTHING);
                }
            }
        } catch (Exception e) {
            Logger.error("sendEnemyCastle error: " + e);
        }
    }

    public void broadcastAction(short action, short actor, short target) {
        // Add delay BEFORE broadcasting unit actions to make them visible to spectators
        // Only delay for unit actions (moves, attacks, spells, skills)
        if (spectators.size() > 0 && action < 30 && action > -1) {
            try {
                Thread.sleep(1000); // 1 second delay before broadcasting unit action
            } catch (InterruptedException e) {
                // Ignore interruption
            }
        }
        
        actions.add(new GameAction(null, action, actor, target));
        Iterator<User> it = spectators.iterator();
        while (it.hasNext()) {
            User spectator = it.next();
            spectator.sendAction(action, actor, target);
        }
    }

    public void broadcastCastle(Castle castle) {
        Iterator<User> it = spectators.iterator();
        while (it.hasNext()) {
            User spectator = it.next();
            spectator.sendCastle(castle);
        }
    }

    public void broadcastText(String text) {
        Iterator<User> it = spectators.iterator();
        while (it.hasNext()) {
            User spectator = it.next();
            spectator.sendText(text);
        }
    }

    private void replayHistory(User user) {
        Logger.info("replayHistory: Replaying " + actions.size() + " actions to spectator (chatID=" + user.getChatID() + ")");
        Iterator<GameAction> it = actions.iterator();
        int count = 0;
        while (it.hasNext()) {
            GameAction gameAction = it.next();
            Logger.info("replayHistory: Action " + count + ": action=" + gameAction.getAction() + ", actor=" + gameAction.getActor() + ", target=" + gameAction.getTarget());
            user.sendAction(gameAction.getAction(), gameAction.getActor(), gameAction.getTarget());
            count++;
        }
        Logger.info("replayHistory: Replayed " + count + " actions");
    }


    /////////////////////////////////////////////////////////////////
    // Game loop
    /////////////////////////////////////////////////////////////////
    public void run() {
        try {
            Logger.info("AIArenaGame.run(): Starting game loop, castle1 barracks: " + castle1.getBarracks().size() + ", castle2 barracks: " + castle2.getBarracks().size());
            broadcastAction(Action.START_GAME, Action.NOTHING, Action.NOTHING);
            while (!over) {
                runTurn(castle1, ai1, (short) 1);
                if (over) break;
                castle2.refresh(Unit.TEAM_1);
                runTurn(castle2, ai2, (short) 2);
                if (over) break;
                castle1.refresh(Unit.TEAM_1);
            }
        } catch (Exception e) {
            Logger.error("AIArenaGame.run " + e);
        }
    }

    private void runTurn(Castle castle, AI ai, short side) {
        currentCastle = castle;
        castle.startTurn(Unit.TEAM_1);
        broadcastAction(Action.ARENA_TURN, side, Action.NOTHING);
        
        System.out.println("\n=== AI " + side + " Turn (" + (castle == castle1 ? label1 : label2) + ") ===");
        
        ai.computeTurn();
    }


    /////////////////////////////////////////////////////////////////
    // Interpret the action
    /////////////////////////////////////////////////////////////////
    public void interpretAction(Player player, short action, short actorLocation, short target) throws Exception {
        processAction(action, actorLocation, target);
    }


    /////////////////////////////////////////////////////////////////
    // Process the action
    /////////////////////////////////////////////////////////////////
    private void processAction(short action, short actorLocation, short target) throws Exception {
        if (action == Action.NOTHING || over) return;

        short tmpActorLocation = actorLocation;
        short tmpTarget = target;

        // Prompt before actual game actions (unit actions or deploy)
        boolean isGameAction = (action < 30) || (action == Action.DEPLOY);
        if (isGameAction) {
            promptForAction();
        }

        if (action < 30) {
            Unit actor = battleField.getUnitAt(tmpActorLocation);
            if (actor == null) {
                System.out.println("  WARNING: Unit not found at location " + formatLocation(tmpActorLocation));
                return;
            }

            // Log action to console for debugging
            String actionType = "Unknown";
            if (action == Action.ATTACK) actionType = "ATTACK";
            else if (action == Action.MOVE) actionType = "MOVE";
            else if (action == Action.SPELL) actionType = "SPELL";
            else if (action == Action.SKILL) actionType = "SKILL";
            else if (action == Action.OTHER) actionType = "OTHER";
            
            String castleName = (currentCastle == castle1) ? label1 : label2;
            String fromLoc = formatLocation(tmpActorLocation);
            String toLoc = formatLocation(tmpTarget);
            
            System.out.println("  ACTION: " + castleName + " - " + actor.getName() + " (" + actor.getID() + ")");
            System.out.println("    Type: " + actionType);
            System.out.println("    From: " + fromLoc + " (location " + tmpActorLocation + ")");
            System.out.println("    To:   " + toLoc + " (location " + tmpTarget + ")");
            
            Unit targetUnit = battleField.getUnitAt(tmpTarget);
            if (targetUnit != null) {
                System.out.println("    Target Unit: " + targetUnit.getName() + " (" + targetUnit.getID() + ") at " + formatLocation(tmpTarget));
            }

            String description = actor.performAction(action, tmpTarget);
            if (description != null) {
                Log.game(description);
                System.out.println("    Result: " + description);
            }

            broadcastAction(action, tmpActorLocation, tmpTarget);
            return;
        }

        switch (action) {
            case Action.DEPLOY:
                String deployCastleName = (currentCastle == castle1) ? label1 : label2;
                
                // The AI calls castle.deploy() BEFORE interpretAction(), so the unit is already deployed
                // Check if unit is already on the battlefield (at target location or anywhere)
                Unit deployedUnit = battleField.getUnitAt(tmpTarget);
                boolean unitOnBattlefield = false;
                
                // Check if there's a unit of this type already deployed by this castle
                if (deployedUnit != null && deployedUnit.getID() == actorLocation && deployedUnit.getCastle() == currentCastle) {
                    unitOnBattlefield = true;
                } else {
                    // Check if unit is deployed elsewhere on the battlefield
                    Vector<Unit> allUnits = battleField.getUnits();
                    for (int i = 0; i < allUnits.size(); i++) {
                        Unit u = allUnits.elementAt(i);
                        if (u.getID() == actorLocation && u.getCastle() == currentCastle) {
                            deployedUnit = u;
                            unitOnBattlefield = true;
                            break;
                        }
                    }
                }
                
                // Find barracks index from original order (since unit is already deployed, it's not in current barracks)
                Vector<Short> originalOrder = (currentCastle == castle1) ? originalBarracks1Order : originalBarracks2Order;
                short unitIndex = -1;
                boolean foundIndex = false;
                
                // Debug: show original barracks order
                String originalOrderStr = "";
                for (int i = 0; i < originalOrder.size() && i < 20; i++) {
                    originalOrderStr += i + ":" + getUnitTypeName(originalOrder.elementAt(i)) + " ";
                }
                System.out.println("    Original barracks order (first 20): " + originalOrderStr);
                System.out.println("    Looking for unit ID " + actorLocation + " (" + getUnitTypeName(actorLocation) + ")");
                
                // Find first occurrence of this unit type in original barracks order
                for (short i = 0; i < originalOrder.size(); i++) {
                    if (originalOrder.elementAt(i) == actorLocation) {
                        unitIndex = i;
                        foundIndex = true;
                        System.out.println("    Found at index " + i + " in original order");
                        break;
                    }
                }
                
                // If not found in original order, check current barracks (in case it wasn't deployed yet)
                if (!foundIndex) {
                    Vector<UndeployedUnit> barracks = currentCastle.getBarracks();
                    for (int i = 0; i < barracks.size(); i++) {
                        UndeployedUnit uu = barracks.elementAt(i);
                        if (uu.getID() == actorLocation) {
                            unitIndex = (short) i;
                            foundIndex = true;
                            break;
                        }
                    }
                }
                
                if (!foundIndex) {
                    // Unit type doesn't exist in this castle's barracks - this is an error
                    // The AI already deployed it, so we need to remove it from the battlefield
                    String barracksList = "";
                    Vector<UndeployedUnit> barracks = currentCastle.getBarracks();
                    for (int i = 0; i < barracks.size(); i++) {
                        UndeployedUnit uu = barracks.elementAt(i);
                        barracksList += uu.getUnit().getName() + "(" + uu.getID() + ") ";
                    }
                    Logger.error("AIArenaGame.DEPLOY: Unit ID " + actorLocation + " (" + getUnitTypeName(actorLocation) + ") not found in barracks or original order. Barracks: " + barracksList);
                    System.out.println("  ERROR: Unit ID " + actorLocation + " (" + getUnitTypeName(actorLocation) + ") not in castle barracks!");
                    System.out.println("  Barracks contains: " + barracksList);
                    System.out.println("  Removing invalidly deployed unit from battlefield");
                    
                    // Remove the unit from battlefield if it was deployed
                    if (deployedUnit != null && deployedUnit.getCastle() == currentCastle) {
                        battleField.remove(deployedUnit);
                        currentCastle.removeOut(deployedUnit);
                        System.out.println("    Removed " + deployedUnit.getName() + " from location " + formatLocation(deployedUnit.getLocation()));
                    } else {
                        // Check if unit is at target location
                        Unit unitAtTarget = battleField.getUnitAt(tmpTarget);
                        if (unitAtTarget != null && unitAtTarget.getID() == actorLocation && unitAtTarget.getCastle() == currentCastle) {
                            battleField.remove(unitAtTarget);
                            currentCastle.removeOut(unitAtTarget);
                            System.out.println("    Removed " + unitAtTarget.getName() + " from location " + formatLocation(tmpTarget));
                        }
                    }
                    
                    return; // Don't broadcast - this unit type doesn't exist in this castle
                }
                
                // Get unit name for display
                String unitName = unitOnBattlefield && deployedUnit != null ? deployedUnit.getName() : getUnitTypeName(actorLocation);
                String locationStr = unitOnBattlefield && deployedUnit != null ? 
                    "(already at " + formatLocation(deployedUnit.getLocation()) + ")" : 
                    "to " + formatLocation(tmpTarget);
                
                // Verify: what unit is actually at this index in original order?
                String actualUnitAtIndex = unitIndex >= 0 && unitIndex < originalOrder.size() ? 
                    getUnitTypeName(originalOrder.elementAt(unitIndex)) : "INVALID";
                
                // Single line console output
                System.out.println("  DEPLOY: " + deployCastleName + " - " + unitName + " " + locationStr + " (index=" + unitIndex + ", actual at index=" + actualUnitAtIndex + ")");
                
                if (!unitName.equals(actualUnitAtIndex)) {
                    System.out.println("    WARNING: Index mismatch! Deploying " + unitName + " but index " + unitIndex + " contains " + actualUnitAtIndex);
                }
                
                // Broadcast the deploy action
                if (currentCastle == castle1) {
                    broadcastAction(Action.DEPLOY, unitIndex, tmpTarget);
                } else {
                    broadcastAction(Action.DEPLOY_ENEMY, unitIndex, tmpTarget);
                }
                break;

            case Action.END_TURN:
                broadcastAction(Action.END_TURN, actorLocation, tmpTarget);
                break;
        }

    }

    private void LogActionError(String action, short target) {
        Logger.warn("AIArenaGame: " + action + " failed at " + target);
    }

    /////////////////////////////////////////////////////////////////
    // Prompt for console input before action
    /////////////////////////////////////////////////////////////////
    private void promptForAction() {
        System.out.print("\n[Press Enter to continue with next action...] ");
        try {
            BufferedReader reader = new BufferedReader(new InputStreamReader(System.in));
            reader.readLine();
        } catch (Exception e) {
            Logger.error("Error reading console input: " + e);
        }
    }

    /////////////////////////////////////////////////////////////////
    // Format location as (x, y) coordinates
    // x is column (0-10), y is row (0-10, where 0 is top, 10 is bottom)
    /////////////////////////////////////////////////////////////////
    private String formatLocation(short location) {
        short x = BattleField.getX(location);
        short y = BattleField.getY(location);
        return "(" + x + ", " + y + ")"; // x=column, y=row (0=top, 10=bottom)
    }

    /////////////////////////////////////////////////////////////////
    // Get unit type name from ID
    /////////////////////////////////////////////////////////////////
    private String getUnitTypeName(short unitID) {
        try {
            Unit testUnit = Unit.getUnit(unitID, null);
            if (testUnit != null) {
                return testUnit.getName();
            }
        } catch (Exception e) {
            // Ignore
        }
        return "Unknown(" + unitID + ")";
    }


    /////////////////////////////////////////////////////////////////
    // Make sure a target is within the targeting vector
    /////////////////////////////////////////////////////////////////
    private boolean validateTarget(Vector targets, short target) {
        for (int i = 0; i < targets.size(); i++) {
            Short location = (Short) targets.elementAt(i);
            if (location.byteValue() == target) return true;
        }
        return false;
    }


    /////////////////////////////////////////////////////////////////
    // Game over man
    /////////////////////////////////////////////////////////////////
    public boolean over() {
        return over;
    }

    public int getGameId() {
        return gameId;
    }

    public int getLevel1() {
        return level1;
    }

    public int getLevel2() {
        return level2;
    }

    public String getLabel1() {
        return label1;
    }

    public String getLabel2() {
        return label2;
    }

    public int getSpectatorCount() {
        return spectators.size();
    }

    public void endGame(Castle winner) {
        if (over) return;
        over = true;
        if (winner == castle1) lastWinner = 1;
        else if (winner == castle2) lastWinner = 2;
        broadcastAction(Action.ARENA_RESULT, lastWinner, Action.NOTHING);
        Iterator<User> it = spectators.iterator();
        while (it.hasNext()) {
            User spectator = it.next();
            spectator.endGame();
        }
    }


    /////////////////////////////////////////////////////////////////
    // Game interface
    /////////////////////////////////////////////////////////////////
    public void sendText(Player sender, String message) {
    }

    public void disconnect(Player player) {
    }

    public void interrupt(Player player) {
    }

    public Random random() {
        return random;
    }

    public void resynch() {
    }

    public int getDelay() {
        return 500;
    }

    public void banish(Unit unit) {
    }

    public Castle getCurrentCastle() {
        return currentCastle;
    }

    public short getLastWinner() {
        return lastWinner;
    }
}

