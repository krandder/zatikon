///////////////////////////////////////////////////////////////////////
// Name: ClientNetManager
// Desc: The net manager
// Date: 2/7/2003 - Gabe Jones
//     11/18/2010 - Tony Schwartz
//   Updates: Finished redrawArmy
// TODO:
///////////////////////////////////////////////////////////////////////
package leo.client;

// imports

import leo.shared.*;
import leo.shared.network.SocketProvider;
import org.tinylog.Logger;

import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.net.Socket;
import java.util.Vector;

import javax.net.ssl.SSLHandshakeException;
import java.io.IOException;

public class ClientNetManager implements Runnable {


    private final boolean useTls;
    /////////////////////////////////////////////////////////////////
    // Properties
    /////////////////////////////////////////////////////////////////
    private Thread runner;
    private Socket socket;
    private DataInputStream dis;
    private DataOutputStream dos;
    private boolean active = true;
    private final int player = 1;
    private int counter = 0; 


    /////////////////////////////////////////////////////////////////
    // Constructor
    /////////////////////////////////////////////////////////////////
    public ClientNetManager(boolean useTls) {
        this.useTls = useTls;
    }


    /////////////////////////////////////////////////////////////////
    // End
    /////////////////////////////////////////////////////////////////
    private void end() {
    }


    /////////////////////////////////////////////////////////////////
    // Start
    /////////////////////////////////////////////////////////////////
    public void start() { //System.out.println("Started net loop.");
        active = true;
        runner = new Thread(this, "ClientNetManagerThread");
        runner.start();
    }


    /////////////////////////////////////////////////////////////////
    // Connect to the server
    /////////////////////////////////////////////////////////////////
    public LoginResponse connect(LoginAttempt loginAttempt) throws Exception {
        try {
            // Create the connection to the server
            //socket = SocketProvider.newSocket(Client.serverName, Client.LOGIN_PORT, useTls);
            try {
                socket = SocketProvider.newSocket(Client.serverName, Client.LOGIN_PORT, useTls);
                socket.setTcpNoDelay(true);
            } catch (SSLHandshakeException e) {
                // Handle SSL handshake issues (e.g., expired/invalid certificate)
                Logger.error("SSL handshake failed: " + e.getMessage(), e);
                LoginResponse response = new LoginResponse("SSL handshake failed: " + e.getMessage());
                return response;
                //throw e;
            } catch (IOException e) {
                // Handle other IO-related issues
                Logger.error("Failed to connect: " + e.getMessage(), e);
                LoginResponse response = new LoginResponse("Failed to connect: " + e.getMessage());
                return response;
            }

            // Bye delay
            //socket.setSoTimeout(0);
            //socket.setTcpNoDelay(true);

            // Initialize the streams
            dis = new DataInputStream(socket.getInputStream());
            dos = new DataOutputStream(socket.getOutputStream());

            // Send the login request
            dos.writeUTF(loginAttempt.getUsername());
            dos.writeUTF(loginAttempt.getPassword());
            dos.writeUTF(loginAttempt.getEmail());
            dos.writeShort(loginAttempt.isNewAccount());
            dos.writeUTF(loginAttempt.getVersion());
            dos.writeBoolean(loginAttempt.newsletter());

            // Get the response
            Logger.debug("Waiting for login response");
            int response1 = dis.readInt();
            int response2 = dis.readInt();
            LoginResponse response = null;
            //Logger.info("login response: " + response1 + " " + response2);
            if(response1 == LoginResponse.FAIL_OLD_VERSION) {
                //Logger.info("wrong version");
                response = new LoginResponse(response1, response2, dis.readUTF());
            } else {
                response = new LoginResponse(response1, response2);
            }
            Logger.debug("Got login response");

            return response;

        } catch (Exception e) {
            Logger.error("connect: " + e);
            throw e;
        }
    }


    /////////////////////////////////////////////////////////////////
    // Initialize the game state
    /////////////////////////////////////////////////////////////////
    public void requestGame() {
        try { // Start the join
            Client.setState("lobby");
            dos.writeShort(Action.JOIN);

        } catch (Exception e) {
            Logger.error("req game: " + e);
            Client.getGameData().screenDisconnect();
        }
    }


    /////////////////////////////////////////////////////////////////
    // Initialize the game state
    /////////////////////////////////////////////////////////////////
    public void requestDuel() {
        try { // Start the join
            Client.setState("lobby");
            dos.writeShort(Action.JOIN_DUEL);

        } catch (Exception e) {
            Logger.error("req duel " + e);
            Client.getGameData().screenDisconnect();
        }
    }

    /////////////////////////////////////////////////////////////////
    // Initialize the game state for Mirrored Random mode
    /////////////////////////////////////////////////////////////////
    public void requestMirrDuel() {
        try { // Start the join
            Client.setState("lobby");
            dos.writeShort(Action.JOIN_MIRRORED_DUEL);

        } catch (Exception e) {
            Logger.error("req duel " + e);
            Client.getGameData().screenDisconnect();
        }
    }


    /////////////////////////////////////////////////////////////////
    // Initialize the game state
    /////////////////////////////////////////////////////////////////
    public void requestPractice() {
        try { // Start the join
            Client.setState("lobby");
            dos.writeShort(Action.PRACTICE);

        } catch (Exception e) {
            Logger.error("req practice " + e);
            Client.getGameData().screenDisconnect();
        }
    }


    /////////////////////////////////////////////////////////////////
    // Initialize the game state
    /////////////////////////////////////////////////////////////////
    public void requestCooperative() {
        try { // Start the join
            Client.setState("lobby");
            dos.writeShort(Action.COOPERATIVE);

        } catch (Exception e) {
            Logger.error("req coop" + e);
            Client.getGameData().screenDisconnect();
        }
    }

    /////////////////////////////////////////////////////////////////
    // Watch AI Arena games
    /////////////////////////////////////////////////////////////////
    public void requestWatchArena() {
        try {
            Client.setState("lobby");
            dos.writeShort(Action.WATCH_ARENA);
        } catch (Exception e) {
            Logger.error("req watch arena " + e);
            Client.getGameData().screenDisconnect();
        }
    }

    /////////////////////////////////////////////////////////////////
    // Request list of active arena games
    /////////////////////////////////////////////////////////////////
    public void requestArenaGameList() {
        try {
            dos.writeShort(Action.ARENA_GAME_LIST);
        } catch (Exception e) {
            Logger.error("req arena game list " + e);
            Client.getGameData().screenDisconnect();
        }
    }

    /////////////////////////////////////////////////////////////////
    // Watch a specific arena game
    /////////////////////////////////////////////////////////////////
    public void requestWatchArenaGame(int gameId) {
        try {
            Client.setState("lobby");
            dos.writeShort(Action.WATCH_ARENA_GAME);
            dos.writeInt(gameId);
        } catch (Exception e) {
            Logger.error("req watch arena game " + e);
            Client.getGameData().screenDisconnect();
        }
    }


    /////////////////////////////////////////////////////////////////
    // Get the edit army data
    /////////////////////////////////////////////////////////////////
    public void getArmyUnits() {
        try { // Clear the castles
            //Client.getGameData().getArmy().clear();

            // Wait for the game to end
            //runner.sleep(1000);

            // Start the join
            dos.writeShort(Action.GET_ARMY);

        } catch (Exception e) {
            Logger.error("get army units " + e);
            Client.getGameData().screenDisconnect();
        }
    }

    /////////////////////////////////////////////////////////////////
    // Check if still connected
    /////////////////////////////////////////////////////////////////
    public void requestPing() {
        try {
            dos.writeShort(Action.PING);

        } catch (Exception e) {
            Logger.error("req practice " + e);
            Client.getGameData().screenDisconnect();
        }
    }

    /////////////////////////////////////////////////////////////////
    // Main loop
    /////////////////////////////////////////////////////////////////
    public void run() { //System.out.println("Main net thread begun");
        try {
            while (active && !Client.shuttingDown() && !Client.timingOut()) {
                short action = dis.readShort();
                if (!active) return;
                
                // Special handling for actions that don't follow the standard format
                if (action == Action.ARENA_GAME_LIST) {
                    getArenaGameList();
                    continue;
                }
                
                //System.out.println("Run Action received: " + action);
                short ID = dis.readShort();
                if (!active) return;
                //System.out.println("Run Actor received: " + ID);
                short target = dis.readShort();
                if (!active) return;
                //System.out.println("Run Target received: " + target);
                
                process(action, ID, target);
                
                // Add delay in arena mode AFTER processing unit actions to make moves visible
                // Only delay for unit actions (moves, attacks, spells, skills) to avoid blocking setup
                if (Client.standalone && Client.getGameData().playing() && action < 30 && action > -1) {
                    try {
                        Thread.sleep(1000); // 1 second delay after processing unit action
                    } catch (InterruptedException e) {
                        // Ignore interruption
                    }
                }
            }

            //System.out.println("Main net loop ended.");

        } catch (Exception e) { //kill();
            Logger.error("ClientNetManager.run: " + e);
            Client.getGameData().screenDisconnect();
        }
    }


    /////////////////////////////////////////////////////////////////
    // Process an action
    /////////////////////////////////////////////////////////////////
    private void process(short action, short actor, short target) throws Exception {
        try {
            // System.out.println("received: " + action + ", " + actor + ", " + target);

            // If under 30, it's a unit action
            if (action < 30 && action > -1) {
                // For arena games, we need to be playing to process unit actions
                if (!Client.getGameData().playing()) {
                    Logger.debug("Received unit action " + action + " but not in playing state, ignoring");
                    return;
                }
                Unit unit = Client.getGameData().getBattleField().getUnitAt(actor);
                if (unit == null) {
                    // In arena mode, try to find unit by searching all units
                    // This can happen during replay when units have moved or actions are processed quickly
                    Vector<Unit> allUnits = Client.getGameData().getBattleField().getUnits();
                    
                    // Strategy 1: For MOVE actions, the unit should be at the target location after moving
                    if (action == Action.MOVE) {
                        unit = Client.getGameData().getBattleField().getUnitAt(target);
                        if (unit != null) {
                            Logger.debug("Found unit for move at target: " + unit.getName() + " at " + target);
                        }
                    }
                    
                    // Strategy 2: Search for unit at actor location (might have moved but action is replayed)
                    if (unit == null) {
                        unit = Client.getGameData().getBattleField().getUnitAt(actor);
                    }
                    
                    // Strategy 3: Search all units for one with matching action type AND location near actor/target
                    if (unit == null) {
                        Unit bestMatch = null;
                        int bestDistance = Integer.MAX_VALUE;
                        for (int i = 0; i < allUnits.size(); i++) {
                            Unit u = allUnits.elementAt(i);
                            Vector<Action> actions = u.getActions();
                            for (int j = 0; j < actions.size(); j++) {
                                Action a = actions.elementAt(j);
                                if (a.getType() == action) {
                                    // Found a unit with matching action type
                                    // Prefer units closer to the actor location
                                    int distance = BattleField.getDistance(u.getLocation(), actor);
                                    if (distance < bestDistance) {
                                        bestMatch = u;
                                        bestDistance = distance;
                                    }
                                }
                            }
                        }
                        if (bestMatch != null) {
                            unit = bestMatch;
                            Logger.debug("Found unit by action type and proximity: " + unit.getName() + " at " + unit.getLocation() + " (distance " + bestDistance + " from " + actor + ")");
                        }
                    }
                    
                    if (unit == null) {
                        Logger.warn("process: Unit action " + action + " at location " + actor + " to " + target + " - unit not found (total units: " + allUnits.size() + ")");
                        // Log all units for debugging
                        for (int i = 0; i < Math.min(allUnits.size(), 10); i++) {
                            Unit u = allUnits.elementAt(i);
                            Logger.debug("  Unit " + i + ": " + u.getName() + " at " + u.getLocation() + ", castle=" + (u.getCastle() == Client.getGameData().getMyCastle() ? "myCastle" : "enemyCastle"));
                        }
                        return;
                    }
                }
                // Find the action index for this unit (performAction expects index, not type)
                Vector<Action> unitActions = unit.getActions();
                short actionIndex = -1;
                for (short i = 0; i < unitActions.size(); i++) {
                    Action a = unitActions.elementAt(i);
                    if (a.getType() == action) {
                        actionIndex = i;
                        break;
                    }
                }
                if (actionIndex == -1) {
                    Logger.warn("process: Unit " + unit.getName() + " at " + unit.getLocation() + " doesn't have action type " + action);
                    return;
                }
                String result = unit.performAction(actionIndex, target);
                if (result != null) {
                    Client.getGameData().getTextBoard().add(result);
                }
            }

            switch (action) {
                case Action.TIME_OUT:
                    Client.timeOut();
                    break;

                case Action.NOOB:
                    if (!BuildConfig.skipTutorial) {
                        Client.getGameData().noob();
                    }
                    break;

                case Action.QUIT:
                    System.exit(0);
                    break;

                case Action.GROW:
                    Client.getGameData().getBattleField().getUnitAt(actor).grow(target);
                    break;

                case Action.DISCONNECT:
                    Client.restart();
                    Client.getGameData().opponentDisconnect();
                    break;

                case Action.RESYNCH:
                    Client.restart();
                    Client.getGameData().resynch();
                    break;

                case Action.RESYNCH_READY:
                    Client.getGameData().setPlaying(true);
                    break;

                case Action.END_RESYNCH:
                    Client.getGameData().endResynch();
                    break;

                case Action.TOP_SCORES:
                    String topString = dis.readUTF();
                    Client.getGameData().showHighScores(topString);

                    //Thread.sleep(500);
                    //ScoresBox top = new ScoresBox(topString);
                    break;

                case Action.NEED_EMAIL:
                    Client.needEmail(true);
                    break;

                case Action.ACCEPT_KEY:
                    ClientMessageDialog npak = new ClientMessageDialog("Congratulations, you've activated " + Unit.GAME_NAME[actor] + "!");
                    break;

                case Action.NO_REFERRAL:
                    ClientMessageDialog noref = new ClientMessageDialog("That address has already been referred.");
                    break;

                case Action.REJECT_KEY:
                    ClientMessageDialog nprk = new ClientMessageDialog("Your registration key was rejected.");
                    AccountFrame af = new AccountFrame(Client.getFrame());
                    break;

                case Action.REGISTER:
                    Client.register(actor);
                    break;

                case Action.DEPLOY_ALLY:
                    Client.getGameData().getMyCastle().add(0, Unit.getUnit(actor, Client.getGameData().getMyCastle()));
                    Client.getGameData().getTextBoard().add(Client.getGameData().getMyCastle().deploy(Unit.TEAM_2, Client.getGameData().getMyCastle().getUnit(0), target));
                    break;

                case Action.DEPLOY:
                    Logger.info("DEPLOY received: actor=" + actor + ", target=" + target);
                    Unit deployUnit = Client.getGameData().getMyCastle().getUnit(actor);
                    if (deployUnit == null) {
                        Logger.error("DEPLOY failed: Unit at index " + actor + " not found in myCastle. myCastle has " + Client.getGameData().getMyCastle().getBarracks().size() + " unit types");
                    } else {
                        Logger.info("DEPLOY: Deploying " + deployUnit.getName() + " from myCastle to location " + target);
                        String deployResult = Client.getGameData().getMyCastle().deploy(Unit.TEAM_1, deployUnit, target);
                        Client.getGameData().getTextBoard().add(deployResult);
                        // Check if unit was actually deployed
                        Unit deployedUnit = Client.getGameData().getBattleField().getUnitAt(target);
                        if (deployedUnit != null) {
                            Logger.info("DEPLOY: Unit " + deployedUnit.getName() + " deployed at " + target + ", hidden=" + deployedUnit.isHidden() + ", location=" + deployedUnit.getLocation());
                        } else {
                            Logger.warn("DEPLOY: Unit not found at target location " + target + " after deploy");
                        }
                        Logger.info("DEPLOY: After deploy, battlefield has " + (Client.getGameData().getBattleField() != null ? Client.getGameData().getBattleField().getUnits().size() : 0) + " units");
                    }
                    break;

                case Action.END_TURN:
                    Client.getGameData().endTurn(false);
                    break;

                case Action.REFRESH:
                    Client.getGameData().getMyCastle().refresh(Unit.TEAM_1);
                    break;

                case Action.REFRESH_ENEMY:
                    Client.getGameData().getEnemyCastle().refresh(Unit.TEAM_1);
                    break;

                case Action.REFRESH_ENEMY_ALLY:
                    Client.getGameData().getEnemyCastle().refresh(Unit.TEAM_2);
                    break;

                case Action.REFRESH_ALLY:
                    Client.getGameData().getMyCastle().refresh(Unit.TEAM_2);
                    break;

                case Action.DEPLOY_ENEMY:
                    // In arena games, units already exist in the castle, so find by index
                    // In other games, actor is unit ID and we need to add the unit first
                    Logger.info("DEPLOY_ENEMY received: actor=" + actor + ", target=" + target);
                    Logger.info("enemyCastle has " + Client.getGameData().getEnemyCastle().getBarracks().size() + " unit types");
                    Unit enemyUnit = Client.getGameData().getEnemyCastle().getUnit(actor);
                    if (enemyUnit == null) {
                        // In arena mode, the unit might have been deployed already before spectator joined
                        // Check if unit already exists on battlefield at target location
                        Unit existingUnit = Client.getGameData().getBattleField().getUnitAt(target);
                        if (existingUnit != null && existingUnit.getCastle() == Client.getGameData().getEnemyCastle()) {
                            Logger.info("DEPLOY_ENEMY: Unit already deployed at target " + target + ": " + existingUnit.getName());
                            // Unit already deployed, skip
                            break;
                        }
                        // Unit doesn't exist, try to add it
                        // In arena mode, we need to figure out the unit ID from the index
                        // For now, try adding units until we get the right index
                        Logger.warn("DEPLOY_ENEMY: Unit at index " + actor + " not found in enemyCastle, trying to add units to match index");
                        Vector<UndeployedUnit> barracks = Client.getGameData().getEnemyCastle().getBarracks();
                        // Add units until we have enough to reach the index
                        while (barracks.size() <= actor) {
                            // We don't know the unit ID, so we can't add it properly
                            // This is a fallback - ideally the unit should have been sent via NEW_ENEMY_UNIT
                            Logger.error("DEPLOY_ENEMY: Cannot determine unit ID for index " + actor + ", skipping deploy");
                            break;
                        }
                        if (barracks.size() > actor) {
                            enemyUnit = Client.getGameData().getEnemyCastle().getUnit(actor);
                        }
                    }
                    if (enemyUnit == null) {
                        Logger.error("DEPLOY_ENEMY failed: Could not find or create unit at index " + actor);
                    } else {
                        Logger.info("DEPLOY_ENEMY: Deploying " + enemyUnit.getName() + " from enemyCastle to location " + target);
                        String deployResult = Client.getGameData().getEnemyCastle().deploy(Unit.TEAM_1, enemyUnit, target);
                        Client.getGameData().getTextBoard().add(deployResult);
                        // Check if unit was actually deployed
                        Unit deployedUnit = Client.getGameData().getBattleField().getUnitAt(target);
                        if (deployedUnit != null) {
                            Logger.info("DEPLOY_ENEMY: Unit " + deployedUnit.getName() + " deployed at " + target + ", hidden=" + deployedUnit.isHidden() + ", location=" + deployedUnit.getLocation());
                        } else {
                            Logger.warn("DEPLOY_ENEMY: Unit not found at target location " + target + " after deploy");
                        }
                        Logger.info("DEPLOY_ENEMY: After deploy, battlefield has " + (Client.getGameData().getBattleField() != null ? Client.getGameData().getBattleField().getUnits().size() : 0) + " units");
                    }
                    break;

                case Action.DEPLOY_ENEMY_ALLY:
                    Client.getGameData().getEnemyCastle().add(Unit.getUnit(actor, Client.getGameData().getEnemyCastle()));
                    Client.getGameData().getTextBoard().add(Client.getGameData().getEnemyCastle().deploy(Unit.TEAM_2, Client.getGameData().getEnemyCastle().getUnit(0), target));
                    break;

                case Action.NEW_UNIT:
                    Logger.info("NEW_UNIT received: unitID=" + actor + ", adding to myCastle");
                    Client.getGameData().getMyCastle().add(Unit.getUnit(actor, Client.getGameData().getMyCastle()));
                    Logger.info("myCastle now has " + Client.getGameData().getMyCastle().getBarracks().size() + " unit types, total units: " + getTotalUnitCount(Client.getGameData().getMyCastle()));
                    Client.getGameData().castleChange();
                    break;

                case Action.NEW_ENEMY_UNIT:
                    // Add unit to enemy castle (for arena games)
                    Logger.info("NEW_ENEMY_UNIT received: unitID=" + actor + ", adding to enemyCastle");
                    Client.getGameData().getEnemyCastle().add(Unit.getUnit(actor, Client.getGameData().getEnemyCastle()));
                    Logger.info("enemyCastle now has " + Client.getGameData().getEnemyCastle().getBarracks().size() + " unit types, total units: " + getTotalUnitCount(Client.getGameData().getEnemyCastle()));
                    break;

                case Action.CLEAR_CASTLE:
                    Client.getGameData().getMyCastle().clear();
                    break;

                case Action.NEW_ARMY_UNIT:
                    Client.getGameData().getArmy().add(Unit.getUnit(actor, Client.getGameData().getArmy()));
                    Client.getGameData().castleChange();
                    break;

                case Action.UNLOCK_UNITS:
                    Client.getUnits()[actor] = target;
                    break;

                case Action.RECRUIT_UNIT:
                    Client.getGameData().getMyCastle().getObserver().playSound(Constants.SOUND_BUY);
                    Client.getUnits()[actor] = target;
                    Client.getGameData().recruit(actor);
                    break;

                case Action.START_TURN_ENEMY_ALLY:
                    Client.getGameData().getMyCastle().getObserver().playSound(Constants.SOUND_END_TURN);
                    Client.getGameData().getEnemyCastle().startTurn(Unit.TEAM_2);
                    Client.getGameData().setCastlePlaying(Client.getGameData().getEnemyCastle());
                    break;

                case Action.START_TURN_ENEMY:
                    Client.getGameData().getMyCastle().getObserver().playSound(Constants.SOUND_END_TURN);
                    Client.getGameData().getEnemyCastle().startTurn(Unit.TEAM_1);
                    Client.getGameData().setCastlePlaying(Client.getGameData().getEnemyCastle());
                    break;

                case Action.P1_TURN:
                    Client.getGameData().setCurrPlayer(1);
                    break;

                case Action.P2_TURN:
                    Client.getGameData().setCurrPlayer(2);
                    break;

                case Action.START_TURN:
                    Client.getGameData().getMyCastle().getObserver().playSound(Constants.SOUND_START_TURN);
                    Client.getGameData().getMyCastle().startTurn(Unit.TEAM_1);
                    Client.getGameData().setTimer(90);
                    //System.out.println("My turn.");
                    if (Client.getGameData().getMyCastle().depleted() && !Client.getGameData().drawOffered() && !Client.getGameData().getEnemyCastle().depleted()) {
                        try {
                            Thread.sleep(500);
                        } catch (Exception e) {
                        }
                        Client.getGameData().endTurn();
                    } else {
                        Client.getGameData().setCastlePlaying(Client.getGameData().getMyCastle());
                    }
                    break;


                case Action.START_TURN_ALLY:
                    Client.getGameData().getMyCastle().getObserver().playSound(Constants.SOUND_START_TURN);
                    Client.getGameData().getMyCastle().startTurn(Unit.TEAM_2);
                    Client.getGameData().setCastlePlaying(null);
                    break;


                case Action.START_GAME:
                    Logger.info("START_GAME received, actor=" + actor);
                    Client.getImages().stopMusic();
                    Client.getGameData().screenGame();

                    Client.getChat().disallowRematch();

                    if (actor != Action.SET_RANDOM) {
                        Client.getGameData().setPanelLocation();
                        Client.getGameData().setGameType(Constants.CONSTRUCTED);
                    } else
                        Client.getGameData().setGameType(Constants.RANDOM);
                    Logger.info("START_GAME processed, playing=" + Client.getGameData().playing() + ", battleField=" + (Client.getGameData().getBattleField() != null));
                    break;

                case Action.ENEMY_LEFT:
                    leo.shared.Observer observer = Client.getGameData().getMyCastle().getObserver();
                    observer.enemySurrendered();
                    break;

                case Action.ALLY_LEFT:
                    leo.shared.Observer observer2 = Client.getGameData().getMyCastle().getObserver();
                    observer2.allySurrendered();
                    break;

                case Action.SET_RATING:
                    Client.setRating(actor, target);
                    break;

                case Action.SET_RANK:
                    Client.setRank(actor, target);
                    break;

                case Action.SET_WINS:
                    Client.setWins(actor, target);
                    break;

                case Action.SET_LOSSES:
                    Client.setLosses(actor, target);
                    break; 

                case Action.SET_GOLD:
                    try {
                        Client.setGold(dis.readLong());
                    } catch (Exception e) {
                    }
                    //Client.setGold(actor, target);
                    break;

                case Action.OPPONENT:
                    getOpponent();
                    Client.getGameData().screenVersus();
                    Client.getImages().stopMusic();
                    try {
                        Thread.sleep(4000);
                    } catch (Exception e) {
                    }
                    break;


                case Action.NEW_GAME:
                    // For arena games, don't restart - just set up the game screen
                    // Check if we're waiting for arena or already in arena state
                    Logger.info("NEW_GAME received, current state: " + Client.getState());
                    if (Client.getState().equals("home") || Client.getState().equals("lobby") || 
                        Client.getState().equals("game")) {
                        // This is likely an arena game starting
                        Logger.info("Setting up arena game screen");
                        Client.getImages().stopMusic();
                        Client.getGameData().screenGame();
                        Client.getGameData().setPlaying(true);
                        Logger.info("Game screen set up, playing=" + Client.getGameData().playing());
                    } else {
                        Logger.info("Restarting client for NEW_GAME");
                        Client.restart();
                    }
                    break;

                case Action.NEW_CASTLE:
                    break;

                case Action.NEW_ARMY:
                    Client.getGameData().getArmy().clear();
                    break;

                case Action.CANCEL:
                    //Client.getGameData().screenRoster();
                    Client.getGameData().cancelQueue();
                    break;

                case Action.SERVER_WILL_SHUTDOWN:
                    Client.setServerWillShutDown(true);
                    //Client.getGameData().screenRoster();
                    //Client.getGameData().screenMessage("Server is shutting down, can't start a new game.");
                    break;

                case Action.CLEAR_TEAM:
                    Client.getGameData().getTeamLoadingPanel().clearTeams();
                    break;

                case Action.SELECT_TEAM:
                    int chatplayerid = dis.readInt();
                    ChatPlayer chatplayer = Client.getPlayer(chatplayerid);
                    if (chatplayer != null)
                        Client.getGameData().getTeamLoadingPanel().setTeam("" + chatplayer, actor, target);
                    else
                        Client.getGameData().getTeamLoadingPanel().setTeam("", actor, target);
                    break;

                case Action.NEW_PASSWORD:
                    ClientMessageDialog npa = new ClientMessageDialog("Your password was accepted");
                    break;

                case Action.REJECT_PASSWORD:
                    ClientMessageDialog npr = new ClientMessageDialog("Your password was rejected");
                    break;

                case Action.AI:
                    Client.getGameData().getEnemyCastle().ai();
                    break;

                case Action.ARENA_STATE:
                    // Arena game state - level1 in actor, level2 in target
                    Logger.info("Arena game state: AI Level " + actor + " vs AI Level " + target);
                    break;

                case Action.ARENA_TURN:
                    // Arena turn indicator - actor indicates which AI's turn (1 or 2)
                    Logger.debug("Arena turn: AI " + actor);
                    if (actor == 1) {
                        Client.getGameData().setCastlePlaying(Client.getGameData().getMyCastle());
                    } else if (actor == 2) {
                        Client.getGameData().setCastlePlaying(Client.getGameData().getEnemyCastle());
                    }
                    break;

                case Action.ARENA_RESULT:
                    // Arena game result
                    Logger.info("Arena game result received");
                    break;

                case Action.ARENA_GAME_LIST:
                    getArenaGameList();
                    break;

                case Action.SEND_ARCHIVE:
                    getCastleArchives();
                    break;
   
   /*case Action.SET_CONSTRUCTED:
 Client.getGameData().setGameType(Constants.CONSTRUCTED);
 //Client.getGameData().setPanelLocation();
 break;
   
   case Action.SET_RANDOM:
 Client.getGameData().setGameType(Constants.RANDOM);
 break;
   
   case Action.SET_MIRRORED_RANDOM:
 Client.getGameData().setGameType(Constants.MIRRORED_RANDOM);
 //Client.getGameData().setPanelLocation();
 break;*/

                case Action.DISABLE_REPICK_P1:
                    Client.getGameData().DisableRepickP1();
                    break;

                case Action.DISABLE_REPICK_P2:
                    Client.getGameData().DisableRepickP2();
                    break;

                case Action.MOVE_PANEL:
                    Client.getGameData().setPanelLocation();
                    break;

                case Action.OFFER_DRAW:
                    if (Client.getGameData().getMyDraw()) {
                        Client.getGameData().getMyCastle().getObserver().drawGame();
                        break;
                    }

                    if (Client.getGameData().drawOffered()) {
                        Client.addText(Client.getGameData().getEnemyName() + " has accepted your draw.");
                    } else {
                        Client.addText(Client.getGameData().getEnemyName() + " has offered you a draw.");
                        Client.getGameData().offerDraw();
                    }
                    break;

                case Action.PING:
                    //System.out.println("Client receiving ping");
                    break;                 
            }
        } catch (Exception e) {
            Logger.error("process: " + action + " " + actor + " " + target + " " + e);
            throw e;
        }
    }


    /////////////////////////////////////////////////////////////////
    // Send a new password
    /////////////////////////////////////////////////////////////////
    public void sendNewPassword(String oldPassword, String newPassword) {
        try {
            dos.writeShort(Action.NEW_PASSWORD);
            dos.writeUTF(oldPassword);
            dos.writeUTF(newPassword);
        } catch (Exception e) {
            Logger.error("sendNewPassword: " + e);
            Client.getGameData().screenDisconnect();
        }
    }


    /////////////////////////////////////////////////////////////////
    // send your email
    /////////////////////////////////////////////////////////////////
    public void sendEmail(String email) {
        try {
            dos.writeShort(Action.NEED_EMAIL);
            dos.writeUTF(email);
        } catch (Exception e) {
            Logger.error("sendEmail: " + e);
            Client.getGameData().screenDisconnect();
        }
    }


    /////////////////////////////////////////////////////////////////
    // send the referral
    /////////////////////////////////////////////////////////////////
    public void referFriend(String email) {
        try {
            dos.writeShort(Action.REFER_FRIEND);
            dos.writeUTF(email);
        } catch (Exception e) {
            Logger.error("referFriend " + e);
            Client.getGameData().screenDisconnect();
        }
    }


    /////////////////////////////////////////////////////////////////
    // Get arena game list
    /////////////////////////////////////////////////////////////////
    private void getArenaGameList() {
        try {
            int count = dis.readInt();
            Logger.info("Received arena game list with " + count + " games");
            Vector<ArenaGameInfo> games = new Vector<ArenaGameInfo>();
            for (int i = 0; i < count; i++) {
                int gameId = dis.readInt();
                int level1 = dis.readInt();
                int level2 = dis.readInt();
                int spectatorCount = dis.readInt();
                short lastWinner = dis.readShort();
                games.add(new ArenaGameInfo(gameId, level1, level2, spectatorCount, lastWinner));
                Logger.info("Arena game: ID=" + gameId + ", Level " + level1 + " vs " + level2 + ", Spectators=" + spectatorCount);
            }
            // Use EventQueue to ensure UI updates happen on EDT
            final Vector<ArenaGameInfo> gamesToShow = games;
            java.awt.EventQueue.invokeLater(() -> {
                Client.getGameData().showArenaGameList(gamesToShow);
            });
        } catch (Exception e) {
            Logger.error("ClientNetManager.getArenaGameList: " + e);
            Logger.error("Stack trace: ", e);
        }
    }

    /////////////////////////////////////////////////////////////////
    // Arena game info class
    /////////////////////////////////////////////////////////////////
    public static class ArenaGameInfo {
        public final int gameId;
        public final int level1;
        public final int level2;
        public final int spectatorCount;
        public final short lastWinner;

        public ArenaGameInfo(int gameId, int level1, int level2, int spectatorCount, short lastWinner) {
            this.gameId = gameId;
            this.level1 = level1;
            this.level2 = level2;
            this.spectatorCount = spectatorCount;
            this.lastWinner = lastWinner;
        }
    }

    /////////////////////////////////////////////////////////////////
    // Helper to count total units in a castle
    /////////////////////////////////////////////////////////////////
    private int getTotalUnitCount(Castle castle) {
        int total = 0;
        Vector<UndeployedUnit> barracks = castle.getBarracks();
        for (int i = 0; i < barracks.size(); i++) {
            total += barracks.elementAt(i).count();
        }
        return total;
    }

    /////////////////////////////////////////////////////////////////
    // Get the castle archives
    /////////////////////////////////////////////////////////////////
    private void getCastleArchives() {
        try {
            for (int i = 0; i < 10; i++) {
                String name = dis.readUTF();
                short size = dis.readShort();
                if (size > 0) {
                    Client.getCastleArchives()[i] =
                            new CastleArchive(name, size);
                } else {
                    Client.getCastleArchives()[i] =
                            new CastleArchive("<empty>", size);
                }

                //System.out.println
                // (
                // Client.getCastleArchives()[i].toString()
                // + ": " +
                // Client.getCastleArchives()[i].size()
                // );
            }
        } catch (Exception e) {
            Logger.error("getCastleArchive: " + e);
            Client.getGameData().screenDisconnect();
        }
    }


    /////////////////////////////////////////////////////////////////
    // Opponent info
    /////////////////////////////////////////////////////////////////
    private void getOpponent() {
        try {
            int enemyRating = dis.readInt();
            char tmp;
            String name = "";
            while (true) {
                tmp = dis.readChar();
                if (tmp != 0)
                    name = name + tmp;
                else {
                    Client.getGameData().setOpponent(enemyRating, name);
                    return;
                }
            }

        } catch (Exception e) {
            Logger.error("ClientNetManager.getOpponent: " + e);
            Client.getGameData().screenDisconnect();
        }
    }


    /////////////////////////////////////////////////////////////////
    // Send action
    /////////////////////////////////////////////////////////////////
    public void sendAction(short action, short actor, short target) {
        try {
            dos.writeShort(action);
            dos.writeShort(actor);
            dos.writeShort(target);
        } catch (Exception e) {
            Logger.error("ClientNetManager.sendAction: " + e);
            Client.getGameData().screenDisconnect();
        }
    }


    /////////////////////////////////////////////////////////////////
    // Send action
    /////////////////////////////////////////////////////////////////
    public void sendAction(short action) {
        try {
            dos.writeShort(action);
        } catch (Exception e) {
            Logger.error("ClientNetManager.sendAction: " + e);
            Client.getGameData().screenDisconnect();
        }
    }


    /////////////////////////////////////////////////////////////////
    // Send castle
    /////////////////////////////////////////////////////////////////
    public void sendCastle() {
        try {
            Vector units = Client.getGameData().getArmy().getBarracks();
            dos.writeShort(Action.SET_ARMY);

            for (int i = 0; i < units.size(); i++) {
                UndeployedUnit unit = (UndeployedUnit) units.elementAt(i);
                for (int c = 0; c < unit.count(); c++)
                    dos.writeShort(unit.getID());
            }
            dos.writeShort(Action.END_ARMY);
        } catch (Exception e) {
            Logger.error("sendCastle " + e);
            Client.getGameData().screenDisconnect();
        }
    }


    /////////////////////////////////////////////////////////////////
    // Save a castle
    /////////////////////////////////////////////////////////////////
    public void saveCastleArchive(short index, String name) {
        try {
            dos.writeShort(Action.SAVE_ARCHIVE);
            dos.writeShort(index);
            dos.writeUTF(name);

        } catch (Exception e) {
            Logger.error("saveCastleArchive " + e);
            Client.getGameData().screenDisconnect();
        }
    }


    /////////////////////////////////////////////////////////////////
    // send a byte
    /////////////////////////////////////////////////////////////////
    public void sendByte(short sendMe) {
        try {
            dos.writeShort(sendMe);

        } catch (Exception e) {
            Logger.error("sendByte " + e);
            Client.getGameData().screenDisconnect();
        }
    }


    /////////////////////////////////////////////////////////////////
    // Try to register
    /////////////////////////////////////////////////////////////////
    public void register(String key) {
        try {
            dos.writeShort(Action.REGISTER);
            dos.writeUTF(key);

        } catch (Exception e) {
            Logger.error("register " + e);
            Client.getGameData().screenDisconnect();
        }
    }


    /////////////////////////////////////////////////////////////////
    // Shut down
    /////////////////////////////////////////////////////////////////
    public void stop() { //active = false;
    }


    /////////////////////////////////////////////////////////////////
    // Shut down
    /////////////////////////////////////////////////////////////////
    public void kill() {
        try {
            active = false;
            if (socket != null)
                socket.close();
        } catch (Exception e) {
            Logger.error("ClientNetManager.kill: " + e);
        } finally {
            socket = null;
            dis = null;
            dos = null;
        }

    }
}
