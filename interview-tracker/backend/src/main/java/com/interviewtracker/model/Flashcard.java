package com.interviewtracker.model;

import jakarta.persistence.*;
import lombok.Data;
import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.annotation.LastModifiedDate;
import org.springframework.data.jpa.domain.support.AuditingEntityListener;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.HashSet;
import java.util.Set;

@Entity
@Table(name = "flashcards")
@Data
@EntityListeners(AuditingEntityListener.class)
public class Flashcard {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "topic_id")
    private Topic sourceTopic; // Optional link to topic

    @Column(length = 1000, nullable = false)
    private String front; // Question/Concept

    @Column(length = 5000, nullable = false)
    private String back; // Answer/Explanation

    @Enumerated(EnumType.STRING)
    private DifficultyLevel difficulty; // EASY, MEDIUM, HARD

    private String category; // For organization

    @ElementCollection
    @CollectionTable(name = "flashcard_tags", joinColumns = @JoinColumn(name = "flashcard_id"))
    @Column(name = "tag")
    private Set<String> tags = new HashSet<>(); // Additional categorization

    // Spaced Repetition (SM-2 Algorithm)
    private Integer easeFactor = 2500; // 2500 = 2.5 (stored as int for precision)
    private Integer interval = 1; // Days until next review
    private Integer repetitions = 0; // Successful reviews in a row
    private LocalDate nextReviewDate;
    private Integer reviewCount = 0; // Total reviews
    private Integer successCount = 0; // Successful reviews

    @CreatedDate
    private LocalDateTime createdDate;

    @LastModifiedDate
    private LocalDateTime lastModifiedDate;

    private LocalDateTime lastReviewedDate;

    private Boolean archived = false; // For mastered cards
}
