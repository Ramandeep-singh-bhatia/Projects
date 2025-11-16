package com.interviewtracker.model;

import com.fasterxml.jackson.annotation.JsonManagedReference;
import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.annotation.LastModifiedDate;
import org.springframework.data.jpa.domain.support.AuditingEntityListener;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

@Entity
@Table(name = "study_plans")
@EntityListeners(AuditingEntityListener.class)
@Data
@NoArgsConstructor
public class StudyPlan {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 200)
    private String name;

    @Column(nullable = false)
    private LocalDate interviewDate;

    @Column(nullable = false)
    private LocalDate startDate;

    @Column(nullable = false)
    private Integer daysAvailable;

    @Column(nullable = false)
    private Integer hoursPerDay;

    @Column(length = 1000)
    private String priorityFocus;

    @Column(length = 1000)
    private String topicSelection;

    @CreatedDate
    @Column(nullable = false, updatable = false)
    private LocalDateTime createdDate;

    @LastModifiedDate
    @Column(nullable = false)
    private LocalDateTime lastModifiedDate;

    @Column(nullable = false)
    private Boolean active = true;

    @OneToMany(mappedBy = "studyPlan", cascade = CascadeType.ALL, orphanRemoval = true)
    @JsonManagedReference
    private List<StudyPlanItem> items = new ArrayList<>();

    @Transient
    public Integer getTotalTopics() {
        return items != null ? (int) items.stream()
                .filter(item -> item.getItemType() != StudyPlanItemType.REST)
                .count() : 0;
    }

    @Transient
    public Integer getCompletedTopics() {
        return items != null ? (int) items.stream()
                .filter(item -> item.getCompleted() != null && item.getCompleted())
                .count() : 0;
    }
}
