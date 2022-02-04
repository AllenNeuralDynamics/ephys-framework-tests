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
    session_probe = models.ForeignKey('SessionProbe', models.CASCADE, blank=True, null=True)
    structure = models.ForeignKey('Structure', models.CASCADE, blank=True, null=True)
    local_index = models.IntegerField(blank=True, null=True)
    probe_horizontal_position = models.IntegerField(blank=True, null=True)
    probe_vertical_position = models.IntegerField(blank=True, null=True)
    anterior_posterior_ccf_coordinate = models.FloatField(blank=True, null=True)
    dorsal_ventral_ccf_coordinate = models.FloatField(blank=True, null=True)
    left_right_ccf_coordinate = models.FloatField(blank=True, null=True)
    lfp_sampling_rate = models.FloatField(blank=True, null=True)
    sampling_rate = models.FloatField(blank=True, null=True)


class Genotype(models.Model):
    name = models.TextField(blank=True, null=True)

class Mouse(models.Model):
    sex = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    genotype = models.ForeignKey(Genotype, models.CASCADE, blank=True, null=True)

class ProbePhase(models.Model):
    name = models.TextField(blank=True, null=True)

class Session(models.Model):
    specimen = models.ForeignKey(Mouse, models.CASCADE, blank=True, null=True)
    session_type = models.ForeignKey('SessionType', models.CASCADE, blank=True, null=True)
    acquisition_datetime = models.DateTimeField(blank=True, null=True)
    publication_datetime = models.DateTimeField(blank=True, null=True)

class SessionProbe(models.Model):
    session = models.ForeignKey(Session, models.CASCADE, blank=True, null=True)
    probe_phase = models.ForeignKey(ProbePhase, models.CASCADE, blank=True, null=True)
    lfp_sampling_rate = models.FloatField(blank=True, null=True)
    sampling_rate = models.FloatField(blank=True, null=True)
    probe_name = models.TextField(blank=True, null=True)


class SessionType(models.Model):
    name = models.TextField(blank=True, null=True)


class StimulusPresentation(models.Model):
    stimulus_type = models.ForeignKey('StimulusType', models.CASCADE, blank=True, null=True)
    session = models.ForeignKey(Session, models.CASCADE, blank=True, null=True)

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
    stimulus_presentation_id = models.IntegerField(blank=True, null=True)
    stimulus_condition_id = models.IntegerField(blank=True, null=True)


class StimulusType(models.Model):
    name = models.TextField(blank=True, null=True)


class Structure(models.Model):
    name = models.TextField(blank=True, null=True)
    abbreviation = models.TextField(blank=True, null=True)
    color_hex_triplet = models.TextField(blank=True, null=True)
    structure_id_path = models.TextField(blank=True, null=True)
    hemisphere_id = models.IntegerField(blank=True, null=True)
    graph_order = models.IntegerField(blank=True, null=True)
    parent_structure_id = models.IntegerField(blank=True, null=True)


class Unit(models.Model):
    channel = models.ForeignKey(Channel, models.CASCADE, blank=True, null=True)
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
    quality = models.TextField(blank=True, null=True)
    waveform_pt_ratio = models.FloatField(db_column='waveform_PT_ratio', blank=True, null=True)  # Field name made lowercase.
    waveform_amplitude = models.FloatField(blank=True, null=True)
    waveform_duration = models.FloatField(blank=True, null=True)
    waveform_halfwidth = models.FloatField(blank=True, null=True)
    waveform_spread = models.FloatField(blank=True, null=True)
    waveform_velocity_above = models.FloatField(blank=True, null=True)
    waveform_velocity_below = models.FloatField(blank=True, null=True)
    waveform_recovery_slope = models.FloatField(blank=True, null=True)
    waveform_repolarization_slope = models.FloatField(blank=True, null=True)


class UnitSpikeTimes(models.Model):
    unit = models.ForeignKey(Unit, models.CASCADE, blank=True, null=True)
    spike_times = ArrayField(models.FloatField())

class TrialSpikeCounts(models.Model):
    stimulus = models.ForeignKey(StimulusPresentation, models.CASCADE, blank=True, null=True)
    unit = models.ForeignKey(Unit, models.CASCADE, blank=True, null=True)
    spike_count = models.IntegerField(blank=True, null=True)
    spike_rate = models.FloatField(blank=True, null=True)

