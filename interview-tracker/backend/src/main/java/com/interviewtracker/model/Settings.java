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
}
