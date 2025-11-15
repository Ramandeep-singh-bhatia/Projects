package com.interviewtracker.model;

import com.fasterxml.jackson.annotation.JsonBackReference;
import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDate;

@Entity
@Table(name = "study_plan_items")
@Data
@NoArgsConstructor
public class StudyPlanItem {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "study_plan_id", nullable = false)
    @JsonBackReference
    private StudyPlan studyPlan;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "topic_id")
    private Topic topic;

    @Column(nullable = false)
    private LocalDate scheduledDate;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private StudyPlanItemType itemType;

    @Column(nullable = false)
    private Integer estimatedMinutes;

    @Column
    private Integer displayOrder;

    @Column
    private Boolean completed = false;

    @Column
    private Integer actualMinutesSpent;

    @Column(length = 1000)
    private String notes;
}
