package com.interviewtracker.repository;

import com.interviewtracker.model.Flashcard;
import com.interviewtracker.model.Topic;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDate;
import java.util.List;

@Repository
public interface FlashcardRepository extends JpaRepository<Flashcard, Long> {

    List<Flashcard> findBySourceTopic(Topic topic);

    List<Flashcard> findByArchivedFalse();

    List<Flashcard> findByCategory(String category);

    @Query("SELECT f FROM Flashcard f WHERE f.archived = false AND f.nextReviewDate <= :date ORDER BY f.nextReviewDate")
    List<Flashcard> findDueForReview(@Param("date") LocalDate date);

    @Query("SELECT f FROM Flashcard f WHERE f.archived = false ORDER BY f.nextReviewDate")
    List<Flashcard> findAllActiveOrderedByReviewDate();

    @Query("SELECT f FROM Flashcard f WHERE LOWER(f.front) LIKE LOWER(CONCAT('%', :searchTerm, '%')) " +
           "OR LOWER(f.back) LIKE LOWER(CONCAT('%', :searchTerm, '%'))")
    List<Flashcard> searchFlashcards(@Param("searchTerm") String searchTerm);

    long countByArchivedFalse();

    long countByNextReviewDateLessThanEqual(LocalDate date);
}
