package com.interviewtracker.model;

import com.fasterxml.jackson.annotation.JsonBackReference;
import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.jpa.domain.support.AuditingEntityListener;

import java.time.LocalDateTime;

@Entity
@Table(name = "confidence_history")
@EntityListeners(AuditingEntityListener.class)
@Data
@NoArgsConstructor
public class ConfidenceHistory {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "topic_id", nullable = false)
    @JsonBackReference
    private Topic topic;

    @CreatedDate
    @Column(nullable = false, updatable = false)
    private LocalDateTime changeDate;

    @Column(nullable = false)
    private Integer oldConfidence;

    @Column(nullable = false)
    private Integer newConfidence;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private ChangeReason changeReason;

    @Column(length = 500)
    private String notes;
}
