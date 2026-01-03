///////////////////////////////////////////////////////////////////////
// Name: LobbyAIArena
// Desc: Schedules AI vs AI arena matches
// TODO:
///////////////////////////////////////////////////////////////////////
package leo.server.lobby;

// imports

import leo.server.CastleArchive;
import leo.server.Server;
import leo.server.User;
import leo.server.game.AIArenaGame;
import leo.shared.Log;
import org.tinylog.Logger;

import java.util.Stack;
import java.util.Vector;


public class LobbyAIArena implements Runnable {

    /////////////////////////////////////////////////////////////////
    // Properties
    /////////////////////////////////////////////////////////////////
    private final Server server;
    private final Thread runner;
    private final Vector<User> spectators = new Vector<User>();
    private final Vector<User> pendingSpectators = new Vector<User>();
    private final Stack<User> removes = new Stack<User>();
    private final Vector<ArenaRequest> requests = new Vector<ArenaRequest>();
    private final boolean autoLoop;
    private volatile boolean running = true;
    private volatile AIArenaGame currentGame = null;
    private final Vector<AIArenaGame> activeGames = new Vector<AIArenaGame>();
    private int nextGameId = 1;


    /////////////////////////////////////////////////////////////////
    // Arena request
    /////////////////////////////////////////////////////////////////
    public static class ArenaRequest {
        public final int aiLevel1;
        public final int aiLevel2;
        public final Long seed;
        public final CastleArchive castle1;
        public final CastleArchive castle2;

        public ArenaRequest(int aiLevel1, int aiLevel2, Long seed, CastleArchive castle1, CastleArchive castle2) {
            this.aiLevel1 = aiLevel1;
            this.aiLevel2 = aiLevel2;
            this.seed = seed;
            this.castle1 = castle1;
            this.castle2 = castle2;
        }
    }


    /////////////////////////////////////////////////////////////////
    // Constructor
    /////////////////////////////////////////////////////////////////
    public LobbyAIArena(Server server, boolean autoLoop) {
        this.server = server;
        this.autoLoop = autoLoop;
        runner = new Thread(this, "LobbyAIArenaThread");
        runner.start();
    }


    /////////////////////////////////////////////////////////////////
    // Add a spectator to the lobby
    /////////////////////////////////////////////////////////////////
    public void addSpectator(User spectator) {
        if (spectator == null) return;
        pendingSpectators.add(spectator);
    }


    /////////////////////////////////////////////////////////////////
    // Schedule a match
    /////////////////////////////////////////////////////////////////
    public void scheduleMatch(User spectator, ArenaRequest request) {
        if (spectator != null) pendingSpectators.add(spectator);
        if (request != null) requests.add(request);
    }


    /////////////////////////////////////////////////////////////////
    // Main thread
    /////////////////////////////////////////////////////////////////
    public void run() {
        while (running) {
            try {
                cleanSpectators();

                // Clean up finished games
                for (int i = activeGames.size() - 1; i >= 0; i--) {
                    AIArenaGame game = activeGames.elementAt(i);
                    if (game.over()) {
                        activeGames.removeElementAt(i);
                        Log.system("Removed finished game ID=" + game.getGameId() + " from activeGames");
                    }
                }
                // Also clear currentGame if it's over
                if (currentGame != null && currentGame.over()) {
                    Log.system("currentGame ID=" + currentGame.getGameId() + " is over, will be replaced");
                }

                // Start new game if needed
                if ((currentGame == null || currentGame.over()) && (requests.size() > 0 || autoLoop)) {
                    // Remove finished currentGame from activeGames if it exists
                    if (currentGame != null && currentGame.over()) {
                        activeGames.remove(currentGame);
                    }
                    
                    ArenaRequest request = requests.size() > 0 ? requests.remove(0) : defaultRequest();
                    try {
                        int gameId = nextGameId++;
                        currentGame = new AIArenaGame(
                                server,
                                request.aiLevel1,
                                request.aiLevel2,
                                request.castle1,
                                request.castle2,
                                request.seed != null ? request.seed : server.getSeed(),
                                "AI Level " + request.aiLevel1,
                                "AI Level " + request.aiLevel2,
                                gameId
                        );
                        // Add to activeGames immediately when created
                        activeGames.add(currentGame);
                        Log.system("Started new arena game ID=" + gameId + ", total active games: " + activeGames.size());
                    } catch (Exception e) {
                        Logger.error("LobbyAIArena starting game: " + e);
                        currentGame = null;
                    }
                    attachAllSpectators();
                } else if (currentGame != null) {
                    attachNewSpectators();
                }

                Thread.sleep(500);
            } catch (Exception e) {
                Log.error("LobbyAIArena.run " + e);
            }
        }
    }

    private ArenaRequest defaultRequest() {
        return new ArenaRequest(5, 5, server.getSeed(), null, null);
    }

    private void cleanSpectators() {
        for (int i = 0; i < spectators.size(); i++) {
            User user = spectators.elementAt(i);
            if (user.getPlayer() == null || user.isClosed()) {
                removes.add(user);
            }
        }
        for (int i = 0; i < pendingSpectators.size(); i++) {
            User user = pendingSpectators.elementAt(i);
            if (user.getPlayer() == null || user.isClosed()) {
                removes.add(user);
            }
        }

        while (removes.size() > 0) {
            User user = removes.pop();
            spectators.remove(user);
            pendingSpectators.remove(user);
        }
    }

    private void attachAllSpectators() {
        if (currentGame == null) return;
        Vector<User> all = new Vector<User>();
        all.addAll(spectators);
        all.addAll(pendingSpectators);
        spectators.clear();
        pendingSpectators.clear();

        for (int i = 0; i < all.size(); i++) {
            User user = all.elementAt(i);
            if (!spectators.contains(user)) spectators.add(user);
            currentGame.addSpectator(user);
        }
    }

    private void attachNewSpectators() {
        if (currentGame == null) return;
        while (pendingSpectators.size() > 0) {
            User user = pendingSpectators.remove(0);
            if (!spectators.contains(user)) spectators.add(user);
            currentGame.addSpectator(user);
        }
    }


    /////////////////////////////////////////////////////////////////
    // Get list of active games
    /////////////////////////////////////////////////////////////////
    public Vector<AIArenaGame> getActiveGames() {
        Vector<AIArenaGame> games = new Vector<AIArenaGame>();
        // Include currentGame if it exists and is not over
        if (currentGame != null && !currentGame.over()) {
            games.add(currentGame);
            Log.system("getActiveGames: Added currentGame ID=" + currentGame.getGameId());
        }
        // Also include any other active games
        for (int i = 0; i < activeGames.size(); i++) {
            AIArenaGame game = activeGames.elementAt(i);
            if (!game.over() && game != currentGame) {
                games.add(game);
                Log.system("getActiveGames: Added game ID=" + game.getGameId());
            }
        }
        Log.system("getActiveGames: Returning " + games.size() + " active games");
        return games;
    }

    /////////////////////////////////////////////////////////////////
    // Get a specific game by ID
    /////////////////////////////////////////////////////////////////
    public AIArenaGame getGameById(int gameId) {
        for (int i = 0; i < activeGames.size(); i++) {
            AIArenaGame game = activeGames.elementAt(i);
            if (game.getGameId() == gameId && !game.over()) {
                return game;
            }
        }
        return null;
    }

    /////////////////////////////////////////////////////////////////
    // Watch a specific game
    /////////////////////////////////////////////////////////////////
    public boolean watchGame(User user, int gameId) {
        AIArenaGame game = getGameById(gameId);
        if (game != null) {
            game.addSpectator(user);
            if (!spectators.contains(user)) spectators.add(user);
            return true;
        }
        return false;
    }

    /////////////////////////////////////////////////////////////////
    // Stop the lobby thread
    /////////////////////////////////////////////////////////////////
    public void stop() {
        Log.system("Stopping lobbyAIArena thread...");
        running = false;
        runner.interrupt();
    }
}
