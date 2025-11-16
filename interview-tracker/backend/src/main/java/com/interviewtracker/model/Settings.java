package com.interviewtracker.model;

import jakarta.persistence.*;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotNull;
import lombok.Data;
import lombok.NoArgsConstructor;

@Entity
@Table(name = "settings")
@Data
@NoArgsConstructor
public class Settings {

    @Id
    private Long id = 1L; // Singleton - always ID 1

    @NotNull
    @Min(value = 1, message = "Daily study hours must be at least 1")
    @Max(value = 12, message = "Daily study hours must be at most 12")
    @Column(nullable = false)
    private Integer dailyStudyHours = 4;

    @NotNull
    @Min(value = 0, message = "Weekly DSA goal must be at least 0")
    @Column(nullable = false)
    private Integer weeklyDsaGoal = 5;

    @NotNull
    @Min(value = 0, message = "Weekly HLD goal must be at least 0")
    @Column(nullable = false)
    private Integer weeklyHldGoal = 2;

    @NotNull
    @Min(value = 0, message = "Weekly LLD goal must be at least 0")
    @Column(nullable = false)
    private Integer weeklyLldGoal = 2;

    @NotNull
    @Min(value = 0, message = "Weekly Behavioral goal must be at least 0")
    @Column(nullable = false)
    private Integer weeklyBehavioralGoal = 3;

    @NotNull
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private WeekStartDay weekStartDay = WeekStartDay.MONDAY;

    @NotNull
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private Theme theme = Theme.AUTO;

    // Confidence Decay Settings
    @NotNull
    @Column(nullable = false)
    private Boolean confidenceDecayEnabled = true;

    @NotNull
    @Min(value = 1, message = "Decay threshold must be at least 1 day")
    @Max(value = 30, message = "Decay threshold must be at most 30 days")
    @Column(nullable = false)
    private Integer decayThresholdDays = 7;

    @NotNull
    @Min(value = 1, message = "Decay interval must be at least 1 day")
    @Max(value = 30, message = "Decay interval must be at most 30 days")
    @Column(nullable = false)
    private Integer decayIntervalDays = 7;

    @NotNull
    @Column(nullable = false)
    private Double decayRate = 0.5;

    @NotNull
    @Column(nullable = false)
    private Double decayRateEasy = 0.3;

    @NotNull
    @Column(nullable = false)
    private Double decayRateMedium = 0.5;

    @NotNull
    @Column(nullable = false)
    private Double decayRateHard = 0.8;

    // Pomodoro Settings
    @NotNull
    @Min(value = 15, message = "Work duration must be between 15-60 minutes")
    @Max(value = 60, message = "Work duration must be between 15-60 minutes")
    @Column(nullable = false)
    private Integer pomodoroWorkDuration = 25;

    @NotNull
    @Min(value = 3, message = "Short break must be between 3-10 minutes")
    @Max(value = 10, message = "Short break must be between 3-10 minutes")
    @Column(nullable = false)
    private Integer pomodoroShortBreak = 5;

    @NotNull
    @Min(value = 10, message = "Long break must be between 10-30 minutes")
    @Max(value = 30, message = "Long break must be between 10-30 minutes")
    @Column(nullable = false)
    private Integer pomodoroLongBreak = 15;

    @NotNull
    @Min(value = 2, message = "Pomodoros before long break must be between 2-8")
    @Max(value = 8, message = "Pomodoros before long break must be between 2-8")
    @Column(nullable = false)
    private Integer pomodorosBeforeLongBreak = 4;

    @NotNull
    @Column(nullable = false)
    private Boolean pomodoroAutoStartNext = false;

    @NotNull
    @Column(nullable = false)
    private Boolean pomodoroAutoStartBreak = true;

    @NotNull
    @Column(nullable = false)
    private Boolean pomodoroSoundEnabled = true;

    @NotNull
    @Min(value = 0, message = "Volume must be between 0-100")
    @Max(value = 100, message = "Volume must be between 0-100")
    @Column(nullable = false)
    private Integer pomodoroSoundVolume = 50;
}
