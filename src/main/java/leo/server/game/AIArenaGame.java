///////////////////////////////////////////////////////////////////////
// Name: AIArenaGame
// Desc: An AI vs AI arena experience for spectators
// TODO:
///////////////////////////////////////////////////////////////////////
package leo.server.game;

// imports

import leo.server.AI;
import leo.server.GameAction;
import leo.server.Server;
import leo.server.User;
import leo.server.observers.ArenaObserver;
import leo.shared.Action;
import leo.shared.BattleField;
import leo.shared.Castle;
import leo.server.CastleArchive;
import leo.shared.Log;
import leo.shared.Unit;
import leo.shared.UnitType;
import org.tinylog.Logger;

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
    private volatile boolean over = false;
    private volatile Castle currentCastle;
    private volatile short lastWinner = Action.NOTHING;


    /////////////////////////////////////////////////////////////////
    // Constructor
    /////////////////////////////////////////////////////////////////
    public AIArenaGame(Server server, int level1, int level2, CastleArchive castleArchive1, CastleArchive castleArchive2, long seed, String label1, String label2) {
        this.server = server;
        this.level1 = level1;
        this.level2 = level2;
        this.seed = seed;
        this.label1 = label1;
        this.label2 = label2;
        random = new Random(seed);

        castle1 = buildCastle(castleArchive1);
        castle2 = buildCastle(castleArchive2);
        currentCastle = castle1;

        battleField = new BattleField(castle1, castle2);
        castle1.setBattleField(battleField);
        castle2.setBattleField(battleField);
        castle1.setLocation(BattleField.getLocation((byte) 5, (byte) 10));
        castle2.setLocation(BattleField.getLocation((byte) 5, (byte) 0));
        observer = new ArenaObserver(this);
        castle1.setObserver(observer);
        castle2.setObserver(observer);
        castle1.ai();
        castle2.ai();
        castle1.refresh(Unit.TEAM_1);
        castle2.refresh(Unit.TEAM_1);

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
            return castle;
        }
        return generateCastle(castle);
    }

    private Castle generateCastle(Castle castle) {
        castle.add(Unit.getUnit(UnitType.GENERAL.value(), castle));
        castle.add(Unit.getUnit(UnitType.GATE_GUARD.value(), castle));
        castle.add(Unit.getUnit(UnitType.TACTICIAN.value(), castle));
        castle.add(Unit.getUnit(UnitType.TACTICIAN.value(), castle));

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
        user.startGame(this);
        user.sendAction(Action.NEW_GAME, Action.NOTHING, Action.NOTHING);
        user.sendAction(Action.ARENA_STATE, (short) level1, (short) level2);
        user.sendCastle(castle1);
        user.sendCastle(castle2);
        replayHistory(user);
        if (currentCastle == castle1)
            user.sendAction(Action.ARENA_TURN, (short) 1, Action.NOTHING);
        else
            user.sendAction(Action.ARENA_TURN, (short) 2, Action.NOTHING);
    }

    public void broadcastAction(short action, short actor, short target) {
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
        Iterator<GameAction> it = actions.iterator();
        while (it.hasNext()) {
            GameAction gameAction = it.next();
            user.sendAction(gameAction.getAction(), gameAction.getActor(), gameAction.getTarget());
        }
    }


    /////////////////////////////////////////////////////////////////
    // Game loop
    /////////////////////////////////////////////////////////////////
    public void run() {
        try {
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

        if (action < 30) {
            Unit actor = battleField.getUnitAt(tmpActorLocation);
            if (actor == null) return;

            String description = actor.performAction(action, tmpTarget);
            if (description != null) Log.game(description);

            broadcastAction(action, tmpActorLocation, tmpTarget);
            return;
        }

        switch (action) {
            case Action.DEPLOY:
                Unit unit = currentCastle.getUnit(actorLocation);

                if (unit == null) {
                    LogActionError("deploy", actorLocation);
                    return;
                }

                Vector targets = unit.getCastleTargets();
                if (!validateTarget(targets, tmpTarget)) {
                    LogActionError("deploy-invalid-target", tmpTarget);
                    return;
                }

                currentCastle.deploy(Unit.TEAM_1, unit, tmpTarget);
                broadcastAction(Action.DEPLOY, actorLocation, tmpTarget);
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
