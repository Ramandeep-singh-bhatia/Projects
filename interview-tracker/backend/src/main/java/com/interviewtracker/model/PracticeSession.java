package com.interviewtracker.model;

import com.fasterxml.jackson.annotation.JsonBackReference;
import jakarta.persistence.*;
import jakarta.validation.constraints.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.jpa.domain.support.AuditingEntityListener;

import java.time.LocalDateTime;

@Entity
@Table(name = "practice_sessions")
@EntityListeners(AuditingEntityListener.class)
@Data
@NoArgsConstructor
public class PracticeSession {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "topic_id", nullable = false)
    @JsonBackReference
    private Topic topic;

    @CreatedDate
    @Column(nullable = false, updatable = false)
    private LocalDateTime sessionDate;

    @NotNull(message = "Duration is required")
    @Min(value = 1, message = "Duration must be at least 1 minute")
    @Column(nullable = false)
    private Integer duration; // in minutes

    @NotNull(message = "Performance rating is required")
    @Min(value = 1, message = "Performance rating must be between 1 and 10")
    @Max(value = 10, message = "Performance rating must be between 1 and 10")
    @Column(nullable = false)
    private Integer performanceRating;

    @Column(length = 2000)
    private String whatWentWell;

    @Column(length = 2000)
    private String mistakesMade;

    @Column(length = 2000)
    private String sessionNotes;

    @NotNull(message = "Session type is required")
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private SessionType sessionType;
}
