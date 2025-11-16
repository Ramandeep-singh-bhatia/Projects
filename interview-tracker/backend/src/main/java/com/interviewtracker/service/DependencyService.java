package com.interviewtracker.service;

import com.interviewtracker.exception.ResourceNotFoundException;
import com.interviewtracker.model.Topic;
import com.interviewtracker.repository.TopicRepository;
import jakarta.transaction.Transactional;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.*;

@Service
public class DependencyService {

    @Autowired
    private TopicRepository topicRepository;

    @Autowired
    private TopicService topicService;

    /**
     * Add a prerequisite to a topic
     */
    @Transactional
    public void addPrerequisite(Long topicId, Long prerequisiteId) {
        Topic topic = topicService.getTopicById(topicId);
        Topic prerequisite = topicService.getTopicById(prerequisiteId);

        // Validate same category
        if (topic.getCategory() != prerequisite.getCategory()) {
            throw new IllegalArgumentException("Prerequisites must be from the same category");
        }

        // Validate no circular dependency
        if (wouldCreateCircularDependency(topicId, prerequisiteId)) {
            throw new IllegalArgumentException("Adding this prerequisite would create a circular dependency");
        }

        topic.getPrerequisites().add(prerequisite);
        topicRepository.save(topic);
    }

    /**
     * Remove a prerequisite from a topic
     */
    @Transactional
    public void removePrerequisite(Long topicId, Long prerequisiteId) {
        Topic topic = topicService.getTopicById(topicId);
        Topic prerequisite = topicService.getTopicById(prerequisiteId);

        topic.getPrerequisites().remove(prerequisite);
        topicRepository.save(topic);
    }

    /**
     * Get all prerequisites for a topic (direct only)
     */
    public Set<Topic> getPrerequisites(Long topicId) {
        Topic topic = topicService.getTopicById(topicId);
        return topic.getPrerequisites();
    }

    /**
     * Get all dependent topics (topics that depend on this one)
     */
    public Set<Topic> getDependentTopics(Long topicId) {
        Topic topic = topicService.getTopicById(topicId);
        return topic.getDependentTopics();
    }

    /**
     * Get complete learning path for a topic (all prerequisites recursively)
     */
    public List<Map<String, Object>> getLearningPath(Long topicId) {
        Topic topic = topicService.getTopicById(topicId);
        List<Map<String, Object>> path = new ArrayList<>();
        Set<Long> visited = new HashSet<>();

        buildLearningPath(topic, path, visited, 0);
        Collections.reverse(path); // Start from the base prerequisites

        return path;
    }

    private void buildLearningPath(Topic topic, List<Map<String, Object>> path,
                                   Set<Long> visited, int level) {
        if (visited.contains(topic.getId())) {
            return; // Already processed
        }

        visited.add(topic.getId());

        // Process prerequisites first (depth-first)
        for (Topic prereq : topic.getPrerequisites()) {
            buildLearningPath(prereq, path, visited, level + 1);
        }

        // Add current topic to path
        Map<String, Object> item = new HashMap<>();
        item.put("topicId", topic.getId());
        item.put("topicName", topic.getTopic());
        item.put("subtopic", topic.getSubtopic());
        item.put("confidence", topic.getConfidence());
        item.put("category", topic.getCategory());
        item.put("level", level);
        item.put("status", getTopicStatus(topic.getConfidence()));
        item.put("prerequisiteCount", topic.getPrerequisites().size());

        path.add(item);
    }

    private String getTopicStatus(int confidence) {
        if (confidence >= 8) return "STRONG";
        if (confidence >= 6) return "READY";
        if (confidence >= 4) return "IN_PROGRESS";
        return "WEAK";
    }

    /**
     * Get all topics that are blocked by unmet prerequisites
     */
    public List<Map<String, Object>> getBlockedTopics() {
        List<Topic> allTopics = topicRepository.findAll();
        List<Map<String, Object>> blocked = new ArrayList<>();

        for (Topic topic : allTopics) {
            List<Topic> unmetPrereqs = new ArrayList<>();

            for (Topic prereq : topic.getPrerequisites()) {
                if (prereq.getConfidence() < 6) {
                    unmetPrereqs.add(prereq);
                }
            }

            if (!unmetPrereqs.isEmpty()) {
                Map<String, Object> item = new HashMap<>();
                item.put("topicId", topic.getId());
                item.put("topicName", topic.getTopic());
                item.put("category", topic.getCategory());
                item.put("confidence", topic.getConfidence());
                item.put("unmetPrerequisites", unmetPrereqs.stream().map(p -> {
                    Map<String, Object> prereqMap = new HashMap<>();
                    prereqMap.put("id", p.getId());
                    prereqMap.put("name", p.getTopic());
                    prereqMap.put("confidence", p.getConfidence());
                    return prereqMap;
                }).toList());
                item.put("blockedBy", unmetPrereqs.size());

                blocked.add(item);
            }
        }

        return blocked;
    }

    /**
     * Validate that adding a prerequisite won't create a circular dependency
     */
    public boolean validateNonCircular(Long topicId, Long prerequisiteId) {
        return !wouldCreateCircularDependency(topicId, prerequisiteId);
    }

    private boolean wouldCreateCircularDependency(Long topicId, Long prerequisiteId) {
        if (topicId.equals(prerequisiteId)) {
            return true; // Topic can't be its own prerequisite
        }

        // Check if topicId is already a prerequisite of prerequisiteId (directly or indirectly)
        Topic prerequisiteTopic = topicService.getTopicById(prerequisiteId);
        return hasPrerequisite(prerequisiteTopic, topicId, new HashSet<>());
    }

    private boolean hasPrerequisite(Topic topic, Long searchId, Set<Long> visited) {
        if (visited.contains(topic.getId())) {
            return false; // Already checked
        }

        visited.add(topic.getId());

        for (Topic prereq : topic.getPrerequisites()) {
            if (prereq.getId().equals(searchId)) {
                return true; // Found circular dependency
            }

            if (hasPrerequisite(prereq, searchId, visited)) {
                return true; // Found in deeper level
            }
        }

        return false;
    }

    /**
     * Get topics that are ready to study (all prerequisites met)
     */
    public List<Topic> getReadyTopics() {
        List<Topic> allTopics = topicRepository.findAll();
        List<Topic> ready = new ArrayList<>();

        for (Topic topic : allTopics) {
            if (arePrerequisitesMet(topic)) {
                ready.add(topic);
            }
        }

        return ready;
    }

    /**
     * Check if all prerequisites for a topic are met (confidence >= 6)
     */
    public boolean arePrerequisitesMet(Topic topic) {
        for (Topic prereq : topic.getPrerequisites()) {
            if (prereq.getConfidence() < 6) {
                return false;
            }
        }
        return true;
    }

    /**
     * Get next logical topic to study based on completed prerequisites
     */
    public Optional<Topic> getNextLogicalTopic() {
        List<Topic> allTopics = topicRepository.findAll();

        // Find topics with all prerequisites met but low confidence
        return allTopics.stream()
                .filter(this::arePrerequisitesMet)
                .filter(t -> t.getConfidence() < 7)
                .min(Comparator.comparingInt(Topic::getConfidence)
                        .thenComparing(t -> t.getPrerequisites().size(), Comparator.reverseOrder()));
    }

    /**
     * Bulk import prerequisites from JSON structure
     */
    @Transactional
    public void importPrerequisites(List<Map<String, Object>> prerequisiteData) {
        for (Map<String, Object> entry : prerequisiteData) {
            String topicName = (String) entry.get("topic");
            @SuppressWarnings("unchecked")
            List<String> prereqNames = (List<String>) entry.get("prerequisites");

            // Find topic by name
            List<Topic> topics = topicRepository.findAll().stream()
                    .filter(t -> t.getTopic().equalsIgnoreCase(topicName))
                    .toList();

            if (topics.isEmpty()) {
                continue;
            }

            Topic topic = topics.get(0);

            // Find and add prerequisites
            for (String prereqName : prereqNames) {
                List<Topic> prereqs = topicRepository.findAll().stream()
                        .filter(t -> t.getTopic().equalsIgnoreCase(prereqName))
                        .filter(t -> t.getCategory() == topic.getCategory())
                        .toList();

                if (!prereqs.isEmpty()) {
                    Topic prereq = prereqs.get(0);
                    if (!wouldCreateCircularDependency(topic.getId(), prereq.getId())) {
                        topic.getPrerequisites().add(prereq);
                    }
                }
            }

            topicRepository.save(topic);
        }
    }
}
