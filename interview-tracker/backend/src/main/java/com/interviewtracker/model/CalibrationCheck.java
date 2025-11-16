package com.interviewtracker.model;

import jakarta.persistence.*;
import lombok.Data;
import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.jpa.domain.support.AuditingEntityListener;

import java.time.LocalDateTime;

@Entity
@Table(name = "calibration_checks")
@Data
@EntityListeners(AuditingEntityListener.class)
public class CalibrationCheck {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "topic_id", nullable = false)
    private Topic topic;

    @CreatedDate
    private LocalDateTime checkDate;

    private Integer confidenceBefore;
    private Integer confidenceAfter;

    @Enumerated(EnumType.STRING)
    private CalibrationType type; // QUICK_VERIFY, PROBLEM, EXPLANATION, QUIZ

    private Boolean passed;

    @Column(length = 5000)
    private String userResponse;

    @Column(length = 2000)
    private String notes;
}
