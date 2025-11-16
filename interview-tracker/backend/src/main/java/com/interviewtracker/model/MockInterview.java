package com.interviewtracker.model;

import com.fasterxml.jackson.annotation.JsonManagedReference;
import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.jpa.domain.support.AuditingEntityListener;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

@Entity
@Table(name = "mock_interviews")
@EntityListeners(AuditingEntityListener.class)
@Data
@NoArgsConstructor
public class MockInterview {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @CreatedDate
    @Column(nullable = false, updatable = false)
    private LocalDateTime startTime;

    @Column
    private LocalDateTime endTime;

    @Column(nullable = false)
    private Integer plannedDuration; // in minutes

    @Column
    private Integer actualDuration; // in minutes

    @Column(nullable = false)
    private Integer questionCount;

    @Column
    private Integer overallPerformance; // 1-10

    @Column
    private Integer overallConfidence; // 1-10

    @Column(length = 2000)
    private String generalNotes;

    @Column
    private Integer pressureLevel; // 1-5 scale

    @Column(nullable = false)
    private Boolean completed = false;

    @OneToMany(mappedBy = "mockInterview", cascade = CascadeType.ALL, orphanRemoval = true)
    @JsonManagedReference
    private List<MockInterviewQuestion> questions = new ArrayList<>();
}
