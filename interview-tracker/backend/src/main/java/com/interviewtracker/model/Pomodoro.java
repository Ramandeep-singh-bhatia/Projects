package com.interviewtracker.model;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.jpa.domain.support.AuditingEntityListener;

import java.time.LocalDateTime;

@Entity
@Table(name = "pomodoros")
@EntityListeners(AuditingEntityListener.class)
@Data
@NoArgsConstructor
public class Pomodoro {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "topic_id")
    private Topic topic;

    @CreatedDate
    @Column(nullable = false, updatable = false)
    private LocalDateTime startTime;

    @Column
    private LocalDateTime endTime;

    @Column(nullable = false)
    private Integer duration; // in minutes

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private PomodoroPhase phase;

    @Column(nullable = false)
    private Boolean completed = false;

    @Column
    private Integer pomodoroNumber; // 1-4 in cycle

    @OneToOne
    @JoinColumn(name = "linked_session_id")
    private PracticeSession linkedSession;

    @Column(length = 2000)
    private String notes;
}
