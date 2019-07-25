import json
import sys
import time

import pygame

from live_chords import get_current_song, file, version, select_account


def setup_screen():
    pygame.init()
    pygame.font.init()

    pygame.init()
    pygame.font.init()
    active_font = pygame.font.SysFont('lucida console', 35)
    active_font_colour = (180, 180, 180)
    inactive_font = pygame.font.SysFont('lucida console', 25)
    inactive_font_colour = (150, 150, 150)
    artist_font = pygame.font.SysFont('monospace', 20)
    artist_font_color = (90, 90, 90)

    screen_size = screen_width, screen_height = 1580, 920
    black = (0, 0, 0)
    active_line_colour = (50, 50, 50)
    inactive_line_colour = (30, 30, 30)

    screen = pygame.display.set_mode(screen_size, pygame.RESIZABLE)
    colors = {'active_line': active_line_colour, 'inactive_line': inactive_line_colour, 'artist': artist_font_color,
              'active_font': active_font_colour, 'inactive_font': inactive_font_colour}

    fonts = {'active': active_font, 'inactive': inactive_font, 'artist': artist_font}

    clock = pygame.time.Clock()
    return fonts, colors, screen, clock


def draw_background(screen, fonts, colors, artist, title, synced, azlyrics, tabs, syncing=False):
    size = screen.get_size()
    screen.fill(colors['inactive_line'])
    screenheight = int(round(size[1] / 6))

    title_string = "Title: " + title.replace("%20", " ")
    artist_string = "Artist: " + artist.replace("%20", " ")
    azlyrics_string = "lyrics found = " + str(azlyrics)
    tabs_stirng = "tabs found = " + str(tabs)
    string = title_string + "\n" + artist_string

    pos = (10,10)
    for line in string.splitlines():
        pos = blit_text(screen, line, pos, fonts['artist'], colors['inactive_font'])

    string = azlyrics_string + "\n" + tabs_stirng
    pos = (size[0] - 400, 10)
    print(pos)
    for line in string.splitlines():
        pos = blit_text(screen, line, pos, fonts['artist'], colors['artist'])

    if synced:
        synced_string = "song is synced. To re-sync the song from current position, press space once"
        pos = blit_text(screen, synced_string, pos, fonts['artist'], colors['inactive_font'])
        synced_string = "press n if next song is playing"
        pos = blit_text(screen, synced_string, pos, fonts['artist'], colors['inactive_font'])
    elif syncing:
        string = "syncing, press space for next line"
        blit_text(screen, string, pos, fonts['artist'], colors['inactive_font'])
    else:
        string = "Restart song before syncing. Than press space to enter syncing mode and press space to go te next "\
                 "line. The time of pressing space is save when all lines are completed"
        blit_text(screen, string, pos, fonts['artist'], colors['inactive_font'])
    return screen

def blit_text(surface, text, pos, font, color=pygame.Color('black')):
    words = text.split(" ")  # 2D array where each row is a list of words.
    space = font.size(' ')[0]  # The width of a space.
    max_width, max_height = surface.get_size()
    x, y = pos
    for word in words:
        word_surface = font.render(word, 0, color)
        word_width, word_height = word_surface.get_size()
        if x + word_width >= max_width:
            x = pos[0]  # Reset the x.
            y += word_height  # Start on new row.
        surface.blit(word_surface, (x, y))
        x += word_width + space
    x = pos[0]  # Reset the x.
    y += word_height  # Start on new row.

    return x, y

def draw_lyrics(screen, fonts, colors, chorded_lyrics, active_line):
    if len(chorded_lyrics) >= 1:
        drawing_line = active_line-4
        if drawing_line < 0:
            drawing_line = 0
        size = screen.get_size()
        height = int(round(size[1] / 6)) #height of one line
        left_offset = 100
        x = 50
        y = 70
        startY = 0
        stopY = 0
        while y < size[1] and drawing_line < len(chorded_lyrics):
            if drawing_line == active_line:
                current_font = fonts['active']
                current_color = colors['active_font']
                startY = y
            else:
                current_font = fonts['inactive']
                current_color = colors['inactive_font']

            if chorded_lyrics[drawing_line]['group'] in ["start","intro","solo"]:
                lines = chorded_lyrics[drawing_line]['lyrics']
            else:
                lyrics = chorded_lyrics[drawing_line]['lyrics']
                chords = chorded_lyrics[drawing_line]['chords']
                lines = chords + "\n" + lyrics + "\n\n"

            for line in lines.splitlines():
                x, y = blit_text(screen, line, (x, y), current_font, current_color)
                if drawing_line == active_line:
                    stopY = y
                    rect = pygame.Rect(0, startY, size[0], stopY)
                    # pygame.draw.rect(screen, colors['active_line'], rect)
                    # x, y = blit_text(screen, line, (x, y), current_font, current_color)
            drawing_line += 1

    return screen


def sync_song(screen, fonts, colors, chorded_lyrics, active_line, artist, title, synced, clock, t0, azlyrics, tabs, server):
    autosync = False
    print("t0 = " + str(t0))
    if autosync:
        t = 0
        for line in chorded_lyrics:
            line['start'] = t
            line['stop'] = t + 5
            t += 5
            pygame.display.update()
    else:
        t_1 = time.time()
        syncing = True
        while syncing:
            t = time.time() - t_1 + t0
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        active_line += 1
                        if active_line == len(chorded_lyrics):
                            syncing = False
                        else:
                            draw_background(screen, fonts, colors, artist, title, synced, azlyrics, tabs, True)
                            draw_lyrics(screen, fonts, colors, chorded_lyrics, active_line)
                            chorded_lyrics[active_line - 1]['stop'] = t
                            chorded_lyrics[active_line]['start'] = t
                            print("start = " + str(chorded_lyrics[active_line - 1]['start']) + " stop = " + str(
                                chorded_lyrics[active_line - 1]['stop']) + " text = " + chorded_lyrics[active_line - 1][
                                      'lyrics'])
                            pygame.display.update()
                if event.type == pygame.QUIT:
                    pygame.quit();
                    sys.exit()
            clock.tick(100)
    synced = True
    datafile = file(artist.replace(" ", "%20"), title.replace(" ", "%20"), version, server)
    datafile.open_file()
    datafile.from_dict()
    datafile.chorded_lyrics = chorded_lyrics
    datafile.synced = synced
    datafile.to_dict()
    datafile.close_file()

    return chorded_lyrics, synced


def main():
    username = select_account()
    scope = 'user-read-currently-playing user-modify-playback-state'
    clientid = 'cb3d87487c3f45678e4f28c0f1787d59'
    clientsecret = '720cb763c5114ce581303e30846d962d'
    redirect_uri = 'http://google.com/'


    print("Choose which kind of server connection you want")
    print("1: Localhost")
    print("2: Remote server")
    print("3: No server conncetion")
    serverinput = input("-->: ")
    server = "http://localhost:8081/live_chords/"

    if serverinput == "2":
        server = "http://82.75.204.165:8081/live_chords/"
    elif serverinput == "3":
        server = "no_server"

    fonts, colors, screen, clock = setup_screen()
    artist = ""
    artist_old = ""
    title = ""
    title_old = ""
    recheck_sec = 5
    sleeptime = 1 / 60
    recheck_amount = recheck_sec / sleeptime
    count = 0
    active_line = 0
    t0 = 0
    synced = False
    syncing = False
    chorded_lyrics = {}
    has_azlyrics = False
    has_tabs = False



    while True:
        if count == 0:  # if count is zero. That means that the script will look for which song is playing
            title, artist, t0 = get_current_song(username, clientid, clientsecret, redirect_uri)
            artist = artist.replace(" ", "%20")
            title = title.replace(" ", "%20")
            t1 = time.time()

        if (artist != artist_old) or (title != title_old):  # if song has changed open the file
            datafile = file(artist, title, version, server)
            datafile.open_file()  # opens file, and if it doesn't exist the lyrics will be downloaded, analyzed etc
            # datafile.close_file()  # if it's a new file the file is saved
            artist_old = artist  # keeping track of song
            title_old = title
            active_line = 0

            tabs = datafile.tabs
            synced = datafile.synced
            has_tabs = datafile.has_tabs
            has_azlyrics = datafile.has_azlyrics
            chorded_lyrics = datafile.chorded_lyrics
            if synced:  # if synced, find the current time of the song (because only every 5 seconds a new song is checked, it might be the case that as soon as a synced song is loaded spotify is already 3 seconds in.
                active_line = 0  # find the current active line. It could be that the song is already in the middle, this will be picked up when the song is synced
                for line in chorded_lyrics:  # compare each line's stop and starttime with t0
                    stoptime = line['stop']
                    starttime = line['start']
                    if starttime <= t0 <= stoptime:
                        break
                    active_line += 1
                if active_line == len(chorded_lyrics):
                    active_line = len(chorded_lyrics) - 1
            screen = draw_background(screen, fonts, colors, artist, title, synced, has_azlyrics, has_tabs)
            screen = draw_lyrics(screen, fonts, colors, chorded_lyrics, active_line)
            pygame.display.update()
        else:
            if synced:
                count = 1  # while the song is running, do not look for a new song.
                t = time.time() - t1 + t0
                if t > chorded_lyrics[active_line]['stop']:  # check if we need to go to a new line
                    active_line += 1
                    if active_line == len(chorded_lyrics):
                        count = 0
                        active_line = len(chorded_lyrics) - 1
                        time.sleep(2)
                    print("active_line = " + str(active_line))
                    print("time = " + str(round(t / 60)) + ":" + str(round(t % 60, 2)))
                    screen = draw_background(screen, fonts, colors, artist, title, synced, has_azlyrics, has_tabs)
                    screen = draw_lyrics(screen, fonts, colors, chorded_lyrics, active_line)
                    pygame.display.update()
                clock.tick(100)  # loop every ms
            else:
                time.sleep(sleeptime)  # do nothing and loop while counting to 5 sec. however don't sleep 5 sec so the screen is updated
                count += 1
                if count >= recheck_amount:
                    count = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                # SYNC THE SONG WHEN NOT SYNCED, THIS SHOULD START AT START OF SONG
                if event.key == pygame.K_SPACE and not synced:
                    syncing = True
                    print("start syncing")
                    title, artist, t0 = get_current_song(username, clientid, clientsecret, redirect_uri)
                    chorded_lyrics, synced = sync_song(screen, fonts, colors, chorded_lyrics, active_line, artist,
                                                       title, synced, clock, t0, has_azlyrics, has_tabs, server)
                    #datafile.close_file()
                elif event.key == pygame.K_SPACE:
                    synced = False
                    print("Start resyncing")
                    title, artist, t0 = get_current_song(username, clientid, clientsecret, redirect_uri)
                    t = time.time() - t1 + t0
                    chorded_lyrics, synced = sync_song(screen, fonts, colors, chorded_lyrics, active_line, artist,
                                                       title, synced, clock, t0, has_azlyrics, has_tabs, server)
                if (event.key == pygame.K_n or event.key == pygame.K_b) and synced:
                    count = 0
            if event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                print("SCREENRESIZE = " + str(screen.get_size()))
                screen = draw_background(screen, fonts, colors, artist, title, synced, has_azlyrics, has_tabs)
                screen = draw_lyrics(screen, fonts, colors, chorded_lyrics, active_line)
                pygame.display.update()

if __name__ == "__main__":
    main()
