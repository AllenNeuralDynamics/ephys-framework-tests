# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.contrib.postgres.fields import ArrayField


class Channel(models.Model):
    session_probe = models.ForeignKey('SessionProbe', models.DO_NOTHING, blank=True, null=True)
    structure = models.ForeignKey('Structure', models.DO_NOTHING, blank=True, null=True)
    local_index = models.IntegerField(blank=True, null=True)
    probe_horizontal_position = models.IntegerField(blank=True, null=True)
    probe_vertical_position = models.IntegerField(blank=True, null=True)
    anterior_posterior_ccf_coordinate = models.FloatField(blank=True, null=True)
    dorsal_ventral_ccf_coordinate = models.FloatField(blank=True, null=True)
    left_right_ccf_coordinate = models.FloatField(blank=True, null=True)
    lfp_sampling_rate = models.FloatField(blank=True, null=True)
    sampling_rate = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'channel'


class Genotype(models.Model):
    name = models.CharField(max_length=-1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'genotype'


class Mouse(models.Model):
    sex = models.CharField(max_length=-1, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    genotype = models.ForeignKey(Genotype, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mouse'


class ProbePhase(models.Model):
    name = models.CharField(max_length=-1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'probe_phase'


class Session(models.Model):
    specimen = models.ForeignKey(Mouse, models.DO_NOTHING, blank=True, null=True)
    session_type = models.ForeignKey('SessionType', models.DO_NOTHING, blank=True, null=True)
    acquisition_datetime = models.DateTimeField(blank=True, null=True)
    publication_datetime = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'session'


class SessionProbe(models.Model):
    session = models.ForeignKey(Session, models.DO_NOTHING, blank=True, null=True)
    probe_phase = models.ForeignKey(ProbePhase, models.DO_NOTHING, blank=True, null=True)
    lfp_sampling_rate = models.FloatField(blank=True, null=True)
    sampling_rate = models.FloatField(blank=True, null=True)
    probe_name = models.CharField(max_length=-1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'session_probe'


class SessionType(models.Model):
    name = models.CharField(max_length=-1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'session_type'


class StimulusPresentation(models.Model):
    stimulus_type = models.ForeignKey('StimulusType', models.DO_NOTHING, blank=True, null=True)
    session = models.ForeignKey(Session, models.DO_NOTHING, blank=True, null=True)
    color = models.IntegerField(blank=True, null=True)
    contrast = models.FloatField(blank=True, null=True)
    frame = models.IntegerField(blank=True, null=True)
    orientation = models.IntegerField(blank=True, null=True)
    phase = models.FloatField(blank=True, null=True)
    size = models.FloatField(blank=True, null=True)
    spatial_frequency = models.FloatField(blank=True, null=True)
    stimulus_block = models.IntegerField(blank=True, null=True)
    start_time = models.FloatField(blank=True, null=True)
    stop_time = models.FloatField(blank=True, null=True)
    temporal_frequency = models.FloatField(blank=True, null=True)
    x_position = models.FloatField(blank=True, null=True)
    y_position = models.FloatField(blank=True, null=True)
    duration = models.FloatField(blank=True, null=True)
    stimulus_condition_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'stimulus_presentation'


class StimulusType(models.Model):
    name = models.CharField(max_length=-1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'stimulus_type'


class Structure(models.Model):
    name = models.CharField(max_length=-1, blank=True, null=True)
    abbreviation = models.CharField(max_length=-1, blank=True, null=True)
    color_hex_triplet = models.CharField(max_length=-1, blank=True, null=True)
    structure_id_path = models.CharField(max_length=-1, blank=True, null=True)
    hemisphere_id = models.IntegerField(blank=True, null=True)
    graph_order = models.IntegerField(blank=True, null=True)
    parent_structure_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'structure'


class Unit(models.Model):
    channel = models.ForeignKey(Channel, models.DO_NOTHING, blank=True, null=True)
    amplitude_cutoff = models.FloatField(blank=True, null=True)
    cumulative_drift = models.FloatField(blank=True, null=True)
    d_prime = models.FloatField(blank=True, null=True)
    firing_rate = models.FloatField(blank=True, null=True)
    isi_violations = models.IntegerField(blank=True, null=True)
    isolation_distance = models.FloatField(blank=True, null=True)
    l_ratio = models.FloatField(db_column='L_ratio', blank=True, null=True)  # Field name made lowercase.
    max_drift = models.FloatField(blank=True, null=True)
    nn_hit_rate = models.FloatField(blank=True, null=True)
    nn_miss_rate = models.FloatField(blank=True, null=True)
    presence_ratio = models.FloatField(blank=True, null=True)
    silhouette_score = models.FloatField(blank=True, null=True)
    snr = models.FloatField(blank=True, null=True)
    quality = models.CharField(max_length=-1, blank=True, null=True)
    waveform_pt_ratio = models.FloatField(db_column='waveform_PT_ratio', blank=True, null=True)  # Field name made lowercase.
    waveform_amplitude = models.FloatField(blank=True, null=True)
    waveform_duration = models.FloatField(blank=True, null=True)
    waveform_halfwidth = models.FloatField(blank=True, null=True)
    waveform_spread = models.FloatField(blank=True, null=True)
    waveform_velocity_above = models.FloatField(blank=True, null=True)
    waveform_velocity_below = models.FloatField(blank=True, null=True)
    waveform_recovery_slope = models.FloatField(blank=True, null=True)
    waveform_repolarization_slope = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'unit'


class UnitSpikeTimes(models.Model):
    unit_id = models.AutoField(primary_key=True)
    spike_times = ArrayField(models.FloatField())

    class Meta:
        managed = False
        db_table = 'unit_spike_times'
