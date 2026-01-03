///////////////////////////////////////////////////////////////////////
// Name: ArenaGameListPanel
// Desc: Display list of active arena games for spectating
// Date: 1/2/2026
// TODO:
///////////////////////////////////////////////////////////////////////
package leo.client;

// imports

import leo.shared.Constants;
import org.tinylog.Logger;

import java.awt.*;
import java.util.Vector;


public class ArenaGameListPanel extends LeoContainer {

    /////////////////////////////////////////////////////////////////
    // Properties
    /////////////////////////////////////////////////////////////////
    private Vector<ClientNetManager.ArenaGameInfo> games = new Vector<ClientNetManager.ArenaGameInfo>();
    private final Vector<ArenaGameButton> gameButtons = new Vector<ArenaGameButton>();

    /////////////////////////////////////////////////////////////////
    // Constructor
    /////////////////////////////////////////////////////////////////
    public ArenaGameListPanel() {
        super(Constants.OFFSET,
                Constants.OFFSET,
                Constants.SCREEN_WIDTH - (Constants.OFFSET * 2),
                Constants.SCREEN_HEIGHT - (Constants.OFFSET * 2));

        // Cancel button
        add(new CancelButton(
                (getWidth() / 2) - 50,
                getHeight() - 65,
                100,
                25));

        // Refresh button
        add(new RefreshButton(
                (getWidth() / 2) + 60,
                getHeight() - 65,
                100,
                25));
    }

    /////////////////////////////////////////////////////////////////
    // Set games list
    /////////////////////////////////////////////////////////////////
    public void setGames(Vector<ClientNetManager.ArenaGameInfo> newGames) {
        Logger.info("ArenaGameListPanel.setGames() called with " + newGames.size() + " games");
        // Remove old buttons
        for (int i = 0; i < gameButtons.size(); i++) {
            remove(gameButtons.elementAt(i));
        }
        gameButtons.clear();

        games = newGames;

        // Create buttons for each game
        int startY = 100;
        int buttonHeight = 60;
        int spacing = 10;
        int maxGames = Math.min(games.size(), 8); // Show max 8 games

        for (int i = 0; i < maxGames; i++) {
            ClientNetManager.ArenaGameInfo game = games.elementAt(i);
            int y = startY + (i * (buttonHeight + spacing));
            ArenaGameButton button = new ArenaGameButton(
                    getScreenX() + 50,
                    y,
                    getWidth() - 100,
                    buttonHeight,
                    game
            );
            add(button);
            gameButtons.add(button);
        }

        if (games.size() == 0) {
            // Show "No games available" message
            Logger.info("No arena games available - showing empty list");
        } else {
            Logger.info("Displaying " + games.size() + " arena games in list");
        }
    }

    /////////////////////////////////////////////////////////////////
    // Refresh button
    /////////////////////////////////////////////////////////////////
    private class RefreshButton extends LeoComponent {
        public RefreshButton(int x, int y, int width, int height) {
            super(x, y, width, height);
        }

        public void draw(Graphics2D g, Frame mainFrame) {
            g.setColor(Color.BLUE);
            g.fillRect(getScreenX(), getScreenY(), getWidth(), getHeight());
            g.setColor(Color.WHITE);
            FontMetrics fm = g.getFontMetrics();
            String text = "Refresh";
            int textX = getScreenX() + (getWidth() - fm.stringWidth(text)) / 2;
            int textY = getScreenY() + (getHeight() + fm.getAscent()) / 2 - 2;
            g.drawString(text, textX, textY);
        }

        public boolean clickAt(int x, int y) {
            if (isWithin(x, y)) {
                Client.getNetManager().requestArenaGameList();
                return true;
            }
            return false;
        }
    }

    /////////////////////////////////////////////////////////////////
    // Arena game button
    /////////////////////////////////////////////////////////////////
    private class ArenaGameButton extends LeoComponent {
        private final ClientNetManager.ArenaGameInfo gameInfo;

        public ArenaGameButton(int x, int y, int width, int height, ClientNetManager.ArenaGameInfo gameInfo) {
            super(x, y, width, height);
            this.gameInfo = gameInfo;
        }

        public void draw(Graphics2D g, Frame mainFrame) {
            // Background
            g.setColor(Color.DARK_GRAY);
            g.fillRect(getScreenX(), getScreenY(), getWidth(), getHeight());
            g.setColor(Color.BLACK);
            g.drawRect(getScreenX(), getScreenY(), getWidth() - 1, getHeight() - 1);

            // Text
            g.setColor(Color.WHITE);
            FontMetrics fm = g.getFontMetrics();
            String gameText = "Game #" + gameInfo.gameId + ": AI Level " + gameInfo.level1 + " vs AI Level " + gameInfo.level2;
            String spectatorText = "Spectators: " + gameInfo.spectatorCount;
            
            int textY = getScreenY() + (getHeight() / 2) - 5;
            g.drawString(gameText, getScreenX() + 10, textY);
            g.drawString(spectatorText, getScreenX() + 10, textY + fm.getHeight());
        }

        public boolean clickAt(int x, int y) {
            if (isWithin(x, y)) {
                Client.getNetManager().requestWatchArenaGame(gameInfo.gameId);
                Client.getGameData().screenLoading("Connecting to arena game...");
                return true;
            }
            return false;
        }
    }
}

