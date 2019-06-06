import sys
import time

import pygame

from live_chords import get_current_song, file, version


def setup_screen():
    pygame.init()
    pygame.font.init()

    pygame.init()
    pygame.font.init()
    active_font = pygame.font.SysFont('lucida console', 30)
    active_font_colour = (180, 180, 180)
    inactive_font = pygame.font.SysFont('monospace', 25)
    inactive_font_colour = (150, 150, 150)
    artist_font = pygame.font.SysFont('monospace', 20)
    artist_font_color = (90, 90, 90)

    screen_size = screen_width, screen_height = 1580, 920
    black = (0, 0, 0)
    active_line_colour = (50, 50, 50)
    inactive_line_colour = (30, 30, 30)

    screen = pygame.display.set_mode(screen_size)
    colors = {'active_line': active_line_colour, 'inactive_line': inactive_line_colour, 'artist': artist_font_color,
              'active_font': active_font_colour, 'inactive_font': inactive_font_colour}

    fonts = {'active': active_font, 'inactive': inactive_font, 'artist': artist_font}

    clock = pygame.time.Clock()
    return fonts, colors, screen, clock


def draw_background(screen, fonts, colors, artist, title, synced, azlyrics, tabs, syncing=False):
    size = screen.get_size()
    screen.fill(colors['inactive_line'])
    screenheight = int(round(size[1] / 6))
    rect = pygame.Rect(0, int(screenheight * 2.5), size[0], screenheight)
    pygame.draw.rect(screen, colors['active_line'], rect)

    title_string = "Title: " + title.replace("%20", " ")
    artist_string = "by: " + artist.replace("%20", " ")
    azlyrics_string = "azlyrics found = " + str(azlyrics)
    tabs_stirng = "tabs found = " + str(tabs)
    title_info = fonts['artist'].render(title_string, False, colors['artist'])
    artist_info = fonts['artist'].render(artist_string, False, colors['artist'])
    azlyrics_info = fonts['artist'].render(azlyrics_string, False, colors['artist'])
    tabs_info = fonts['artist'].render(tabs_stirng, False, colors['artist'])
    # screen.blit(title_info,(10,10))
    # screen.blit(artist_info,(10,40))
    # screen.blit(azlyrics_info,(10,70,))
    # screen.blit(tabs_info,(10,100))
    infostring = "{} {} {} {}".format(title_string, artist_string, azlyrics_string, tabs_stirng)
    info_draw = fonts['artist'].render(infostring, False, colors['artist'])
    screen.blit(info_draw, (10, 10))

    if synced:
        synced_string = "song is synced"
        synced_info = fonts['artist'].render(synced_string, False, colors['artist'])
        screen.blit(synced_info, (size[0] - 400, 10))
    elif syncing:
        string = "syncing, press space for next line"
        synced_info = fonts['artist'].render(string, False, colors['artist'])
        screen.blit(synced_info, (size[0] - 400, 10))
    else:
        synced_string = "song is not synced"
        synced_info = fonts['artist'].render(synced_string, False, (180, 180, 180))
        screen.blit(synced_info, (size[0] - 400, 10))
        string = "Press space to start syncing"
        synced_info = fonts['artist'].render(string, False, (180, 180, 180))
        screen.blit(synced_info, (size[0] - 400, 35))
        string = "Song will restart"
        synced_info = fonts['artist'].render(string, False, (180, 180, 180))
        screen.blit(synced_info, (size[0] - 400, 60))
        string = "than press space to go to next line"
        synced_info = fonts['artist'].render(string, False, (180, 180, 180))
        screen.blit(synced_info, (size[0] - 400, 85))
        string = "when song is done, syncing is done"
        synced_info = fonts['artist'].render(string, False, (180, 180, 180))
        screen.blit(synced_info, (size[0] - 400, 110))
        string = "make sure to press space at start of song"
        synced_info = fonts['artist'].render(string, False, (180, 180, 180))
        screen.blit(synced_info, (size[0] - 400, 160))

    return screen


def draw_lyrics(screen, fonts, colors, chorded_lyrics, active_line):
    if len(chorded_lyrics) >= 1:
        size = screen.get_size()
        height = int(round(size[1] / 6)) #height of one line
        left_offset = 100
        if active_line > 1:
            chords_info = fonts['inactive'].render(chorded_lyrics[active_line - 2]['chords'], False,
                                                   colors['inactive_font'])
            screen.blit(chords_info, (left_offset, height * 0.5))
            lyrics_info = fonts['inactive'].render(chorded_lyrics[active_line - 2]['lyrics'], False,
                                                   colors['inactive_font'])
            screen.blit(lyrics_info, (left_offset, height * 0.8))
        if active_line > 0:
            chords_info = fonts['inactive'].render(chorded_lyrics[active_line - 1]['chords'], False,
                                                   colors['inactive_font'])
            screen.blit(chords_info, (left_offset, height * 1.5))
            lyrics_info = fonts['inactive'].render(chorded_lyrics[active_line - 1]['lyrics'], False,
                                                   colors['inactive_font'])
            screen.blit(lyrics_info, (left_offset, height * 1.8))
        if active_line < len(chorded_lyrics) - 1:
            chords_info = fonts['inactive'].render(chorded_lyrics[active_line + 1]['chords'], False,
                                                   colors['inactive_font'])
            screen.blit(chords_info, (left_offset, height * 3.5))
            lyrics_info = fonts['inactive'].render(chorded_lyrics[active_line + 1]['lyrics'], False,
                                                   colors['inactive_font'])
            screen.blit(lyrics_info, (left_offset, height * 3.8))
        if active_line < len(chorded_lyrics) - 2:
            chords_info = fonts['inactive'].render(chorded_lyrics[active_line + 2]['chords'], False,
                                                   colors['inactive_font'])
            screen.blit(chords_info, (left_offset, height * 4.5))
            lyrics_info = fonts['inactive'].render(chorded_lyrics[active_line + 2]['lyrics'], False,
                                                   colors['inactive_font'])
            screen.blit(lyrics_info, (left_offset, height * 4.8))
        chords_info = fonts['active'].render(chorded_lyrics[active_line]['chords'], False, colors['active_font'])
        screen.blit(chords_info, (left_offset, height * 2.5))
        lyrics_info = fonts['active'].render(chorded_lyrics[active_line]['lyrics'], False, colors['active_font'])
        screen.blit(lyrics_info, (left_offset, height * 2.8))
    return screen


def sync_song(screen, fonts, colors, chorded_lyrics, active_line, artist, title, synced, clock, t0, azlyrics, tabs):
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
    datafile = file(artist.replace(" ", "%20"), title.replace(" ", "%20"), version)
    datafile.open_file()
    datafile.from_dict()
    datafile.chorded_lyrics = chorded_lyrics
    datafile.synced = synced
    datafile.to_dict()
    datafile.close_file()

    return chorded_lyrics, synced


def main():
    username = 'rickwinters12'
    scope = 'user-read-currently-playing user-modify-playback-state'

    clientid = 'cb3d87487c3f45678e4f28c0f1787d59'
    clientsecret = '720cb763c5114ce581303e30846d962d'
    redirect_uri = 'http://google.com/'

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
    t = 0
    t0 = 0

    while True:
        if count == 0:  # if count is zero. That means that the script will look for which song is playing
            title, artist, t0 = get_current_song(username, clientid, clientsecret, redirect_uri)
            artist = artist.replace(" ", "%20")
            title = title.replace(" ", "%20")
            t1 = time.time()

        if (artist != artist_old) or (title != title_old):  # if song has changed open the file
            datafile = file(artist, title, version)
            datafile.open_file()  # opens file, and if it doesn't exist the lyrics will be downloaded, analyzed etc
            datafile.close_file()  # if it's a new file the file is saved
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
                    print("time = " + str(round((t + t0) / 60) - 1) + ":" + str(round((t + t0) % 60, 2)))
                    screen = draw_background(screen, fonts, colors, artist, title, synced, has_azlyrics, has_tabs)
                    screen = draw_lyrics(screen, fonts, colors, chorded_lyrics, active_line)
                    pygame.display.update()
                clock.tick(100)  # loop every ms
            else:
                time.sleep(
                    sleeptime)  # do nothing and loop while counting to 5 sec. however don't sleep 5 sec so the screen is updated
                count += 1
                if count == recheck_amount:
                    count = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not synced:
                    print("start syncing")
                    title, artist, t0 = get_current_song(username, clientid, clientsecret, redirect_uri)
                    chorded_lyrics, synced = sync_song(screen, fonts, colors, chorded_lyrics, active_line, artist,
                                                       title, synced, clock, t0, has_azlyrics, has_tabs)
                if event.key == pygame.K_SPACE and synced:
                    count = 0


if __name__ == "__main__":
    main()
