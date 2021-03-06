# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-09-19 15:30
from __future__ import unicode_literals

import carnatic.models
from django.db import migrations, models
import django.db.models.deletion
import django.db.models.manager


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('data', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Artist',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('mbid', models.UUIDField(blank=True, null=True)),
                ('gender', models.CharField(blank=True, choices=[(b'M', b'Male'), (b'F', b'Female')], max_length=1, null=True)),
                ('begin', models.CharField(blank=True, max_length=10, null=True)),
                ('end', models.CharField(blank=True, max_length=10, null=True)),
                ('artist_type', models.CharField(choices=[(b'P', b'Person'), (b'G', b'Group')], default=b'P', max_length=1)),
                ('dummy', models.BooleanField(db_index=True, default=False)),
                ('description_edited', models.BooleanField(default=False)),
                ('description', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='data.Description')),
                ('group_members', models.ManyToManyField(blank=True, related_name='groups', to='carnatic.Artist')),
                ('gurus', models.ManyToManyField(related_name='students', to='carnatic.Artist')),
                ('images', models.ManyToManyField(related_name='carnatic_artist_image_set', to='data.Image')),
            ],
            options={
                'abstract': False,
            },
            bases=(carnatic.models.CarnaticStyle, models.Model),
        ),
        migrations.CreateModel(
            name='ArtistAlias',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('alias', models.CharField(max_length=100)),
                ('primary', models.BooleanField(default=False)),
                ('locale', models.CharField(blank=True, max_length=10, null=True)),
                ('artist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='aliases', to='carnatic.Artist')),
            ],
            options={
                'abstract': False,
            },
            bases=(carnatic.models.CarnaticStyle, models.Model),
        ),
        migrations.CreateModel(
            name='Composer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('mbid', models.UUIDField(blank=True, null=True)),
                ('gender', models.CharField(blank=True, choices=[(b'M', b'Male'), (b'F', b'Female')], max_length=1, null=True)),
                ('begin', models.CharField(blank=True, max_length=10, null=True)),
                ('end', models.CharField(blank=True, max_length=10, null=True)),
                ('description', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='data.Description')),
                ('images', models.ManyToManyField(related_name='carnatic_composer_image_set', to='data.Image')),
                ('references', models.ManyToManyField(blank=True, related_name='carnatic_composer_reference_set', to='data.Source')),
                ('source', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='carnatic_composer_source_set', to='data.Source')),
            ],
            options={
                'abstract': False,
            },
            bases=(carnatic.models.CarnaticStyle, models.Model),
        ),
        migrations.CreateModel(
            name='ComposerAlias',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('alias', models.CharField(max_length=100)),
                ('primary', models.BooleanField(default=False)),
                ('locale', models.CharField(blank=True, max_length=10, null=True)),
                ('composer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='aliases', to='carnatic.Composer')),
            ],
            options={
                'abstract': False,
            },
            bases=(carnatic.models.CarnaticStyle, models.Model),
        ),
        migrations.CreateModel(
            name='Concert',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mbid', models.UUIDField(blank=True, null=True)),
                ('title', models.CharField(max_length=100)),
                ('artistcredit', models.CharField(max_length=255)),
                ('year', models.IntegerField(blank=True, null=True)),
                ('status', models.CharField(blank=True, max_length=100, null=True)),
                ('rel_type', models.CharField(blank=True, max_length=100, null=True)),
                ('artists', models.ManyToManyField(related_name='primary_concerts', to='carnatic.Artist')),
                ('collection', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='data.Collection')),
                ('description', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='data.Description')),
                ('images', models.ManyToManyField(related_name='carnatic_concert_image_set', to='data.Image')),
            ],
            options={
                'abstract': False,
            },
            bases=(carnatic.models.CarnaticStyle, models.Model),
        ),
        migrations.CreateModel(
            name='ConcertRecording',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('track', models.IntegerField()),
                ('disc', models.IntegerField()),
                ('disctrack', models.IntegerField()),
                ('concert', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='carnatic.Concert')),
            ],
            options={
                'ordering': ('track',),
            },
        ),
        migrations.CreateModel(
            name='Form',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('attrfromrecording', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='FormAlias',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('form', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='aliases', to='carnatic.Form')),
            ],
        ),
        migrations.CreateModel(
            name='GeographicRegion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
            bases=(carnatic.models.CarnaticStyle, models.Model),
        ),
        migrations.CreateModel(
            name='Instrument',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('percussion', models.BooleanField(default=False)),
                ('name', models.CharField(max_length=50)),
                ('mbid', models.UUIDField(blank=True, null=True)),
                ('hidden', models.BooleanField(default=False)),
                ('description', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='data.Description')),
                ('images', models.ManyToManyField(related_name='carnatic_instrument_image_set', to='data.Image')),
                ('references', models.ManyToManyField(blank=True, related_name='carnatic_instrument_reference_set', to='data.Source')),
                ('source', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='carnatic_instrument_source_set', to='data.Source')),
            ],
            options={
                'abstract': False,
            },
            bases=(carnatic.models.CarnaticStyle, models.Model),
            managers=[
                ('fuzzymanager', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='InstrumentAlias',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('instrument', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='aliases', to='carnatic.Instrument')),
            ],
            options={
                'abstract': False,
            },
            bases=(carnatic.models.CarnaticStyle, models.Model),
            managers=[
                ('fuzzymanager', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='InstrumentPerformance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lead', models.BooleanField(default=False)),
                ('attributes', models.CharField(blank=True, max_length=200, null=True)),
                ('artist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='carnatic.Artist')),
                ('instrument', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='carnatic.Instrument')),
            ],
            options={
                'abstract': False,
            },
            bases=(carnatic.models.CarnaticStyle, models.Model),
        ),
        migrations.CreateModel(
            name='Raaga',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('common_name', models.CharField(max_length=50)),
                ('uuid', models.UUIDField(db_index=True)),
                ('description', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='data.Description')),
                ('images', models.ManyToManyField(related_name='carnatic_raaga_image_set', to='data.Image')),
                ('references', models.ManyToManyField(blank=True, related_name='carnatic_raaga_reference_set', to='data.Source')),
                ('source', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='carnatic_raaga_source_set', to='data.Source')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RaagaAlias',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('raaga', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='aliases', to='carnatic.Raaga')),
            ],
            managers=[
                ('fuzzymanager', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='Recording',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('mbid', models.UUIDField(blank=True, null=True)),
                ('length', models.IntegerField(blank=True, null=True)),
                ('description', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='data.Description')),
            ],
            options={
                'abstract': False,
            },
            bases=(carnatic.models.CarnaticStyle, models.Model),
        ),
        migrations.CreateModel(
            name='RecordingForm',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sequence', models.IntegerField()),
                ('form', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='carnatic.Form')),
                ('recording', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='carnatic.Recording')),
            ],
            options={
                'ordering': ('sequence',),
            },
        ),
        migrations.CreateModel(
            name='RecordingRaaga',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sequence', models.IntegerField(blank=True, null=True)),
                ('raaga', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='carnatic.Raaga')),
                ('recording', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='carnatic.Recording')),
            ],
        ),
        migrations.CreateModel(
            name='RecordingTaala',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sequence', models.IntegerField(blank=True, null=True)),
                ('recording', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='carnatic.Recording')),
            ],
        ),
        migrations.CreateModel(
            name='RecordingWork',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sequence', models.IntegerField(blank=True, null=True)),
                ('recording', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='carnatic.Recording')),
            ],
        ),
        migrations.CreateModel(
            name='Taala',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('common_name', models.CharField(max_length=50)),
                ('num_aksharas', models.IntegerField(null=True)),
                ('uuid', models.UUIDField(db_index=True)),
                ('description', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='data.Description')),
                ('images', models.ManyToManyField(related_name='carnatic_taala_image_set', to='data.Image')),
                ('references', models.ManyToManyField(blank=True, related_name='carnatic_taala_reference_set', to='data.Source')),
                ('source', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='carnatic_taala_source_set', to='data.Source')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TaalaAlias',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('taala', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='aliases', to='carnatic.Taala')),
            ],
            managers=[
                ('fuzzymanager', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='Work',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('mbid', models.UUIDField(blank=True, null=True)),
                ('composers', models.ManyToManyField(blank=True, related_name='works', to='carnatic.Composer')),
                ('description', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='data.Description')),
                ('form', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='carnatic.Form')),
                ('images', models.ManyToManyField(related_name='carnatic_work_image_set', to='data.Image')),
                ('lyricists', models.ManyToManyField(blank=True, related_name='lyric_works', to='carnatic.Composer')),
                ('raaga', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='carnatic.Raaga')),
                ('references', models.ManyToManyField(blank=True, related_name='carnatic_work_reference_set', to='data.Source')),
                ('source', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='carnatic_work_source_set', to='data.Source')),
                ('taala', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='carnatic.Taala')),
            ],
            options={
                'abstract': False,
            },
            bases=(carnatic.models.CarnaticStyle, models.Model),
        ),
        migrations.CreateModel(
            name='WorkRaaga',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sequence', models.IntegerField(blank=True, null=True)),
                ('raaga', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='carnatic.Raaga')),
                ('work', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='carnatic.Work')),
            ],
        ),
        migrations.CreateModel(
            name='WorkTaala',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sequence', models.IntegerField(blank=True, null=True)),
                ('taala', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='carnatic.Taala')),
                ('work', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='carnatic.Work')),
            ],
        ),
        migrations.AddField(
            model_name='recordingwork',
            name='work',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='carnatic.Work'),
        ),
        migrations.AddField(
            model_name='recordingtaala',
            name='taala',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='carnatic.Taala'),
        ),
        migrations.AddField(
            model_name='recording',
            name='forms',
            field=models.ManyToManyField(through='carnatic.RecordingForm', to='carnatic.Form'),
        ),
        migrations.AddField(
            model_name='recording',
            name='images',
            field=models.ManyToManyField(related_name='carnatic_recording_image_set', to='data.Image'),
        ),
        migrations.AddField(
            model_name='recording',
            name='performance',
            field=models.ManyToManyField(through='carnatic.InstrumentPerformance', to='carnatic.Artist'),
        ),
        migrations.AddField(
            model_name='recording',
            name='raagas',
            field=models.ManyToManyField(through='carnatic.RecordingRaaga', to='carnatic.Raaga'),
        ),
        migrations.AddField(
            model_name='recording',
            name='references',
            field=models.ManyToManyField(blank=True, related_name='carnatic_recording_reference_set', to='data.Source'),
        ),
        migrations.AddField(
            model_name='recording',
            name='source',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='carnatic_recording_source_set', to='data.Source'),
        ),
        migrations.AddField(
            model_name='recording',
            name='taalas',
            field=models.ManyToManyField(through='carnatic.RecordingTaala', to='carnatic.Taala'),
        ),
        migrations.AddField(
            model_name='recording',
            name='works',
            field=models.ManyToManyField(through='carnatic.RecordingWork', to='carnatic.Work'),
        ),
        migrations.AddField(
            model_name='instrumentperformance',
            name='recording',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='carnatic.Recording'),
        ),
        migrations.AddField(
            model_name='concertrecording',
            name='recording',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='carnatic.Recording'),
        ),
        migrations.AddField(
            model_name='concert',
            name='recordings',
            field=models.ManyToManyField(through='carnatic.ConcertRecording', to='carnatic.Recording'),
        ),
        migrations.AddField(
            model_name='concert',
            name='references',
            field=models.ManyToManyField(blank=True, related_name='carnatic_concert_reference_set', to='data.Source'),
        ),
        migrations.AddField(
            model_name='concert',
            name='source',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='carnatic_concert_source_set', to='data.Source'),
        ),
        migrations.AddField(
            model_name='composer',
            name='state',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='carnatic.GeographicRegion'),
        ),
        migrations.AddField(
            model_name='artist',
            name='main_instrument',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='carnatic.Instrument'),
        ),
        migrations.AddField(
            model_name='artist',
            name='references',
            field=models.ManyToManyField(blank=True, related_name='carnatic_artist_reference_set', to='data.Source'),
        ),
        migrations.AddField(
            model_name='artist',
            name='source',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='carnatic_artist_source_set', to='data.Source'),
        ),
        migrations.AddField(
            model_name='artist',
            name='state',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='carnatic.GeographicRegion'),
        ),
    ]
