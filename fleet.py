#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tempfile
import json
import os
import paramiko
import datetime
from subprocess import run
from randomemoji import random_emoji

class MatchException(Exception):
    def __init__(self, expected, found):
        self.expected = expected
        self.found = found

    def __str__(self):
        if self.found is not None:
            return f'Expected \'{self.expected}\', found \'{self.found}\'.'
        return 'Unexpected EOF.'

class Parser:
    def __init__(self, reader):
        self.reader = reader
        reader.seek(0,2)
        self.eof_pos = reader.tell()
        reader.seek(0,0)

    def pos(self):
        return self.reader.tell()

    def eof(self):
        return self.pos() == self.eof_pos

    def next(self):
        if self.eof():
            return None
        return self.reader.read(1)
    
    def peek(self):
        if self.eof():
            return None
        rewind = self.reader.tell()
        char = self.next()
        self.reader.seek(rewind)
        return char
    
    def match(self, char):
        found = self.next()
        if found != char:
            raise MatchException(char, found)

    def try_match(self, char):
        if self.peek() == char:
            self.next()

    def match_while(self, condition):
        consumed = []
        while not self.eof() and condition(self.peek()):
            consumed.append(self.next())
        return consumed

def get_input_from_editor(initial_msg, editor_exe):
    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tf:
        tf.write(initial_msg.encode('utf-8'))
        tf.flush()
        run([editor_exe, tf.name])

    with open(tf.name, 'r') as tf:
        edited_msg = tf.read()
    
    os.remove(tf.name)
    
    return edited_msg


def write_journal(tweet):
    basepath = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(basepath, 'secrets.json'), 'r') as secrets_file:
        secrets = json.load(secrets_file)
    flounder = secrets['flounder']

    with paramiko.Transport(('flounder.online', 2024)) as transport:
        transport.connect(
                username=flounder['user'], password=flounder['password'])
        with paramiko.SFTPClient.from_transport(transport) as sftp:
            with sftp.file('journal.gmi', 'r') as journal_file:
                parser = Parser(journal_file)

                # Ignore initial whitespace
                parser.match_while(lambda c: c.decode('UTF-8').isspace())

                # Today's date is used for multiple things below
                today = datetime.date.today()
                
                # If already at EOF we can insert the post at top with header;
                # it's the first post.
                if parser.eof():
                    situation = 'first post'
                else:
                    try:
                        # Expect to find a '#'
                        parser.match(b'#')

                        # Ignore following whitespace 
                        parser.match_while(
                                lambda c: c.decode('UTF-8').isspace())
                        
                        # Expect day/month/year separated by '-'
                        year = ''.join(x.decode('UTF-8') for x in
                                parser.match_while(
                                    lambda c: c.decode('UTF-8').isnumeric()))
                        parser.match(b'-')
                        month = ''.join(x.decode('UTF-8') for x in
                                parser.match_while(
                                    lambda c: c.decode('UTF-8').isnumeric()))
                        parser.match(b'-')
                        day = ''.join(x.decode('UTF-8') for x in 
                                parser.match_while(
                                    lambda c: c.decode('UTF-8').isnumeric()))

                        # Match against current date
                        if (int(year) == today.year
                                and int(month) == today.month
                                and int(day) == today.day):
                            situation = 'same day'
                        else:
                            situation = 'new day'
                    except MatchException:
                        # If we fail to match anything we're probably dealing
                        # with inconsistent formatting/hand-input content, and
                        # default to behaving as though it is a first post.
                        # This should also fix future posts.
                        situation = 'first post'

                del parser

                # Do the actual insertion.
                # For this we need to read the file into memory, modify it, and
                # write a new file.
                
                # Save the contents of the file
                journal_file.seek(0)
                contents = journal_file.readlines()

            # Now we modify the file "offline"
            # Where to do this depends on the situation.

            def get_header():
                return f'# {today.year}-{today.month}-{today.day}'

            def get_separator():
                return f'> ~ {random_emoji()} ~'

            if situation in ('first post', 'new day'): 
                #               Just insert at top, with header.
                contents[0:0] = [get_header(), '\n\n', tweet, '\n\n']
            elif situation == 'same day':
                #               Insert before last post
                # Account for leading newlines
                index = 0
                while not contents[index]:
                    index += 1
                index += 1
                contents[index:index] = [
                        '\n', tweet, '\n\n', get_separator(), '\n']
            else:
                raise Exception(f'Unhandled situation \'{situation}\'.')

            # Now we need to reopen the file in write mode to re-write the
            # contents. Because this will truncate the file (which will erase
            # everything if the operation fails), we will save a backup first.
            with open(f'{basepath}/.journal.bak', 'w') as backup:
                for line in contents:
                    backup.write(line)

            with sftp.file('journal.gmi', 'w') as journal_file:
                for line in contents:
                    journal_file.write(line.encode('UTF-8'))

    # Fun statistics for the user to look at
    print(f'Wrote {len(tweet)} chars to flounder.')
    print(f'Open https://{flounder["user"]}.flounder.online/journal.gmi to see'
            ' your post.')


def write_gemlog(tweet, editor):
    basepath = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(basepath, 'secrets.json'), 'r') as secrets_file:
        secrets = json.load(secrets_file)
    flounder = secrets['flounder']

    with paramiko.Transport(('flounder.online', 2024)) as transport:
        transport.connect(
                username=flounder['user'], password=flounder['password'])
        with paramiko.SFTPClient.from_transport(transport) as sftp:
            # 👇 Post edition loop; broken out of if post & details are valid
            while True:
                # 👇 Title prompt loop; broken out of if title is valid
                while True:
                    # Prompt for, and canonicalize, title of new gemlog entry
                    title = input('Gemlog title: ').strip()
                    today = datetime.date.today()
                    canonic_title = (
                            f'{today.year}-{today.month:02d}-{today.day:02d}'
                            f'{title.replace(" ", "-")}')
                    filename = f'gemlog/{canonic_title}.gmi'

                    # Check that title does not already exist.
                    try:
                        sftp.stat(filename)
                        # File exists, because exception was not raised
                        print('A file of that title already exists!')
                        continue
                    except IOError:
                        # File does not exist
                        break
                
                # Confirmation
                print('')
                print('Please confirm the post details below.')
                print('Title: ', title)
                print('Date: ',
                        f'{today.year}-{today.month:02d}-{today.day:02d}')
                print('Post:\n')
                print(tweet)
                print('')

                answer = input('Does this look ok? [y/N] ').strip().lower()

                if answer in ('y', 'yes'):
                    break

                # Go through tweet edition again;
                # We restart the editor but with the existing text
                tweet = get_input_from_editor(tweet, editor)

                continue # to title prompt and confirmation
            
            # Title and tweet are confirmed. Write new file to sshftp
            with sftp.open(filename, 'w') as outfile:
                outfile.write(f'# {title}\n\n')
                outfile.write(tweet)
                outfile.write('\n\n=> //miguelmurca.flounder.online 🔙')

    # Fun statistics for the user to look at
    print(f'Wrote {len(tweet)} chars to flounder.')
    print(f'Open https://{flounder["user"]}.flounder.online/{filename} to see'
            ' your post.')


if __name__ == "__main__":
    editor = os.environ.get('VISUAL', '/usr/bin/vim')
    default = 'Write tweet here. Leave empty or quit without saving to abort.'
    tweet = get_input_from_editor(default, editor)

    if tweet == default:
        print('Aborted.')
        exit(0)

    tweet = tweet.strip()
    if not tweet:
        print('Aborted.')
        exit(0)

    to_journal = True
    if len(tweet) > 280:
        print('Your post is longer than 280 characters.')
        answer = (input('Do you wish to write a gemlog instead? [y/N] ')
                    .strip().lower())
        if answer in ('y', 'yes'):
            to_journal = False

    if to_journal:
        write_journal(tweet)
    else:
        write_gemlog(tweet, editor)
