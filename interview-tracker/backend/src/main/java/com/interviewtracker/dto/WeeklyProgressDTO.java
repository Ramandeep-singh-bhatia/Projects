package com.interviewtracker.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDate;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class WeeklyProgressDTO {
    private LocalDate weekStartDate;
    private LocalDate weekEndDate;
    private Integer dsaGoal;
    private Integer dsaActual;
    private Integer hldGoal;
    private Integer hldActual;
    private Integer lldGoal;
    private Integer lldActual;
    private Integer behavioralGoal;
    private Integer behavioralActual;

    public String getDsaStatus() {
        return getStatus(dsaActual, dsaGoal);
    }

    public String getHldStatus() {
        return getStatus(hldActual, hldGoal);
    }

    public String getLldStatus() {
        return getStatus(lldActual, lldGoal);
    }

    public String getBehavioralStatus() {
        return getStatus(behavioralActual, behavioralGoal);
    }

    private String getStatus(int actual, int goal) {
        if (goal == 0) return "NONE";
        double percentage = (actual * 100.0) / goal;
        if (percentage >= 100) return "GREEN";
        if (percentage >= 70) return "YELLOW";
        return "RED";
    }

    public Double getDsaPercentage() {
        return getPercentage(dsaActual, dsaGoal);
    }

    public Double getHldPercentage() {
        return getPercentage(hldActual, hldGoal);
    }

    public Double getLldPercentage() {
        return getPercentage(lldActual, lldGoal);
    }

    public Double getBehavioralPercentage() {
        return getPercentage(behavioralActual, behavioralGoal);
    }

    private Double getPercentage(int actual, int goal) {
        if (goal == 0) return 0.0;
        return Math.min(100.0, (actual * 100.0) / goal);
    }
}
