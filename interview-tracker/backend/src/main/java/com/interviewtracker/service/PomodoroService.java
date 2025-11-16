package com.interviewtracker.service;

import com.interviewtracker.exception.ResourceNotFoundException;
import com.interviewtracker.model.*;
import com.interviewtracker.repository.PomodoroRepository;
import jakarta.transaction.Transactional;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.*;
import java.util.stream.Collectors;

@Service
public class PomodoroService {

    @Autowired
    private PomodoroRepository pomodoroRepository;

    @Autowired
    private PracticeSessionService sessionService;

    @Autowired
    private SettingsService settingsService;

    @Autowired
    private TopicService topicService;

    /**
     * Start a new Pomodoro
     */
    @Transactional
    public Pomodoro startPomodoro(Long topicId, PomodoroPhase phase, Integer pomodoroNumber) {
        // Check if there's already an active Pomodoro
        Optional<Pomodoro> active = pomodoroRepository.findActivePomodoro();
        if (active.isPresent()) {
            throw new IllegalStateException("Another Pomodoro is already active");
        }

        Settings settings = settingsService.getSettings();

        Pomodoro pomodoro = new Pomodoro();
        if (topicId != null) {
            pomodoro.setTopic(topicService.getTopicById(topicId));
        }
        pomodoro.setPhase(phase);
        pomodoro.setPomodoroNumber(pomodoroNumber != null ? pomodoroNumber : 1);
        pomodoro.setCompleted(false);

        // Set duration based on phase
        int duration = switch (phase) {
            case WORK -> settings.getPomodoroWorkDuration();
            case SHORT_BREAK -> settings.getPomodoroShortBreak();
            case LONG_BREAK -> settings.getPomodoroLongBreak();
        };
        pomodoro.setDuration(duration);

        return pomodoroRepository.save(pomodoro);
    }

    /**
     * Get active Pomodoro
     */
    public Optional<Pomodoro> getActivePomodoro() {
        return pomodoroRepository.findActivePomodoro();
    }

    /**
     * Complete a Pomodoro
     */
    @Transactional
    public Pomodoro completePomodoro(Long pomodoroId) {
        Pomodoro pomodoro = pomodoroRepository.findById(pomodoroId)
                .orElseThrow(() -> new ResourceNotFoundException("Pomodoro not found"));

        pomodoro.setEndTime(LocalDateTime.now());
        pomodoro.setCompleted(true);

        return pomodoroRepository.save(pomodoro);
    }

    /**
     * Stop a Pomodoro early
     */
    @Transactional
    public Pomodoro stopPomodoro(Long pomodoroId) {
        Pomodoro pomodoro = pomodoroRepository.findById(pomodoroId)
                .orElseThrow(() -> new ResourceNotFoundException("Pomodoro not found"));

        pomodoro.setEndTime(LocalDateTime.now());
        pomodoro.setCompleted(false); // Not completed if stopped early

        // Adjust duration to actual time spent
        long actualMinutes = ChronoUnit.MINUTES.between(pomodoro.getStartTime(), pomodoro.getEndTime());
        pomodoro.setDuration((int) actualMinutes);

        return pomodoroRepository.save(pomodoro);
    }

    /**
     * Log a session after Pomodoro completion
     */
    @Transactional
    public Pomodoro logPomodoroSession(Long pomodoroId, Integer performanceRating, String quickNotes) {
        Pomodoro pomodoro = pomodoroRepository.findById(pomodoroId)
                .orElseThrow(() -> new ResourceNotFoundException("Pomodoro not found"));

        if (pomodoro.getTopic() != null && pomodoro.getPhase() == PomodoroPhase.WORK) {
            PracticeSession session = new PracticeSession();
            session.setDuration(pomodoro.getDuration());
            session.setPerformanceRating(performanceRating);
            session.setSessionNotes(quickNotes != null ? quickNotes : "Pomodoro session");
            session.setSessionType(SessionType.REVISION);

            PracticeSession savedSession = sessionService.createSession(pomodoro.getTopic().getId(), session);
            pomodoro.setLinkedSession(savedSession);
            pomodoro.setNotes(quickNotes);
            pomodoroRepository.save(pomodoro);
        }

        return pomodoro;
    }

    /**
     * Get Pomodoro statistics
     */
    public Map<String, Object> getPomodoroStatistics() {
        Map<String, Object> stats = new HashMap<>();

        // Total completed work Pomodoros
        LocalDateTime monthAgo = LocalDateTime.now().minusMonths(1);
        List<Pomodoro> allCompleted = pomodoroRepository.findCompletedByPhaseAfter(
                PomodoroPhase.WORK, monthAgo);

        stats.put("totalPomodoros", allCompleted.size());

        // This week vs last week
        LocalDateTime weekAgo = LocalDateTime.now().minusWeeks(1);
        LocalDateTime twoWeeksAgo = LocalDateTime.now().minusWeeks(2);

        long thisWeek = pomodoroRepository.countCompletedWorkPomodorosAfter(weekAgo);
        long lastWeek = pomodoroRepository.findCompletedByPhaseAfter(PomodoroPhase.WORK, twoWeeksAgo).stream()
                .filter(p -> p.getStartTime().isBefore(weekAgo))
                .count();

        stats.put("pomodorosThisWeek", thisWeek);
        stats.put("pomodorosLastWeek", lastWeek);

        // Average per day (last 30 days)
        stats.put("averagePerDay", allCompleted.size() / 30.0);

        // By category
        Map<TopicCategory, Long> byCategory = allCompleted.stream()
                .filter(p -> p.getTopic() != null)
                .collect(Collectors.groupingBy(
                        p -> p.getTopic().getCategory(),
                        Collectors.counting()
                ));
        stats.put("pomodorosByCategory", byCategory);

        // Current streak
        int currentStreak = calculatePomodoroStreak();
        stats.put("currentStreak", currentStreak);

        return stats;
    }

    private int calculatePomodoroStreak() {
        List<Pomodoro> completed = pomodoroRepository.findRecentCompleted(100);

        if (completed.isEmpty()) {
            return 0;
        }

        // Get unique days with Pomodoros
        Set<String> days = completed.stream()
                .map(p -> p.getStartTime().toLocalDate().toString())
                .collect(Collectors.toSet());

        String today = LocalDateTime.now().toLocalDate().toString();
        String yesterday = LocalDateTime.now().minusDays(1).toLocalDate().toString();

        if (!days.contains(today) && !days.contains(yesterday)) {
            return 0;
        }

        int streak = days.contains(today) ? 1 : 0;
        LocalDateTime checkDate = days.contains(today) ?
                LocalDateTime.now().minusDays(1) : LocalDateTime.now().minusDays(2);

        while (days.contains(checkDate.toLocalDate().toString())) {
            streak++;
            checkDate = checkDate.minusDays(1);
        }

        return streak;
    }

    /**
     * Get Pomodoro history
     */
    public List<Pomodoro> getPomodoroHistory(int limit) {
        return pomodoroRepository.findRecentCompleted(limit);
    }

    /**
     * Get Pomodoros for a topic
     */
    public List<Pomodoro> getPomodorosForTopic(Long topicId) {
        return pomodoroRepository.findByTopicIdOrderByStartTimeDesc(topicId);
    }
}
