///////////////////////////////////////////////////////////////////////
// Name: GameMedia
// Desc: The image loader
// Date: 2/13/2003 - Gabe Jones
//   9/13/2010 - Fletcher Cole & Alexander McCaleb
// TODO:
///////////////////////////////////////////////////////////////////////
package leo.client;

// imports
//import leo.client.Client;
//import leo.client.Sound;
//import leo.client.OggClip;

import leo.shared.Constants;
import org.tinylog.Logger;

import javax.imageio.ImageIO;
import java.awt.*;
import java.awt.image.BufferedImage;
//import java.io.BufferedInputStream;
import java.io.File;
import java.net.URL;
import java.net.URLClassLoader;

public class GameMedia {
    public static final int MAX_SOUND_COUNT = 8;
    public static final int MAX_SOUND_INDIVIDUAL = 3;

    /////////////////////////////////////////////////////////////////
    // Properties
    /////////////////////////////////////////////////////////////////
    private final Image[] images = new Image[Constants.IMG_COUNT];
    private final Image[] grayedImages = new Image[Constants.IMG_COUNT];
    private final Image[] rotatedImages = new Image[Constants.IMG_COUNT];
    private final Sound[] sounds = new Sound[Constants.SOUND_COUNT];
    private int soundCount = 0;
    private OggClip music;
    private final Toolkit tk = Toolkit.getDefaultToolkit();
    private boolean soundLoaded = false;
    private boolean artLoaded = false;
    private Image placeholderImage = null; // Cached placeholder image


    /////////////////////////////////////////////////////////////////
    // Constructor
    /////////////////////////////////////////////////////////////////
    public GameMedia() {
    }

    public String getUserDir() {
        return (System.getProperty("user.home") + "/zatikon");

    }

    // Helper method to safely load a sound
    private void loadSoundSafely(ClassLoader soundLoader, int soundIndex, String soundFile) {
        try {
            URL url = soundLoader.getResource(Constants.SOUND_LOC + soundFile);
            if (url != null) {
                sounds[soundIndex] = new Sound(url);
            }
        } catch (UnsatisfiedLinkError e) {
            // LWJGL natives not available, sound will be disabled
            Logger.debug("Sound " + soundFile + " disabled (LWJGL natives not available)");
        } catch (NoClassDefFoundError e) {
            // LWJGL classes not available, sound will be disabled
            Logger.debug("Sound " + soundFile + " disabled (LWJGL classes not available: " + e.getMessage() + ")");
        } catch (Exception e) {
            Logger.warn("Failed to load " + soundFile + ": " + e.getMessage());
        }
    }

    private void loadSounds() {
        URL url;
        URL[] urls = new URL[1];

        try {
            // Load the sound loader
            ClassLoader soundLoader = Thread.currentThread().getContextClassLoader();

            String jarPath = getUserDir() + Constants.SOUND_JAR;
            File jarFile = new File(jarPath);
            if (!jarFile.exists()) {
                Logger.warn("sound.jar not found at: " + jarPath + ", falling back to main JAR resources");
                soundLoader = Thread.currentThread().getContextClassLoader();
            } else {
                urls[0] = jarFile.toURI().toURL();
                soundLoader = new URLClassLoader(urls, Thread.currentThread().getContextClassLoader());
                Logger.info("Loaded sound.jar from: " + jarPath);
            }


            // The background music
            try {
                url = soundLoader.getResource(Constants.SOUND_LOC + "music.ogg");
                if (url != null) {
                    music = new OggClip(url);
                } else {
                    Logger.warn("music.ogg not found, music will be disabled");
                }
            } catch (UnsatisfiedLinkError e) {
                Logger.warn("LWJGL native libraries not available, music will be disabled: " + e.getMessage());
                music = null;
            } catch (NoClassDefFoundError e) {
                Logger.warn("LWJGL classes not available, music will be disabled: " + e.getMessage());
                music = null;
            } catch (Exception e) {
                Logger.error("Failed to load music: " + e);
                music = null;
            }

            int loadingSound;

            loadingSound = Constants.SOUND_VICTORY;
            loadSoundSafely(soundLoader, loadingSound, "victory.wav");

            loadingSound = Constants.SOUND_PRELUDE;
            loadSoundSafely(soundLoader, loadingSound, "prelude.wav");

            loadingSound = Constants.SOUND_BOW;
            loadSoundSafely(soundLoader, loadingSound, "bow.wav");

            loadingSound = Constants.SOUND_XBOW;
            loadSoundSafely(soundLoader, loadingSound, "xbow.wav");

            loadingSound = Constants.SOUND_RELOAD;
            loadSoundSafely(soundLoader, loadingSound, "reload.wav");

            loadingSound = Constants.SOUND_ORG_HIT;
            loadSoundSafely(soundLoader, loadingSound, "orghit.wav");

            loadingSound = Constants.SOUND_ORG_DEATH;
            loadSoundSafely(soundLoader, loadingSound, "orgdeath.wav");

            loadingSound = Constants.SOUND_INORG_HIT;
            loadSoundSafely(soundLoader, loadingSound, "inorghit.wav");

            loadingSound = Constants.SOUND_INORG_DEATH;
            loadSoundSafely(soundLoader, loadingSound, "inorgdeath.wav");

            loadingSound = Constants.SOUND_SWING;
            loadSoundSafely(soundLoader, loadingSound, "swing.wav");

            loadingSound = Constants.SOUND_DETONATE;
            loadSoundSafely(soundLoader, loadingSound, "detonate.wav");

            loadingSound = Constants.SOUND_DEFEAT;
            loadSoundSafely(soundLoader, loadingSound, "defeat.wav");

            loadingSound = Constants.SOUND_END_TURN;
            loadSoundSafely(soundLoader, loadingSound, "endturn.wav");

            loadingSound = Constants.SOUND_START_TURN;
            loadSoundSafely(soundLoader, loadingSound, "startturn.wav");

            loadingSound = Constants.SOUND_EXPLOSION;
            loadSoundSafely(soundLoader, loadingSound, "explosion.wav");

            loadingSound = Constants.SOUND_FIREBALL;
            loadSoundSafely(soundLoader, loadingSound, "fireball.wav");

            loadingSound = Constants.SOUND_BOOM;
            loadSoundSafely(soundLoader, loadingSound, "boom.wav");

            loadingSound = Constants.SOUND_TING;
            loadSoundSafely(soundLoader, loadingSound, "ting.wav");

            loadingSound = Constants.SOUND_POOF;
            loadSoundSafely(soundLoader, loadingSound, "poof.wav");

            loadingSound = Constants.SOUND_MAGIC_BOLT;
            loadSoundSafely(soundLoader, loadingSound, "magicbolt.wav");

            loadingSound = Constants.SOUND_STUNBALL;
            loadSoundSafely(soundLoader, loadingSound, "stunball.wav");

            loadingSound = Constants.SOUND_GROWL;
            loadSoundSafely(soundLoader, loadingSound, "growl.wav");

            loadingSound = Constants.SOUND_EYE;
            loadSoundSafely(soundLoader, loadingSound, "eye.wav");

            loadingSound = Constants.SOUND_JUDGEMENT;
            loadSoundSafely(soundLoader, loadingSound, "judgement.wav");

            loadingSound = Constants.SOUND_START_CHANNEL;
            loadSoundSafely(soundLoader, loadingSound, "startchannel.wav");

            loadingSound = Constants.SOUND_END_CHANNEL;
            loadSoundSafely(soundLoader, loadingSound, "endchannel.wav");

            loadingSound = Constants.SOUND_SQUISH;
            loadSoundSafely(soundLoader, loadingSound, "squish.wav");

            loadingSound = Constants.SOUND_CATAPULT;
            loadSoundSafely(soundLoader, loadingSound, "catapult.wav");

            loadingSound = Constants.SOUND_SHEATH;
            loadSoundSafely(soundLoader, loadingSound, "sheath.wav");

            loadingSound = Constants.SOUND_UNSHEATH;
            loadSoundSafely(soundLoader, loadingSound, "unsheath.wav");

            loadingSound = Constants.SOUND_WRITE;
            loadSoundSafely(soundLoader, loadingSound, "write.wav");

            loadingSound = Constants.SOUND_PAPER;
            loadSoundSafely(soundLoader, loadingSound, "paper.wav");

            loadingSound = Constants.SOUND_BUILD;
            loadSoundSafely(soundLoader, loadingSound, "build.wav");

            loadingSound = Constants.SOUND_NATURE;
            loadSoundSafely(soundLoader, loadingSound, "nature.wav");

            loadingSound = Constants.SOUND_WHEEL;
            loadSoundSafely(soundLoader, loadingSound, "wheel.wav");

            loadingSound = Constants.SOUND_BUTTON;
            loadSoundSafely(soundLoader, loadingSound, "button.wav");

            loadingSound = Constants.SOUND_RALLY;
            loadSoundSafely(soundLoader, loadingSound, "rally.wav");

            loadingSound = Constants.SOUND_CHARGE;
            loadSoundSafely(soundLoader, loadingSound, "charge.wav");

            loadingSound = Constants.SOUND_BOWPULL;
            loadSoundSafely(soundLoader, loadingSound, "bowpull.wav");

            loadingSound = Constants.SOUND_WOLF;
            loadSoundSafely(soundLoader, loadingSound, "wolf.wav");

            loadingSound = Constants.SOUND_SHAPESHIFT;
            loadSoundSafely(soundLoader, loadingSound, "shapeshift.wav");

            loadingSound = Constants.SOUND_BUY;
            loadSoundSafely(soundLoader, loadingSound, "buy.wav");

            loadingSound = Constants.SOUND_MOUSEOVER;
            loadSoundSafely(soundLoader, loadingSound, "mouseover.wav");

            loadingSound = Constants.SOUND_GOLD;
            loadSoundSafely(soundLoader, loadingSound, "gold.wav");

        } catch (Exception e) {
            Logger.error("loadSounds " + e);
        }
        soundLoaded = true;
        Logger.info("loadSounds() completed");
    }


    /////////////////////////////////////////////////////////////////
    // Preload some interface art
    /////////////////////////////////////////////////////////////////
    public void preload() {
        URL url = null;
        URL[] urls = new URL[1];
        try {
            // Load the art loader
            ClassLoader artLoader = Thread.currentThread().getContextClassLoader();

            try {
                String jarPath = getUserDir() + Constants.ART_JAR;
                urls[0] = new File(jarPath).toURI().toURL();
                artLoader = new URLClassLoader(urls);
            } catch (Exception e) {
                Logger.error("Classloader preload " + e);
            }

            // user icon
            images[Constants.IMG_USER_ICON] = loadImageSafely(artLoader, Constants.ART_LOC + "usericon.png", "usericon.png");
            images[Constants.IMG_USER_ICON_CRU] = loadImageSafely(artLoader, Constants.ART_LOC + "usericon_c.png", "usericon_c.png");
            images[Constants.IMG_USER_ICON_LEG] = loadImageSafely(artLoader, Constants.ART_LOC + "usericon_l.png", "usericon_l.png");
            images[Constants.IMG_USER_ICON_CRU_LEG] = loadImageSafely(artLoader, Constants.ART_LOC + "usericon_cl.png", "usericon_cl.png");
            //url = artLoader.getResource(Constants.ART_LOC + "battleicon.png");
            //images[Constants.IMG_BATTLE_ICON] = ImageIO.read(url);
            images[Constants.IMG_IDLE_ICON] = loadImageSafely(artLoader, Constants.ART_LOC + "usericon_idle.png", "usericon_idle.png");
            images[Constants.IMG_SINGLE_ICON] = loadImageSafely(artLoader, Constants.ART_LOC + "singleicon.png", "singleicon.png");
            images[Constants.IMG_CONSTRUCTED_ICON] = loadImageSafely(artLoader, Constants.ART_LOC + "constructedicon.png", "constructedicon.png");
            images[Constants.IMG_COOPERATIVE_ICON] = loadImageSafely(artLoader, Constants.ART_LOC + "cooperativeicon.png", "cooperativeicon.png");
            images[Constants.IMG_RANDOM_ICON] = loadImageSafely(artLoader, Constants.ART_LOC + "randomicon.png", "randomicon.png");
            images[Constants.IMG_TEAM_ICON] = loadImageSafely(artLoader, Constants.ART_LOC + "teamicon.png", "teamicon.png");
            images[Constants.IMG_EDIT_ICON] = loadImageSafely(artLoader, Constants.ART_LOC + "editicon.png", "editicon.png");

            images[Constants.IMG_WAITING_CONSTRUCTED_ICON] = loadImageSafely(artLoader, Constants.ART_LOC + "waiting_constructedicon.png", "waiting_constructedicon.png");
            images[Constants.IMG_WAITING_RANDOM_ICON] = loadImageSafely(artLoader, Constants.ART_LOC + "waiting_randomicon.png", "waiting_randomicon.png");
            images[Constants.IMG_WAITING_COOPERATIVE_ICON] = loadImageSafely(artLoader, Constants.ART_LOC + "waiting_cooperativeicon.png", "waiting_cooperativeicon.png");
            images[Constants.IMG_WAITING_TEAM_ICON] = loadImageSafely(artLoader, Constants.ART_LOC + "waiting_teamicon.png", "waiting_teamicon.png");

            images[Constants.IMG_TEAM_ICONS_BUTTON] = loadImageSafely(artLoader, Constants.ART_LOC + "team_icons.png", "team_icons.png");
            images[Constants.IMG_PLUS_BUTTON] = loadImageSafely(artLoader, Constants.ART_LOC + "plus.png", "plus.png");
            images[Constants.IMG_MINUS_BUTTON] = loadImageSafely(artLoader, Constants.ART_LOC + "minus.png", "minus.png");

            // sound
            images[Constants.IMG_MUTE] = loadImageSafely(artLoader, Constants.ART_LOC + "sound.png", "sound.png");

            // music
            images[Constants.IMG_MUSIC] = loadImageSafely(artLoader, Constants.ART_LOC + "music.png", "music.png");

        } catch (Exception e) {
            Logger.error("preload: " + url + " " + e);
        }
    }


    /////////////////////////////////////////////////////////////////
    // Helper method to safely load an image
    /////////////////////////////////////////////////////////////////
    private Image loadImageSafely(ClassLoader loader, String resourcePath, String resourceName) {
        try {
            URL url = loader.getResource(resourcePath);
            if (url == null) {
                Logger.error("Failed to find resource: " + resourcePath);
                return null;
            }
            return ImageIO.read(url);
        } catch (Exception e) {
            Logger.error("Failed to load image " + resourceName + ": " + e);
            return null;
        }
    }

    /////////////////////////////////////////////////////////////////
    // Load the images
    /////////////////////////////////////////////////////////////////
    public void load() {
        Logger.info("GameMedia.load() started");
        URL url = null;
        URL[] urls = new URL[1];

        try {
            /////////////////////////////////////////////////////////
            // Sounds
            /////////////////////////////////////////////////////////
            Logger.info("About to load sounds...");
            loadSounds();
            Logger.info("Sounds loaded, setting music volume...");
            Client.setMusicVolume(Client.settings().getMusicVolume());
            Logger.info("Music volume set, starting art loading...");

            /////////////////////////////////////////////////////////
            // Art
            /////////////////////////////////////////////////////////

            // Load the art loader
            // Try to load from external art.jar first, fall back to main JAR classpath
            ClassLoader artLoader = Thread.currentThread().getContextClassLoader();
            boolean artJarLoaded = false;

            try {
                String jarPath = getUserDir() + Constants.ART_JAR;
                File jarFile = new File(jarPath);
                if (!jarFile.exists()) {
                    Logger.warn("art.jar not found at: " + jarPath + ", falling back to main JAR resources");
                    Logger.warn("Expected location: " + jarFile.getAbsolutePath());
                    // Use context classloader which has access to main JAR resources
                    artLoader = Thread.currentThread().getContextClassLoader();
                } else {
                    urls[0] = jarFile.toURI().toURL();
                    artLoader = new URLClassLoader(urls, Thread.currentThread().getContextClassLoader());
                    artJarLoaded = true;
                    Logger.info("Loaded art.jar from: " + jarPath);
                    
                    // Test if we can actually access resources
                    URL testUrl = artLoader.getResource(Constants.ART_LOC + "splat.png");
                    if (testUrl == null) {
                        Logger.warn("WARNING: art.jar loaded but cannot access resources. Falling back to main JAR.");
                        artLoader = Thread.currentThread().getContextClassLoader();
                    } else {
                        Logger.info("Successfully accessed test resource from art.jar: " + testUrl);
                    }
                }
            } catch (Exception e) {
                Logger.error("classloader load " + e);
                Logger.error("Stack trace: ", e);
                // Fall back to context classloader
                artLoader = Thread.currentThread().getContextClassLoader();
            }

            // start loading image urls
            Logger.info("Starting to load images...");
            images[Constants.IMG_SPLAT] = loadImageSafely(artLoader, Constants.ART_LOC + "splat.png", "splat.png");
            Logger.info("First image loaded, continuing with rest...");

            // load an empty
            images[Constants.IMG_POOF] = images[Constants.IMG_SPLAT];

            // miss
            images[Constants.IMG_MISS] = loadImageSafely(artLoader, Constants.ART_LOC + "miss.png", "miss.png");
            images[Constants.IMG_MIRACLE] = loadImageSafely(artLoader, Constants.ART_LOC + "miracle.png", "miracle.png");
            images[Constants.IMG_DEATH] = loadImageSafely(artLoader, Constants.ART_LOC + "death.png", "death.png");
            images[Constants.IMG_FIREBALL] = loadImageSafely(artLoader, Constants.ART_LOC + "fireball.png", "fireball.png");
            images[Constants.IMG_BIG_POOF] = loadImageSafely(artLoader, Constants.ART_LOC + "bigpoof.png", "bigpoof.png");
            images[Constants.IMG_DISABLE] = loadImageSafely(artLoader, Constants.ART_LOC + "disable.png", "disable.png");

            images[Constants.IMG_MY_CASTLE] = loadImageSafely(artLoader, Constants.ART_LOC + "castle1.gif", "castle1.gif");
            images[Constants.IMG_ENEMY_CASTLE] = loadImageSafely(artLoader, Constants.ART_LOC + "castle2.gif", "castle2.gif");

            /////////////////////////////////////////////////////////////////
            // Units
            /////////////////////////////////////////////////////////////////


            // Footman
            images[Constants.IMG_FOOTMAN] = loadImageSafely(artLoader, Constants.ART_LOC + "footman1.png", "footman1.png");
            images[Constants.IMG_FOOTMAN_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "footman2.png", "footman2.png");


            // Bowman
            images[Constants.IMG_BOWMAN] = loadImageSafely(artLoader, Constants.ART_LOC + "bowman1.png", "bowman1.png");
            images[Constants.IMG_BOWMAN_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "bowman2.png", "bowman2.png");


            // overwatch Bowman
            images[Constants.IMG_OBOWMAN] = loadImageSafely(artLoader, Constants.ART_LOC + "obowman1.png", "obowman1.png");
            images[Constants.IMG_OBOWMAN_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "obowman2.png", "obowman2.png");


            // Cavalry
            images[Constants.IMG_CAVALRY] = loadImageSafely(artLoader, Constants.ART_LOC + "cavalry1.png", "cavalry1.png");
            images[Constants.IMG_CAVALRY_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "cavalry2.png", "cavalry2.png");


            // Archer
            images[Constants.IMG_ARCHER] = loadImageSafely(artLoader, Constants.ART_LOC + "archer1.png", "archer1.png");
            images[Constants.IMG_ARCHER_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "archer2.png", "archer2.png");


            // Pikeman
            images[Constants.IMG_PIKEMAN] = loadImageSafely(artLoader, Constants.ART_LOC + "pikeman1.png", "pikeman1.png");
            images[Constants.IMG_PIKEMAN_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "pikeman2.png", "pikeman2.png");


            // Knight
            images[Constants.IMG_KNIGHT] = loadImageSafely(artLoader, Constants.ART_LOC + "knight1.png", "knight1.png");
            images[Constants.IMG_KNIGHT_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "knight2.png", "knight2.png");


            // Ranger
            images[Constants.IMG_RANGER_MELEE] = loadImageSafely(artLoader, Constants.ART_LOC + "rangermelee1.png", "rangermelee1.png");
            images[Constants.IMG_RANGER_MELEE_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "rangermelee2.png", "rangermelee2.png");
            images[Constants.IMG_RANGER_RANGED] = loadImageSafely(artLoader, Constants.ART_LOC + "rangerranged1.png", "rangerranged1.png");
            images[Constants.IMG_RANGER_RANGED_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "rangerranged2.png", "rangerranged2.png");


            // Ranger with his wolf
            images[Constants.IMG_RANGER_WOLF_MELEE] = loadImageSafely(artLoader, Constants.ART_LOC + "rangerwolfmelee1.png", "rangerwolfmelee1.png");
            images[Constants.IMG_RANGER_WOLF_MELEE_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "rangerwolfmelee2.png", "rangerwolfmelee2.png");
            images[Constants.IMG_RANGER_WOLF_RANGED] = loadImageSafely(artLoader, Constants.ART_LOC + "rangerwolfranged1.png", "rangerwolfranged1.png");
            images[Constants.IMG_RANGER_WOLF_RANGED_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "rangerwolfranged2.png", "rangerwolfranged2.png");


            // Wolf
            images[Constants.IMG_WOLF] = loadImageSafely(artLoader, Constants.ART_LOC + "wolf1.png", "wolf1.png");
            images[Constants.IMG_WOLF_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "wolf2.png", "wolf2.png");


            // Summoner
            images[Constants.IMG_SUMMONER] = loadImageSafely(artLoader, Constants.ART_LOC + "summoner1.png", "summoner1.png");
            images[Constants.IMG_SUMMONER_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "summoner2.png", "summoner2.png");


            // Imp
            images[Constants.IMG_IMP] = loadImageSafely(artLoader, Constants.ART_LOC + "imp1.png", "imp1.png");
            images[Constants.IMG_IMP_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "imp2.png", "imp2.png");


            // Demon
            images[Constants.IMG_DEMON] = loadImageSafely(artLoader, Constants.ART_LOC + "demon1.png", "demon1.png");
            images[Constants.IMG_DEMON_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "demon2.png", "demon2.png");
            images[Constants.IMG_ARCH_DEMON] = loadImageSafely(artLoader, Constants.ART_LOC + "archdemon1.png", "archdemon1.png");
            images[Constants.IMG_ARCH_DEMON_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "archdemon2.png", "archdemon2.png");


            // Priest
            images[Constants.IMG_PRIEST] = loadImageSafely(artLoader, Constants.ART_LOC + "priest1.png", "priest1.png");
            images[Constants.IMG_PRIEST_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "priest2.png", "priest2.png");


            // Enchanter
            images[Constants.IMG_ENCHANTER] = loadImageSafely(artLoader, Constants.ART_LOC + "enchanter1.png", "enchanter1.png");
            images[Constants.IMG_ENCHANTER_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "enchanter2.png", "enchanter2.png");


            // Templar
            images[Constants.IMG_TEMPLAR] = loadImageSafely(artLoader, Constants.ART_LOC + "templar1.png", "templar1.png");
            images[Constants.IMG_TEMPLAR_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "templar2.png", "templar2.png");


            // Warrior
            images[Constants.IMG_WARRIOR] = loadImageSafely(artLoader, Constants.ART_LOC + "warrior1.png", "warrior1.png");
            images[Constants.IMG_WARRIOR_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "warrior2.png", "warrior2.png");


            // Rider
            images[Constants.IMG_RIDER] = loadImageSafely(artLoader, Constants.ART_LOC + "rider1.png", "rider1.png");
            images[Constants.IMG_RIDER_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "rider2.png", "rider2.png");


            // Healer
            images[Constants.IMG_HEALER] = loadImageSafely(artLoader, Constants.ART_LOC + "healer1.png", "healer1.png");
            images[Constants.IMG_HEALER_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "healer2.png", "healer2.png");


            // Wizard
            images[Constants.IMG_WIZARD] = loadImageSafely(artLoader, Constants.ART_LOC + "wizard1.png", "wizard1.png");
            images[Constants.IMG_WIZARD_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "wizard2.png", "wizard2.png");


            // Scout
            images[Constants.IMG_SCOUT] = loadImageSafely(artLoader, Constants.ART_LOC + "scout1.png", "scout1.png");
            images[Constants.IMG_SCOUT_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "scout2.png", "scout2.png");


            // Assassin
            images[Constants.IMG_ASSASSIN] = loadImageSafely(artLoader, Constants.ART_LOC + "assassin1.png", "assassin1.png");
            images[Constants.IMG_ASSASSIN_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "assassin2.png", "assassin2.png");


            // Tactician
            images[Constants.IMG_TACTICIAN] = loadImageSafely(artLoader, Constants.ART_LOC + "tactician1.png", "tactician1.png");
            images[Constants.IMG_TACTICIAN_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "tactician2.png", "tactician2.png");


            // General
            images[Constants.IMG_GENERAL] = loadImageSafely(artLoader, Constants.ART_LOC + "general1.png", "general1.png");
            images[Constants.IMG_GENERAL_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "general2.png", "general2.png");


            // Strategist
            images[Constants.IMG_STRATEGIST] = loadImageSafely(artLoader, Constants.ART_LOC + "strategist1.png", "strategist1.png");
            images[Constants.IMG_STRATEGIST_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "strategist2.png", "strategist2.png");


            // Wall
            images[Constants.IMG_WALL] = loadImageSafely(artLoader, Constants.ART_LOC + "wall1.png", "wall1.png");
            images[Constants.IMG_WALL_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "wall2.png", "wall2.png");


            // Catapult
            images[Constants.IMG_CATAPULT] = loadImageSafely(artLoader, Constants.ART_LOC + "catapult1.png", "catapult1.png");
            images[Constants.IMG_CATAPULT_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "catapult2.png", "catapult2.png");


            // Ballista
            images[Constants.IMG_BALLISTA] = loadImageSafely(artLoader, Constants.ART_LOC + "ballista1.png", "ballista1.png");
            images[Constants.IMG_BALLISTA_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "ballista2.png", "ballista2.png");


            // Necromancer
            images[Constants.IMG_NECROMANCER] = loadImageSafely(artLoader, Constants.ART_LOC + "necromancer1.png", "necromancer1.png");
            images[Constants.IMG_NECROMANCER_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "necromancer2.png", "necromancer2.png");


            // Lich
            images[Constants.IMG_LICH] = loadImageSafely(artLoader, Constants.ART_LOC + "lich1.png", "lich1.png");
            images[Constants.IMG_LICH_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "lich2.png", "lich2.png");


            // Skeleton
            images[Constants.IMG_SKELETON] = loadImageSafely(artLoader, Constants.ART_LOC + "skeleton1.png", "skeleton1.png");
            images[Constants.IMG_SKELETON_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "skeleton2.png", "skeleton2.png");


            // Zombie
            images[Constants.IMG_ZOMBIE] = loadImageSafely(artLoader, Constants.ART_LOC + "zombie1.png", "zombie1.png");
            images[Constants.IMG_ZOMBIE_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "zombie2.png", "zombie2.png");


            // Sergeant
            images[Constants.IMG_SERGEANT] = loadImageSafely(artLoader, Constants.ART_LOC + "sergeant1.png", "sergeant1.png");
            images[Constants.IMG_SERGEANT_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "sergeant2.png", "sergeant2.png");


            // Abjurer
            images[Constants.IMG_ABJURER] = loadImageSafely(artLoader, Constants.ART_LOC + "abjurer1.png", "abjurer1.png");
            images[Constants.IMG_ABJURER_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "abjurer2.png", "abjurer2.png");


            // Seal
            images[Constants.IMG_SEAL] = loadImageSafely(artLoader, Constants.ART_LOC + "seal1.png", "seal1.png");
            images[Constants.IMG_SEAL_ENEMY] = images[Constants.IMG_SEAL];


            // Warlock
            images[Constants.IMG_WARLOCK] = loadImageSafely(artLoader, Constants.ART_LOC + "warlock1.png", "warlock1.png");
            images[Constants.IMG_WARLOCK_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "warlock2.png", "warlock2.png");


            // Crossbowman
            images[Constants.IMG_CROSSBOWMAN] = loadImageSafely(artLoader, Constants.ART_LOC + "crossbowman1.png", "crossbowman1.png");
            images[Constants.IMG_CROSSBOWMAN_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "crossbowman2.png", "crossbowman2.png");


            // Unloaded Crossbowman
            images[Constants.IMG_UNCROSSBOWMAN] = loadImageSafely(artLoader, Constants.ART_LOC + "uncrossbowman1.png", "uncrossbowman1.png");
            images[Constants.IMG_UNCROSSBOWMAN_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "uncrossbowman2.png", "uncrossbowman2.png");


            // Dragon
            images[Constants.IMG_DRAGON] = loadImageSafely(artLoader, Constants.ART_LOC + "dragon1.png", "dragon1.png");
            images[Constants.IMG_DRAGON_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "dragon2.png", "dragon2.png");


            // Draco-lich
            images[Constants.IMG_DRACOLICH] = loadImageSafely(artLoader, Constants.ART_LOC + "dracolich1.png", "dracolich1.png");
            images[Constants.IMG_DRACOLICH_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "dracolich2.png", "dracolich2.png");


            // Hydra
            images[Constants.IMG_HYDRA] = loadImageSafely(artLoader, Constants.ART_LOC + "hydra1.png", "hydra1.png");
            images[Constants.IMG_HYDRA_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "hydra2.png", "hydra2.png");


            // Five headed hydra
            images[Constants.IMG_HYDRA_5] = loadImageSafely(artLoader, Constants.ART_LOC + "hydra3.png", "hydra3.png");
            images[Constants.IMG_HYDRA_5_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "hydra4.png", "hydra4.png");


            // Four headed hydra
            images[Constants.IMG_HYDRA_4] = loadImageSafely(artLoader, Constants.ART_LOC + "hydra5.png", "hydra5.png");
            images[Constants.IMG_HYDRA_4_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "hydra6.png", "hydra6.png");


            // three headed hydra
            images[Constants.IMG_HYDRA_3] = loadImageSafely(artLoader, Constants.ART_LOC + "hydra7.png", "hydra7.png");
            images[Constants.IMG_HYDRA_3_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "hydra8.png", "hydra8.png");


            // two headed hydra
            images[Constants.IMG_HYDRA_2] = loadImageSafely(artLoader, Constants.ART_LOC + "hydra9.png", "hydra9.png");
            images[Constants.IMG_HYDRA_2_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "hydra10.png", "hydra10.png");


            // one headed hydra
            images[Constants.IMG_HYDRA_1] = loadImageSafely(artLoader, Constants.ART_LOC + "hydra11.png", "hydra11.png");
            images[Constants.IMG_HYDRA_1_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "hydra12.png", "hydra12.png");


            // Tower
            images[Constants.IMG_TOWER] = loadImageSafely(artLoader, Constants.ART_LOC + "tower1.gif", "tower1.gif");
            images[Constants.IMG_TOWER_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "tower2.gif", "tower2.gif");


            // Command Post
            images[Constants.IMG_COMMAND_POST] = loadImageSafely(artLoader, Constants.ART_LOC + "commandPost1.gif", "commandPost1.gif");
            images[Constants.IMG_COMMAND_POST_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "commandPost2.gif", "commandPost2.gif");


            // Barracks
            images[Constants.IMG_BARRACKS] = loadImageSafely(artLoader, Constants.ART_LOC + "barracks1.gif", "barracks1.gif");
            images[Constants.IMG_BARRACKS_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "barracks2.gif", "barracks2.gif");


            // Soldier
            images[Constants.IMG_SOLDIER] = loadImageSafely(artLoader, Constants.ART_LOC + "soldier1.png", "soldier1.png");
            images[Constants.IMG_SOLDIER_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "soldier2.png", "soldier2.png");


            // Druid
            images[Constants.IMG_DRUID] = loadImageSafely(artLoader, Constants.ART_LOC + "druid1.png", "druid1.png");
            images[Constants.IMG_DRUID_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "druid2.png", "druid2.png");


            // Channeler
            images[Constants.IMG_CHANNELER] = loadImageSafely(artLoader, Constants.ART_LOC + "channeler1.png", "channeler1.png");
            images[Constants.IMG_CHANNELER_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "channeler2.png", "channeler2.png");


            // Lycanthrope
            images[Constants.IMG_LYCANTHROPE] = loadImageSafely(artLoader, Constants.ART_LOC + "lycanthrope1.png", "lycanthrope1.png");
            images[Constants.IMG_LYCANTHROPE_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "lycanthrope2.png", "lycanthrope2.png");


            // Werewolf
            images[Constants.IMG_WEREWOLF] = loadImageSafely(artLoader, Constants.ART_LOC + "werewolf1.png", "werewolf1.png");
            images[Constants.IMG_WEREWOLF_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "werewolf2.png", "werewolf2.png");


            // Lycanwolf
            images[Constants.IMG_LYCANWOLF] = loadImageSafely(artLoader, Constants.ART_LOC + "lycanwolf1.png", "lycanwolf1.png");
            images[Constants.IMG_LYCANWOLF_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "lycanwolf2.png", "lycanwolf2.png");


            // Horse archer
            images[Constants.IMG_MOUNTED_ARCHER] = loadImageSafely(artLoader, Constants.ART_LOC + "mountedarcher1.png", "mountedarcher1.png");
            images[Constants.IMG_MOUNTED_ARCHER_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "mountedarcher2.png", "mountedarcher2.png");


            // Geomancer
            images[Constants.IMG_GEOMANCER] = loadImageSafely(artLoader, Constants.ART_LOC + "geomancer1.png", "geomancer1.png");
            images[Constants.IMG_GEOMANCER_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "geomancer2.png", "geomancer2.png");


            // Rock
            images[Constants.IMG_ROCK] = loadImageSafely(artLoader, Constants.ART_LOC + "rock1.png", "rock1.png");
            images[Constants.IMG_ROCK_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "rock2.png", "rock2.png");


            // Swordsman
            images[Constants.IMG_SWORDSMAN] = loadImageSafely(artLoader, Constants.ART_LOC + "swordsman1.png", "swordsman1.png");
            images[Constants.IMG_SWORDSMAN_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "swordsman2.png", "swordsman2.png");


            // Witch
            images[Constants.IMG_WITCH] = loadImageSafely(artLoader, Constants.ART_LOC + "witch1.png", "witch1.png");
            images[Constants.IMG_WITCH_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "witch2.png", "witch2.png");


            // Toad
            images[Constants.IMG_TOAD] = loadImageSafely(artLoader, Constants.ART_LOC + "toad1.png", "toad1.png");
            images[Constants.IMG_TOAD_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "toad2.png", "toad2.png");


            // Shield maiden
            images[Constants.IMG_SHIELD_MAIDEN] = loadImageSafely(artLoader, Constants.ART_LOC + "shieldmaiden1.png", "shieldmaiden1.png");
            images[Constants.IMG_SHIELD_MAIDEN_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "shieldmaiden2.png", "shieldmaiden2.png");


            // Magus
            images[Constants.IMG_MAGUS] = loadImageSafely(artLoader, Constants.ART_LOC + "magus1.png", "magus1.png");
            images[Constants.IMG_MAGUS_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "magus2.png", "magus2.png");


            // Spirit
            images[Constants.IMG_SPIRIT] = loadImageSafely(artLoader, Constants.ART_LOC + "spirit1.png", "spirit1.png");
            images[Constants.IMG_SPIRIT_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "spirit2.png", "spirit2.png");


            // Will-o-the-wisps
            images[Constants.IMG_WILL_O_THE_WISPS] = loadImageSafely(artLoader, Constants.ART_LOC + "will-o-the-wisps1.png", "will-o-the-wisps1.png");
            images[Constants.IMG_WILL_O_THE_WISPS_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "will-o-the-wisps2.png", "will-o-the-wisps2.png");


            // Golem
            images[Constants.IMG_GOLEM] = loadImageSafely(artLoader, Constants.ART_LOC + "golem1.png", "golem1.png");
            images[Constants.IMG_GOLEM_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "golem2.png", "golem2.png");


            // Armory
            images[Constants.IMG_ARMORY] = loadImageSafely(artLoader, Constants.ART_LOC + "armory1.gif", "armory1.gif");
            images[Constants.IMG_ARMORY_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "armory2.gif", "armory2.gif");


            // Serpent
            images[Constants.IMG_SERPENT] = loadImageSafely(artLoader, Constants.ART_LOC + "serpent1.png", "serpent1.png");
            images[Constants.IMG_SERPENT_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "serpent2.png", "serpent2.png");


            // Fire archer
            images[Constants.IMG_FIRE_ARCHER] = loadImageSafely(artLoader, Constants.ART_LOC + "firearcher1.png", "firearcher1.png");
            images[Constants.IMG_FIRE_ARCHER_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "firearcher2.png", "firearcher2.png");


            // Mimic
            images[Constants.IMG_MIMIC] = loadImageSafely(artLoader, Constants.ART_LOC + "mimic1.png", "mimic1.png");
            images[Constants.IMG_MIMIC_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "mimic2.png", "mimic2.png");


            // Paladin
            images[Constants.IMG_PALADIN] = loadImageSafely(artLoader, Constants.ART_LOC + "paladin1.png", "paladin1.png");
            images[Constants.IMG_PALADIN_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "paladin2.png", "paladin2.png");


            // Shaman
            images[Constants.IMG_SHAMAN] = loadImageSafely(artLoader, Constants.ART_LOC + "shaman1.png", "shaman1.png");
            images[Constants.IMG_SHAMAN_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "shaman2.png", "shaman2.png");


            // Martyr
            images[Constants.IMG_MARTYR] = loadImageSafely(artLoader, Constants.ART_LOC + "martyr1.png", "martyr1.png");
            images[Constants.IMG_MARTYR_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "martyr2.png", "martyr2.png");


            // Rogue
            images[Constants.IMG_ROGUE] = loadImageSafely(artLoader, Constants.ART_LOC + "rogue1.png", "rogue1.png");
            images[Constants.IMG_ROGUE_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "rogue2.png", "rogue2.png");


            // Diabolist
            images[Constants.IMG_DIABOLIST] = loadImageSafely(artLoader, Constants.ART_LOC + "diabolist1.png", "diabolist1.png");
            images[Constants.IMG_DIABOLIST_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "diabolist2.png", "diabolist2.png");
            // Devil
            images[Constants.IMG_DEVIL] = loadImageSafely(artLoader, Constants.ART_LOC + "devil1.png", "devil1.png");
            images[Constants.IMG_DEVIL_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "devil2.png", "devil2.png");


            // Ghost
            images[Constants.IMG_GHOST] = loadImageSafely(artLoader, Constants.ART_LOC + "ghost1.png", "ghost1.png");
            images[Constants.IMG_GHOST_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "ghost2.png", "ghost2.png");


            // templar aura
            images[Constants.IMG_TEMPLAR_AURA] = loadImageSafely(artLoader, Constants.ART_LOC + "templaraura1.png", "templaraura1.png");
            images[Constants.IMG_TEMPLAR_AURA_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "templaraura2.png", "templaraura2.png");


            // gate guard
            images[Constants.IMG_GATE_GUARD] = loadImageSafely(artLoader, Constants.ART_LOC + "gateguard1.png", "gateguard1.png");
            images[Constants.IMG_GATE_GUARD_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "gateguard2.png", "gateguard2.png");


            // feathered serpent
            images[Constants.IMG_FEATHERED_SERPENT] = loadImageSafely(artLoader, Constants.ART_LOC + "featheredserpent1.png", "featheredserpent1.png");
            images[Constants.IMG_FEATHERED_SERPENT_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "featheredserpent2.png", "featheredserpent2.png");


            // berserker
            images[Constants.IMG_BERSERKER] = loadImageSafely(artLoader, Constants.ART_LOC + "berserker1.png", "berserker1.png");
            images[Constants.IMG_BERSERKER_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "berserker2.png", "berserker2.png");


            // berserker, dead
            images[Constants.IMG_DEAD_BERSERKER] = loadImageSafely(artLoader, Constants.ART_LOC + "deadberserker1.png", "deadberserker1.png");
            images[Constants.IMG_DEAD_BERSERKER_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "deadberserker2.png", "deadberserker2.png");


            // artificer
            images[Constants.IMG_ARTIFICER] = loadImageSafely(artLoader, Constants.ART_LOC + "artificer1.png", "artificer1.png");
            images[Constants.IMG_ARTIFICER_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "artificer2.png", "artificer2.png");


            // Changeling
            images[Constants.IMG_CHANGELING] = loadImageSafely(artLoader, Constants.ART_LOC + "changeling1.png", "changeling1.png");
            images[Constants.IMG_CHANGELING_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "changeling2.png", "changeling2.png");


            // Doppelganger
            images[Constants.IMG_DOPPELGANGER] = loadImageSafely(artLoader, Constants.ART_LOC + "doppelganger1.png", "doppelganger1.png");
            images[Constants.IMG_DOPPELGANGER_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "doppelganger2.png", "doppelganger2.png");


            // Skinwalker
            images[Constants.IMG_SKINWALKER] = loadImageSafely(artLoader, Constants.ART_LOC + "skinwalker1.png", "skinwalker1.png");
            images[Constants.IMG_SKINWALKER_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "skinwalker2.png", "skinwalker2.png");


            // Acolyte
            images[Constants.IMG_ACOLYTE] = loadImageSafely(artLoader, Constants.ART_LOC + "acolyte1.png", "acolyte1.png");
            images[Constants.IMG_ACOLYTE_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "acolyte2.png", "acolyte2.png");


            // Axeman
            images[Constants.IMG_AXEMAN] = loadImageSafely(artLoader, Constants.ART_LOC + "axeman1.png", "axeman1.png");
            images[Constants.IMG_AXEMAN_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "axeman2.png", "axeman2.png");


            // Mourner
            images[Constants.IMG_MOURNER] = loadImageSafely(artLoader, Constants.ART_LOC + "mourner1.png", "mourner1.png");
            images[Constants.IMG_MOURNER_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "mourner2.png", "mourner2.png");


            // Heretic
            images[Constants.IMG_HERETIC] = loadImageSafely(artLoader, Constants.ART_LOC + "heretic1.png", "heretic1.png");
            images[Constants.IMG_HERETIC_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "heretic2.png", "heretic2.png");


            // War elephant
            images[Constants.IMG_WAR_ELEPHANT] = loadImageSafely(artLoader, Constants.ART_LOC + "warelephant1.png", "warelephant1.png");
            images[Constants.IMG_WAR_ELEPHANT_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "warelephant2.png", "warelephant2.png");


            // fanatic
            images[Constants.IMG_FANATIC] = loadImageSafely(artLoader, Constants.ART_LOC + "fanatic1.png", "fanatic1.png");
            images[Constants.IMG_FANATIC_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "fanatic2.png", "fanatic2.png");


            // the dismounted knight
            images[Constants.IMG_DISMOUNTED_KNIGHT] = loadImageSafely(artLoader, Constants.ART_LOC + "dismountedknight1.png", "dismountedknight1.png");
            images[Constants.IMG_DISMOUNTED_KNIGHT_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "dismountedknight2.png", "dismountedknight2.png");


            // bear
            images[Constants.IMG_BEAR] = loadImageSafely(artLoader, Constants.ART_LOC + "bear1.png", "bear1.png");
            images[Constants.IMG_BEAR_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "bear2.png", "bear2.png");


            // quartermaster
            images[Constants.IMG_QUARTERMASTER] = loadImageSafely(artLoader, Constants.ART_LOC + "quartermaster1.png", "quartermaster1.png");
            images[Constants.IMG_QUARTERMASTER_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "quartermaster2.png", "quartermaster2.png");


            // mason
            images[Constants.IMG_MASON] = loadImageSafely(artLoader, Constants.ART_LOC + "mason1.png", "mason1.png");
            images[Constants.IMG_MASON_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "mason2.png", "mason2.png");


            // wall mason
            images[Constants.IMG_WALL_MASON] = loadImageSafely(artLoader, Constants.ART_LOC + "wallmason1.png", "wallmason1.png");
            images[Constants.IMG_WALL_MASON_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "wallmason2.png", "wallmason2.png");


            // double dop
            images[Constants.IMG_DOUBLE_DOP] = loadImageSafely(artLoader, Constants.ART_LOC + "doubledop1.png", "doubledop1.png");
            images[Constants.IMG_DOUBLE_DOP_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "doubledop2.png", "doubledop2.png");


            // confessor
            images[Constants.IMG_CONFESSOR] = loadImageSafely(artLoader, Constants.ART_LOC + "confessor1.png", "confessor1.png");
            images[Constants.IMG_CONFESSOR_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "confessor2.png", "confessor2.png");


            // possessed
            images[Constants.IMG_POSSESSED] = loadImageSafely(artLoader, Constants.ART_LOC + "possessed1.png", "possessed1.png");
            images[Constants.IMG_POSSESSED_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "possessed2.png", "possessed2.png");


            // barbarian
            images[Constants.IMG_BARBARIAN] = loadImageSafely(artLoader, Constants.ART_LOC + "barbarian1.png", "barbarian1.png");
            images[Constants.IMG_BARBARIAN_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "barbarian2.png", "barbarian2.png");


            // alchemist
            images[Constants.IMG_ALCHEMIST] = loadImageSafely(artLoader, Constants.ART_LOC + "alchemist1.png", "alchemist1.png");
            images[Constants.IMG_ALCHEMIST_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "alchemist2.png", "alchemist2.png");


            // bounty hunter
            images[Constants.IMG_BOUNTY_HUNTER] = loadImageSafely(artLoader, Constants.ART_LOC + "bountyhunter1.png", "bountyhunter1.png");
            images[Constants.IMG_BOUNTY_HUNTER_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "bountyhunter2.png", "bountyhunter2.png");


            // shield bearer
            images[Constants.IMG_SHIELD_BEARER] = loadImageSafely(artLoader, Constants.ART_LOC + "shieldbearer1.png", "shieldbearer1.png");
            images[Constants.IMG_SHIELD_BEARER_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "shieldbearer2.png", "shieldbearer2.png");


            // chieftain
            images[Constants.IMG_CHIEFTAIN] = loadImageSafely(artLoader, Constants.ART_LOC + "chieftain1.png", "chieftain1.png");
            images[Constants.IMG_CHIEFTAIN_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "chieftain2.png", "chieftain2.png");


            // lancer
            images[Constants.IMG_LANCER] = loadImageSafely(artLoader, Constants.ART_LOC + "lancer1.png", "lancer1.png");
            images[Constants.IMG_LANCER_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "lancer2.png", "lancer2.png");


            // archangel
            images[Constants.IMG_ARCHANGEL] = loadImageSafely(artLoader, Constants.ART_LOC + "archangel1.png", "archangel1.png");
            images[Constants.IMG_ARCHANGEL_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "archangel2.png", "archangel2.png");


            // conjurer
            images[Constants.IMG_CONJURER] = loadImageSafely(artLoader, Constants.ART_LOC + "conjurer1.png", "conjurer1.png");
            images[Constants.IMG_CONJURER_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "conjurer2.png", "conjurer2.png");


            // portal
            images[Constants.IMG_PORTAL] = loadImageSafely(artLoader, Constants.ART_LOC + "portal1.png", "portal1.png");
            images[Constants.IMG_PORTAL_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "portal2.png", "portal2.png");


            // gate
            images[Constants.IMG_GATE] = loadImageSafely(artLoader, Constants.ART_LOC + "gate1.png", "gate1.png");
            images[Constants.IMG_GATE_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "gate2.png", "gate2.png");


            // diplomat
            images[Constants.IMG_DIPLOMAT] = loadImageSafely(artLoader, Constants.ART_LOC + "diplomat1.png", "diplomat1.png");
            images[Constants.IMG_DIPLOMAT_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "diplomat2.png", "diplomat2.png");


            // longbowman
            images[Constants.IMG_LONGBOWMAN] = loadImageSafely(artLoader, Constants.ART_LOC + "longbowman1.png", "longbowman1.png");
            images[Constants.IMG_LONGBOWMAN_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "longbowman2.png", "longbowman2.png");


            // sycophant
            images[Constants.IMG_SYCOPHANT] = loadImageSafely(artLoader, Constants.ART_LOC + "sycophant1.png", "sycophant1.png");
            images[Constants.IMG_SYCOPHANT_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "sycophant2.png", "sycophant2.png");


            // wyvern
            images[Constants.IMG_WYVERN] = loadImageSafely(artLoader, Constants.ART_LOC + "wyvern1.png", "wyvern1.png");
            images[Constants.IMG_WYVERN_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "wyvern2.png", "wyvern2.png");


            // egg
            images[Constants.IMG_EGG] = loadImageSafely(artLoader, Constants.ART_LOC + "egg1.png", "egg1.png");
            images[Constants.IMG_EGG_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "egg2.png", "egg2.png");


            // captain
            images[Constants.IMG_CAPTAIN] = loadImageSafely(artLoader, Constants.ART_LOC + "captain1.png", "captain1.png");
            images[Constants.IMG_CAPTAIN_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "captain2.png", "captain2.png");


            // abbey
            images[Constants.IMG_ABBEY] = loadImageSafely(artLoader, Constants.ART_LOC + "abbey1.png", "abbey1.png");
            images[Constants.IMG_ABBEY_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "abbey2.png", "abbey2.png");


            // supplicant
            images[Constants.IMG_SUPPLICANT] = loadImageSafely(artLoader, Constants.ART_LOC + "supplicant1.png", "supplicant1.png");
            images[Constants.IMG_SUPPLICANT_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "supplicant2.png", "supplicant2.png");


            ////////////////////////////////////////////////////////////////////
            // New units as of 9/15/10
            ////////////////////////////////////////////////////////////////////


            // duelist (new unit)
            images[Constants.IMG_DUELIST] = loadImageSafely(artLoader, Constants.ART_LOC + "duelist1.png", "duelist1.png");
            images[Constants.IMG_DUELIST_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "duelist2.png", "duelist2.png");


            // militia (new unit)
            images[Constants.IMG_MILITIA] = loadImageSafely(artLoader, Constants.ART_LOC + "militia1.png", "militia1.png");
            images[Constants.IMG_MILITIA_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "militia2.png", "militia2.png");


            // conspirator (new unit)
            images[Constants.IMG_CONSPIRATOR] = loadImageSafely(artLoader, Constants.ART_LOC + "conspirator1.png", "conspirator1.png");
            images[Constants.IMG_CONSPIRATOR_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "conspirator2.png", "conspirator2.png");


            // upgraded soldier offensive
            images[Constants.IMG_SOLDIER_O] = loadImageSafely(artLoader, Constants.ART_LOC + "soldiero1.png", "soldiero1.png");
            images[Constants.IMG_SOLDIER_O_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "soldiero2.png", "soldiero2.png");


            // upgraded soldier defensive
            images[Constants.IMG_SOLDIER_D] = loadImageSafely(artLoader, Constants.ART_LOC + "soldierd1.png", "soldierd1.png");
            images[Constants.IMG_SOLDIER_D_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "soldierd2.png", "soldierd2.png");
/* 
  // newunit3
  System.out.println(url + "WORLD");
            images[Constants.IMG_NEWUNIT3] = loadImageSafely(artLoader, Constants.ART_LOC + "newunit31.png", "newunit31.png");
            images[Constants.IMG_NEWUNIT3_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "newunit32.png", "newunit32.png");
 
  // newunit4
  System.out.println(url + "WORLD");
            images[Constants.IMG_NEWUNIT4] = loadImageSafely(artLoader, Constants.ART_LOC + "newunit41.png", "newunit41.png");
            images[Constants.IMG_NEWUNIT4_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "newunit42.png", "newunit42.png");
 
  // newunit5
  System.out.println(url + "WORLD");
            images[Constants.IMG_NEWUNIT5] = loadImageSafely(artLoader, Constants.ART_LOC + "newunit51.png", "newunit51.png");
            images[Constants.IMG_NEWUNIT5_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "newunit52.png", "newunit52.png");
 
  // newunit6
  System.out.println(url + "WORLD");
            images[Constants.IMG_NEWUNIT6] = loadImageSafely(artLoader, Constants.ART_LOC + "newunit61.png", "newunit61.png");
            images[Constants.IMG_NEWUNIT6_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "newunit62.png", "newunit62.png");
 
  // newunit7
  System.out.println(url + "WORLD");
            images[Constants.IMG_NEWUNIT7] = loadImageSafely(artLoader, Constants.ART_LOC + "newunit71.png", "newunit71.png");
            images[Constants.IMG_NEWUNIT7_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "newunit72.png", "newunit72.png");
 
  // newunit8
  System.out.println(url + "WORLD");
            images[Constants.IMG_NEWUNIT8] = loadImageSafely(artLoader, Constants.ART_LOC + "newunit81.png", "newunit81.png");
            images[Constants.IMG_NEWUNIT8_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "newunit82.png", "newunit82.png");
 
  // newunit9
  System.out.println(url + "WORLD");
            images[Constants.IMG_NEWUNIT9] = loadImageSafely(artLoader, Constants.ART_LOC + "newunit91.png", "newunit91.png");
            images[Constants.IMG_NEWUNIT9_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "newunit92.png", "newunit92.png");
 
  // newunit10
  System.out.println(url + "WORLD");
            images[Constants.IMG_NEWUNIT10] = loadImageSafely(artLoader, Constants.ART_LOC + "newunit101.png", "newunit101.png");
            images[Constants.IMG_NEWUNIT10_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "newunit102.png", "newunit102.png");
 
  // newunit11
  System.out.println(url + "WORLD");
            images[Constants.IMG_NEWUNIT11] = loadImageSafely(artLoader, Constants.ART_LOC + "newunit111.png", "newunit111.png");
            images[Constants.IMG_NEWUNIT11_ENEMY] = loadImageSafely(artLoader, Constants.ART_LOC + "newunit112.png", "newunit112.png");

*/
            /////////////////////////////////////////////////////////////////
            // Projectiles
            /////////////////////////////////////////////////////////////////

            // Arrow
            images[Constants.IMG_ARROW] = loadImageSafely(artLoader, Constants.ART_LOC + "arrow.gif", "arrow.gif");

            // Stone
            images[Constants.IMG_STONE] = loadImageSafely(artLoader, Constants.ART_LOC + "stone.png", "stone.png");

            // Green ball
            images[Constants.IMG_GREEN_BALL] = loadImageSafely(artLoader, Constants.ART_LOC + "greenball.png", "greenball.png");

            // purple ball
            images[Constants.IMG_PURPLE_BALL] = loadImageSafely(artLoader, Constants.ART_LOC + "purpleball.png", "purpleball.png");

            // Spear
            images[Constants.IMG_SPEAR] = loadImageSafely(artLoader, Constants.ART_LOC + "spear.png", "spear.png");
            images[Constants.IMG_SPEAR_2] = images[Constants.IMG_SPEAR];

            // magic ball 1-6
            images[Constants.IMG_MAGIC_BALL_1] = loadImageSafely(artLoader, Constants.ART_LOC + "magicball1.png", "magicball1.png");
            images[Constants.IMG_MAGIC_BALL_2] = loadImageSafely(artLoader, Constants.ART_LOC + "magicball2.png", "magicball2.png");
            images[Constants.IMG_MAGIC_BALL_3] = loadImageSafely(artLoader, Constants.ART_LOC + "magicball3.png", "magicball3.png");
            images[Constants.IMG_MAGIC_BALL_4] = loadImageSafely(artLoader, Constants.ART_LOC + "magicball4.png", "magicball4.png");
            images[Constants.IMG_MAGIC_BALL_5] = loadImageSafely(artLoader, Constants.ART_LOC + "magicball5.png", "magicball5.png");
            images[Constants.IMG_MAGIC_BALL_6] = loadImageSafely(artLoader, Constants.ART_LOC + "magicball6.png", "magicball6.png");

            // white ball
            images[Constants.IMG_WHITE_BALL] = loadImageSafely(artLoader, Constants.ART_LOC + "whiteball.png", "whiteball.png");

            // red ball
            images[Constants.IMG_RED_BALL] = loadImageSafely(artLoader, Constants.ART_LOC + "redball.png", "redball.png");


            /////////////////////////////////////////////////////////////////
            // Interface
            /////////////////////////////////////////////////////////////////

            // action button
            images[Constants.IMG_ACTION] = loadImageSafely(artLoader, Constants.ART_LOC + "action.jpg", "action.jpg");
            images[Constants.IMG_ACTION_DISABLE] = loadImageSafely(artLoader, Constants.ART_LOC + "actiondisable.jpg", "actiondisable.jpg");
            images[Constants.IMG_ACTION_PASSIVE] = loadImageSafely(artLoader, Constants.ART_LOC + "actionpassive.gif", "actionpassive.gif");
            images[Constants.IMG_ACTION_HIGHLIGHT] = loadImageSafely(artLoader, Constants.ART_LOC + "actionhighlight.jpg", "actionhighlight.jpg");
            images[Constants.IMG_ACTION_OVERLAY] = loadImageSafely(artLoader, Constants.ART_LOC + "actionoverlay.png", "actionoverlay.png");

            // panels
            images[Constants.IMG_BACK_PANEL] = loadImageSafely(artLoader, Constants.ART_LOC + "backpanel.jpg", "backpanel.jpg");
            images[Constants.IMG_BACK_PANEL_GAME] = loadImageSafely(artLoader, Constants.ART_LOC + "backpanelgame.jpg", "backpanelgame.jpg");
            images[Constants.IMG_STAT_PANEL] = loadImageSafely(artLoader, Constants.ART_LOC + "statpanel.jpg", "statpanel.jpg");

            // deploy button
            images[Constants.IMG_DEPLOY] = loadImageSafely(artLoader, Constants.ART_LOC + "deploy.jpg", "deploy.jpg");
            images[Constants.IMG_DEPLOY_HIGHLIGHT] = loadImageSafely(artLoader, Constants.ART_LOC + "deployhighlight.jpg", "deployhighlight.jpg");
            images[Constants.IMG_DEPLOY_SELECTED] = loadImageSafely(artLoader, Constants.ART_LOC + "deployselected.jpg", "deployselected.jpg");
            images[Constants.IMG_DEPLOY_GREY] = loadImageSafely(artLoader, Constants.ART_LOC + "deploygrey.jpg", "deploygrey.jpg");

            // end panel
            images[Constants.IMG_END_PANEL] = loadImageSafely(artLoader, Constants.ART_LOC + "endpanel.jpg", "endpanel.jpg");
            images[Constants.IMG_END_TURN] = loadImageSafely(artLoader, Constants.ART_LOC + "endturn.jpg", "endturn.jpg");
            images[Constants.IMG_SURRENDER] = loadImageSafely(artLoader, Constants.ART_LOC + "surrender.jpg", "surrender.jpg");
            images[Constants.IMG_DRAW] = loadImageSafely(artLoader, Constants.ART_LOC + "draw.jpg", "draw.jpg");

            // highlights
            images[Constants.IMG_BLUE] = loadImageSafely(artLoader, Constants.ART_LOC + "blue.gif", "blue.gif");
            images[Constants.IMG_BLUE_BORDER] = loadImageSafely(artLoader, Constants.ART_LOC + "blueborder.gif", "blueborder.gif");
            images[Constants.IMG_RED] = loadImageSafely(artLoader, Constants.ART_LOC + "red.gif", "red.gif");
            images[Constants.IMG_RED_BORDER] = loadImageSafely(artLoader, Constants.ART_LOC + "redborder.gif", "redborder.gif");
            images[Constants.IMG_GREEN] = loadImageSafely(artLoader, Constants.ART_LOC + "green.gif", "green.gif");
            images[Constants.IMG_GREEN_BORDER] = loadImageSafely(artLoader, Constants.ART_LOC + "greenborder.gif", "greenborder.gif");
            images[Constants.IMG_PURPLE] = loadImageSafely(artLoader, Constants.ART_LOC + "purple.gif", "purple.gif");
            images[Constants.IMG_PURPLE_BORDER] = loadImageSafely(artLoader, Constants.ART_LOC + "purpleborder.gif", "purpleborder.gif");
            images[Constants.IMG_BLACK] = loadImageSafely(artLoader, Constants.ART_LOC + "black.gif", "black.gif");
            images[Constants.IMG_BLACK_BORDER] = loadImageSafely(artLoader, Constants.ART_LOC + "blackborder.gif", "blackborder.gif");
            images[Constants.IMG_YELLOW] = loadImageSafely(artLoader, Constants.ART_LOC + "yellow.gif", "yellow.gif");
            images[Constants.IMG_YELLOW_BORDER] = loadImageSafely(artLoader, Constants.ART_LOC + "yellowborder.gif", "yellowborder.gif");

            // poof animation
            images[Constants.IMG_POOF_1] = loadImageSafely(artLoader, Constants.ART_LOC + "poof1.png", "poof1.png");
            images[Constants.IMG_POOF_2] = loadImageSafely(artLoader, Constants.ART_LOC + "poof2.png", "poof2.png");
            images[Constants.IMG_POOF_3] = loadImageSafely(artLoader, Constants.ART_LOC + "poof3.png", "poof3.png");
            images[Constants.IMG_POOF_4] = loadImageSafely(artLoader, Constants.ART_LOC + "poof4.png", "poof4.png");
            images[Constants.IMG_POOF_5] = loadImageSafely(artLoader, Constants.ART_LOC + "poof5.png", "poof5.png");
            images[Constants.IMG_POOF_6] = loadImageSafely(artLoader, Constants.ART_LOC + "poof6.png", "poof6.png");
            images[Constants.IMG_POOF_7] = loadImageSafely(artLoader, Constants.ART_LOC + "poof7.png", "poof7.png");
            images[Constants.IMG_POOF_8] = loadImageSafely(artLoader, Constants.ART_LOC + "poof8.png", "poof8.png");
            images[Constants.IMG_POOF_9] = loadImageSafely(artLoader, Constants.ART_LOC + "poof9.png", "poof9.png");
            images[Constants.IMG_POOF_10] = loadImageSafely(artLoader, Constants.ART_LOC + "poof10.png", "poof10.png");
            images[Constants.IMG_POOF_11] = loadImageSafely(artLoader, Constants.ART_LOC + "poof11.png", "poof11.png");
            images[Constants.IMG_POOF_12] = loadImageSafely(artLoader, Constants.ART_LOC + "poof12.png", "poof12.png");
            images[Constants.IMG_POOF_13] = loadImageSafely(artLoader, Constants.ART_LOC + "poof13.png", "poof13.png");
            images[Constants.IMG_POOF_14] = loadImageSafely(artLoader, Constants.ART_LOC + "poof14.png", "poof14.png");
            images[Constants.IMG_POOF_15] = loadImageSafely(artLoader, Constants.ART_LOC + "poof15.png", "poof15.png");
            images[Constants.IMG_POOF_16] = loadImageSafely(artLoader, Constants.ART_LOC + "poof16.png", "poof16.png");
            images[Constants.IMG_POOF_17] = loadImageSafely(artLoader, Constants.ART_LOC + "poof17.png", "poof17.png");
            images[Constants.IMG_POOF_18] = loadImageSafely(artLoader, Constants.ART_LOC + "poof18.png", "poof18.png");
            images[Constants.IMG_POOF_19] = loadImageSafely(artLoader, Constants.ART_LOC + "poof19.png", "poof19.png");
            images[Constants.IMG_POOF_20] = loadImageSafely(artLoader, Constants.ART_LOC + "poof20.png", "poof20.png");

            // explosion
            images[Constants.IMG_EXPLOSION_1] = loadImageSafely(artLoader, Constants.ART_LOC + "explosion1.png", "explosion1.png");
            images[Constants.IMG_EXPLOSION_2] = loadImageSafely(artLoader, Constants.ART_LOC + "explosion2.png", "explosion2.png");
            images[Constants.IMG_EXPLOSION_3] = loadImageSafely(artLoader, Constants.ART_LOC + "explosion3.png", "explosion3.png");
            images[Constants.IMG_EXPLOSION_4] = loadImageSafely(artLoader, Constants.ART_LOC + "explosion4.png", "explosion4.png");
            images[Constants.IMG_EXPLOSION_5] = loadImageSafely(artLoader, Constants.ART_LOC + "explosion5.png", "explosion5.png");
            images[Constants.IMG_EXPLOSION_6] = loadImageSafely(artLoader, Constants.ART_LOC + "explosion6.png", "explosion6.png");
            images[Constants.IMG_EXPLOSION_7] = loadImageSafely(artLoader, Constants.ART_LOC + "explosion7.png", "explosion7.png");
            images[Constants.IMG_EXPLOSION_8] = loadImageSafely(artLoader, Constants.ART_LOC + "explosion8.png", "explosion8.png");
            images[Constants.IMG_EXPLOSION_9] = loadImageSafely(artLoader, Constants.ART_LOC + "explosion9.png", "explosion9.png");
            images[Constants.IMG_EXPLOSION_10] = loadImageSafely(artLoader, Constants.ART_LOC + "explosion10.png", "explosion10.png");
            images[Constants.IMG_EXPLOSION_11] = loadImageSafely(artLoader, Constants.ART_LOC + "explosion11.png", "explosion11.png");
            images[Constants.IMG_EXPLOSION_12] = loadImageSafely(artLoader, Constants.ART_LOC + "explosion12.png", "explosion12.png");
            images[Constants.IMG_EXPLOSION_13] = loadImageSafely(artLoader, Constants.ART_LOC + "explosion13.png", "explosion13.png");
            images[Constants.IMG_EXPLOSION_14] = loadImageSafely(artLoader, Constants.ART_LOC + "explosion14.png", "explosion14.png");
            images[Constants.IMG_EXPLOSION_15] = loadImageSafely(artLoader, Constants.ART_LOC + "explosion15.png", "explosion15.png");
            images[Constants.IMG_EXPLOSION_16] = loadImageSafely(artLoader, Constants.ART_LOC + "explosion16.png", "explosion16.png");

            // tiles
            images[Constants.IMG_LIGHT_TILE] = loadImageSafely(artLoader, Constants.ART_LOC + "lighttile.jpg", "lighttile.jpg");
            images[Constants.IMG_DARK_TILE] = loadImageSafely(artLoader, Constants.ART_LOC + "darktile.jpg", "darktile.jpg");

            // detonate
            images[Constants.IMG_DETONATE_1] = loadImageSafely(artLoader, Constants.ART_LOC + "detonate1.png", "detonate1.png");
            images[Constants.IMG_DETONATE_2] = loadImageSafely(artLoader, Constants.ART_LOC + "detonate2.png", "detonate2.png");
            images[Constants.IMG_DETONATE_3] = loadImageSafely(artLoader, Constants.ART_LOC + "detonate3.png", "detonate3.png");
            images[Constants.IMG_DETONATE_4] = loadImageSafely(artLoader, Constants.ART_LOC + "detonate4.png", "detonate4.png");
            images[Constants.IMG_DETONATE_5] = loadImageSafely(artLoader, Constants.ART_LOC + "detonate5.png", "detonate5.png");
            images[Constants.IMG_DETONATE_6] = loadImageSafely(artLoader, Constants.ART_LOC + "detonate6.png", "detonate6.png");
            images[Constants.IMG_DETONATE_7] = loadImageSafely(artLoader, Constants.ART_LOC + "detonate7.png", "detonate7.png");
            images[Constants.IMG_DETONATE_8] = loadImageSafely(artLoader, Constants.ART_LOC + "detonate8.png", "detonate8.png");
            images[Constants.IMG_DETONATE_9] = loadImageSafely(artLoader, Constants.ART_LOC + "detonate9.png", "detonate9.png");
            images[Constants.IMG_DETONATE_10] = loadImageSafely(artLoader, Constants.ART_LOC + "detonate10.png", "detonate10.png");
            images[Constants.IMG_DETONATE_11] = loadImageSafely(artLoader, Constants.ART_LOC + "detonate11.png", "detonate11.png");
            images[Constants.IMG_DETONATE_12] = loadImageSafely(artLoader, Constants.ART_LOC + "detonate12.png", "detonate12.png");
            images[Constants.IMG_DETONATE_13] = loadImageSafely(artLoader, Constants.ART_LOC + "detonate13.png", "detonate13.png");
            images[Constants.IMG_DETONATE_14] = loadImageSafely(artLoader, Constants.ART_LOC + "detonate14.png", "detonate14.png");
            images[Constants.IMG_DETONATE_15] = loadImageSafely(artLoader, Constants.ART_LOC + "detonate15.png", "detonate15.png");
            images[Constants.IMG_DETONATE_16] = loadImageSafely(artLoader, Constants.ART_LOC + "detonate16.png", "detonate16.png");

            images[Constants.IMG_BIG_POOF_1] = loadImageSafely(artLoader, Constants.ART_LOC + "bigpoof1.png", "bigpoof1.png");
            images[Constants.IMG_BIG_POOF_2] = loadImageSafely(artLoader, Constants.ART_LOC + "bigpoof2.png", "bigpoof2.png");
            images[Constants.IMG_BIG_POOF_3] = loadImageSafely(artLoader, Constants.ART_LOC + "bigpoof3.png", "bigpoof3.png");
            images[Constants.IMG_BIG_POOF_4] = loadImageSafely(artLoader, Constants.ART_LOC + "bigpoof4.png", "bigpoof4.png");
            images[Constants.IMG_BIG_POOF_5] = loadImageSafely(artLoader, Constants.ART_LOC + "bigpoof5.png", "bigpoof5.png");
            images[Constants.IMG_BIG_POOF_6] = loadImageSafely(artLoader, Constants.ART_LOC + "bigpoof6.png", "bigpoof6.png");
            images[Constants.IMG_BIG_POOF_7] = loadImageSafely(artLoader, Constants.ART_LOC + "bigpoof7.png", "bigpoof7.png");
            images[Constants.IMG_BIG_POOF_8] = loadImageSafely(artLoader, Constants.ART_LOC + "bigpoof8.png", "bigpoof8.png");
            images[Constants.IMG_BIG_POOF_9] = loadImageSafely(artLoader, Constants.ART_LOC + "bigpoof9.png", "bigpoof9.png");
            images[Constants.IMG_BIG_POOF_10] = loadImageSafely(artLoader, Constants.ART_LOC + "bigpoof10.png", "bigpoof10.png");
            images[Constants.IMG_BIG_POOF_11] = loadImageSafely(artLoader, Constants.ART_LOC + "bigpoof11.png", "bigpoof11.png");
            images[Constants.IMG_BIG_POOF_12] = loadImageSafely(artLoader, Constants.ART_LOC + "bigpoof12.png", "bigpoof12.png");
            images[Constants.IMG_BIG_POOF_13] = loadImageSafely(artLoader, Constants.ART_LOC + "bigpoof13.png", "bigpoof13.png");
            images[Constants.IMG_BIG_POOF_14] = loadImageSafely(artLoader, Constants.ART_LOC + "bigpoof14.png", "bigpoof14.png");
            images[Constants.IMG_BIG_POOF_15] = loadImageSafely(artLoader, Constants.ART_LOC + "bigpoof15.png", "bigpoof15.png");
            images[Constants.IMG_BIG_POOF_16] = loadImageSafely(artLoader, Constants.ART_LOC + "bigpoof16.png", "bigpoof16.png");
            images[Constants.IMG_BIG_POOF_17] = loadImageSafely(artLoader, Constants.ART_LOC + "bigpoof17.png", "bigpoof17.png");
            images[Constants.IMG_BIG_POOF_18] = loadImageSafely(artLoader, Constants.ART_LOC + "bigpoof18.png", "bigpoof18.png");
            images[Constants.IMG_BIG_POOF_19] = loadImageSafely(artLoader, Constants.ART_LOC + "bigpoof19.png", "bigpoof19.png");
            images[Constants.IMG_BIG_POOF_20] = loadImageSafely(artLoader, Constants.ART_LOC + "bigpoof20.png", "bigpoof20.png");
            images[Constants.IMG_BIG_POOF_21] = loadImageSafely(artLoader, Constants.ART_LOC + "bigpoof21.png", "bigpoof21.png");
            images[Constants.IMG_BIG_POOF_22] = loadImageSafely(artLoader, Constants.ART_LOC + "bigpoof22.png", "bigpoof22.png");
            images[Constants.IMG_BIG_POOF_23] = loadImageSafely(artLoader, Constants.ART_LOC + "bigpoof23.png", "bigpoof23.png");
            images[Constants.IMG_BIG_POOF_24] = loadImageSafely(artLoader, Constants.ART_LOC + "bigpoof24.png", "bigpoof24.png");
            images[Constants.IMG_BIG_POOF_25] = loadImageSafely(artLoader, Constants.ART_LOC + "bigpoof25.png", "bigpoof25.png");

            // Clergy effects
            images[Constants.IMG_EYE] = loadImageSafely(artLoader, Constants.ART_LOC + "eye.png", "eye.png");
            images[Constants.IMG_STAR] = loadImageSafely(artLoader, Constants.ART_LOC + "star.png", "star.png");

            // holy burst
            images[Constants.IMG_BURST_1] = loadImageSafely(artLoader, Constants.ART_LOC + "burst1.png", "burst1.png");
            images[Constants.IMG_BURST_2] = loadImageSafely(artLoader, Constants.ART_LOC + "burst2.png", "burst2.png");
            images[Constants.IMG_BURST_3] = loadImageSafely(artLoader, Constants.ART_LOC + "burst3.png", "burst3.png");
            images[Constants.IMG_BURST_4] = loadImageSafely(artLoader, Constants.ART_LOC + "burst4.png", "burst4.png");
            images[Constants.IMG_BURST_5] = loadImageSafely(artLoader, Constants.ART_LOC + "burst5.png", "burst5.png");
            images[Constants.IMG_BURST_6] = loadImageSafely(artLoader, Constants.ART_LOC + "burst6.png", "burst6.png");
            images[Constants.IMG_BURST_7] = loadImageSafely(artLoader, Constants.ART_LOC + "burst7.png", "burst7.png");
            images[Constants.IMG_BURST_8] = loadImageSafely(artLoader, Constants.ART_LOC + "burst8.png", "burst8.png");
            images[Constants.IMG_BURST_9] = loadImageSafely(artLoader, Constants.ART_LOC + "burst9.png", "burst9.png");
            images[Constants.IMG_BURST_10] = loadImageSafely(artLoader, Constants.ART_LOC + "burst10.png", "burst10.png");
            images[Constants.IMG_BURST_11] = loadImageSafely(artLoader, Constants.ART_LOC + "burst11.png", "burst11.png");
            images[Constants.IMG_BURST_12] = loadImageSafely(artLoader, Constants.ART_LOC + "burst12.png", "burst12.png");
            images[Constants.IMG_BURST_13] = loadImageSafely(artLoader, Constants.ART_LOC + "burst13.png", "burst13.png");
            images[Constants.IMG_BURST_14] = loadImageSafely(artLoader, Constants.ART_LOC + "burst14.png", "burst14.png");
            images[Constants.IMG_BURST_15] = loadImageSafely(artLoader, Constants.ART_LOC + "burst15.png", "burst15.png");
            images[Constants.IMG_BURST_16] = loadImageSafely(artLoader, Constants.ART_LOC + "burst16.png", "burst16.png");
            images[Constants.IMG_BURST_17] = loadImageSafely(artLoader, Constants.ART_LOC + "burst17.png", "burst17.png");
            images[Constants.IMG_BURST_18] = loadImageSafely(artLoader, Constants.ART_LOC + "burst18.png", "burst18.png");
            images[Constants.IMG_BURST_19] = loadImageSafely(artLoader, Constants.ART_LOC + "burst19.png", "burst19.png");
            images[Constants.IMG_BURST_20] = loadImageSafely(artLoader, Constants.ART_LOC + "burst20.png", "burst20.png");

            // some nature magic
            images[Constants.IMG_WHEEL] = loadImageSafely(artLoader, Constants.ART_LOC + "wheel.png", "wheel.png");
            images[Constants.IMG_FACE] = loadImageSafely(artLoader, Constants.ART_LOC + "face.png", "face.png");
            images[Constants.IMG_MASK] = loadImageSafely(artLoader, Constants.ART_LOC + "mask.png", "mask.png");

            // white flag
            images[Constants.IMG_WHITE_FLAG] = loadImageSafely(artLoader, Constants.ART_LOC + "whiteflag.png", "whiteflag.png");

            // menu animation
            images[Constants.IMG_MENU] = loadImageSafely(artLoader, Constants.ART_LOC + "menu.jpg", "menu.jpg");

            // url = artLoader.getResource(Constants.ART_LOC + "single.png");
            // images[Constants.IMG_SINGLE] = ImageIO.read(url);
            images[Constants.IMG_SINGLE_RED] = loadImageSafely(artLoader, Constants.ART_LOC + "singlered.png", "singlered.png");

            // url = artLoader.getResource(Constants.ART_LOC + "constructed.png");
            // images[Constants.IMG_CONSTRUCTED] = ImageIO.read(url);
            images[Constants.IMG_CONSTRUCTED_RED] = loadImageSafely(artLoader, Constants.ART_LOC + "constructedred.png", "constructedred.png");

            // url = artLoader.getResource(Constants.ART_LOC + "random.png");
            // images[Constants.IMG_RANDOM] = ImageIO.read(url);
            images[Constants.IMG_RANDOM_RED] = loadImageSafely(artLoader, Constants.ART_LOC + "randomred.png", "randomred.png");

            // url = artLoader.getResource(Constants.ART_LOC + "edit.png");
            // images[Constants.IMG_EDIT] = ImageIO.read(url);
            images[Constants.IMG_EDIT_RED] = loadImageSafely(artLoader, Constants.ART_LOC + "editred.png", "editred.png");

            // url = artLoader.getResource(Constants.ART_LOC + "archive.png");
            // images[Constants.IMG_ARCHIVE] = ImageIO.read(url);
            images[Constants.IMG_ARCHIVE_RED] = loadImageSafely(artLoader, Constants.ART_LOC + "archivered.png", "archivered.png");

            // url = artLoader.getResource(Constants.ART_LOC + "buy.png");
            // images[Constants.IMG_BUY] = ImageIO.read(url);
            images[Constants.IMG_BUY_RED] = loadImageSafely(artLoader, Constants.ART_LOC + "buyred.png", "buyred.png");
            //url = artLoader.getResource(Constants.ART_LOC + "buydisabled.png");
            //images[Constants.IMG_BUY_DISABLED] = ImageIO.read(url);

            // buttons
            images[Constants.IMG_ACCOUNT] = loadImageSafely(artLoader, Constants.ART_LOC + "account.png", "account.png");
            images[Constants.IMG_ACCOUNT_HIGHLIGHT] = loadImageSafely(artLoader, Constants.ART_LOC + "accounthighlight.png", "accounthighlight.png");

            images[Constants.IMG_CREDITS] = loadImageSafely(artLoader, Constants.ART_LOC + "credits.png", "credits.png");
            images[Constants.IMG_CREDITS_HIGHLIGHT] = loadImageSafely(artLoader, Constants.ART_LOC + "creditshighlight.png", "creditshighlight.png");

            images[Constants.IMG_EXIT] = loadImageSafely(artLoader, Constants.ART_LOC + "exit.jpg", "exit.jpg");
            images[Constants.IMG_EXIT_HIGHLIGHT] = loadImageSafely(artLoader, Constants.ART_LOC + "exithighlight.jpg", "exithighlight.jpg");

            // tutorial
            images[Constants.IMG_TUTORIAL_BORDER] = loadImageSafely(artLoader, Constants.ART_LOC + "tutorialBorder.png", "tutorialBorder.png");
            images[Constants.IMG_TUTORIAL_BACK] = loadImageSafely(artLoader, Constants.ART_LOC + "tutorialBack.png", "tutorialBack.png");
            images[Constants.IMG_TUTORIAL_01] = loadImageSafely(artLoader, Constants.ART_LOC + "tut_01.png", "tut_01.png");
            images[Constants.IMG_TUTORIAL_03] = loadImageSafely(artLoader, Constants.ART_LOC + "tut_03.png", "tut_03.png");
            images[Constants.IMG_TUTORIAL_04] = loadImageSafely(artLoader, Constants.ART_LOC + "tut_04.png", "tut_04.png");
            images[Constants.IMG_TUTORIAL_05] = loadImageSafely(artLoader, Constants.ART_LOC + "tut_05.png", "tut_05.png");
            images[Constants.IMG_TUTORIAL_06] = loadImageSafely(artLoader, Constants.ART_LOC + "tut_06.png", "tut_06.png");
            images[Constants.IMG_TUTORIAL_07] = loadImageSafely(artLoader, Constants.ART_LOC + "tut_07.png", "tut_07.png");
            images[Constants.IMG_TUTORIAL_08] = loadImageSafely(artLoader, Constants.ART_LOC + "tut_08.png", "tut_08.png");
            images[Constants.IMG_TUTORIAL_10] = loadImageSafely(artLoader, Constants.ART_LOC + "tut_10.png", "tut_10.png");
            images[Constants.IMG_TUTORIAL_11] = loadImageSafely(artLoader, Constants.ART_LOC + "tut_11.png", "tut_11.png");
            images[Constants.IMG_TUTORIAL_12] = loadImageSafely(artLoader, Constants.ART_LOC + "tut_12.png", "tut_12.png");
            images[Constants.IMG_TUTORIAL_13] = loadImageSafely(artLoader, Constants.ART_LOC + "tut_13.png", "tut_13.png");
            images[Constants.IMG_TUTORIAL_14] = loadImageSafely(artLoader, Constants.ART_LOC + "tut_14.png", "tut_14.png");
            images[Constants.IMG_TUTORIAL_15] = loadImageSafely(artLoader, Constants.ART_LOC + "tut_15.png", "tut_15.png");
            images[Constants.IMG_TUTORIAL_16] = loadImageSafely(artLoader, Constants.ART_LOC + "tut_16.png", "tut_16.png");
            images[Constants.IMG_TUTORIAL_17] = loadImageSafely(artLoader, Constants.ART_LOC + "tut_17.png", "tut_17.png");
            images[Constants.IMG_TUTORIAL_18] = loadImageSafely(artLoader, Constants.ART_LOC + "tut_18.png", "tut_18.png");
            images[Constants.IMG_TUTORIAL_19] = loadImageSafely(artLoader, Constants.ART_LOC + "tut_19.png", "tut_19.png");
            images[Constants.IMG_TUTORIAL_20] = loadImageSafely(artLoader, Constants.ART_LOC + "tut_20.png", "tut_20.png");
            images[Constants.IMG_TUTORIAL_21] = loadImageSafely(artLoader, Constants.ART_LOC + "tut_21.png", "tut_21.png");
            images[Constants.IMG_TUTORIAL_22] = loadImageSafely(artLoader, Constants.ART_LOC + "tut_22.png", "tut_22.png");
            images[Constants.IMG_TUTORIAL_23] = loadImageSafely(artLoader, Constants.ART_LOC + "tut_23.png", "tut_23.png");
            images[Constants.IMG_TUTORIAL_24] = loadImageSafely(artLoader, Constants.ART_LOC + "tut_24.png", "tut_24.png");
            images[Constants.IMG_TUTORIAL_25] = loadImageSafely(artLoader, Constants.ART_LOC + "tut_25.png", "tut_25.png");
            images[Constants.IMG_TUTORIAL_26] = loadImageSafely(artLoader, Constants.ART_LOC + "tut_26.png", "tut_26.png");
            images[Constants.IMG_TUTORIAL_27] = loadImageSafely(artLoader, Constants.ART_LOC + "tut_27.png", "tut_27.png");
            images[Constants.IMG_TUTORIAL_28] = loadImageSafely(artLoader, Constants.ART_LOC + "tut_28.png", "tut_28.png");
            images[Constants.IMG_TUTORIAL_29] = loadImageSafely(artLoader, Constants.ART_LOC + "tut_29.png", "tut_29.png");
            images[Constants.IMG_TUTORIAL_31] = loadImageSafely(artLoader, Constants.ART_LOC + "tut_31.png", "tut_31.png");
            images[Constants.IMG_TUTORIAL_32] = loadImageSafely(artLoader, Constants.ART_LOC + "tut_32.png", "tut_32.png");
            images[Constants.IMG_TUTORIAL_33] = loadImageSafely(artLoader, Constants.ART_LOC + "tut_33.png", "tut_33.png");
            images[Constants.IMG_TUTORIAL_34] = loadImageSafely(artLoader, Constants.ART_LOC + "tut_34.png", "tut_34.png");
            images[Constants.IMG_TUTORIAL_35] = loadImageSafely(artLoader, Constants.ART_LOC + "tut_35.png", "tut_35.png");
            images[Constants.IMG_TUTORIAL_36] = loadImageSafely(artLoader, Constants.ART_LOC + "tut_36.png", "tut_36.png");

            // tutorial buttons
            images[Constants.IMG_PREV] = loadImageSafely(artLoader, Constants.ART_LOC + "tut_prev.png", "tut_prev.png");
            images[Constants.IMG_PREV_HIGHLIGHTED] = loadImageSafely(artLoader, Constants.ART_LOC + "tut_prev_highlighted.png", "tut_prev_highlighted.png");
            images[Constants.IMG_JUMP_PREV] = loadImageSafely(artLoader, Constants.ART_LOC + "tut_jump_prev.png", "tut_jump_prev.png");
            images[Constants.IMG_JUMP_PREV_HIGHLIGHTED] = loadImageSafely(artLoader, Constants.ART_LOC + "tut_jump_prev_highlighted.png", "tut_jump_prev_highlighted.png");
            images[Constants.IMG_NEXT] = loadImageSafely(artLoader, Constants.ART_LOC + "tut_next.png", "tut_next.png");
            images[Constants.IMG_NEXT_HIGHLIGHTED] = loadImageSafely(artLoader, Constants.ART_LOC + "tut_next_highlighted.png", "tut_next_highlighted.png");
            images[Constants.IMG_JUMP_NEXT] = loadImageSafely(artLoader, Constants.ART_LOC + "tut_jump_next.png", "tut_jump_next.png");
            images[Constants.IMG_JUMP_NEXT_HIGHLIGHTED] = loadImageSafely(artLoader, Constants.ART_LOC + "tut_jump_next_highlighted.png", "tut_jump_next_highlighted.png");
            images[Constants.IMG_CLOSE] = loadImageSafely(artLoader, Constants.ART_LOC + "tut_close.png", "tut_close.png");
            images[Constants.IMG_CLOSE_HIGHLIGHTED] = loadImageSafely(artLoader, Constants.ART_LOC + "tut_close_highlighted.png", "tut_close_highlighted.png");
            images[Constants.IMG_INDEX] = loadImageSafely(artLoader, Constants.ART_LOC + "tut_index.png", "tut_index.png");
            images[Constants.IMG_INDEX_HIGHLIGHTED] = loadImageSafely(artLoader, Constants.ART_LOC + "tut_index_highlighted.png", "tut_index_highlighted.png");

            // Relic Art

            // banish
            images[Constants.IMG_RELIC_BANISH] = loadImageSafely(artLoader, Constants.ART_LOC + "relic_banish.png", "relic_banish.png");

            // clockwork
            images[Constants.IMG_RELIC_CLOCKWORK] = loadImageSafely(artLoader, Constants.ART_LOC + "relic_clockwork.png", "relic_clockwork.png");

            // evasive
            images[Constants.IMG_RELIC_EVASIVE] = loadImageSafely(artLoader, Constants.ART_LOC + "relic_evasive.png", "relic_evasive.png");

            // explode
            images[Constants.IMG_RELIC_EXPLODE] = loadImageSafely(artLoader, Constants.ART_LOC + "relic_explode.png", "relic_explode.png");

            // flight
            images[Constants.IMG_RELIC_FLIGHT] = loadImageSafely(artLoader, Constants.ART_LOC + "relic_flight.png", "relic_flight.png");

            // command
            images[Constants.IMG_RELIC_GIFT_UNIT] = loadImageSafely(artLoader, Constants.ART_LOC + "relic_gift_unit.png", "relic_gift_unit.png");

            // heal'n'move
            images[Constants.IMG_RELIC_HEAL_MOVE] = loadImageSafely(artLoader, Constants.ART_LOC + "relic_heal_move.png", "relic_heal_move.png");

            // parry
            images[Constants.IMG_RELIC_PARRY] = loadImageSafely(artLoader, Constants.ART_LOC + "relic_parry.png", "relic_parry.png");

            // reset
            images[Constants.IMG_RELIC_RESET] = loadImageSafely(artLoader, Constants.ART_LOC + "relic_reset.png", "relic_reset.png");

            // aegis
            images[Constants.IMG_RELIC_SPELL_BLOCK] = loadImageSafely(artLoader, Constants.ART_LOC + "relic_spell_block.png", "relic_spell_block.png");

            // stun
            images[Constants.IMG_RELIC_STUN] = loadImageSafely(artLoader, Constants.ART_LOC + "relic_stun.png", "relic_stun.png");

            // vampiric
            images[Constants.IMG_RELIC_VAMPIRE] = loadImageSafely(artLoader, Constants.ART_LOC + "relic_vampire.png", "relic_vampire.png");

            // unit stats icons
            images[Constants.IMG_ICON_ACTIONS] = loadImageSafely(artLoader, Constants.ART_LOC + "icon_actions.png", "icon_actions.png");
            images[Constants.IMG_ICON_ARMOR] = loadImageSafely(artLoader, Constants.ART_LOC + "icon_armor.png", "icon_armor.png");
            images[Constants.IMG_ICON_DEPLOY] = loadImageSafely(artLoader, Constants.ART_LOC + "icon_deploy.png", "icon_deploy.png");
            images[Constants.IMG_ICON_LIFE] = loadImageSafely(artLoader, Constants.ART_LOC + "icon_life.png", "icon_life.png");
            images[Constants.IMG_ICON_POWER] = loadImageSafely(artLoader, Constants.ART_LOC + "icon_power.png", "icon_power.png");
            images[Constants.IMG_ICON_MURDERER] = loadImageSafely(artLoader, Constants.ART_LOC + "icon_murderer.png", "icon_murderer.png");

            // parry/damage
            images[Constants.IMG_PARRY] = loadImageSafely(artLoader, Constants.ART_LOC + "parry.png", "parry.png");
            images[Constants.IMG_MPBACK] = loadImageSafely(artLoader, Constants.ART_LOC + "mpback.png", "mpback.png");
            images[Constants.IMG_DAMBACK] = loadImageSafely(artLoader, Constants.ART_LOC + "damback.png", "damback.png");

            // splat animations
            images[Constants.IMG_SPLAT_INORGANIC_1] = loadImageSafely(artLoader, Constants.ART_LOC + "splat_inorganic1.png", "splat_inorganic1.png");
            images[Constants.IMG_SPLAT_INORGANIC_2] = loadImageSafely(artLoader, Constants.ART_LOC + "splat_inorganic2.png", "splat_inorganic2.png");
            images[Constants.IMG_SPLAT_INORGANIC_3] = loadImageSafely(artLoader, Constants.ART_LOC + "splat_inorganic3.png", "splat_inorganic3.png");
            images[Constants.IMG_SPLAT_INORGANIC_4] = loadImageSafely(artLoader, Constants.ART_LOC + "splat_inorganic4.png", "splat_inorganic4.png");
            images[Constants.IMG_SPLAT_INORGANIC_5] = loadImageSafely(artLoader, Constants.ART_LOC + "splat_inorganic5.png", "splat_inorganic5.png");
            images[Constants.IMG_SPLAT_ORGANIC_1] = loadImageSafely(artLoader, Constants.ART_LOC + "splat_organic1.png", "splat_organic1.png");
            images[Constants.IMG_SPLAT_ORGANIC_2] = loadImageSafely(artLoader, Constants.ART_LOC + "splat_organic2.png", "splat_organic2.png");
            images[Constants.IMG_SPLAT_ORGANIC_3] = loadImageSafely(artLoader, Constants.ART_LOC + "splat_organic3.png", "splat_organic3.png");
            images[Constants.IMG_SPLAT_ORGANIC_4] = loadImageSafely(artLoader, Constants.ART_LOC + "splat_organic4.png", "splat_organic4.png");
            images[Constants.IMG_SPLAT_ORGANIC_5] = loadImageSafely(artLoader, Constants.ART_LOC + "splat_organic5.png", "splat_organic5.png");

            // summon animation
            images[Constants.IMG_SUMMON_1] = loadImageSafely(artLoader, Constants.ART_LOC + "summon1.png", "summon1.png");
            images[Constants.IMG_SUMMON_2] = loadImageSafely(artLoader, Constants.ART_LOC + "summon2.png", "summon2.png");
            images[Constants.IMG_SUMMON_3] = loadImageSafely(artLoader, Constants.ART_LOC + "summon3.png", "summon3.png");
            images[Constants.IMG_SUMMON_4] = loadImageSafely(artLoader, Constants.ART_LOC + "summon4.png", "summon4.png");
            images[Constants.IMG_SUMMON_5] = loadImageSafely(artLoader, Constants.ART_LOC + "summon5.png", "summon5.png");
            images[Constants.IMG_SUMMON_6] = loadImageSafely(artLoader, Constants.ART_LOC + "summon6.png", "summon6.png");
            images[Constants.IMG_SUMMON_7] = loadImageSafely(artLoader, Constants.ART_LOC + "summon7.png", "summon7.png");
            images[Constants.IMG_SUMMON_8] = loadImageSafely(artLoader, Constants.ART_LOC + "summon8.png", "summon8.png");

            // summon blue animation
            images[Constants.IMG_SUMMON_BLUE_1] = loadImageSafely(artLoader, Constants.ART_LOC + "summonblue1.png", "summonblue1.png");
            images[Constants.IMG_SUMMON_BLUE_2] = loadImageSafely(artLoader, Constants.ART_LOC + "summonblue2.png", "summonblue2.png");
            images[Constants.IMG_SUMMON_BLUE_3] = loadImageSafely(artLoader, Constants.ART_LOC + "summonblue3.png", "summonblue3.png");
            images[Constants.IMG_SUMMON_BLUE_4] = loadImageSafely(artLoader, Constants.ART_LOC + "summonblue4.png", "summonblue4.png");
            images[Constants.IMG_SUMMON_BLUE_5] = loadImageSafely(artLoader, Constants.ART_LOC + "summonblue5.png", "summonblue5.png");
            images[Constants.IMG_SUMMON_BLUE_6] = loadImageSafely(artLoader, Constants.ART_LOC + "summonblue6.png", "summonblue6.png");
            images[Constants.IMG_SUMMON_BLUE_7] = loadImageSafely(artLoader, Constants.ART_LOC + "summonblue7.png", "summonblue7.png");
            images[Constants.IMG_SUMMON_BLUE_8] = loadImageSafely(artLoader, Constants.ART_LOC + "summonblue8.png", "summonblue8.png");

            // lockdown animation
            images[Constants.IMG_LOCKDOWN_1] = loadImageSafely(artLoader, Constants.ART_LOC + "lockdown1.png", "lockdown1.png");
            images[Constants.IMG_LOCKDOWN_2] = loadImageSafely(artLoader, Constants.ART_LOC + "lockdown2.png", "lockdown2.png");
            images[Constants.IMG_LOCKDOWN_3] = loadImageSafely(artLoader, Constants.ART_LOC + "lockdown3.png", "lockdown3.png");
            images[Constants.IMG_LOCKDOWN_4] = loadImageSafely(artLoader, Constants.ART_LOC + "lockdown4.png", "lockdown4.png");
            images[Constants.IMG_LOCKDOWN_5] = loadImageSafely(artLoader, Constants.ART_LOC + "lockdown5.png", "lockdown5.png");
            images[Constants.IMG_LOCKDOWN_6] = loadImageSafely(artLoader, Constants.ART_LOC + "lockdown6.png", "lockdown6.png");
            images[Constants.IMG_LOCKDOWN_7] = loadImageSafely(artLoader, Constants.ART_LOC + "lockdown7.png", "lockdown7.png");
            images[Constants.IMG_LOCKDOWN_8] = loadImageSafely(artLoader, Constants.ART_LOC + "lockdown8.png", "lockdown8.png");
            images[Constants.IMG_LOCKDOWN_9] = loadImageSafely(artLoader, Constants.ART_LOC + "lockdown9.png", "lockdown9.png");
            images[Constants.IMG_LOCKDOWN_10] = loadImageSafely(artLoader, Constants.ART_LOC + "lockdown10.png", "lockdown10.png");
            images[Constants.IMG_LOCKDOWN_11] = loadImageSafely(artLoader, Constants.ART_LOC + "lockdown11.png", "lockdown11.png");

            // tomb lord animation for dracolich
            images[Constants.IMG_TOMB_LORD_1] = loadImageSafely(artLoader, Constants.ART_LOC + "tomblord1.png", "tomblord1.png");
            images[Constants.IMG_TOMB_LORD_2] = loadImageSafely(artLoader, Constants.ART_LOC + "tomblord2.png", "tomblord2.png");

            // images for time animation
            images[Constants.IMG_TIME_1] = loadImageSafely(artLoader, Constants.ART_LOC + "time1.png", "time1.png");
            images[Constants.IMG_TIME_2] = loadImageSafely(artLoader, Constants.ART_LOC + "time2.png", "time2.png");
            images[Constants.IMG_TIME_3] = loadImageSafely(artLoader, Constants.ART_LOC + "time3.png", "time3.png");

            // relic rune
            images[Constants.IMG_RELIC] = loadImageSafely(artLoader, Constants.ART_LOC + "relic.png", "relic.png");

            // mason's wall building animation
            images[Constants.IMG_BUILD_01] = loadImageSafely(artLoader, Constants.ART_LOC + "build01.png", "build01.png");
            images[Constants.IMG_BUILD_02] = loadImageSafely(artLoader, Constants.ART_LOC + "build02.png", "build02.png");
            images[Constants.IMG_BUILD_03] = loadImageSafely(artLoader, Constants.ART_LOC + "build03.png", "build03.png");
            images[Constants.IMG_BUILD_04] = loadImageSafely(artLoader, Constants.ART_LOC + "build04.png", "build04.png");
            images[Constants.IMG_BUILD_05] = loadImageSafely(artLoader, Constants.ART_LOC + "build05.png", "build05.png");
            images[Constants.IMG_BUILD_06] = loadImageSafely(artLoader, Constants.ART_LOC + "build06.png", "build06.png");
            images[Constants.IMG_BUILD_07] = loadImageSafely(artLoader, Constants.ART_LOC + "build07.png", "build07.png");
            images[Constants.IMG_BUILD_08] = loadImageSafely(artLoader, Constants.ART_LOC + "build08.png", "build08.png");
            images[Constants.IMG_BUILD_09] = loadImageSafely(artLoader, Constants.ART_LOC + "build09.png", "build09.png");
            images[Constants.IMG_BUILD_10] = loadImageSafely(artLoader, Constants.ART_LOC + "build10.png", "build10.png");
            images[Constants.IMG_BUILD_11] = loadImageSafely(artLoader, Constants.ART_LOC + "build11.png", "build11.png");
            images[Constants.IMG_BUILD_12] = loadImageSafely(artLoader, Constants.ART_LOC + "build12.png", "build12.png");
            images[Constants.IMG_BUILD_13] = loadImageSafely(artLoader, Constants.ART_LOC + "build13.png", "build13.png");
            images[Constants.IMG_BUILD_14] = loadImageSafely(artLoader, Constants.ART_LOC + "build14.png", "build14.png");
            images[Constants.IMG_BUILD_15] = loadImageSafely(artLoader, Constants.ART_LOC + "build15.png", "build15.png");
            images[Constants.IMG_BUILD_16] = loadImageSafely(artLoader, Constants.ART_LOC + "build16.png", "build16.png");
            images[Constants.IMG_BUILD_17] = loadImageSafely(artLoader, Constants.ART_LOC + "build17.png", "build17.png");
            images[Constants.IMG_BUILD_18] = loadImageSafely(artLoader, Constants.ART_LOC + "build18.png", "build18.png");
            images[Constants.IMG_BUILD_19] = loadImageSafely(artLoader, Constants.ART_LOC + "build19.png", "build19.png");
            images[Constants.IMG_BUILD_20] = loadImageSafely(artLoader, Constants.ART_LOC + "build20.png", "build20.png");
            images[Constants.IMG_BUILD_21] = loadImageSafely(artLoader, Constants.ART_LOC + "build21.png", "build21.png");
            images[Constants.IMG_BUILD_22] = loadImageSafely(artLoader, Constants.ART_LOC + "build22.png", "build22.png");
            images[Constants.IMG_BUILD_23] = loadImageSafely(artLoader, Constants.ART_LOC + "build23.png", "build23.png");
            images[Constants.IMG_BUILD_24] = loadImageSafely(artLoader, Constants.ART_LOC + "build24.png", "build24.png");
            images[Constants.IMG_BUILD_25] = loadImageSafely(artLoader, Constants.ART_LOC + "build25.png", "build25.png");
            images[Constants.IMG_BUILD_26] = loadImageSafely(artLoader, Constants.ART_LOC + "build26.png", "build26.png");
            images[Constants.IMG_BUILD_27] = loadImageSafely(artLoader, Constants.ART_LOC + "build27.png", "build27.png");
            images[Constants.IMG_BUILD_28] = loadImageSafely(artLoader, Constants.ART_LOC + "build28.png", "build28.png");
            images[Constants.IMG_BUILD_29] = loadImageSafely(artLoader, Constants.ART_LOC + "build29.png", "build29.png");
            images[Constants.IMG_BUILD_30] = loadImageSafely(artLoader, Constants.ART_LOC + "build30.png", "build30.png");
            images[Constants.IMG_BUILD_31] = loadImageSafely(artLoader, Constants.ART_LOC + "build31.png", "build31.png");
            images[Constants.IMG_BUILD_32] = loadImageSafely(artLoader, Constants.ART_LOC + "build32.png", "build32.png");
            images[Constants.IMG_BUILD_33] = loadImageSafely(artLoader, Constants.ART_LOC + "build33.png", "build33.png");
            images[Constants.IMG_BUILD_34] = loadImageSafely(artLoader, Constants.ART_LOC + "build34.png", "build34.png");

            // powerup art
            images[Constants.IMG_POWERUP_TOXIC] = loadImageSafely(artLoader, Constants.ART_LOC + "powerup_toxic.png", "powerup_toxic.png");
            images[Constants.IMG_POWERUP_EVASIVE] = loadImageSafely(artLoader, Constants.ART_LOC + "powerup_evasive.png", "powerup_evasive.png");
            images[Constants.IMG_POWERUP_RESILIENT] = loadImageSafely(artLoader, Constants.ART_LOC + "powerup_resilient.png", "powerup_resilient.png");
            images[Constants.IMG_POWERUP_LONGSHANK] = loadImageSafely(artLoader, Constants.ART_LOC + "powerup_longshank.png", "powerup_longshank.png");
            images[Constants.IMG_POWERUP_MIGHTY] = loadImageSafely(artLoader, Constants.ART_LOC + "powerup_mighty.png", "powerup_mighty.png");
            images[Constants.IMG_POWERUP_CLOCKWORK] = loadImageSafely(artLoader, Constants.ART_LOC + "powerup_clockwork.png", "powerup_clockwork.png");
            images[Constants.IMG_POWERUP_VAMPIRIC] = loadImageSafely(artLoader, Constants.ART_LOC + "powerup_vampiric.png", "powerup_vampiric.png");
            images[Constants.IMG_POWERUP_CUNNING] = loadImageSafely(artLoader, Constants.ART_LOC + "powerup_cunning.png", "powerup_cunning.png");
            images[Constants.IMG_POWERUP_EPIC] = loadImageSafely(artLoader, Constants.ART_LOC + "powerup_epic.png", "powerup_epic.png");
            images[Constants.IMG_POWERUP_ARCANE] = loadImageSafely(artLoader, Constants.ART_LOC + "powerup_arcane.png", "powerup_arcane.png");
            images[Constants.IMG_POWERUP_ASCENDANT] = loadImageSafely(artLoader, Constants.ART_LOC + "powerup_ascendant.png", "powerup_ascendant.png");
            images[Constants.IMG_POWERUP_GUARDIAN] = loadImageSafely(artLoader, Constants.ART_LOC + "powerup_guardian.png", "powerup_guardian.png");
            images[Constants.IMG_POWERUP_VIGILANT] = loadImageSafely(artLoader, Constants.ART_LOC + "powerup_vigilant.png", "powerup_vigilant.png");
            images[Constants.IMG_POWERUP_ZEALOUS] = loadImageSafely(artLoader, Constants.ART_LOC + "powerup_zealous.png", "powerup_zealous.png");
            images[Constants.IMG_POWERUP_RAMPAGING] = loadImageSafely(artLoader, Constants.ART_LOC + "powerup_rampaging.png", "powerup_rampaging.png");
            images[Constants.IMG_POWERUP_RUTHLESS] = loadImageSafely(artLoader, Constants.ART_LOC + "powerup_ruthless.png", "powerup_ruthless.png");
            images[Constants.IMG_POWERUP_ENRAGED] = loadImageSafely(artLoader, Constants.ART_LOC + "powerup_enraged.png", "powerup_enraged.png");

            // PLayer Panel Stuff
            images[Constants.IMG_PLAYERPANEL] = loadImageSafely(artLoader, Constants.ART_LOC + "PlayerPanel.jpg", "PlayerPanel.jpg");
            images[Constants.IMG_CHAT_LINE] = loadImageSafely(artLoader, Constants.ART_LOC + "chat_line.png", "chat_line.png");
            images[Constants.IMG_CHAT_UP] = loadImageSafely(artLoader, Constants.ART_LOC + "chat_up.png", "chat_up.png");
            images[Constants.IMG_CHAT_DOWN] = loadImageSafely(artLoader, Constants.ART_LOC + "chat_down.png", "chat_down.png");
            images[Constants.IMG_CHAT] = loadImageSafely(artLoader, Constants.ART_LOC + "chat.png", "chat.png");
            images[Constants.IMG_PLAYERS] = loadImageSafely(artLoader, Constants.ART_LOC + "players.png", "players.png");
            images[Constants.IMG_SCROLL] = loadImageSafely(artLoader, Constants.ART_LOC + "scroll.png", "scroll.png");
            images[Constants.IMG_SCROLL_PLAYER] = loadImageSafely(artLoader, Constants.ART_LOC + "scroll_player.png", "scroll_player.png");
            images[Constants.IMG_SCROLL_BAR] = loadImageSafely(artLoader, Constants.ART_LOC + "scroll_bar.png", "scroll_bar.png");
            images[Constants.IMG_PLAYERS_BUTTON] = loadImageSafely(artLoader, Constants.ART_LOC + "players_button.png", "players_button.png");
            images[Constants.IMG_CHAT_BUTTON] = loadImageSafely(artLoader, Constants.ART_LOC + "chat_button.png", "chat_button.png");

            images[Constants.IMG_BONES] = loadImageSafely(artLoader, Constants.ART_LOC + "bones.png", "bones.png");


            // edit army stuff
            images[Constants.IMG_NEW_UNIT_DOWN] = loadImageSafely(artLoader, Constants.ART_LOC + "newunitdown.jpg", "newunitdown.jpg");
            images[Constants.IMG_NEW_UNIT_DOWN_HIGHLIGHT] = loadImageSafely(artLoader, Constants.ART_LOC + "newunitdownhighlight.jpg", "newunitdownhighlight.jpg");
            images[Constants.IMG_NEW_UNIT_UP] = loadImageSafely(artLoader, Constants.ART_LOC + "newunitup.jpg", "newunitup.jpg");
            images[Constants.IMG_NEW_UNIT_UP_HIGHLIGHT] = loadImageSafely(artLoader, Constants.ART_LOC + "newunituphighlight.jpg", "newunituphighlight.jpg");
            images[Constants.IMG_EDIT_GOLD] = loadImageSafely(artLoader, Constants.ART_LOC + "editgold.jpg", "editgold.jpg");

            images[Constants.IMG_EDIT_STAT_PANEL] = loadImageSafely(artLoader, Constants.ART_LOC + "editstatpanel.jpg", "editstatpanel.jpg");
            images[Constants.IMG_EDIT_CATEGORY_PANEL] = loadImageSafely(artLoader, Constants.ART_LOC + "editcategorypanel.jpg", "editcategorypanel.jpg");
            images[Constants.IMG_EDIT_UNITS_PANEL] = loadImageSafely(artLoader, Constants.ART_LOC + "editunitspanel.jpg", "editunitspanel.jpg");
            images[Constants.IMG_EDIT_CASTLE_PANEL] = loadImageSafely(artLoader, Constants.ART_LOC + "editcastlepanel.jpg", "editcastlepanel.jpg");
            images[Constants.IMG_EDIT_STAT_BOX] = loadImageSafely(artLoader, Constants.ART_LOC + "editstatbox.jpg", "editstatbox.jpg");

            images[Constants.IMG_EDIT_ADD] = loadImageSafely(artLoader, Constants.ART_LOC + "editadd.jpg", "editadd.jpg");
            images[Constants.IMG_EDIT_ADD_HIGHLIGHT] = loadImageSafely(artLoader, Constants.ART_LOC + "editaddhighlight.jpg", "editaddhighlight.jpg");
            images[Constants.IMG_EDIT_ADD_ALERT] = loadImageSafely(artLoader, Constants.ART_LOC + "editaddalert.jpg", "editaddalert.jpg");
            images[Constants.IMG_EDIT_BUTTON] = loadImageSafely(artLoader, Constants.ART_LOC + "editbutton.jpg", "editbutton.jpg");
            images[Constants.IMG_EDIT_BUTTON_HIGHLIGHT] = loadImageSafely(artLoader, Constants.ART_LOC + "editbuttonhighlight.jpg", "editbuttonhighlight.jpg");
            images[Constants.IMG_NEW_UNIT] = loadImageSafely(artLoader, Constants.ART_LOC + "newunit.jpg", "newunit.jpg");
            images[Constants.IMG_NEW_UNIT_DISABLED] = loadImageSafely(artLoader, Constants.ART_LOC + "newunitdisabled.jpg", "newunitdisabled.jpg");
            images[Constants.IMG_NEW_UNIT_SELECTED] = loadImageSafely(artLoader, Constants.ART_LOC + "newunitselected.jpg", "newunitselected.jpg");
            images[Constants.IMG_NEW_UNIT_HIGHLIGHT] = loadImageSafely(artLoader, Constants.ART_LOC + "newunithighlight.jpg", "newunithighlight.jpg");

            // etc
            images[Constants.IMG_BACK_PANEL_EDIT] = loadImageSafely(artLoader, Constants.ART_LOC + "backpaneledit.jpg", "backpaneledit.jpg");

            // coop
            // url = artLoader.getResource(Constants.ART_LOC + "cooperative.png");
            // images[Constants.IMG_COOPERATIVE] = ImageIO.read(url);
            images[Constants.IMG_COOPERATIVE_RED] = loadImageSafely(artLoader, Constants.ART_LOC + "cooperativered.png", "cooperativered.png");

            // new url buttons
            images[Constants.IMG_FORUM] = loadImageSafely(artLoader, Constants.ART_LOC + "forum.png", "forum.png");
            images[Constants.IMG_FORUM_HIGHLIGHT] = loadImageSafely(artLoader, Constants.ART_LOC + "forumhighlight.png", "forumhighlight.png");
            images[Constants.IMG_BLOG] = loadImageSafely(artLoader, Constants.ART_LOC + "blog.png", "blog.png");
            images[Constants.IMG_BLOG_HIGHLIGHT] = loadImageSafely(artLoader, Constants.ART_LOC + "bloghighlight.png", "bloghighlight.png");
            images[Constants.IMG_GUIDE] = loadImageSafely(artLoader, Constants.ART_LOC + "guide.png", "guide.png");
            images[Constants.IMG_GUIDE_HIGHLIGHT] = loadImageSafely(artLoader, Constants.ART_LOC + "guidehighlight.png", "guidehighlight.png");

            images[Constants.IMG_REFER_FRIEND] = loadImageSafely(artLoader, Constants.ART_LOC + "referfriend.png", "referfriend.png");
            images[Constants.IMG_REFER_FRIEND_HIGHLIGHT] = loadImageSafely(artLoader, Constants.ART_LOC + "referfriendhighlight.png", "referfriendhighlight.png");
            images[Constants.IMG_SCORES] = loadImageSafely(artLoader, Constants.ART_LOC + "topscores.png", "topscores.png");
            images[Constants.IMG_SCORES_HIGHLIGHT] = loadImageSafely(artLoader, Constants.ART_LOC + "topscoreshighlight.png", "topscoreshighlight.png");

            // advertisement
            images[Constants.IMG_AD] = loadImageSafely(artLoader, Constants.ART_LOC + "ad.jpg", "ad.jpg");

            // gold border
            images[Constants.IMG_BORDER] = loadImageSafely(artLoader, Constants.ART_LOC + "border.png", "border.png");

            // splotlight
            images[Constants.IMG_SPOTLIGHT] = loadImageSafely(artLoader, Constants.ART_LOC + "spotlight.png", "spotlight.png");
            images[Constants.IMG_BLACKLIGHT] = loadImageSafely(artLoader, Constants.ART_LOC + "blacklight.png", "blacklight.png");

            // team
            images[Constants.IMG_TEAM] = loadImageSafely(artLoader, Constants.ART_LOC + "team.png", "team.png");
            images[Constants.IMG_TEAM_HIGHLIGHT] = loadImageSafely(artLoader, Constants.ART_LOC + "teamhighlight.png", "teamhighlight.png");

            images[Constants.IMG_TEAM_NOT_READY] = loadImageSafely(artLoader, Constants.ART_LOC + "team_notready.png", "team_notready.png");
            images[Constants.IMG_SWORD_1] = loadImageSafely(artLoader, Constants.ART_LOC + "sword_1.png", "sword_1.png");
            images[Constants.IMG_SWORD_2] = loadImageSafely(artLoader, Constants.ART_LOC + "sword_2.png", "sword_2.png");
            images[Constants.IMG_TEAMS_BOX] = loadImageSafely(artLoader, Constants.ART_LOC + "teams_box.png", "teams_box.png");
            images[Constants.IMG_TEAMS_PLAYER] = loadImageSafely(artLoader, Constants.ART_LOC + "teams_player.png", "teams_player.png");

            // clash animation
            images[Constants.IMG_CLASH_1] = loadImageSafely(artLoader, Constants.ART_LOC + "clash1.png", "clash1.png");
            images[Constants.IMG_CLASH_2] = loadImageSafely(artLoader, Constants.ART_LOC + "clash2.png", "clash2.png");
            images[Constants.IMG_CLASH_3] = loadImageSafely(artLoader, Constants.ART_LOC + "clash3.png", "clash3.png");
            images[Constants.IMG_CLASH_4] = loadImageSafely(artLoader, Constants.ART_LOC + "clash4.png", "clash4.png");
            images[Constants.IMG_CLASH_5] = loadImageSafely(artLoader, Constants.ART_LOC + "clash5.png", "clash5.png");
            images[Constants.IMG_CLASH_6] = loadImageSafely(artLoader, Constants.ART_LOC + "clash6.png", "clash6.png");
            images[Constants.IMG_CLASH_7] = loadImageSafely(artLoader, Constants.ART_LOC + "clash7.png", "clash7.png");
            images[Constants.IMG_CLASH_8] = loadImageSafely(artLoader, Constants.ART_LOC + "clash8.png", "clash8.png");

            images[Constants.IMG_TARGET_01] = loadImageSafely(artLoader, Constants.ART_LOC + "target01.png", "target01.png");
            images[Constants.IMG_TARGET_02] = loadImageSafely(artLoader, Constants.ART_LOC + "target02.png", "target02.png");
            images[Constants.IMG_TARGET_03] = loadImageSafely(artLoader, Constants.ART_LOC + "target03.png", "target03.png");
            images[Constants.IMG_TARGET_04] = loadImageSafely(artLoader, Constants.ART_LOC + "target04.png", "target04.png");
            images[Constants.IMG_TARGET_05] = loadImageSafely(artLoader, Constants.ART_LOC + "target05.png", "target05.png");
            images[Constants.IMG_TARGET_06] = loadImageSafely(artLoader, Constants.ART_LOC + "target06.png", "target06.png");
            images[Constants.IMG_TARGET_07] = loadImageSafely(artLoader, Constants.ART_LOC + "target07.png", "target07.png");
            images[Constants.IMG_TARGET_08] = loadImageSafely(artLoader, Constants.ART_LOC + "target08.png", "target08.png");
            images[Constants.IMG_TARGET_09] = loadImageSafely(artLoader, Constants.ART_LOC + "target09.png", "target09.png");
            images[Constants.IMG_TARGET_10] = loadImageSafely(artLoader, Constants.ART_LOC + "target10.png", "target10.png");
            images[Constants.IMG_TARGET_11] = loadImageSafely(artLoader, Constants.ART_LOC + "target11.png", "target11.png");
            images[Constants.IMG_TARGET_12] = loadImageSafely(artLoader, Constants.ART_LOC + "target12.png", "target12.png");

            images[Constants.IMG_SHIELD_1] = loadImageSafely(artLoader, Constants.ART_LOC + "shield1.png", "shield1.png");
            images[Constants.IMG_SHIELD_2] = loadImageSafely(artLoader, Constants.ART_LOC + "shield2.png", "shield2.png");

            images[Constants.IMG_TEAM_ICON_1] = loadImageSafely(artLoader, Constants.ART_LOC + "team_icon_1.png", "team_icon_1.png");
            images[Constants.IMG_TEAM_ICON_2] = loadImageSafely(artLoader, Constants.ART_LOC + "team_icon_2.png", "team_icon_2.png");
            images[Constants.IMG_TEAM_ICON_3] = loadImageSafely(artLoader, Constants.ART_LOC + "team_icon_3.png", "team_icon_3.png");
            images[Constants.IMG_TEAM_ICON_4] = loadImageSafely(artLoader, Constants.ART_LOC + "team_icon_4.png", "team_icon_4.png");

  /*
            images[Constants.IMG_END_GAME_VICTORY] = loadImageSafely(artLoader, Constants.ART_LOC + "endGameScreenVictory.jpg", "endGameScreenVictory.jpg");
            images[Constants.IMG_END_GAME_DEFEAT] = loadImageSafely(artLoader, Constants.ART_LOC + "endGameScreenDefeat.jpg", "endGameScreenDefeat.jpg");
  */

            // All done
            //System.out.println("Images loaded.");

        } catch (Exception e) {
            Logger.error("load() exception: " + e);
            Logger.error("Stack trace: ", e);
        }
        artLoaded = true;
        Logger.info("GameMedia.load() completed. artLoaded=" + artLoaded);
    }


    /////////////////////////////////////////////////////////////////
    // Get the progress
    /////////////////////////////////////////////////////////////////
    public String getProgress() {
  /*float max = Constants.SOUND_COUNT*10;
  max+=Constants.IMG_COUNT*2;
  float sofar;
  
  
  if (!soundLoaded)
  { sofar = 0;
   int count = 0;
                        while(count < Constants.SOUND_COUNT && sounds[count] != null)
                                count++;
   sofar+=count*10;
   //return "Loading sounds: " + count + "/" + Constants.SOUND_COUNT;

  } else if (!artLoaded)
  { int count = 0;
   sofar = Constants.SOUND_COUNT*10;
   while(count < Constants.IMG_COUNT && images[count] != null)
   { 
     count++;
   }
   sofar+=count;
   
   // tmp
   //return "Loading images: " + count + "/" + Constants.IMG_COUNT;

  } else
  { sofar = Constants.SOUND_COUNT*10;
   sofar+=Constants.IMG_COUNT;
   int count = 0;
   while(count < Constants.IMG_COUNT && rotatedImages[count] != null)
   
    count++;
   sofar+=count;
   
   // tmp
   //return "Processing images: " + count + "/" + Constants.IMG_COUNT;
  }*/

        float max = 0;
        max += Constants.SOUND_COUNT * 10;
        max += Constants.IMG_COUNT;
        float sofar = 0;

        for (int i = 0; i < Constants.SOUND_COUNT; i++) {
            if (sounds[i] != null) sofar += 10;
        }
        for (int i = 0; i < Constants.IMG_COUNT; i++) {
            if (images[i] != null) sofar++;
        }

        float percent = max / sofar;
        percent = 100 / percent;
        int value = (int) percent;
        return "Loading game data: " + value + "%";

    }


    /////////////////////////////////////////////////////////////////
    // Rotate the images
    /////////////////////////////////////////////////////////////////
    public void initialize() {
        int debug = 0;
        try {
            GraphicsConfiguration gc = GraphicsEnvironment.
                    getLocalGraphicsEnvironment()
                    .getDefaultScreenDevice()
                    .getDefaultConfiguration();

            for (int i = 0; i < Constants.IMG_COUNT; i++) {
                debug = i;
                Image image = getImage(i);

                if (image == null) {
                    images[i] = images[0];
                } else {
                    BufferedImage buf = new
                            BufferedImage(image.getWidth(null),
                            image.getHeight(null),
                            BufferedImage.TYPE_INT_ARGB);

                    buf.getGraphics().drawImage(image, 0, 0, null);

                    images[i] = copy(buf);
                    image = getImage(i);

                    //if (image.getCapabilities(gc).isAccelerated())
                    // System.out.println(i + " is");
                    //else
                    // System.out.println(i + " isn't");

    /*if (image.getWidth(null) == Constants.SQUARE_SIZE)
    {
     rotatedImages[i] = rotate(buf);
     if (rotatedImages[i] == null)
     { rotatedImages[i] = images[0];
     }
    } else
    {
     rotatedImages[i] = images[0];
    }*/
                }
            }

        } catch (Exception e) {
            Logger.error("Initialize: " + debug + " " + e);
        }
    }


    private BufferedImage rotate(BufferedImage bi) {
        //System.out.println("rotating");
        int width = bi.getWidth();
        int height = bi.getHeight();

        //BufferedImage biFlip = new BufferedImage(height, width, bi.getType());
        BufferedImage biFlip = new BufferedImage(height, width, BufferedImage.TYPE_INT_ARGB);

        for (int x = 0; x < width; x++)
            for (int y = 0; y < height; y++)
                biFlip.setRGB(height - 1 - y, x, bi.getRGB(x, y));
        return biFlip;
    }

/*
 /////////////////////////////////////////////////////////////////
 // Copy the image
 /////////////////////////////////////////////////////////////////
 private Image copy(BufferedImage bi)
 {
  int width = bi.getWidth();
  int height = bi.getHeight();
  
  BufferedImage biCopy = new BufferedImage(width, height, BufferedImage.TYPE_INT_ARGB);

  for(int x=0; x<width; x++)
   for(int y=0; y<height; y++)
    biCopy.setRGB(x, y, bi.getRGB(x, y));
  return biCopy;
 }
 */

    //////////////////////////////////////////////////////////////////////
//Get a copy
//////////////////////////////////////////////////////////////////////
    private BufferedImage copy(BufferedImage img) {
        try {
            //Create an RGB buffered image
            BufferedImage bimage = new BufferedImage(img.getWidth(), img.getHeight(), BufferedImage.TYPE_4BYTE_ABGR_PRE);

            //copy it
            Graphics2D g2 = bimage.createGraphics();
            g2.drawImage(img, 0, 0, null);
            g2.dispose();

            for (int x = 0; x < bimage.getWidth(); x++) {
                for (int y = 0; y < bimage.getHeight(); y++) {
                    bimage.setRGB(x, y, img.getRGB(x, y));
                }
            }
            return bimage;
        } catch (Exception e) {
            Logger.error("GameMedia.copy(): " + e);
            return null;
        }
    }


    /////////////////////////////////////////////////////////////////
    // Play music
    /////////////////////////////////////////////////////////////////
    public void playMusic() {
        try {
            if (!Client.musicOff()) music.play();
        } catch (Exception e) {
            Logger.error("GameMedia.playMusic(): " + e);
        }
    }

    public void stopMusic() {
        try {
            if (!Client.musicOff()) music.stop();
        } catch (Exception e) {
            Logger.error("GameMedia.stopMusic(): " + e);
        }
    }

    public void pauseMusic() {
        try {
            music.pause();
        } catch (Exception e) {
            Logger.error("GameMedia.pauseMusic(): " + e);
        }
    }

    public void resumeMusic() {
        try {
            music.resume();
        } catch (Exception e) {
            Logger.error("GameMedia.resumeMusic(): " + e);
        }
    }

    public void setMusicVol(int vol) {
        try {
            music.setVolume(vol);
        } catch (Exception e) {
            Logger.error("GameMedia.setMusicVol(): " + e);
        }
    }

    public void clean() {
        try {
            for (int i = 0; i < images.length; i++) {
                if (images[i] != null) images[i].flush();
            }
            for (int i = 0; i < rotatedImages.length; i++) {
                if (rotatedImages[i] != null) rotatedImages[i].flush();
            }

            if (music != null) {
                music.close();
            }
        } catch (Exception e) {
            Logger.error("GameMedia.clean(): " + e);
        }
    }

    /////////////////////////////////////////////////////////////////
    // Play a sound
    /////////////////////////////////////////////////////////////////
    public void playSound(short sound) {
        if (!Client.mute() && sounds[sound] != null)
            sounds[sound].play();
    }

    public Sound getSound(short index) {
        return sounds[index];
    }


    /////////////////////////////////////////////////////////////////
    // Create a placeholder image
    /////////////////////////////////////////////////////////////////
    private synchronized Image createPlaceholderImage() {
        if (placeholderImage == null) {
            try {
                BufferedImage placeholder = new BufferedImage(100, 100, BufferedImage.TYPE_INT_ARGB);
                Graphics2D g2d = placeholder.createGraphics();
                g2d.setColor(Color.GRAY);
                g2d.fillRect(0, 0, 100, 100);
                g2d.setColor(Color.DARK_GRAY);
                g2d.drawRect(0, 0, 99, 99);
                g2d.dispose();
                placeholderImage = placeholder;
            } catch (Exception e) {
                Logger.error("Failed to create placeholder image: " + e);
                // Return a minimal valid image
                placeholderImage = new BufferedImage(1, 1, BufferedImage.TYPE_INT_ARGB);
            }
        }
        return placeholderImage;
    }

    /////////////////////////////////////////////////////////////////
    // Get a particular image, also checks for gray images
    /////////////////////////////////////////////////////////////////
    public Image getImage(int i) { //System.out.println(
        // GraphicsEnvironment
        // .getLocalGraphicsEnvironment()
        // .getDefaultScreenDevice()
        // .getAvailableAcceleratedMemory() + " mem");

  /*if (images[i] == null) // This means it is a gray image not yet loaded
  {
   if (images[i - 2] == null) return null;  // Checks if spot is supposed to be null
   BufferedImage new_image = generateShadow(i - 2);
   images[i] = copy(new_image);
  }*/
        Image img = images[i];
        // Return a placeholder image if null to prevent crashes
        if (img == null) {
            // Try to use first image as placeholder if available
            if (images[0] != null) {
                return images[0]; // Use first image as placeholder
            }
            // Create a simple placeholder if no images are loaded yet
            Image placeholder = createPlaceholderImage();
            // Double-check placeholder is not null
            if (placeholder == null) {
                // Last resort: create a minimal image
                placeholder = new BufferedImage(1, 1, BufferedImage.TYPE_INT_ARGB);
            }
            return placeholder;
        }
        return img;
    }

    private BufferedImage generateShadow(int image) {
        // Get non-RGB image
        Image img = images[image];
        if (img == null) {
            // Fallback to first image if available
            img = images[0];
            if (img == null) {
                // Create a dummy image if nothing is loaded
                return new BufferedImage(Constants.SQUARE_SIZE, Constants.SQUARE_SIZE, BufferedImage.TYPE_INT_ARGB);
            }
        }

        // Create an RGB buffered image
        BufferedImage bimage = new BufferedImage(img.getWidth(null), img.getHeight(null), BufferedImage.TYPE_INT_ARGB);

        // copy it
        Graphics2D g2 = bimage.createGraphics();
        g2.drawImage(img, 0, 0, null);
        g2.dispose();

        // color magic
        for (int x = 0; x < bimage.getWidth(); x++) {
            for (int y = 0; y < bimage.getHeight(); y++) {
                int pixel = bimage.getRGB(x, y);
                int a = (pixel >> 24) & 0xff;
                int r = (pixel >> 16) & 0xff;
                int g = (pixel >> 8) & 0xff;
                int b = (pixel >> 0) & 0xff;
                int greyConstant = (int) (((double) r * .299 + (double) g * .587 + (double) b * .114) * .8);
                r = greyConstant;
                g = greyConstant;
                b = greyConstant;
                int newPixel =
                        ((a & 0xFF) << 24) |
                                ((r & 0xFF) << 16) |
                                ((g & 0xFF) << 8) |
                                ((b & 0xFF) << 0);
                bimage.setRGB(x, y, newPixel);
            }
        }
        return bimage;
    }

    public Image getGrayedImage(int image, boolean friendly) {
        if (!friendly)
            ++image;
        if (grayedImages[image] == null) {
            BufferedImage new_image = generateShadow(image);
            grayedImages[image] = copy(new_image);
        }
        return grayedImages[image];
    }

    public Image getTeamIcon(int team) {
        short selectedImage = Constants.IMG_TEAM_ICON_1;
        switch (team) {
            case 2:
                selectedImage = Constants.IMG_TEAM_ICON_2;
                break;
            case 3:
                selectedImage = Constants.IMG_TEAM_ICON_3;
                break;
            case 4:
                selectedImage = Constants.IMG_TEAM_ICON_4;
                break;
        }

        Image icon = getImage(selectedImage);
        //icon = icon.getScaledInstance(17, 17, Image.SCALE_SMOOTH);
        /*
        BufferedImage baseImage = (BufferedImage) image;
        Graphics2D g2d = baseImage.createGraphics();

        int x = baseImage.getWidth() - icon.getWidth(null);
        int y = baseImage.getHeight() - icon.getHeight(null);
        g2d.drawImage(icon, x, y, null);
        g2d.dispose();*/

        return icon;
    }

    /////////////////////////////////////////////////////////////////
    // Get a prerotated image
    /////////////////////////////////////////////////////////////////
    public Image getRotatedImage(int image, boolean friendly) {
        if (rotatedImages[image] == null) {
            Image img = null;
            if (friendly) img = getGrayedImage(image, true);
            else img = getImage(image);
            if (img == null) {
                rotatedImages[image] = images[0];
                return rotatedImages[image];
            }
            if (img.getWidth(null) == Constants.SQUARE_SIZE) {
                BufferedImage buf = new
                        BufferedImage(img.getWidth(null),
                        img.getHeight(null),
                        BufferedImage.TYPE_INT_ARGB);
                buf.getGraphics().drawImage(img, 0, 0, null);
                rotatedImages[image] = rotate(buf);
                if (rotatedImages[image] == null) {
                    Logger.warn("rotate(buf) returned null.");
                    rotatedImages[image] = images[0];
                }
            } else {
                Logger.warn("getWidth (which is: " + img.getWidth(null) + ") != square size.");
                rotatedImages[image] = images[0];
            }
        }
        return rotatedImages[image];
    }

    public int getSoundCount() {
        return soundCount;
    }

    public void soundStarted() {
        ++soundCount;
    }

    public void soundFinished() {
        --soundCount;
    }

    public boolean belowMaxSounds() {
        return soundCount < MAX_SOUND_COUNT;
    }
}
