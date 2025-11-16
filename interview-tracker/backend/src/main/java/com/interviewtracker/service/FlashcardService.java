package com.interviewtracker.service;

import com.interviewtracker.model.Flashcard;
import com.interviewtracker.model.Topic;
import com.interviewtracker.repository.FlashcardRepository;
import com.interviewtracker.repository.TopicRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class FlashcardService {

    private final FlashcardRepository flashcardRepository;
    private final TopicRepository topicRepository;

    // Create flashcard
    @Transactional
    public Flashcard createFlashcard(Flashcard flashcard) {
        if (flashcard.getEaseFactor() == null) {
            flashcard.setEaseFactor(2500); // Default ease factor = 2.5
        }
        if (flashcard.getInterval() == null) {
            flashcard.setInterval(1);
        }
        if (flashcard.getRepetitions() == null) {
            flashcard.setRepetitions(0);
        }
        if (flashcard.getReviewCount() == null) {
            flashcard.setReviewCount(0);
        }
        if (flashcard.getSuccessCount() == null) {
            flashcard.setSuccessCount(0);
        }
        if (flashcard.getNextReviewDate() == null) {
            flashcard.setNextReviewDate(LocalDate.now().plusDays(1));
        }
        if (flashcard.getArchived() == null) {
            flashcard.setArchived(false);
        }
        return flashcardRepository.save(flashcard);
    }

    // Get flashcard by ID
    public Flashcard getFlashcardById(Long id) {
        return flashcardRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Flashcard not found with id: " + id));
    }

    // Get all flashcards
    public List<Flashcard> getAllFlashcards() {
        return flashcardRepository.findAll();
    }

    // Get active flashcards (not archived)
    public List<Flashcard> getActiveFlashcards() {
        return flashcardRepository.findByArchivedFalse();
    }

    // Get flashcards by topic
    public List<Flashcard> getFlashcardsByTopic(Long topicId) {
        Topic topic = topicRepository.findById(topicId)
                .orElseThrow(() -> new RuntimeException("Topic not found with id: " + topicId));
        return flashcardRepository.findBySourceTopic(topic);
    }

    // Get flashcards by category
    public List<Flashcard> getFlashcardsByCategory(String category) {
        return flashcardRepository.findByCategory(category);
    }

    // Update flashcard
    @Transactional
    public Flashcard updateFlashcard(Long id, Flashcard updatedFlashcard) {
        Flashcard existing = getFlashcardById(id);
        existing.setFront(updatedFlashcard.getFront());
        existing.setBack(updatedFlashcard.getBack());
        existing.setDifficulty(updatedFlashcard.getDifficulty());
        existing.setCategory(updatedFlashcard.getCategory());
        existing.setTags(updatedFlashcard.getTags());
        if (updatedFlashcard.getSourceTopic() != null) {
            existing.setSourceTopic(updatedFlashcard.getSourceTopic());
        }
        return flashcardRepository.save(existing);
    }

    // Delete flashcard
    @Transactional
    public void deleteFlashcard(Long id) {
        flashcardRepository.deleteById(id);
    }

    // Archive flashcard (for mastered cards)
    @Transactional
    public Flashcard archiveFlashcard(Long id) {
        Flashcard flashcard = getFlashcardById(id);
        flashcard.setArchived(true);
        return flashcardRepository.save(flashcard);
    }

    // Get flashcards due for review
    public List<Flashcard> getFlashcardsDueForReview() {
        return flashcardRepository.findDueForReview(LocalDate.now());
    }

    // Get next flashcard to review
    public Flashcard getNextFlashcardToReview() {
        List<Flashcard> dueCards = getFlashcardsDueForReview();
        if (dueCards.isEmpty()) {
            return null;
        }
        return dueCards.get(0);
    }

    // Submit flashcard review with SM-2 algorithm
    @Transactional
    public Flashcard submitReview(Long flashcardId, int quality) {
        if (quality < 0 || quality > 5) {
            throw new IllegalArgumentException("Quality must be between 0 and 5");
        }

        Flashcard flashcard = getFlashcardById(flashcardId);

        // Increment review count
        flashcard.setReviewCount(flashcard.getReviewCount() + 1);
        flashcard.setLastReviewedDate(LocalDateTime.now());

        // SM-2 Algorithm
        int easeFactor = flashcard.getEaseFactor();
        int interval = flashcard.getInterval();
        int repetitions = flashcard.getRepetitions();

        if (quality >= 3) {
            // Correct response
            if (repetitions == 0) {
                interval = 1;
            } else if (repetitions == 1) {
                interval = 6;
            } else {
                interval = Math.round(interval * (easeFactor / 1000.0f));
            }
            repetitions++;
            flashcard.setSuccessCount(flashcard.getSuccessCount() + 1);
        } else {
            // Incorrect response
            repetitions = 0;
            interval = 1;
        }

        // Update ease factor
        easeFactor = easeFactor + (280 - (5 - quality) * 280);
        if (easeFactor < 1300) {
            easeFactor = 1300; // Minimum ease factor = 1.3
        }

        // Calculate next review date
        LocalDate nextReviewDate = LocalDate.now().plusDays(interval);

        // Update flashcard
        flashcard.setEaseFactor(easeFactor);
        flashcard.setInterval(interval);
        flashcard.setRepetitions(repetitions);
        flashcard.setNextReviewDate(nextReviewDate);

        return flashcardRepository.save(flashcard);
    }

    // Search flashcards
    public List<Flashcard> searchFlashcards(String searchTerm) {
        return flashcardRepository.searchFlashcards(searchTerm);
    }

    // Get flashcard statistics
    public Map<String, Object> getFlashcardStats() {
        Map<String, Object> stats = new HashMap<>();
        stats.put("totalFlashcards", flashcardRepository.count());
        stats.put("activeFlashcards", flashcardRepository.countByArchivedFalse());
        stats.put("flashcardsDueToday", flashcardRepository.countByNextReviewDateLessThanEqual(LocalDate.now()));

        List<Flashcard> allCards = flashcardRepository.findByArchivedFalse();
        if (!allCards.isEmpty()) {
            double avgSuccessRate = allCards.stream()
                    .filter(f -> f.getReviewCount() > 0)
                    .mapToDouble(f -> (double) f.getSuccessCount() / f.getReviewCount() * 100)
                    .average()
                    .orElse(0.0);
            stats.put("averageSuccessRate", Math.round(avgSuccessRate * 10) / 10.0);

            long masteredCards = allCards.stream()
                    .filter(f -> f.getReviewCount() >= 10 &&
                                 (f.getReviewCount() > 0 ? (double) f.getSuccessCount() / f.getReviewCount() : 0) >= 0.9)
                    .count();
            stats.put("masteredCards", masteredCards);
        } else {
            stats.put("averageSuccessRate", 0.0);
            stats.put("masteredCards", 0L);
        }

        return stats;
    }

    // Auto-generate flashcards from topic notes
    @Transactional
    public List<Flashcard> generateFlashcardsFromTopic(Long topicId) {
        Topic topic = topicRepository.findById(topicId)
                .orElseThrow(() -> new RuntimeException("Topic not found with id: " + topicId));

        List<Flashcard> generatedCards = new ArrayList<>();
        String notes = topic.getThingsToRemember();

        if (notes == null || notes.trim().isEmpty()) {
            return generatedCards;
        }

        // Simple extraction patterns
        // Pattern 1: "X is Y" → Front: "What is X?", Back: "Y"
        Pattern isPattern = Pattern.compile("([A-Za-z][\\w\\s]+)\\s+is\\s+(.+?)[\\.\\n]", Pattern.CASE_INSENSITIVE);
        Matcher isMatcher = isPattern.matcher(notes);
        while (isMatcher.find() && generatedCards.size() < 10) {
            String concept = isMatcher.group(1).trim();
            String definition = isMatcher.group(2).trim();

            Flashcard card = new Flashcard();
            card.setFront("What is " + concept + "?");
            card.setBack(definition);
            card.setSourceTopic(topic);
            card.setCategory(topic.getClass().getSimpleName());
            card.setDifficulty(topic instanceof com.interviewtracker.model.DSATopic ?
                              ((com.interviewtracker.model.DSATopic) topic).getDifficulty() :
                              com.interviewtracker.model.DifficultyLevel.MEDIUM);
            generatedCards.add(card);
        }

        // Pattern 2: Bullet points → Front: "List X", Back: bullet points
        if (notes.contains("-") || notes.contains("•")) {
            String[] lines = notes.split("\\n");
            StringBuilder bulletPoints = new StringBuilder();
            String header = null;

            for (String line : lines) {
                line = line.trim();
                if (line.startsWith("-") || line.startsWith("•")) {
                    if (bulletPoints.length() == 0 && header != null) {
                        bulletPoints.append(line).append("\n");
                    } else {
                        bulletPoints.append(line).append("\n");
                    }
                } else if (!line.isEmpty() && bulletPoints.length() == 0) {
                    header = line;
                }
            }

            if (bulletPoints.length() > 0 && generatedCards.size() < 10) {
                Flashcard card = new Flashcard();
                card.setFront(header != null ? "List: " + header : "Key points for " + topic.getTopic());
                card.setBack(bulletPoints.toString().trim());
                card.setSourceTopic(topic);
                card.setCategory(topic.getClass().getSimpleName());
                generatedCards.add(card);
            }
        }

        return generatedCards; // Return for review, don't auto-save
    }

    // Bulk create flashcards
    @Transactional
    public List<Flashcard> bulkCreateFlashcards(List<Flashcard> flashcards) {
        return flashcards.stream()
                .map(this::createFlashcard)
                .collect(Collectors.toList());
    }
}
