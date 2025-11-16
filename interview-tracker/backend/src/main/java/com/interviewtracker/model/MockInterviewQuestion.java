package com.interviewtracker.model;

import com.fasterxml.jackson.annotation.JsonBackReference;
import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;

@Entity
@Table(name = "mock_interview_questions")
@Data
@NoArgsConstructor
public class MockInterviewQuestion {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "mock_interview_id", nullable = false)
    @JsonBackReference
    private MockInterview mockInterview;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "topic_id", nullable = false)
    private Topic topic;

    @Column(nullable = false)
    private Integer questionNumber;

    @Column(nullable = false)
    private Integer timeSpent; // in minutes

    @Column
    private Integer performanceRating; // 1-10

    @Column(length = 2000)
    private String whatWentWell;

    @Column(length = 2000)
    private String whatNeedsImprovement;

    @Column
    private Boolean couldSolveInRealInterview; // true/false/null for maybe

    @Column(length = 5000)
    private String scratchpadContent;

    @OneToOne
    @JoinColumn(name = "linked_session_id")
    private PracticeSession linkedSession;
}
