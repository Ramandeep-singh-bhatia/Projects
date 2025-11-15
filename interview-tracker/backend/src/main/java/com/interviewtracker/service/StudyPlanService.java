package com.interviewtracker.service;

import com.interviewtracker.exception.ResourceNotFoundException;
import com.interviewtracker.model.*;
import com.interviewtracker.repository.StudyPlanItemRepository;
import com.interviewtracker.repository.StudyPlanRepository;
import com.interviewtracker.repository.TopicRepository;
import jakarta.transaction.Transactional;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.util.*;
import java.util.stream.Collectors;

@Service
public class StudyPlanService {

    @Autowired
    private StudyPlanRepository studyPlanRepository;

    @Autowired
    private StudyPlanItemRepository studyPlanItemRepository;

    @Autowired
    private TopicRepository topicRepository;

    @Autowired
    private DependencyService dependencyService;

    @Autowired
    private SettingsService settingsService;

    /**
     * Generate a smart study plan
     */
    @Transactional
    public StudyPlan generateStudyPlan(LocalDate interviewDate, Integer daysAvailable,
                                      Integer hoursPerDay, String priorityFocus,
                                      String topicSelection, List<Long> customTopicIds) {

        // Create study plan
        StudyPlan studyPlan = new StudyPlan();
        studyPlan.setName("Study Plan for Interview on " + interviewDate);
        studyPlan.setInterviewDate(interviewDate);
        studyPlan.setStartDate(LocalDate.now());
        studyPlan.setDaysAvailable(daysAvailable);
        studyPlan.setHoursPerDay(hoursPerDay);
        studyPlan.setPriorityFocus(priorityFocus);
        studyPlan.setTopicSelection(topicSelection);
        studyPlan.setActive(true);

        // Deactivate other active plans
        List<StudyPlan> activePlans = studyPlanRepository.findByActiveTrueOrderByCreatedDateDesc();
        activePlans.forEach(p -> p.setActive(false));
        studyPlanRepository.saveAll(activePlans);

        studyPlan = studyPlanRepository.save(studyPlan);

        // Get topics based on selection criteria
        List<Topic> selectedTopics = getTopicsForPlan(topicSelection, customTopicIds);

        // Score and sort topics
        List<ScoredTopic> scoredTopics = scoreTopics(selectedTopics, priorityFocus);

        // Sort topics respecting dependencies
        List<Topic> orderedTopics = orderTopicsWithDependencies(scoredTopics);

        // Calculate total available hours
        int totalAvailableHours = daysAvailable * hoursPerDay;

        // Distribute topics across days
        distributeTopicsAcrossDays(studyPlan, orderedTopics, daysAvailable, hoursPerDay, totalAvailableHours);

        return studyPlan;
    }

    private List<Topic> getTopicsForPlan(String topicSelection, List<Long> customTopicIds) {
        return switch (topicSelection) {
            case "ALL" -> topicRepository.findAll();
            case "WEAK" -> topicRepository.findByConfidenceLessThanEqual(5);
            case "CUSTOM" -> customTopicIds != null ? topicRepository.findAllById(customTopicIds) : new ArrayList<>();
            default -> topicRepository.findAll();
        };
    }

    private List<ScoredTopic> scoreTopics(List<Topic> topics, String priorityFocus) {
        Map<TopicCategory, Double> categoryWeights = getPriorityWeights(priorityFocus);

        return topics.stream().map(topic -> {
            double score = calculateTopicScore(topic);
            score *= categoryWeights.getOrDefault(topic.getCategory(), 1.0);
            return new ScoredTopic(topic, score);
        }).collect(Collectors.toList());
    }

    private Map<TopicCategory, Double> getPriorityWeights(String priorityFocus) {
        Map<TopicCategory, Double> weights = new HashMap<>();
        switch (priorityFocus) {
            case "DSA_HEAVY":
                weights.put(TopicCategory.DSA, 0.7);
                weights.put(TopicCategory.HLD, 0.1);
                weights.put(TopicCategory.LLD, 0.1);
                weights.put(TopicCategory.BEHAVIORAL, 0.1);
                break;
            case "SYSTEM_DESIGN_HEAVY":
                weights.put(TopicCategory.DSA, 0.2);
                weights.put(TopicCategory.HLD, 0.5);
                weights.put(TopicCategory.LLD, 0.3);
                weights.put(TopicCategory.BEHAVIORAL, 0.0);
                break;
            default: // BALANCED
                weights.put(TopicCategory.DSA, 0.25);
                weights.put(TopicCategory.HLD, 0.25);
                weights.put(TopicCategory.LLD, 0.25);
                weights.put(TopicCategory.BEHAVIORAL, 0.25);
        }
        return weights;
    }

    private double calculateTopicScore(Topic topic) {
        double confidenceWeight = (11.0 - topic.getConfidence()) / 10.0;
        double difficultyMultiplier = 1.0;

        if (topic instanceof DSATopic) {
            difficultyMultiplier = switch (((DSATopic) topic).getDifficulty()) {
                case EASY -> 1.0;
                case MEDIUM -> 1.5;
                case HARD -> 2.0;
            };
        }

        long daysSinceStudied = topic.getLastStudiedDate() != null ?
                java.time.temporal.ChronoUnit.DAYS.between(topic.getLastStudiedDate(), LocalDate.now().atStartOfDay()) : 90;

        return confidenceWeight * difficultyMultiplier * Math.min(daysSinceStudied / 7.0, 3.0);
    }

    private List<Topic> orderTopicsWithDependencies(List<ScoredTopic> scoredTopics) {
        scoredTopics.sort(Comparator.comparingDouble(ScoredTopic::score).reversed());

        List<Topic> ordered = new ArrayList<>();
        Set<Long> added = new HashSet<>();

        for (ScoredTopic st : scoredTopics) {
            addTopicWithPrereqs(st.topic(), ordered, added);
        }

        return ordered;
    }

    private void addTopicWithPrereqs(Topic topic, List<Topic> ordered, Set<Long> added) {
        if (added.contains(topic.getId())) {
            return;
        }

        // Add prerequisites first
        for (Topic prereq : topic.getPrerequisites()) {
            addTopicWithPrereqs(prereq, ordered, added);
        }

        ordered.add(topic);
        added.add(topic.getId());
    }

    private void distributeTopicsAcrossDays(StudyPlan plan, List<Topic> topics,
                                           int totalDays, int hoursPerDay, int totalHours) {
        LocalDate currentDate = plan.getStartDate();
        int displayOrder = 0;
        int daysSinceRest = 0;

        // Calculate how many topics to include based on available time
        int minutesAvailable = totalHours * 60;
        List<Topic> includedTopics = new ArrayList<>();
        int minutesAllocated = 0;

        for (Topic topic : topics) {
            int estimatedMinutes = estimateTopicTime(topic);
            if (minutesAllocated + estimatedMinutes <= minutesAvailable) {
                includedTopics.add(topic);
                minutesAllocated += estimatedMinutes;
            } else {
                break;
            }
        }

        // Distribute across days
        int priorityPhaseEnd = (int) (totalDays * 0.6); // First 60% for new/priority topics
        int consolidationStart = (int) (totalDays * 0.8); // Last 20% for consolidation

        int topicsPerDay = Math.max(1, includedTopics.size() / totalDays);
        int topicIndex = 0;

        for (int day = 0; day < totalDays && topicIndex < includedTopics.size(); day++) {
            // Insert rest day every 5 days
            daysSinceRest++;
            if (daysSinceRest == 5 && day < totalDays - 3) {
                StudyPlanItem restDay = new StudyPlanItem();
                restDay.setStudyPlan(plan);
                restDay.setScheduledDate(currentDate);
                restDay.setItemType(StudyPlanItemType.REST);
                restDay.setEstimatedMinutes(0);
                restDay.setDisplayOrder(displayOrder++);
                plan.getItems().add(restDay);

                currentDate = currentDate.plusDays(1);
                daysSinceRest = 0;
                continue;
            }

            // Consolidation days before interview
            if (day >= consolidationStart) {
                // Add high-priority topics for quick review
                for (int i = 0; i < 3 && i < includedTopics.size(); i++) {
                    Topic topic = includedTopics.get(i);
                    StudyPlanItem item = new StudyPlanItem();
                    item.setStudyPlan(plan);
                    item.setTopic(topic);
                    item.setScheduledDate(currentDate);
                    item.setItemType(StudyPlanItemType.CONSOLIDATION);
                    item.setEstimatedMinutes(20); // Quick review
                    item.setDisplayOrder(displayOrder++);
                    plan.getItems().add(item);
                }
            } else {
                // Regular study day
                int topicsForToday = Math.min(topicsPerDay, includedTopics.size() - topicIndex);
                int minutesPerDayAvailable = hoursPerDay * 60;
                int minutesUsed = 0;

                for (int t = 0; t < topicsForToday && topicIndex < includedTopics.size(); t++, topicIndex++) {
                    Topic topic = includedTopics.get(topicIndex);
                    int estimatedMinutes = estimateTopicTime(topic);

                    if (minutesUsed + estimatedMinutes <= minutesPerDayAvailable * 1.1) { // Allow 10% overflow
                        StudyPlanItem item = new StudyPlanItem();
                        item.setStudyPlan(plan);
                        item.setTopic(topic);
                        item.setScheduledDate(currentDate);
                        item.setItemType(topic.getSessionCount() == 0 ?
                                StudyPlanItemType.NEW_TOPIC : StudyPlanItemType.REVISION);
                        item.setEstimatedMinutes(estimatedMinutes);
                        item.setDisplayOrder(displayOrder++);
                        plan.getItems().add(item);

                        minutesUsed += estimatedMinutes;
                    }
                }
            }

            currentDate = currentDate.plusDays(1);
        }

        studyPlanRepository.save(plan);
    }

    private int estimateTopicTime(Topic topic) {
        if (topic.getSessionCount() > 0) {
            int avgTime = topic.getTotalTimeSpent() / topic.getSessionCount();
            return topic.getLastStudiedDate() != null ? (int) (avgTime * 0.6) : avgTime; // Revision takes less time
        }
        return 60; // Default for new topics
    }

    public StudyPlan getActivePlan() {
        return studyPlanRepository.findFirstByActiveTrueOrderByCreatedDateDesc().orElse(null);
    }

    public StudyPlan getPlanById(Long id) {
        return studyPlanRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Study plan not found"));
    }

    public List<StudyPlan> getAllPlans() {
        return studyPlanRepository.findAllByOrderByCreatedDateDesc();
    }

    @Transactional
    public void markItemComplete(Long itemId, Integer actualMinutes) {
        StudyPlanItem item = studyPlanItemRepository.findById(itemId)
                .orElseThrow(() -> new ResourceNotFoundException("Study plan item not found"));
        item.setCompleted(true);
        item.setActualMinutesSpent(actualMinutes);
        studyPlanItemRepository.save(item);
    }

    @Transactional
    public void deletePlan(Long id) {
        studyPlanRepository.deleteById(id);
    }

    private record ScoredTopic(Topic topic, double score) {}
}
