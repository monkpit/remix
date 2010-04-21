"""
Convenience methods for creating Remix audio objects by searching.
Created 2010-04-12 by Jason Sundram

See the docs here for how to use the api directly:
http://beta.developer.echonest.com/song.html#search
"""
import os
import simplejson
import sys
import urllib
from urllib2 import quote, urlparse

try:
    from beta_pyechonest import song
except:
    sys.exit("""
                You need to have v4 pyechonest (BETA) installed for cloud.py to work!
                Get it here (make sure you get the beta):
                    http://code.google.com/p/pyechonest/
            """)

from cloud_support import AnalyzedAudioFile


def find_track(artist, title):
    """
        Given an artist and title, uses v4 pyechonest to get a song object,
        download the track and audio analysis for that song, and return an 
        AudioData-type thing.
    """
    songs = song.search(artist=artist, title=title, results=1, buckets=['id:paulify'], limit=True)
    if songs:
        return make_track(songs[0])
    return None

def make_track(s):
    """
        Takes a song object, created by manipulating v4 pyechonest.
        Downloads the audio for the song, as well as the full analysis.
        Synthesizes those into the return value, a remix AudioData object.
        
        returns None if either the audio or the analysis could not be found.
    """
    tracks = s.get_tracks(catalog='paulify', limit=True)
    t = None
    if tracks:
        track = tracks[0]
        
        filename = download(track.audio_url)
        if not os.path.exists(filename + '.json'):
            json = download(track.analysis_url)
            os.rename(json, filename + '.json')
        
        t = AnalyzedAudioFile(filename)
        if t:
            # fill in some things that are missing.
            t.analysis.name = s.title
            t.analysis.identifier = track.id
            t.analysis.metadata['artist'] = s.artist_name
            t.analysis.metadata['id'] = track.id
            t.analysis.metadata['title'] = s.title
            t.analysis.metadata['samplerate'] = t.sampleRate
    return t


def download(url):
    """Copy the contents of a file from a given URL to a local file in the current directory and returns the filename"""
    
    filename = url.split('/')[-1]
    def fix_url(url):
        """urllib requires a properly url-encoded path."""
        parsed = urlparse.urlparse(url)
        parts = [parsed.scheme, '://', parsed.netloc, quote(parsed.path)] 
        if parsed.query:
            parts.extend(['?', parsed.query])
        return ''.join(parts)
    
    if not os.path.exists(filename):
        urllib.urlretrieve(fix_url(url), filename)
    return filename

