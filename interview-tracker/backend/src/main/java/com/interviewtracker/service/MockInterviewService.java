package com.interviewtracker.service;

import com.interviewtracker.exception.ResourceNotFoundException;
import com.interviewtracker.model.*;
import com.interviewtracker.repository.MockInterviewRepository;
import com.interviewtracker.repository.TopicRepository;
import jakarta.transaction.Transactional;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.*;
import java.util.stream.Collectors;

@Service
public class MockInterviewService {

    @Autowired
    private MockInterviewRepository mockInterviewRepository;

    @Autowired
    private TopicRepository topicRepository;

    @Autowired
    private PracticeSessionService sessionService;

    /**
     * Start a new mock interview
     */
    @Transactional
    public Map<String, Object> startMockInterview(List<String> categories, String difficulty,
                                                   Integer duration, String focusArea) {
        MockInterview mockInterview = new MockInterview();
        mockInterview.setPlannedDuration(duration);
        mockInterview.setQuestionCount(calculateQuestionCount(duration));
        mockInterview.setCompleted(false);

        mockInterview = mockInterviewRepository.save(mockInterview);

        // Select questions
        List<Topic> selectedTopics = selectTopicsForMockInterview(categories, difficulty, focusArea,
                mockInterview.getQuestionCount());

        // Create question records
        for (int i = 0; i < selectedTopics.size(); i++) {
            MockInterviewQuestion question = new MockInterviewQuestion();
            question.setMockInterview(mockInterview);
            question.setTopic(selectedTopics.get(i));
            question.setQuestionNumber(i + 1);
            question.setTimeSpent(0);
            mockInterview.getQuestions().add(question);
        }

        mockInterviewRepository.save(mockInterview);

        // Return response
        Map<String, Object> response = new HashMap<>();
        response.put("mockInterviewId", mockInterview.getId());
        response.put("duration", duration);
        response.put("questionCount", mockInterview.getQuestionCount());
        response.put("questions", selectedTopics.stream().map(t -> {
            Map<String, Object> q = new HashMap<>();
            q.put("topicId", t.getId());
            q.put("topic", t.getTopic());
            q.put("subtopic", t.getSubtopic());
            q.put("category", t.getCategory());
            if (t instanceof DSATopic) {
                q.put("difficulty", ((DSATopic) t).getDifficulty());
            }
            return q;
        }).collect(Collectors.toList()));

        return response;
    }

    private int calculateQuestionCount(int duration) {
        return switch (duration) {
            case 30 -> 2;
            case 45 -> 3;
            case 60 -> 4;
            case 90 -> 6;
            default -> Math.max(2, duration / 15);
        };
    }

    private List<Topic> selectTopicsForMockInterview(List<String> categories, String difficulty,
                                                      String focusArea, int count) {
        List<Topic> allTopics = topicRepository.findAll();

        // Filter by categories
        if (categories != null && !categories.isEmpty() && !categories.contains("MIXED")) {
            Set<TopicCategory> categorySet = categories.stream()
                    .map(TopicCategory::valueOf)
                    .collect(Collectors.toSet());
            allTopics = allTopics.stream()
                    .filter(t -> categorySet.contains(t.getCategory()))
                    .collect(Collectors.toList());
        }

        // Filter by difficulty (for DSA topics)
        if (difficulty != null && !difficulty.equals("MIXED")) {
            DifficultyLevel diffLevel = DifficultyLevel.valueOf(difficulty);
            allTopics = allTopics.stream()
                    .filter(t -> !(t instanceof DSATopic) || ((DSATopic) t).getDifficulty() == diffLevel)
                    .collect(Collectors.toList());
        }

        // Filter by focus area
        if ("WEAK".equals(focusArea)) {
            allTopics = allTopics.stream()
                    .filter(t -> t.getConfidence() < 6)
                    .collect(Collectors.toList());
        }

        // Prefer topics not recently practiced
        allTopics.sort(Comparator.comparing(Topic::getLastStudiedDate, Comparator.nullsFirst(Comparator.naturalOrder())));

        // Select diverse topics
        return selectDiverseTopics(allTopics, count);
    }

    private List<Topic> selectDiverseTopics(List<Topic> topics, int count) {
        if (topics.size() <= count) {
            return new ArrayList<>(topics);
        }

        List<Topic> selected = new ArrayList<>();
        Map<TopicCategory, Integer> categoryCount = new HashMap<>();
        Random random = new Random();

        // Try to get diverse categories
        for (int i = 0; i < count && !topics.isEmpty(); i++) {
            // Find topic from least represented category
            topics.sort(Comparator.comparingInt(t ->
                categoryCount.getOrDefault(t.getCategory(), 0)));

            Topic selectedTopic = topics.get(random.nextInt(Math.min(3, topics.size())));
            selected.add(selectedTopic);
            topics.remove(selectedTopic);
            categoryCount.merge(selectedTopic.getCategory(), 1, Integer::sum);
        }

        return selected;
    }

    /**
     * Complete mock interview with assessment
     */
    @Transactional
    public MockInterview completeMockInterview(Long mockInterviewId, Integer overallPerformance,
                                               Integer overallConfidence, String generalNotes,
                                               Integer pressureLevel,
                                               List<Map<String, Object>> questionAssessments) {
        MockInterview mockInterview = mockInterviewRepository.findById(mockInterviewId)
                .orElseThrow(() -> new ResourceNotFoundException("Mock interview not found"));

        mockInterview.setEndTime(LocalDateTime.now());
        mockInterview.setActualDuration((int) ChronoUnit.MINUTES.between(
                mockInterview.getStartTime(), mockInterview.getEndTime()));
        mockInterview.setOverallPerformance(overallPerformance);
        mockInterview.setOverallConfidence(overallConfidence);
        mockInterview.setGeneralNotes(generalNotes);
        mockInterview.setPressureLevel(pressureLevel);
        mockInterview.setCompleted(true);

        // Update question assessments
        for (Map<String, Object> assessment : questionAssessments) {
            Long questionId = ((Number) assessment.get("questionId")).longValue();
            MockInterviewQuestion question = mockInterview.getQuestions().stream()
                    .filter(q -> q.getId().equals(questionId))
                    .findFirst()
                    .orElse(null);

            if (question != null) {
                question.setPerformanceRating((Integer) assessment.get("performanceRating"));
                question.setTimeSpent((Integer) assessment.get("timeSpent"));
                question.setWhatWentWell((String) assessment.get("whatWentWell"));
                question.setWhatNeedsImprovement((String) assessment.get("whatNeedsImprovement"));
                question.setCouldSolveInRealInterview((Boolean) assessment.get("couldSolveInRealInterview"));
                question.setScratchpadContent((String) assessment.get("scratchpadContent"));

                // Create practice session
                PracticeSession session = new PracticeSession();
                session.setDuration(question.getTimeSpent());
                session.setPerformanceRating(question.getPerformanceRating());
                session.setWhatWentWell(question.getWhatWentWell());
                session.setMistakesMade(question.getWhatNeedsImprovement());
                session.setSessionNotes("Mock Interview Question");
                session.setSessionType(SessionType.MOCK_INTERVIEW);

                PracticeSession savedSession = sessionService.createSession(question.getTopic().getId(), session);
                question.setLinkedSession(savedSession);
            }
        }

        return mockInterviewRepository.save(mockInterview);
    }

    public List<MockInterview> getAllMockInterviews() {
        return mockInterviewRepository.findByCompletedTrueOrderByStartTimeDesc();
    }

    public MockInterview getMockInterviewById(Long id) {
        return mockInterviewRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Mock interview not found"));
    }

    public Map<String, Object> getMockInterviewAnalytics() {
        Map<String, Object> analytics = new HashMap<>();

        List<MockInterview> all = mockInterviewRepository.findByCompletedTrueOrderByStartTimeDesc();
        analytics.put("totalMockInterviews", all.size());

        if (!all.isEmpty()) {
            double avgPerformance = all.stream()
                    .filter(m -> m.getOverallPerformance() != null)
                    .mapToInt(MockInterview::getOverallPerformance)
                    .average()
                    .orElse(0.0);
            analytics.put("averagePerformance", avgPerformance);

            // Performance trend (last 5)
            List<Double> trend = all.stream()
                    .limit(5)
                    .filter(m -> m.getOverallPerformance() != null)
                    .map(m -> m.getOverallPerformance().doubleValue())
                    .collect(Collectors.toList());
            Collections.reverse(trend);
            analytics.put("performanceTrend", trend);

            // Success rate (performance >= 7)
            long successful = all.stream()
                    .filter(m -> m.getOverallPerformance() != null && m.getOverallPerformance() >= 7)
                    .count();
            analytics.put("successRate", (successful * 100.0) / all.size());
        }

        return analytics;
    }

    @Transactional
    public void deleteMockInterview(Long id) {
        mockInterviewRepository.deleteById(id);
    }
}
