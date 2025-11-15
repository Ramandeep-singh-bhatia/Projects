package com.interviewtracker.model;

import com.fasterxml.jackson.annotation.JsonManagedReference;
import jakarta.persistence.*;
import jakarta.validation.constraints.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.annotation.LastModifiedDate;
import org.springframework.data.jpa.domain.support.AuditingEntityListener;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

@Entity
@Table(name = "topics")
@Inheritance(strategy = InheritanceType.SINGLE_TABLE)
@DiscriminatorColumn(name = "category", discriminatorType = DiscriminatorType.STRING)
@EntityListeners(AuditingEntityListener.class)
@Data
@NoArgsConstructor
public abstract class Topic {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @NotBlank(message = "Topic is required")
    @Column(nullable = false, length = 500)
    private String topic;

    @Column(length = 500)
    private String subtopic;

    @NotNull(message = "Confidence level is required")
    @Min(value = 1, message = "Confidence must be between 1 and 10")
    @Max(value = 10, message = "Confidence must be between 1 and 10")
    @Column(nullable = false)
    private Integer confidence;

    @Column(length = 1000)
    private String sourceUrl;

    @Column(length = 5000)
    private String notes;

    @Column(length = 5000)
    private String thingsToRemember;

    @CreatedDate
    @Column(nullable = false, updatable = false)
    private LocalDateTime createdDate;

    @LastModifiedDate
    @Column(nullable = false)
    private LocalDateTime lastModifiedDate;

    @Column
    private LocalDateTime lastStudiedDate;

    @OneToMany(mappedBy = "topic", cascade = CascadeType.ALL, orphanRemoval = true, fetch = FetchType.LAZY)
    @JsonManagedReference
    private List<PracticeSession> practiceSessions = new ArrayList<>();

    @OneToMany(mappedBy = "topic", cascade = CascadeType.ALL, orphanRemoval = true, fetch = FetchType.LAZY)
    @JsonManagedReference
    private List<FileMetadata> files = new ArrayList<>();

    /**
     * Calculated field: Total time spent across all practice sessions
     */
    @Transient
    public Integer getTotalTimeSpent() {
        if (practiceSessions == null || practiceSessions.isEmpty()) {
            return 0;
        }
        return practiceSessions.stream()
                .mapToInt(PracticeSession::getDuration)
                .sum();
    }

    /**
     * Calculated field: Number of practice sessions
     */
    @Transient
    public Integer getSessionCount() {
        return practiceSessions != null ? practiceSessions.size() : 0;
    }

    /**
     * Get the category type
     */
    @Transient
    public abstract TopicCategory getCategory();
}
