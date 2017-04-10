# -*- coding: UTF-8 -*-

# Copyright 2013,2014 Music Technology Group - Universitat Pompeu Fabra
#
# This file is part of Dunya
#
# Dunya is free software: you can redistribute it and/or modify it under the
# terms of the GNU Affero General Public License as published by the Free Software
# Foundation (FSF), either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see http://www.gnu.org/licenses/

from django.http import HttpResponse, Http404, JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.conf import settings
from django.templatetags.static import static

from data import utils
from data.models import SourceName
from carnatic.models import *
from carnatic import search
import json
import docserver
import dashboard.views
import collections
import math
import random
import pysolr

def get_filter_items():
    filter_items = [
        Artist.get_filter_criteria(),
        Concert.get_filter_criteria(),
        Instrument.get_filter_criteria(),
        Raaga.get_filter_criteria(),
        Taala.get_filter_criteria()
    ]
    return filter_items

def searchcomplete(request):
    term = request.GET.get("input")
    ret = []
    if term:
        suggestions = Concert.objects.filter(title__istartswith=term)[:3]
        ret = [{"id": i, "category": "concert", "name": l.title, 'mbid': str(l.mbid)} for i, l in enumerate(suggestions, 1)]
        suggestions = Artist.objects.filter(name__istartswith=term)[:3]
        ret += [{"id": i, "category": "artist", "name": l.name, 'mbid': str(l.mbid)} for i, l in enumerate(suggestions, len(ret))]
    return HttpResponse(json.dumps(ret), content_type="application/json")

def recordings_search(request):
    q = request.GET.get('recording', '')

    s_artists = request.GET.get('artists', '')
    s_concerts = request.GET.get('concerts', '')
    s_instruments = request.GET.get('instruments', '')
    s_raga = request.GET.get('ragas', '')
    s_tala = request.GET.get('talas', '')

    recordings = Recording.objects
    if s_artists != '' or s_concerts != '' or q\
            or s_instruments != '' or s_raga != '' or s_tala != '':
        if q and q!='':
            ids = list(Work.objects.filter(title__unaccent__icontains=q).values_list('pk', flat=True))
            recordings = recordings.filter(works__id__in=ids)\
                    | recordings.filter(title__unaccent__icontains=q)\
                    | recordings.filter(concert__title__unaccent__icontains=q)

        if s_artists and s_artists != '':
            artists = s_artists.split()
            recordings = recordings.filter(works__composers__mbid__in=artists)\
                    | recordings.filter(works__lyricists__mbid__in=artists)\
                    | recordings.filter(concert__artists__mbid__in=artists)

        if s_concerts and s_concerts != '':
            recordings = recordings.filter(concert__mbid__in=s_concerts.split())

        if s_instruments and s_instruments != '':
            recordings = recordings.filter(instrumentperformance__instrument__mbid__in=s_instruments.split())

        if s_raga and s_raga != '':
            recordings = recordings.filter(works__raaga__uuid__in=s_raga.split())

        if s_tala and s_tala != '':
            recordings = recordings.filter(works__taala__uuid__in=s_tala.split())


    paginator = Paginator(recordings.all(), 25)
    page = request.GET.get('page')
    next_page = None
    try:
        recordings = paginator.page(page)
        if recordings.has_next():
            next_page = recordings.next_page_number()
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        recordings = paginator.page(1)
        if recordings.has_next():
            next_page = recordings.next_page_number()
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        recordings = paginator.page(paginator.num_pages)
    results = {
            "results": [item.get_dict() for item in recordings.object_list],
            "moreResults": next_page
    }
    return HttpResponse(json.dumps(results), content_type='application/json')

def main(request):
    return render(request, "carnatic/index.html")

def filters(request):

    taalas = Taala.objects.prefetch_related('aliases').all()
    taalalist = []
    for r in taalas:
        taalalist.append({"name": r.name, "uuid": str(r.uuid), "aliases": [a.name for a in r.aliases.all()]})

    raagas = Raaga.objects.prefetch_related('aliases').all()
    raagalist = []
    for r in raagas:
        raagalist.append({"name": r.name, "uuid": str(r.uuid), "aliases": [a.name for a in r.aliases.all()]})

    concerts = Concert.objects.all()
    concertlist = []
    for c in concerts:
        concertlist.append({"name": c.title, "mbid": str(c.mbid)})

    artists = Artist.objects.all()
    artistlist = []
    for a in artists:
        rr = []
        tt = []
        cc = []
        ii = []

        artistlist.append({"name": a.name, "mbid": str(a.mbid), "concerts": [str(c.mbid) for c in cc], "raagas": [str(r.uuid) for r in rr], "taalas": [str(t.uuid) for t in tt], "instruments": [str(i.mbid) for i in ii]})


    instruments = Instrument.objects.all()
    instrumentlist = []
    for i in instruments:
        instrumentlist.append({"name": i.name, "mbid": str(i.mbid)})


    ret = {"artists": artistlist,
           "concerts": concertlist,
           "instruments": instrumentlist,
           u"ragas": raagalist,
           u"talas": taalalist,
           }

    return JsonResponse(ret)

def artistsearch(request):
    artists = Artist.objects.filter(dummy=False).order_by('name')
    ret = []
    for a in artists:
        ret.append({"id": a.id, "name": a.name})
    return HttpResponse(json.dumps(ret), content_type="application/json")

def artistbyid(request, artistid, name=None):
    artist = get_object_or_404(Artist, pk=artistid)
    return redirect(artist.get_absolute_url(), permanent=True)

def artist(request, uuid, name=None):
    artist = get_object_or_404(Artist, mbid=uuid)

    if artist.performs_percussion():
        taalas = artist.get_performed_taalas()
    else:
        taalas = []

    if artist.performs_lead():
    # vocalist or violinist
        raagas = artist.get_performed_raagas()
    else:
        raagas = []

    # Sample is the first recording of any of their concerts (Vignesh, Dec 9)
    permission = utils.get_user_permissions(request.user)
    concerts = artist.concerts(permission=permission)
    sample = None
    if concerts:
        recordings = concerts[0].recordings.all()
        if recordings:
            sample = recordings[0]

    biography = []
    if artist.artist_type == 'G':
        for a in artist.group_members.all():
            s = a.state
            if s:
                r = s.name
            else:
                r = None
            biography.append({"name": a.name, "begin": a.begin, "region": r})

    ret = {"artist": artist,
           "objecttype": "artist",
           "objectid": artist.id,
           "raagas": raagas,
           "taalas": taalas,
           "sample": sample,
           "biography": biography,
           }

    return render(request, "carnatic/artist.html", ret)

def composerbyid(request, composerid, name=None):
    composer = get_object_or_404(Composer, pk=composerid)
    return redirect(composer.get_absolute_url(), permanent=True)

def composer(request, uuid, name=None):
    composer = get_object_or_404(Composer, mbid=uuid)

    works = composer.works.all()
    # We show all compositions, ordered by number of recordings
    works = sorted(works, key=lambda w: w.recording_set.count(), reverse=True)

    musicbrainz = composer.get_musicbrainz_url()
    w = SourceName.objects.get(name="Wikipedia")
    wikipedia = None
    desc = composer.description
    if desc and desc.source.source_name == w:
        wikipedia = composer.description.source.uri

    ret = {"composer": composer,
           "mb": musicbrainz,
           "wiki": wikipedia,
           "works": works}

    return render(request, "carnatic/composer.html", ret)

def concertsearch(request):
    permissions = utils.get_user_permissions(request.user)
    concerts = Concert.objects.with_permissions(None, permissions).order_by('title')
    ret = []
    for c in concerts:
        title = "%s<br>%s" % (c.title, c.artistcredit)
        if c.collection and c.collection.permission == "S":
            title = '<img src="%s" title="bootleg concert" /> %s' % (static('carnatic/img/cassette.png'), title)
        ret.append({"id": c.id, "title": title})
    return HttpResponse(json.dumps(ret), content_type="application/json")

def concertbyid(request, concertid, title=None):
    concert = get_object_or_404(Concert, pk=concertid)
    return redirect(concert.get_absolute_url(), permanent=True)

def concert(request, uuid, title=None):
    concert = get_object_or_404(Concert, mbid=uuid)

    show_restricted = False
    is_restricted = concert.collection and concert.collection.permission == "S"
    if is_restricted and request.show_bootlegs:
        show_restricted = True
    elif is_restricted and not request.show_bootlegs:
        raise Http404

    image = None
    if concert.image:
        image = concert.image.image.url
    if not image:
        image = "/media/images/noconcert.jpg"

    sample = None
    recordings = concert.recordings.all()
    if recordings:
        sample = recordings[:1]

    # Other similar concerts
    similar = concert.get_similar()

    # Raaga in
    ret = {"concert": concert,
           "objecttype": "concert",
           "objectid": concert.id,
           "image": image,
           "sample": sample,
           "similar_concerts": similar,
           "recordings": recordings,
           "bootleg": show_restricted
           }

    return render(request, "carnatic/concert.html", ret)

def recordingbyid(request, recordingid, title=None):
    recording = get_object_or_404(Recording, pk=recordingid)
    return redirect(recording.get_absolute_url(), permanent=True)

def recording(request, uuid, title=None):
    recording = get_object_or_404(Recording, mbid=uuid)

    show_restricted = False
    if recording.is_restricted() and request.show_bootlegs:
        show_restricted = True
    elif recording.is_restricted() and not request.show_bootlegs:
        raise Http404

    try:
        wave = docserver.util.docserver_get_url(recording.mbid, "audioimages", "waveform32", 1, version=settings.FEAT_VERSION_IMAGE)
    except docserver.exceptions.NoFileException:
        wave = None
    try:
        spec = docserver.util.docserver_get_url(recording.mbid, "audioimages", "spectrum32", 1, version=settings.FEAT_VERSION_IMAGE)
    except docserver.exceptions.NoFileException:
        spec = None
    try:
        small = docserver.util.docserver_get_url(recording.mbid, "audioimages", "smallfull", version=settings.FEAT_VERSION_IMAGE)
    except docserver.exceptions.NoFileException:
        small = None
    try:
        audio = docserver.util.docserver_get_mp3_url(recording.mbid)
    except docserver.exceptions.NoFileException:
        audio = None
    try:
        tonic = docserver.util.docserver_get_contents(recording.mbid, "carnaticvotedtonic", "tonic", version=settings.FEAT_VERSION_TONIC)
        notenames = ["A", "A♯", "B", "C", "C♯", "D", "D♯", "E", "F", "F♯", "G", "G♯"]
        tonic = round(float(tonic), 2)
        thebin = (12 * math.log(tonic / 440.0) / math.log(2)) % 12
        thebin = int(round(thebin))
        tonic = str(tonic)
        if thebin <= 11 and thebin >= 0:
            tonicname = notenames[thebin]
        else:
            tonicname = ""
    except docserver.exceptions.NoFileException:
        tonic = None
        tonicname = None
    try:
        akshara = docserver.util.docserver_get_contents(recording.mbid, "rhythm", "aksharaPeriod", version=settings.FEAT_VERSION_RHYTHM)
        akshara = str(round(float(akshara), 3) * 1000)
    except docserver.exceptions.NoFileException:
        akshara = None

    try:
        pitchtrackurl = docserver.util.docserver_get_url(recording.mbid, "carnaticnormalisedpitch", "packedpitch", version=settings.FEAT_VERSION_CARNATIC_NORMALISED_PITCH)
        pitchtrackurl = request.build_absolute_uri(pitchtrackurl)
        histogramurl = docserver.util.docserver_get_url(recording.mbid, "carnaticnormalisedpitch", "drawhistogram", version=settings.FEAT_VERSION_CARNATIC_NORMALISED_PITCH)
        histogramurl = request.build_absolute_uri(histogramurl)
    except docserver.exceptions.NoFileException:
        pitchtrackurl = ""
        histogramurl = ""

    try:
        rhythmurl = docserver.util.docserver_get_url(recording.mbid, "rhythm", "aksharaTicks", version=settings.FEAT_VERSION_RHYTHM)
        rhythmurl = request.build_absolute_uri(rhythmurl)
        aksharaurl = docserver.util.docserver_get_url(recording.mbid, "rhythm", "APcurve", version=settings.FEAT_VERSION_RHYTHM)
        aksharaurl = request.build_absolute_uri(aksharaurl)
    except docserver.exceptions.NoFileException:
        rhythmurl = ""
        aksharaurl = ""

    similar = []
    try:
        similar_mbids = search.similar_recordings(recording.mbid)
        for m in similar_mbids:
            try:
                rec = Recording.objects.get(mbid=m[0])
                similar.append(rec)
            except Recording.DoesNotExist:
                pass
    except pysolr.SolrError:
        # TODO: Show error in similar recordings page instead of empty
        pass
    similar = similar[:10]

    try:
        permission = utils.get_user_permissions(request.user)
        concert = recording.concert_set.with_permissions(None, permission=permission).get()
        recordings = list(concert.recordings.all())
        recordingpos = recordings.index(recording)
    except Concert.DoesNotExist:
        concert = None
        recordings = []
        recordingpos = 0
    nextrecording = None
    prevrecording = None
    if recordingpos > 0:
        prevrecording = recordings[recordingpos - 1]
    if recordingpos + 1 < len(recordings):
        nextrecording = recordings[recordingpos + 1]
    mbid = recording.mbid

    ret = {"recording": recording,
           "objecttype": "recording",
           "objectid": recording.id,
           "waveform": wave,
           "spectrogram": spec,
           "smallimage": small,
           "audio": audio,
           "tonic": tonic,
           "tonicname": tonicname,
           "akshara": akshara,
           "mbid": mbid,
           "nextrecording": nextrecording,
           "prevrecording": prevrecording,
           "pitchtrackurl": pitchtrackurl,
           "histogramurl": histogramurl,
           "rhythmurl": rhythmurl,
           "aksharaurl": aksharaurl,
           "similar": similar,
           "concert": concert,
           "bootleg": show_restricted,
           }

    return render(request, "carnatic/recording.html", ret)

def worksearch(request):
    works = Work.objects.all()
    ret = []
    for w in works:
        ret.append({"id": w.id, "title": w.title})
    return HttpResponse(json.dumps(ret), content_type="application/json")

def workbyid(request, workid, title=None):
    work = get_object_or_404(Work, pk=workid)
    return redirect(work.get_absolute_url(), permanent=True)

def work(request, uuid, title=None):
    work = get_object_or_404(Work, mbid=uuid)

    permission = utils.get_user_permissions(request.user)
    recordings = work.recording_set.with_permissions(None, permission).all()
    if len(recordings):
        sample = random.sample(recordings, 1)
    else:
        sample = None

    ret = {"work": work,
           "objecttype": "work",
           "objectid": work.id,
           "sample": sample,
           }
    return render(request, "carnatic/work.html", ret)

def taalasearch(request):
    taalas = Taala.objects.all().order_by('name')
    ret = []
    for t in taalas:
        ret.append({"id": t.id, "name": str(t)})
    return HttpResponse(json.dumps(ret), content_type="application/json")

def taalabyid(request, taalaid, name=None):
    taala = get_object_or_404(Taala, pk=taalaid)
    return redirect(taala.get_absolute_url(), permanent=True)

def taala(request, uuid, name=None):
    taala = get_object_or_404(Taala, uuid=uuid)

    similar = taala.get_similar()
    recordings = taala.recordings(10)
    sample = None
    if len(recordings):
        sample = random.sample(recordings, 1)[0]

    ret = {"taala": taala,
           "sample": sample,
           "similar": similar
           }
    return render(request, "carnatic/taala.html", ret)

def raagasearch(request):
    raagas = Raaga.objects.all().order_by('name')
    ret = []
    for r in raagas:
        ret.append({"id": r.id, "name": str(r)})
    return HttpResponse(json.dumps(ret), content_type="application/json")

def raagabyid(request, raagaid, name=None):
    raaga = get_object_or_404(Raaga, pk=raagaid)
    return redirect(raaga.get_absolute_url(), permanent=True)

def raaga(request, uuid, name=None):
    raaga = get_object_or_404(Raaga, uuid=uuid)
    similar = raaga.get_similar()
    recordings = raaga.recordings(10)
    sample = None
    if len(recordings):
        sample = random.sample(recordings, 1)[0]

    ret = {"raaga": raaga,
           "sample": sample,
           "similar": similar
           }
    return render(request, "carnatic/raaga.html", ret)

def instrumentsearch(request):
    instruments = Instrument.objects.all().order_by('name')
    ret = []
    for i in instruments:
        ret.append({"id": i.id, "name": i.name})
    return HttpResponse(json.dumps(ret), content_type="application/json")

def instrumentbyid(request, instrumentid, name=None):
    instrument = get_object_or_404(Instrument, pk=instrumentid)
    return redirect(instrument.get_absolute_url(), permanent=True)

def instrument(request, uuid, name=None):
    instrument = get_object_or_404(Instrument, mbid=uuid)
    samples = instrument.samples(10)
    sample = None
    if samples:
        sample = samples[0]
    ret = {"instrument": instrument,
           "sample": sample,
           }

    return render(request, "carnatic/instrument.html", ret)

@user_passes_test(dashboard.views.is_staff)
def formedit(request):
    concerts = Concert.objects.all().prefetch_related('artists')
    concerts = sorted(concerts, key=lambda c:sum([r.forms.count() for r in c.recordings.all().prefetch_related('forms')])*1.0/c.recordings.count())
    ret = {"concerts": concerts}
    return render(request, "carnatic/formedit.html", ret)

from django import forms

@user_passes_test(dashboard.views.is_staff)
def formconcert(request, uuid):
    concert = get_object_or_404(Concert, mbid=uuid)
    forms = Form.objects.all()

    dashrelease = dashboard.models.MusicbrainzRelease.objects.get(mbid=concert.mbid)

    if request.method == "POST":
        for i, t in enumerate(concert.tracklist()):
            fname = "form_%s" % i
            f = request.POST.get(fname)
            try:
                f = int(f)
                if len(t.forms.all()):
                    # If we already have a form, and it's different
                    # to the submitted one, remove
                    form = t.forms.get()
                    if f != form.id:
                        t.forms.clear()
                if len(t.forms.all()) == 0:
                    form = Form.objects.get(pk=f)
                    RecordingForm.objects.create(recording=t, form=form, sequence=1)

            except ValueError:
                # Not set, if we had one, remove it
                if len(t.forms.all()):
                    t.forms.clear()
                # Otherwise, do nothing


    tracks = []
    for i, t in enumerate(concert.tracklist()):
        tracks.append((i, t))
    ret = {"concert": concert, "tracks": tracks,
            "dashrelease": dashrelease, "forms": forms}
    return render(request, "carnatic/formconcert.html", ret)
